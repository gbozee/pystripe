import typing
import stripe
from . import api
from .api.utils import charge_data


class StripeAPI(object):
    def __init__(self, callback_domain="", **kwargs):
        self.domain = callback_domain
        for key, value in kwargs.items():
            setattr(self, key, value)

        stripe.api_key = self.secret_key
        self.stripe = stripe
        self.charge_api = api.Charge(self.stripe)
        self.webhook_api = api.Webhook(self.stripe, signing_secret=self.webhook_secret)
        self.customer_api = api.Customer(self.stripe)
        self.payment_intent_api = api.PaymentIntent(self.stripe)

    def verify_payment(
        self,
        intent_id=None,
        payment_intent=None,
        customer_id=None,
        amount=None,
        currency="usd",
    ):
        return self.payment_intent_api.verify_payment(
            payment_intent=payment_intent,
            intent_id=intent_id,
            amount=amount,
            currency=currency,
        )

    def create_or_process_intent(
        self,
        payment_intent_id=None,
        payment_method=None,
        amount=None,
        currency=None,
        order=None,
        send_result=False,
    ):
        intent = None
        try:
            if payment_method:
                # Create the PaymentIntent
                intent = self.stripe.PaymentIntent.create(
                    payment_method=payment_method,
                    amount=amount * 100,
                    currency=currency,
                    confirmation_method="manual",
                    confirm=True,
                )
            elif payment_intent_id:
                intent = self.stripe.PaymentIntent.confirm(payment_intent_id)
        except self.stripe.error.CardError as e:
            return False, e.user_message
        # Note that if your API version is before 2019-02-11, 'requires_action'
        # appears as 'requires_source_action'.
        if (
            intent.status == "requires_action"
            and intent.next_action.type == "use_stripe_sdk"
        ):
            # Tell the client to handle the action
            return (
                True,
                {
                    "requires_action": True,
                    "payment_intent_client_secret": intent.client_secret,
                },
            )
        elif intent.status == "succeeded":
            api.signals.payment_verified.send(
                sender=self.__class__,
                ref=intent.id,
                amount=int(intent.amount) / 100,
                order=order,
                data=intent,
            )
            if send_result:
                return True, intent
            return True, {}
        else:
            # Invalid status
            return False, {"error": "Invalid PaymentIntent status"}

    def initialize_payment(self, amount=None, currency="usd") -> str:
        result = self.payment_intent_api.create_intent(amount=amount, currency=currency)
        if result[0]:
            return result[2].client_secret

    def charge_card(self, customer, amount=None, currency=None, payment_method=None):
        _payment_method = payment_method
        if not _payment_method:
            payment_methods = self.customer_api.get_payment_methods(customer)
            _payment_method = payment_methods[0]
        result = self.payment_intent_api.create_intent(
            amount=amount,
            currency=currency,
            customer_id=customer,
            payment_method=_payment_method,
        )
        return result

    def save_card_for_customer(
        self, payment_method, customer=None, email=None, name=None
    ):

        result = self.payment_intent_api.verify_payment(
            payment_method=payment_method, customer_id=customer, email=email, name=name
        )
        return result

    def refund_payment(self, payment_intent, amount=None):
        pass

    def processor_info(self, amount, redirect_url=None):
        return {
            "amount": amount * 100,
            "js_script": get_js_script(),
            "key": self.public_key,
            "redirect_url": redirect_url,
        }


def get_js_script():
    return "https://js.stripe.com/v3/"
