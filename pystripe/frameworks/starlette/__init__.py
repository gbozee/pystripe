import asyncio
import functools
import importlib
import typing

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.config import Config
from starlette.datastructures import URL, Secret
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from pystripe.api import signals

config = Config(".env")

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", cast=Secret)
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", cast=Secret)
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", cast=Secret)
STRIPE_APPLICATION_DOMAIN = config("STRIPE_APPLICATION_DOMAIN", default="")


def verify_payment(
    request: Request, response_callback=None, stripe_instance=None, StripeAPI=None
):
    amount = request.query_params.get("amount")
    order = request.path_params.get("order_id")
    charge_id = request.query_params.get("intent_id")
    currency = request.query_params.get("currency") or "usd"
    response = stripe_instance.verify_payment(
        intent_id=charge_id, amount=amount, currency=currency
    )
    if response[0]:
        signals.payment_verified.send(
            sender=StripeAPI,
            ref=charge_id,
            amount=int(amount) / 100,
            order=order,
            data=response[2],
        )
    return response_callback(response[0], order=order)


async def webhook_view(request: Request, background_action=None, **kwargs):
    signature = request.headers.get("stripe-signature")
    body = await request.body()
    return JSONResponse(
        {"status": "Success"},
        background=BackgroundTask(background_action, signature, body, **kwargs),
    )


async def make_payment(
    request: Request, stripe_instance=None, get_payment_info: typing.Coroutine = None
):
    """view responsible for processing payment_intent received from client"""
    data = await request.json()
    order_id = request.path_params.get("order_id")
    intent = None
    amount = None
    currency = None
    transaction = await get_payment_info(order_id, **data)

    result = stripe_instance.create_or_process_intent(
        payment_intent_id=data.get("payment_intent_id"),
        payment_method=data.get("payment_method_id"),
        amount=transaction["amount"],
        currency=transaction["currency"],
        order=order_id,
    )
    if not result[0]:
        if isinstance(result[1], str):
            # Display error on client when limited funds
            return JSONResponse({"error": result[1]})
        # Invalid status from intent
        return JSONResponse({"error": "Invalid PaymentIntent status"}, status_code=500)
    if result[1].get("requires_action"):
        # Tell the client to handle the action
        return JSONResponse(result[1])
    # payment processing was successful
    return JSONResponse({"success": True})


def build_app(
    StripeAPI,
    path="",
    response_callback=None,
    webhook_secret=None,
    instance_only=False,
    post_webhook_processing=None,
    get_payment_info: typing.Coroutine = None,
    _app: Starlette = None,
):
    stripe_instance = StripeAPI(
        public_key=str(STRIPE_PUBLIC_KEY),
        secret_key=str(STRIPE_SECRET_KEY),
        webhook_secret=webhook_secret or str(STRIPE_WEBHOOK_SECRET),
        callback_domain=STRIPE_APPLICATION_DOMAIN,
    )
    if instance_only:
        return stripe_instance
    if _app:
        app = _app
    else:
        app = Starlette()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def background_action(signature, body, **kwargs):
        return stripe_instance.webhook_api.verify(signature, body, full_auth=True)

    verify_action = post_webhook_processing or background_action

    async def new_webhook(request):
        return await webhook_view(
            request, background_action=verify_action, stripe_instance=stripe_instance
        )

    # new_webhook = lambda request: expression asyncio.coroutine(
    #     functools.partial(webhook_view, stripe_instance=stripe_instance)
    # )
    app.add_route(path + "/webhook", new_webhook, methods=["POST"])
    new_verify_payment = lambda request: verify_payment(
        request,
        response_callback=response_callback,
        stripe_instance=stripe_instance,
        StripeAPI=StripeAPI,
    )
    app.add_route(
        path + "/verify-payment/{order_id}", new_verify_payment, methods=["GET"]
    )

    async def new_make_payment(request):
        return await make_payment(
            request, stripe_instance=stripe_instance, get_payment_info=get_payment_info
        )

    app.add_route(path + "/make-payment/{order_id}", new_make_payment, methods=["POST"])
    app.state.stripe = stripe_instance
    return app
