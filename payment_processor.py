import time
import uuid


def process_upi_payment(upi_id, amount):
    """Simulates processing a UPI payment."""
    time.sleep(1.5)  # Simulate network delay

    if not upi_id or "@" not in upi_id:
        return {"status": "failed", "message": "Invalid UPI ID. Must contain '@'."}

    return {
        "status": "success",
        "txn_id": f"UPI_{uuid.uuid4().hex[:10].upper()}",
        "message": f"Successfully paid ₹{amount} via UPI."
    }


def process_card_payment(card_name, card_number, expiry, cvv, amount):
    """Simulates processing a Credit/Debit card."""
    time.sleep(2)  # Simulate banking gateway delay

    # Basic mock validation
    if len(card_number.replace(" ", "")) != 16:
        return {"status": "failed", "message": "Invalid Card Number. Must be 16 digits."}
    if not card_name or not expiry or not cvv:
        return {"status": "failed", "message": "Please fill in all card details."}

    return {
        "status": "success",
        "txn_id": f"TXN_{uuid.uuid4().hex[:12].upper()}",
        "message": f"Successfully paid ₹{amount} via Card."
    }


def process_cash_payment(amount):
    """Registers a Cash on Delivery order."""
    time.sleep(0.5)
    return {
        "status": "success",
        "txn_id": f"COD_{uuid.uuid4().hex[:8].upper()}",
        "message": f"Order placed for ₹{amount}. Pay cash at the counter."
    }