"""Delivery zones and fees — the authoritative source for delivery pricing."""

DELIVERY_ZONES = [
    {
        "group": "Island (Before Sangotedo)",
        "locations": [
            ("Victoria Island (VI)", 3500),
            ("Ikoyi", 3500),
            ("Banana Island", 3500),
            ("Oniru", 3500),
            ("Lekki Phase 1", 3500),
            ("Lekki Phase 2", 3500),
            ("Ikate", 3500),
            ("Osapa London", 3500),
            ("Chevron", 3500),
            ("Ikota", 3500),
            ("Ajah", 3500),
            ("VGC", 3500),
            ("Abraham Adesanya", 3500),
        ],
    },
    {
        "group": "Island (Sangotedo & Beyond)",
        "locations": [
            ("Sangotedo", 3500),
            ("Ogidan", 3500),
            ("Monastery Road", 3500),
            ("Awoyaya", 3500),
            ("Mayfair Gardens", 3500),
            ("Lakowe", 3500),
            ("Bogije", 3500),
            ("Eleko", 3500),
            ("Epe", 3500),
            ("Ibeju-Lekki", 3500),
            ("Other parts of Lagos Island not mentioned", 3300),
        ],
    },
    {
        "group": "Mainland",
        "locations": [
            ("Ojo", 5500),
            ("Alaba", 5500),
            ("Festac Town", 5500),
            ("Amuwo-Odofin", 5500),
            ("Satellite Town", 5500),
            ("Trade Fair", 5500),
            ("Mile 2", 5500),
            ("Orile", 5500),
            ("Apapa", 5500),
            ("Badagry", 5500),
            ("Agbara", 5500),
            ("Gbagada", 5500),
            ("Ketu", 5500),
            ("Mile 12", 5500),
            ("Magodo", 5500),
            ("Ikorodu", 5500),
            ("Alagbole", 5500),
            ("Ipaja", 5500),
            ("Iyana Ipaja", 5500),
            ("Ayobo", 5500),
            ("Egbeda", 5500),
            ("Idimu", 5500),
            ("Isheri Osun", 5500),
            ("Ejigbo", 5500),
            ("Oshodi", 5500),
            ("Isolo", 5500),
            ("Mushin", 5500),
            ("Ilupeju", 5500),
            ("Yaba", 5500),
            ("Surulere", 5500),
            ("Ebute Metta", 5500),
            ("Ikeja", 5500),
            ("Maryland", 5500),
            ("Ogba", 5500),
            ("Ojodu", 5500),
            ("Berger & Environs", 5500),
            ("Agege", 5500),
            ("Ifako-Ijaiye", 5500),
            ("Abule Egba", 5500),
            ("Alagbado", 5500),
            ("Alakuko", 5500),
            ("Iju", 5500),
            ("Other parts of Lagos Mainland not mentioned", 5300),
        ],
    },
]

# Flat lookup: location name -> fee
DELIVERY_FEES = {
    loc: fee for zone in DELIVERY_ZONES for (loc, fee) in zone["locations"]
}

DEFAULT_FEE = 5500


def get_delivery_fee(location):
    return DELIVERY_FEES.get(location, DEFAULT_FEE)
