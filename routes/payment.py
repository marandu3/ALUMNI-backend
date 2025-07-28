from fastapi import APIRouter, HTTPException
from selcom.selcom_client import create_checkout_order
from models.payment import PaymentRecord
from database.config import payment_collection
import uuid

router = APIRouter()

@router.post("/pay")
async def initiate_payment(name: str, email: str, phone: str, amount: int):
    order_id = str(uuid.uuid4())[:8]

    # ✅ Await the async function call
    response = await create_checkout_order(order_id, amount, name, email, phone)

    # ✅ Use .get safely
    status = response.get("result", "unknown")

    # ✅ Add purpose optionally or default
    record = PaymentRecord(
        name=name,
        email=email,
        phone=phone,
        amount=amount,
        purpose="Alumni Payment",
        status=status,
        order_id=order_id,
        selcom_response=response
    )

    # ✅ Await MongoDB insert if using Motor
    payment_collection.insert_one(record.dict())

    return {
        "message": "Payment initiated and logged",
        "order_id": order_id,
        "status": status,
        "selcom_response": response
    }


@router.get("/payments")
async def list_payments():
    payments = payment_collection.find({}, {"_id": 0})
    payment_list = [PaymentRecord(**payment) for payment in payments]  # Using list comprehension for cleaner code
    if not payment_list:
        raise HTTPException(status_code=404, detail="No users found")
    return payment_list
    return payment_list  # Return the list of payment records
