import typing
from .utils import charge_data, payment_intent_data
from .customer import Customer


class PaymentIntent:
    def __init__(self, stripe):
        self.stripe = stripe
        self.customer_api = Customer(stripe)

    def verify_payment(
        self,
        payment_method=None,
        intent_id=None,
        payment_intent=None,
        customer_id=None,
        email: str = None,
        amount=None,
        currency=None,
        name=None,
        update=True,
    ) -> typing.Optional[typing.Tuple[bool, str, typing.Any]]:
        _payment_method = payment_method
        if (intent_id or payment_intent) and all([currency, amount]):
            _payment_intent = payment_intent
            if not _payment_intent:
                _payment_intent = self.stripe.PaymentIntent.retrieve(intent_id)
                _payment_method = _payment_intent.payment_method
                if _payment_intent.currency == currency and int(
                    _payment_intent.amount
                ) == int(amount):
                    if _payment_intent.status == "succeeded":
                        return True, "Payment verified", _payment_intent
                    return False, "Payment verification failed", _payment_intent

        customer, full_customer = self.customer_api.create_or_update_customer(
            customer_id=customer_id, email=email, name=name
        ) 
        # attach payment method to customer
        payment_method = self.stripe.PaymentMethod.attach(
            _payment_method, customer=customer
        )
        return full_customer

    def create_intent(
        self,
        payment_method=None,
        amount=None,
        currency="usd",
        customer_id=None,
        email: str = None,
        name=None,
        update=True,
        **kwargs
    ):
        _customer_id = customer_id
        if not customer_id:
            kwargs["setup_future_usage"] = "off_session"
        else:
            kwargs["off_session"] = True
            kwargs["confirm"] = True
        if payment_method:
            kwargs["payment_method"] = payment_method
            kwargs["customer"] = _customer_id
        error_code = None
        success = False
        try:
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount * 100, currency=currency, **kwargs
            )
            success = True
        except self.stripe.error.CardError as e:
            err = e.error
            # Error code will be authentication_required if authentication is needed
            print("Code is: %s" % err.code)
            error_code = err.code  # could also include insufficient_funds
            payment_intent_id = err.payment_intent["id"]
            payment_intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)

        return success, error_code, payment_intent

    def update_intent(self, payment_intent, amount=None, currency="usd"):
        intent = stripe.PaymentIntent.modify(
            payment_intent, amount=amount * 100, currency=currency
        )
        return intent

