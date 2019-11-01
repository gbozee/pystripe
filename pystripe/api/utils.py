def charge_data(raw_data, full_auth=False):
    data = raw_data["object"]
    if full_auth:
        return data
    status = data.get("status")
    amount_refunded = data.get("amount_refunded")
    if amount_refunded:
        amount_refunded = amount_refunded / 100
    amount = data["amount"]
    session = data["id"]
    payment_details = data["payment_method_details"]["card"]
    customer = data["customer"]
    currency = data["currency"]
    failure_code = data.get("failure_code")
    failure_message = data.get("failure_message")
    _id = data["id"]
    outcome = data.get("outcome")
    failure = {}
    if failure_code:
        failure = {"code": failure_code, "message": failure_message}
    return {
        "id": session,
        "amount": amount / 100,
        "currency": currency,
        "customer": customer,
        "payment_details": payment_details,
        "status": status,
        "amount_refunded": amount_refunded,
        "failure": failure,
        "outcome": outcome,
        "amount_refunded": amount_refunded,
    }
