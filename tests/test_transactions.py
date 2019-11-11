from collections import namedtuple
from dispatch import receiver
from pystripe import utils, api

Intent = namedtuple(
    "Intent", ["status", "next_action", "amount", "id", "client_secret"]
)
ActionType = namedtuple("ActionType", ["type"])


@receiver(api.signals.payment_verified)
def payment_intent_succeeded_called(sender, **kwargs):
    kwargs.pop("signal", None)
    generic_function(**kwargs)


def generic_function(**params):
    print(params)


def test_create_or_process_intent(mocker, stripe_api: utils.StripeAPI):
    mock_create = mocker.patch("stripe.PaymentIntent")
    mock_successful_call = mocker.patch("test_transactions.generic_function")
    kkk = Intent(
        status="succeeded",
        next_action=ActionType(None),
        id="intent_id",
        amount=5000,
        client_secret=None,
    )
    mock_create.create.return_value = kkk
    # when payment works without any issue
    result = stripe_api.create_or_process_intent(
        payment_intent_id=None,
        payment_method="pm_1001",
        amount=50,
        currency="usd",
        order="BCDE",
    )
    assert result[0]
    assert result[1] == {}
    mock_successful_call.assert_called_with(
        amount=50.0, ref="intent_id", order="BCDE", data=kkk
    )
    # requies authentication
    mock_create.confirm.return_value = Intent(
        status="requires_action",
        next_action=ActionType("use_stripe_sdk"),
        client_secret="client_secret",
        amount=5000,
        id="tt_id",
    )
    result = stripe_api.create_or_process_intent(
        payment_intent_id="pi_1001",
        payment_method=None,
        amount=50,
        currency="usd",
        order="BCDE",
    )
    assert result[0]
    assert result[1] == {
        "requires_action": True,
        "payment_intent_client_secret": "client_secret",
    }
    mock_create.confirm.assert_called_with("pi_1001")
    # insufficient funds
    mock_create.create.side_effect = stripe_api.stripe.error.CardError(
        "Limited funds", {}, 500
    )
    result = stripe_api.create_or_process_intent(
        payment_intent_id=None,
        payment_method="pm_1001",
        amount=50,
        currency="usd",
        order="BCDE",
    )
    assert not result[0]
    assert result[1] == "Limited funds"
    # invalid payment_intent_id
    mock_create.create.side_effect = None
    mock_create.create.return_value = Intent(
        status="failed",
        next_action=ActionType(None),
        id="intent_id",
        amount=5000,
        client_secret=None,
    )
    result = stripe_api.create_or_process_intent(
        payment_intent_id=None,
        payment_method="pm_1001",
        amount=50,
        currency="usd",
        order="BCDE",
    )
    assert not result[0]
    assert result[1] == {"error": "Invalid PaymentIntent status"}


