from pystripe import utils


def test_verify_payment_failed(mocker, stripe_api: utils.StripeAPI):
    mock_retrieve = mocker.patch("pystripe.utils.stripe.Charge.retrieve")
    mock_retrieve.return_value = {
        "amount": 2000,
        "currency": "ngn",
        "paid": False,
        "status": "failed",
    }
    response = stripe_api.verify_payment(
        "ch_1FXNg3Hv0Y0PURSq6tlZoChw", amount=2000, currency="usd"
    )
    assert not response[0]
    assert response[1] == "Transaction Failed"


charge_response = {
    "amount": 2000,
    "amount_refunded": 0,
    "application": None,
    "application_fee": None,
    "application_fee_amount": None,
    "balance_transaction": "txn_1FZoRwHv0Y0PURSqgcComCIX",
    "billing_details": {
        "address": {
            "city": None,
            "country": None,
            "line1": None,
            "line2": None,
            "postal_code": None,
            "state": None,
        },
        "email": None,
        "name": None,
        "phone": None,
    },
    "captured": True,
    "created": 1572569832,
    "currency": "usd",
    "customer": None,
    "description": None,
    "destination": None,
    "dispute": None,
    "failure_code": None,
    "failure_message": None,
    "fraud_details": {},
    "id": "ch_1FZoRwHv0Y0PURSqnDbvKK42",
    "invoice": None,
    "livemode": False,
    "metadata": {},
    "object": "charge",
    "on_behalf_of": None,
    "order": None,
    "outcome": {
        "network_status": "approved_by_network",
        "reason": None,
        "risk_level": "normal",
        "risk_score": 12,
        "seller_message": "Payment complete.",
        "type": "authorized",
    },
    "paid": True,
    "payment_intent": None,
    "payment_method": "card_1FZoRwHv0Y0PURSq7drRCuCw",
    "payment_method_details": {
        "card": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": None,
                "cvc_check": None,
            },
            "country": "US",
            "exp_month": 11,
            "exp_year": 2020,
            "fingerprint": "yIwZJF6Qz10rsS7J",
            "funding": "credit",
            "installments": None,
            "last4": "4242",
            "network": "visa",
            "three_d_secure": None,
            "wallet": None,
        },
        "type": "card",
    },
    "receipt_email": None,
    "receipt_number": None,
    "receipt_url": "https://pay.stripe.com/receipts/acct_1EJOOLHv0Y0PURSq/ch_1FZoRwHv0Y0PURSqnDbvKK42/rcpt_G60SjDYrDpVUwUczznvTsno16zrgEm4",
    "refunded": False,
    "refunds": {
        "data": [],
        "has_more": False,
        "object": "list",
        "total_count": 0,
        "url": "/v1/charges/ch_1FZoRwHv0Y0PURSqnDbvKK42/refunds",
    },
    "review": None,
    "shipping": None,
    "source": {
        "address_city": None,
        "address_country": None,
        "address_line1": None,
        "address_line1_check": None,
        "address_line2": None,
        "address_state": None,
        "address_zip": None,
        "address_zip_check": None,
        "brand": "Visa",
        "country": "US",
        "customer": None,
        "cvc_check": None,
        "dynamic_last4": None,
        "exp_month": 11,
        "exp_year": 2020,
        "fingerprint": "yIwZJF6Qz10rsS7J",
        "funding": "credit",
        "id": "card_1FZoRwHv0Y0PURSq7drRCuCw",
        "last4": "4242",
        "metadata": {},
        "name": None,
        "object": "card",
        "tokenization_method": None,
    },
    "source_transfer": None,
    "statement_descriptor": None,
    "statement_descriptor_suffix": None,
    "status": "succeeded",
    "transfer_data": None,
    "transfer_group": None,
}


def test_verify_payment_success(mocker, stripe_api):
    mock_retrieve = mocker.patch("pystripe.utils.stripe.Charge.retrieve")
    mock_retrieve.return_value = charge_response
    response = stripe_api.verify_payment(
        "ch_1FXNg3Hv0Y0PURSq6tlZoChw", amount=20, currency="usd"
    )
    assert response[0]
    assert response[1] == "Verification successful"
    assert response[2] == {
        "id": "ch_1FZoRwHv0Y0PURSqnDbvKK42",
        "amount": 20.0,
        "currency": "usd",
        "customer": None,
        "payment_details": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": None,
                "cvc_check": None,
            },
            "country": "US",
            "exp_month": 11,
            "exp_year": 2020,
            "fingerprint": "yIwZJF6Qz10rsS7J",
            "funding": "credit",
            "installments": None,
            "last4": "4242",
            "network": "visa",
            "three_d_secure": None,
            "wallet": None,
        },
        "status": "succeeded",
        "amount_refunded": 0,
        "failure": {},
        "outcome": {
            "network_status": "approved_by_network",
            "reason": None,
            "risk_level": "normal",
            "risk_score": 12,
            "seller_message": "Payment complete.",
            "type": "authorized",
        },
    }
