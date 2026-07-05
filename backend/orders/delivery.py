"""Delivery zones and fees — the authoritative source for delivery pricing."""

DELIVERY_ZONES = [
    {
        "group": "Island (Before Sangotedo)",
        "locations": [
            ("Victoria Island (VI)", 4000),
            ("Ikoyi", 4000),
            ("Banana Island", 4000),
            ("Oniru", 4000),
            ("Lekki Phase 1", 4000),
            ("Lekki Phase 2", 4000),
            ("Ikate", 4000),
            ("Osapa London", 4000),
            ("Chevron", 4000),
            ("Ikota", 4000),
            ("Ajah", 4000),
            ("VGC", 4000),
            ("Abraham Adesanya", 4000),
        ],
    },
    {
        "group": "Island (Sangotedo & Beyond)",
        "locations": [
            ("Sangotedo", 4000),
            ("Ogidan", 4000),
            ("Monastery Road", 4000),
            ("Awoyaya", 4000),
            ("Mayfair Gardens", 4000),
            ("Lakowe", 4000),
            ("Bogije", 4000),
            ("Eleko", 4000),
            ("Epe", 4000),
            ("Ibeju-Lekki", 4000),
            ("Other parts of Lagos Island not mentioned", 3800),
        ],
    },
    {
        "group": "Mainland",
        "locations": [
            ("Ojo", 4500),
            ("Alaba", 4500),
            ("Festac Town", 4500),
            ("Amuwo-Odofin", 4500),
            ("Satellite Town", 4500),
            ("Trade Fair", 4500),
            ("Mile 2", 4500),
            ("Orile", 4500),
            ("Apapa", 4500),
            ("Badagry", 4500),
            ("Agbara", 4500),
            ("Gbagada", 4500),
            ("Ketu", 4500),
            ("Mile 12", 4500),
            ("Magodo", 4500),
            ("Ikorodu", 4500),
            ("Alagbole", 4500),
            ("Ipaja", 4500),
            ("Iyana Ipaja", 4500),
            ("Ayobo", 4500),
            ("Egbeda", 4500),
            ("Idimu", 4500),
            ("Isheri Osun", 4500),
            ("Ejigbo", 4500),
            ("Oshodi", 4500),
            ("Isolo", 4500),
            ("Mushin", 4500),
            ("Ilupeju", 4500),
            ("Yaba", 4500),
            ("Surulere", 4500),
            ("Ebute Metta", 4500),
            ("Ikeja", 4500),
            ("Maryland", 4500),
            ("Ogba", 4500),
            ("Ojodu", 4500),
            ("Berger & Environs", 4500),
            ("Agege", 4500),
            ("Ifako-Ijaiye", 4500),
            ("Abule Egba", 4500),
            ("Alagbado", 4500),
            ("Alakuko", 4500),
            ("Iju", 4500),
            ("Other parts of Lagos Mainland not mentioned", 4300),
        ],
    },
]

# Flat lookup: location name -> fee
DELIVERY_FEES = {
    loc: fee for zone in DELIVERY_ZONES for (loc, fee) in zone["locations"]
}

DEFAULT_FEE = 4500


def get_delivery_fee(location):
    return DELIVERY_FEES.get(location, DEFAULT_FEE)
