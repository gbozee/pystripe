from .utils import charge_data


class Charge:
    def __init__(self, stripe):
        self.stripe = stripe

    def verify_payment(self, charge_id, amount=None, currency="usd"):
        try:
            charge = self.stripe.Charge.retrieve(charge_id)
            amount_in_dollar = charge["amount"] / 100
            _currency = charge["currency"]
            paid = charge["paid"]
            status = charge["status"]
            if (
                currency == _currency
                and amount == amount_in_dollar
                and paid
                and status == "succeeded"
            ):
                return (
                    True,
                    "Verification successful",
                    charge_data({"object": charge}),
                    charge,
                )
            return False, "Transaction Failed"
        except self.stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            print("Status is: %s" % e.http_status)
            print("Type is: %s" % e.error.type)
            print("Code is: %s" % e.error.code)
            # param is '' in this case
            print("Param is: %s" % e.error.param)
            print("Message is: %s" % e.error.message)
            return False, "Card Error"
        except (
            self.stripe.error.RateLimitError,
            self.stripe.error.InvalidRequestError,
            self.stripe.error.AuthenticationError,
            self.stripe.error.APIConnectionError,
            self.stripe.error.StripeError,
        ) as e:
            # Too many requests made to the API too quickly
            return False, "Stripe API Error"

    def add_or_update_card(
        self, card_token, customer_id=None, email=None, name=None, update=False
    ):
        _customer_id = customer_id
        if not _customer_id:
            customer = self.stripe.Customer.create(
                source=card_token, email=email, name=name
            )
            _customer_id = customer.id
        if update:
            kwargs = {}
            if email:
                kwargs["email"] = email
            if name:
                kwargs["name"] = name
            customer = self.stripe.Customer.modify(
                _customer_id, source=card_token, **kwargs
            )
            _customer_id = customer.id
        return _customer_id

    def charge_card(
        self,
        card_token,
        customer_id=None,
        email: str = None,
        amount=None,
        currency="usd",
        name=None,
    ):
        _customer_id = self.add_or_update_card(
            card_token, customer_id=customer_id, email=email, name=name
        )
        # test when charge is successful
        # test when charge fails
        charge = self.stripe.Charge.create(
            amount=amount * 100, currency=currency, customer=_customer_id
        )
        return charge
