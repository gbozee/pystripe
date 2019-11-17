from collections import namedtuple

import pytest
import stripe


def test_verify_payment_endpoint(client, mocker):
    pass


async def _get_payment_info(order, **kwargs):
    return {"amount": 50, "currency": "usd"}


Intent = namedtuple(
    "Intent", ["status", "next_action", "amount", "id", "client_secret"]
)
ActionType = namedtuple("ActionType", ["type"])


def test_make_payment_success_no_auth(client, mocker):
    new_client = client(get_payment_info=_get_payment_info)
    mock_create = mocker.patch("stripe.PaymentIntent")
    mock_create.create.return_value = Intent(
        status="succeeded",
        next_action=ActionType(None),
        id="intent_id",
        amount=5000,
        client_secret=None,
    )
    response = new_client.post(
        "/paystack/make-payment/ABCD", json={"payment_method_id": "pm_1001"}
    )
    mock_create.create.assert_called_with(
        payment_method="pm_1001",
        amount=5000,
        currency="usd",
        confirmation_method="manual",
        confirm=True,
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_make_payment_require_auth(client, mocker):
    new_client = client(get_payment_info=_get_payment_info)
    mock_create = mocker.patch("stripe.PaymentIntent")
    mock_create.confirm.return_value = Intent(
        status="requires_action",
        next_action=ActionType("use_stripe_sdk"),
        client_secret="client_secret",
        amount=5000,
        id="tt_id",
    )
    response = new_client.post(
        "/paystack/make-payment/ABCD", json={"payment_intent_id": "pm_1001"}
    )
    mock_create.confirm.assert_called_with("pm_1001")
    assert response.status_code == 200
    assert response.json() == {
        "requires_action": True,
        "payment_intent_client_secret": "client_secret",
    }


def test_make_payment_insufficient_funds(client, mocker):
    new_client = client(get_payment_info=_get_payment_info)
    mock_create = mocker.patch("stripe.PaymentIntent")
    mock_create.create.side_effect = stripe.error.CardError("Limited funds", {}, 500)
    response = new_client.post(
        "/paystack/make-payment/ABCD", json={"payment_method_id": "pm_1001"}
    )
    mock_create.create.assert_called_with(
        payment_method="pm_1001",
        amount=5000,
        currency="usd",
        confirmation_method="manual",
        confirm=True,
    )
    assert response.status_code == 200
    assert response.json() == {"error": "Limited funds"}
