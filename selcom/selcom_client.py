import os
from dotenv import load_dotenv
from apigwClient import Client  # uses the one you uploaded

load_dotenv()

# Setup Selcom Client
BASE_URL = os.getenv("SELCOM_BASE_URL")
API_KEY = os.getenv("SELCOM_API_KEY")
SECRET_KEY = os.getenv("SELCOM_SECRET_KEY")
VENDOR = os.getenv("SELCOM_VENDOR")

client = Client(BASE_URL, API_KEY, SECRET_KEY)

async def create_checkout_order(order_id: str, amount: int, name: str, email: str, phone: str):
    payload = {
        "vendor": VENDOR,
        "order_id": order_id,
        "buyer_email": email,
        "buyer_name": name,
        "buyer_phone": phone,
        "amount": amount,
        "currency": "TZS",
        "buyer_remarks": "Alumni donation",
        "merchant_remarks": "Alumni system",
        "no_of_items": 1
    }

    path = "/v1/checkout/create-order-minimal"
    return client.postFunc(path, payload)
