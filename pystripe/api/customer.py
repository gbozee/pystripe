class Customer:
    def __init__(self, stripe):
        self.stripe = stripe

    def create_or_update_customer(
        self, customer_id=None, email=None, name=None, update=True
    ):
        _customer_id = customer_id
        customer = None
        if email:
            existing = self.existing_instances(email)
            customer = self.merge_customers(existing)
            if customer:
                _customer_id = customer.id
        if not _customer_id:
            customer = self.stripe.Customer.create(email=email, name=name)
            _customer_id = customer.id
        if update:
            kwargs = {}
            if email:
                kwargs["email"] = email
            if name:
                kwargs["name"] = name
            if kwargs and _customer_id:
                customer = self.stripe.Customer.modify(_customer_id, **kwargs)
                _customer_id = customer.id
        return _customer_id, customer

    def existing_instances(self, email, limit=100):
        result = self.stripe.Customer.list(email=email, limit=limit)
        instances = result["data"]
        return instances

    def merge_customers(self, customers):
        order_by_created = sorted(customers, key=lambda x: x["created"])
        order_by_created.reverse()
        if order_by_created:
            last, *remaining = order_by_created
            for j in remaining:
                self.stripe.Customer.delete(j["id"])
            return last

    def get_payment_methods(self, customer, limit=100):
        result = self.stripe.PaymentMethod.list(
            customer=customer, type="card", limit=limit
        )
        return [x.id for x in result["data"]]

    def add_payment_method(self, payment_method, customer):
        user_payment_methods = self.get_payment_methods(customer)
        if user_payment_methods:
            if not payment_method in user_payment_methods:
                self.stripe.PaymentMethod.attach(payment_method, customer=customer)
        return payment_method
