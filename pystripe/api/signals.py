from dispatch import Signal

payment_verified = Signal(providing_args=["charge_id", "amount", "order", "data"])

event_signal = Signal(providing_args=["event", "data"])

successful_payment_signal = Signal(providing_args=["data"])

payment_intent_succeeded_signal = Signal(providing_args=["data"])

failed_payment_signal = Signal(providing_args=["data"])
