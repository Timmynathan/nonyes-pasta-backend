import hashlib
import hmac
import json
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Product, ProductSize, AddOn
from . import paystack
from .models import Order, OrderItem, PendingOrder
from .serializers import OrderSerializer

DELIVERY_FEE = 1500


class DebugConfigView(APIView):
    """TEMPORARY — reports what env config the live server sees. Remove after debugging."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        import sys
        tok = settings.TELEGRAM_BOT_TOKEN
        chat = settings.TELEGRAM_CHAT_ID
        result = {
            'python_version': sys.version,
            'telegram_token_set': bool(tok),
            'telegram_token_len': len(tok),
            'telegram_token_preview': (tok[:8] + '...' + tok[-4:]) if tok else '',
            'telegram_chat_set': bool(chat),
            'telegram_chat_value': repr(chat),
            'owner_email': repr(settings.OWNER_EMAIL),
            'email_host_user_set': bool(settings.EMAIL_HOST_USER),
        }
        # Run the REAL notification function on the latest order and report any hidden error
        import traceback
        last = Order.objects.order_by('-created_at').first()
        if last:
            lines = []
            for it in last.items.all():
                pname = it.product.name if it.product else 'Unknown'
                lines.append(f'  - {it.quantity}x {pname}')
            try:
                _send_owner_notification(last, 'debug@example.com', lines)
                result['notification_ran'] = 'OK — check Telegram'
            except Exception:
                result['notification_error'] = traceback.format_exc()
        else:
            result['notification_ran'] = 'no orders to test with'
        return Response(result)


class InitiateCheckoutView(APIView):
    """
    Validates the cart, stores details in PendingOrder, initialises a
    Paystack transaction and returns the authorization_url.
    No Order row is created here — that happens in the webhook.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email', '').strip()
        delivery_name = data.get('delivery_name', '').strip()
        delivery_phone = data.get('delivery_phone', '').strip()
        delivery_address = data.get('delivery_address', '').strip()
        cart = data.get('cart', [])

        if not all([email, delivery_name, delivery_phone, delivery_address, cart]):
            return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate cart items and calculate total
        subtotal = 0
        for item in cart:
            try:
                product = Product.objects.get(pk=item['product_id'])
            except Product.DoesNotExist:
                return Response({'detail': f"Product {item['product_id']} not found."}, status=400)

            unit_price = product.base_price
            if item.get('size_id'):
                try:
                    size = ProductSize.objects.get(pk=item['size_id'], product=product)
                    unit_price = size.price
                except ProductSize.DoesNotExist:
                    return Response({'detail': 'Invalid size.'}, status=400)

            add_ons = AddOn.objects.filter(pk__in=item.get('add_on_ids', []))
            unit_price = float(unit_price) + sum(float(a.price) for a in add_ons)
            subtotal += unit_price * item.get('quantity', 1)

        total = subtotal + DELIVERY_FEE
        reference = f"NP-{uuid.uuid4().hex[:12]}"

        PendingOrder.objects.create(
            reference=reference,
            email=email,
            delivery_name=delivery_name,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            cart=cart,
        )

        frontend_origin = request.headers.get('Origin', f"{request.scheme}://{request.get_host()}")
        callback_url = f"{frontend_origin}/track/{reference}"

        paystack_data = paystack.initialize_transaction(
            email=email,
            amount_naira=total,
            reference=reference,
            callback_url=callback_url,
        )

        return Response({'authorization_url': paystack_data['data']['authorization_url'], 'reference': reference})


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    """
    Paystack POSTs here after a successful payment.
    Verifies the HMAC signature, creates the Order, sends notification email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Verify Paystack signature
        signature = request.headers.get('X-Paystack-Signature', '')
        secret = settings.PAYSTACK_SECRET_KEY.encode()
        expected = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return Response({'detail': 'Invalid signature.'}, status=400)

        payload = json.loads(request.body)
        if payload.get('event') != 'charge.success':
            return Response({'detail': 'Ignored.'}, status=200)

        reference = payload['data']['reference']

        # Idempotency — skip if order already created
        if Order.objects.filter(paystack_reference=reference).exists():
            return Response({'detail': 'Already processed.'}, status=200)

        try:
            pending = PendingOrder.objects.get(reference=reference)
        except PendingOrder.DoesNotExist:
            return Response({'detail': 'Pending order not found.'}, status=404)

        # Create the real order
        order = Order.objects.create(
            delivery_name=pending.delivery_name,
            delivery_phone=pending.delivery_phone,
            delivery_address=pending.delivery_address,
            delivery_fee=DELIVERY_FEE,
            status=Order.STATUS_PAID,
            paystack_reference=reference,
        )

        subtotal = 0
        item_lines = []
        for item in pending.cart:
            product = Product.objects.get(pk=item['product_id'])
            unit_price = float(product.base_price)

            size = None
            size_label = ''
            if item.get('size_id'):
                size = ProductSize.objects.get(pk=item['size_id'])
                unit_price = float(size.price)
                size_label = f" ({size.name})"

            add_ons = AddOn.objects.filter(pk__in=item.get('add_on_ids', []))
            unit_price += sum(float(a.price) for a in add_ons)
            qty = item.get('quantity', 1)
            line_total = unit_price * qty
            subtotal += line_total
            spice = item.get('spice_level', 'mild')

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                size=size,
                quantity=qty,
                unit_price=unit_price,
                line_total=line_total,
                spice_level=spice,
            )
            order_item.add_ons.set(add_ons)
            spice_label = ' 🌶🌶' if spice == 'extra' else ''
            item_lines.append(f"  • {qty}x {product.name}{size_label}{spice_label} — ₦{line_total:,.0f}")

        order.subtotal = subtotal
        order.total = subtotal + DELIVERY_FEE
        order.save()

        customer_email = pending.email
        pending.delete()

        # Notify Nonye — must never break order creation or the webhook response
        try:
            _send_owner_notification(order, customer_email, item_lines)
        except Exception:
            pass

        return Response({'detail': 'Order created.'}, status=200)


def _send_owner_notification(order, customer_email, item_lines):
    # OWNER_EMAIL may be a single address or a comma-separated list
    owner_emails = [e.strip() for e in settings.OWNER_EMAIL.split(',') if e.strip()]

    items_text = '\n'.join(item_lines)
    message = f"""New order received! 🎉

Order Number : {order.order_number}
Customer     : {order.delivery_name}
Phone        : {order.delivery_phone}
Email        : {customer_email}
Address      : {order.delivery_address}

Items:
{items_text}

Subtotal     : ₦{order.subtotal:,.0f}
Delivery Fee : ₦{order.delivery_fee:,.0f}
TOTAL PAID   : ₦{order.total:,.0f}

Payment confirmed via Paystack. Reference: {order.paystack_reference}
"""
    # Telegram first — it uses HTTPS and works even where outbound SMTP is blocked
    _send_telegram(message)

    if owner_emails:
        try:
            send_mail(
                subject=f"[Nonye's Pasta] New Order — {order.order_number}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=owner_emails,
                fail_silently=True,
            )
        except Exception:
            pass


def _send_telegram(message):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={'chat_id': chat_id, 'text': message},
            timeout=10,
        )
    except Exception:
        pass


# ── Legacy endpoints kept for order tracking page ──────────────────────────

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'order_number'


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
