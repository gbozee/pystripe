from pystripe.api import signals
from pystripe import utils
from dispatch import receiver
import pytest


@receiver(signals.successful_payment_signal)
def signal_called(sender, **kwargs):
    kwargs.pop("signal", None)
    generic_function(**kwargs)


def generic_function(**params):
    print(params)


@receiver(signals.failed_payment_signal)
def signal_called_2(sender, **kwargs):
    kwargs.pop("signal", None)
    generic_function(**kwargs)


@pytest.fixture
def mock_generic_func(mocker):
    mock_successful_call = mocker.patch("test_webhooks.generic_function")
    mock_digest = mocker.patch("stripe.WebhookSignature.verify_header")
    mock_digest.return_value = True
    return mock_successful_call


def test_successful_charge_webhook_signal(
    mock_generic_func, stripe_api: utils.StripeAPI
):
    body = """{
        "id": "evt_1FZp49Hv0Y0PURSqIxXfx6W1", 
        "object": "event", 
        "api_version": "2019-03-14", 
        "created": 1572572201, 
        "data": {
            "object": {
                "id": "ch_1FZp48Hv0Y0PURSq0buZ6d6f", 
                "object": "charge", 
                "amount": 2000, 
                "amount_refunded": 0, 
                "application": null, 
                "application_fee": null, 
                "application_fee_amount": null, 
                "balance_transaction": "txn_1FZp48Hv0Y0PURSqV70KLTLF", 
                "billing_details": {
                    "address": {"city": null, "country": null, "line1": null, "line2": null, "postal_code": null, "state": null}, 
                    "email": null, 
                    "name": null, 
                    "phone": null
                }, 
                "captured": true, "created": 1572572200, "currency": "usd", "customer": null, "description": null, "destination": null, "dispute": null, "failure_code": null, "failure_message": null, "fraud_details": {}, "invoice": null, "livemode": false, "metadata": {}, "on_behalf_of": null, "order": null, 
                "outcome": {"network_status": "approved_by_network", "reason": null, "risk_level": "normal", "risk_score": 42, "seller_message": "Payment complete.", "type": "authorized"}, 
                "paid": true, 
                "payment_intent": null, 
                "payment_method": "card_1FZp48Hv0Y0PURSqsmipr0Rv", 
                "payment_method_details": {"card": {"brand": "visa", "checks": {"address_line1_check": null, "address_postal_code_check": null, "cvc_check": null}, "country": "US", "exp_month": 11, "exp_year": 2020, "fingerprint": "yIwZJF6Qz10rsS7J", "funding": "credit", "installments": null, "last4": "4242", "network": "visa", "three_d_secure": null, "wallet": null}, "type": "card"}, "receipt_email": null, "receipt_number": null, "receipt_url": "https://pay.stripe.com/receipts/acct_1EJOOLHv0Y0PURSq/ch_1FZp48Hv0Y0PURSq0buZ6d6f/rcpt_G616Ubt8hAj7Th4vdY2MfK34OAIxOPi", "refunded": false, "refunds": {"object": "list", "data": [], "has_more": false, "total_count": 0, "url": "/v1/charges/ch_1FZp48Hv0Y0PURSq0buZ6d6f/refunds"}, "review": null, "shipping": null, "source": {"id": "card_1FZp48Hv0Y0PURSqsmipr0Rv", "object": "card", "address_city": null, "address_country": null, "address_line1": null, "address_line1_check": null, "address_line2": null, "address_state": null, "address_zip": null, "address_zip_check": null, "brand": "Visa", "country": "US", "customer": null, "cvc_check": null, "dynamic_last4": null, "exp_month": 11, "exp_year": 2020, "fingerprint": "yIwZJF6Qz10rsS7J", "funding": "credit", "last4": "4242", "metadata": {}, "name": null, "tokenization_method": null}, "source_transfer": null, "statement_descriptor": null, "statement_descriptor_suffix": null, "status": "succeeded", "transfer_data": null, "transfer_group": null}}, "livemode": false, "pending_webhooks": 3, 
                "request": {"id": "req_fGRGYYasLgdcRq", "idempotency_key": null}, 
        "type": "charge.succeeded"
    }"""
    stripe_api.webhook_api.verify("unique_signature", body)
    mock_generic_func.assert_called_once_with(
        event="charge.succeeded",
        data={
            "id": "ch_1FZp48Hv0Y0PURSq0buZ6d6f",
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
                "risk_score": 42,
                "seller_message": "Payment complete.",
                "type": "authorized",
            },
        },
    )


