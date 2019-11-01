import asyncio
import functools
import importlib

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, RedirectResponse

# from pystripe.api import signals

from starlette.config import Config
from starlette.datastructures import URL, Secret

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
    txrf = request.query_params.get("trxref")
    response = stripe_instance.verify_payment(txrf, amount=int(amount))
    if response[0]:
        signals.payment_verified.send(
            sender=StripeAPI, ref=txrf, amount=int(amount) / 100, order=order
        )
    return response_callback(response[0], order=order)


async def webhook_view(request: Request, stripe_instance=None, full_auth=True):
    signature = request.headers.get("stripe-signature")
    body = await request.body()
    return JSONResponse(
        {"status": "Success"},
        background=BackgroundTask(
            stripe_instance.webhook_api.verify, signature, body, full_auth=full_auth
        ),
    )


def build_app(StripeAPI, response_callback=None, full_auth=True):
    app = Starlette()
    stripe_instance = StripeAPI(
        public_key=str(STRIPE_PUBLIC_KEY),
        secret_key=str(STRIPE_SECRET_KEY),
        webhook_secret=str(STRIPE_WEBHOOK_SECRET),
        callback_domain=STRIPE_APPLICATION_DOMAIN,
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    async def new_webhook(request):
        return await webhook_view(
            request, stripe_instance=stripe_instance, full_auth=full_auth
        )

    # new_webhook = lambda request: expression asyncio.coroutine(
    #     functools.partial(webhook_view, stripe_instance=stripe_instance)
    # )
    app.add_route("/webhook", new_webhook, methods=["POST"])
    new_verify_payment = lambda request: verify_payment(
        request,
        response_callback=response_callback,
        stripe_instance=stripe_instance,
        StripeAPI=StripeAPI,
    )
    app.add_route("/verify-payment/{order_id}", new_verify_payment, methods=["GET"])
    app.state.stripe = stripe_instance
    return app
