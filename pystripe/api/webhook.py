from .exceptions import StripeException
from . import signals
from .utils import charge_data, payment_intent_data


class Webhook(object):
    def __init__(self, _stripe, signing_secret=None):
        self.stripe = _stripe
        self.signing_secret = signing_secret

    def verify(self, unique_code, request_body, full_auth=False, **kwargs):
        # import stripe
        event = None
        try:
            event = self.stripe.Webhook.construct_event(
            # event = stripe.Webhook.construct_event(
                request_body, unique_code, self.signing_secret
            )
        except ValueError as e:
            raise StripeException("Error verifying webhook")
        except self.stripe.error.SignatureVerificationError as e:
            raise StripeException("Error verifying webhook")
        else:
            relevant_info = {"event": event["type"]}
            if event["type"] == "checkout.session.completed":
                pass
            if event["type"] in [
                "charge.failed",
                "charge.succeeded",
                "charge.refunded",
            ]:
                relevant_info["data"] = charge_data(event["data"], full_auth=full_auth)
            if event["type"] == "payment_intent.succeeded":
                relevant_info["data"] = payment_intent_data(
                    event["data"], full_auth=full_auth
                )
            if event["type"] == "charge.refund.updated":  # refund update
                pass
            if event["type"] == "charge.expired":
                pass
            options = {
                "charge.succeeded": signals.successful_payment_signal,
                "charge.failed": signals.failed_payment_signal,
                "charge.refunded": signals.successful_payment_signal,
                "payment_intent.succeeded": signals.payment_intent_succeeded_signal,
            }
            try:
                signal_func = options[event["type"]]
            except KeyError:
                signal_func = signals.event_signal
            signal_func.send(sender=self, **relevant_info)
            return event["type"], relevant_info