def test_failed_payment_transfer(mock_generic_func, stripe_api):
    body = """
    {"id": "evt_1FZpYhHv0Y0PURSqOU8uvKJD", "object": "event", "api_version": "2019-03-14", "created": 1572574095, "data": {"object": {"id": "ch_1FZpYhHv0Y0PURSqnaxbrowv", "object": "charge", "amount": 2000, "amount_refunded": 0, "application": null, "application_fee": null, "application_fee_amount": null, "balance_transaction": null, "billing_details": {"address": {"city": null, "country": null, "line1": null, "line2": null, "postal_code": 
null, "state": null}, "email": null, "name": null, "phone": null}, "captured": false, "created": 1572574095, "currency": "usd", "customer": null, "description": null, "destination": null, "dispute": null, "failure_code": "card_declined", "failure_message": "Your card was declined.", "fraud_details": {}, "invoice": null, "livemode": false, "metadata": {}, "on_behalf_of": null, "order": null, "outcome": {"network_status": "declined_by_network", "reason": "generic_decline", "risk_level": "normal", "risk_score": 55, "seller_message": "The bank did not return any further details with this decline.", "type": "issuer_declined"}, "paid": false, "payment_intent": null, "payment_method": "card_1FZpYhHv0Y0PURSqJWu9ppxe", "payment_method_details": {"card": {"brand": "visa", "checks": {"address_line1_check": null, "address_postal_code_check": null, "cvc_check": null}, "country": "US", "exp_month": 11, "exp_year": 2020, "fingerprint": "invoLvA3S2339Hlz", "funding": "credit", "installments": null, "last4": "0002", "network": "visa", "three_d_secure": null, "wallet": null}, "type": "card"}, "receipt_email": null, "receipt_number": null, "receipt_url": "https://pay.stripe.com/receipts/acct_1EJOOLHv0Y0PURSq/ch_1FZpYhHv0Y0PURSqnaxbrowv/rcpt_G61bfiwujEVbmBleDeprVDK1Z4eXnCX", "refunded": false, "refunds": {"object": "list", "data": [], "has_more": false, "total_count": 0, "url": "/v1/charges/ch_1FZpYhHv0Y0PURSqnaxbrowv/refunds"}, "review": null, "shipping": null, "source": {"id": "card_1FZpYhHv0Y0PURSqJWu9ppxe", "object": "card", "address_city": null, "address_country": null, "address_line1": null, "address_line1_check": null, "address_line2": null, "address_state": null, "address_zip": null, "address_zip_check": null, "brand": "Visa", "country": "US", "customer": null, "cvc_check": null, "dynamic_last4": null, "exp_month": 11, "exp_year": 2020, "fingerprint": "invoLvA3S2339Hlz", "funding": "credit", "last4": "0002", "metadata": {}, "name": null, "tokenization_method": null}, "source_transfer": null, "statement_descriptor": null, "statement_descriptor_suffix": null, "status": "failed", "transfer_data": null, "transfer_group": null}}, "livemode": false, "pending_webhooks": 3, "request": {"id": "req_t91WTWN0dgrmmJ", "idempotency_key": null}, "type": "charge.failed"}
    """
    stripe_api.webhook_api.verify("unique_signature", body)
    mock_generic_func.assert_called_once_with(
        event="charge.failed",
        data={
            "id": "ch_1FZpYhHv0Y0PURSqnaxbrowv",
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
                "fingerprint": "invoLvA3S2339Hlz",
                "funding": "credit",
                "installments": None,
                "last4": "0002",
                "network": "visa",
                "three_d_secure": None,
                "wallet": None,
            },
            "status": "failed",
            "amount_refunded": 0,
            "failure": {"code": "card_declined", "message": "Your card was declined."},
            "outcome": {
                "network_status": "declined_by_network",
                "reason": "generic_decline",
                "risk_level": "normal",
                "risk_score": 55,
                "seller_message": "The bank did not return any further details with this decline.",
                "type": "issuer_declined",
            },
        },
    )


