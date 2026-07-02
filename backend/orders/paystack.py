import requests
from django.conf import settings

BASE_URL = "https://api.paystack.co"


def initialize_transaction(email, amount_naira, reference, callback_url=None):
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": email,
        "amount": int(amount_naira * 100),  # kobo
        "reference": reference,
        "currency": "NGN",
    }
    if callback_url:
        payload["callback_url"] = callback_url
    response = requests.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def verify_transaction(reference):
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()