def test_refund_payment(mock_generic_func, stripe_api):
    body = """{
        "id": "evt_1FZpUiHv0Y0PURSq6ht36S8d", 
        "object": "event", "api_version": "2019-03-14", 
        "created": 1572573848, "data": {"object": {"id": "ch_1FZpUgHv0Y0PURSqfcRHxRDP", "object": "charge", "amount": 2000, "amount_refunded": 2000, "application": null, "application_fee": null, "application_fee_amount": null, "balance_transaction": "txn_1FZpUgHv0Y0PURSqadIi9xwK", "billing_details": {"address": {"city": null, "country": null, "line1": null, "line2": null, "postal_code": null, "state": null}, "email": null, "name": null, "phone": null}, "captured": true, "created": 1572573846, "currency": "usd", "customer": null, "description": null, "destination": null, "dispute": null, "failure_code": null, "failure_message": null, "fraud_details": {}, "invoice": null, "livemode": false, "metadata": {}, "on_behalf_of": null, "order": null, "outcome": {"network_status": "approved_by_network", "reason": null, "risk_level": "normal", "risk_score": 51, 
        "seller_message": "Payment complete.", "type": "authorized"}, "paid": true, "payment_intent": null, "payment_method": "card_1FZpUgHv0Y0PURSqykuRPITN", "payment_method_details": {"card": {"brand": "visa", "checks": {"address_line1_check": null, "address_postal_code_check": null, "cvc_check": null}, "country": "US", "exp_month": 11, "exp_year": 2020, "fingerprint": "yIwZJF6Qz10rsS7J", "funding": "credit", "installments": null, "last4": "4242", "network": "visa", "three_d_secure": null, "wallet": null}, "type": "card"}, "receipt_email": null, "receipt_number": null, "receipt_url": "https://pay.stripe.com/receipts/acct_1EJOOLHv0Y0PURSq/ch_1FZpUgHv0Y0PURSqfcRHxRDP/rcpt_G61XPmyNekRgoLd7Rgm626Yg0niyGmu", "refunded": true, "refunds": {"object": "list", "data": [{"id": "re_1FZpUhHv0Y0PURSqAcxHxT8r", "object": "refund", "amount": 2000, "balance_transaction": "txn_1FZpUhHv0Y0PURSqFGxqIJ5D", "charge": "ch_1FZpUgHv0Y0PURSqfcRHxRDP", "created": 1572573847, "currency": "usd", "metadata": {}, "reason": null, "receipt_number": null, "source_transfer_reversal": null, "status": "succeeded", "transfer_reversal": null}], "has_more": false, "total_count": 1, "url": "/v1/charges/ch_1FZpUgHv0Y0PURSqfcRHxRDP/refunds"}, "review": null, "shipping": null, "source": {"id": "card_1FZpUgHv0Y0PURSqykuRPITN", "object": "card", "address_city": null, "address_country": null, "address_line1": null, "address_line1_check": null, "address_line2": null, "address_state": null, "address_zip": null, "address_zip_check": null, "brand": "Visa", "country": "US", "customer": null, "cvc_check": null, "dynamic_last4": null, "exp_month": 11, "exp_year": 2020, "fingerprint": "yIwZJF6Qz10rsS7J", "funding": "credit", "last4": "4242", "metadata": {}, "name": null, "tokenization_method": null}, "source_transfer": null, "statement_descriptor": null, "statement_descriptor_suffix": null, "status": "succeeded", "transfer_data": null, "transfer_group": null}, "previous_attributes": {"amount_refunded": 0, "refunded": false, "refunds": {"data": [], "total_count": 0}}}, "livemode": false, "pending_webhooks": 3, "request": {"id": "req_I1sL6KvveyA7Bp", "idempotency_key": null}, "type": "charge.refunded"}
    """

    stripe_api.webhook_api.verify("unique_signature", body)
    mock_generic_func.assert_called_once_with(
        event="charge.refunded",
        data={
            "id": "ch_1FZpUgHv0Y0PURSqfcRHxRDP",
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
            "amount_refunded": 20.0,
            "failure": {},
            "outcome": {
                "network_status": "approved_by_network",
                "reason": None,
                "risk_level": "normal",
                "risk_score": 51,
                "seller_message": "Payment complete.",
                "type": "authorized",
            },
        },
    )
