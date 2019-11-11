import json
import logging
import urllib.parse
from os.path import abspath

from dispatch import receiver
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from pystripe import utils as stripe_utils
from pystripe.api import signals
from pystripe.frameworks.starlette import build_app
from pystripe.utils import StripeAPI


@receiver(signals.payment_verified)
def verified_payment(sender, **kwargs):
    logging.info(kwargs)
    pass


@receiver(signals.successful_payment_signal)
def on_successful_payment(sender, event=None, data=None, **kwargs):

    logging.info({event: data})
    customer = data["customer"]
    payment_method = data["payment_method"]
    # attempt charging the card again.
    stripe_instance: stripe_utils.StripeAPI = app.state.stripe
    # add customer to card
    rr = stripe_instance.save_card_for_customer(
        payment_method, customer=customer, email="gbozee@gmail.com", name="Sholaosho"
    )
    # result = stripe_instance.charge_card(amount=40, customer=customer, currency="usd")
    pass


@receiver(signals.failed_payment_signal)
def on_failed_payment(sender, **kwargs):
    logging.info(kwargs)
    pass


def response_callback(status, order=None):
    return JSONResponse({"status": status, "order": order})


async def get_payment_info(order_id):
    return 20, "eur"


app = build_app(
    StripeAPI,
    webhook_secret="whsec_icv68RjYQK2MQ1Kq3O0TDxrvJJhqbEHt",
    response_callback=response_callback,
    get_payment_info=get_payment_info,
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.route("/return-url", methods="GET")
def return_url(request: Request):
    return templates.TemplateResponse("return.html", {"request": request})


@app.route("/", methods=["GET"])
def payment_page(request: Request):
    stripe_instance: stripe_utils.StripeAPI = app.state.stripe
    # client_secret = stripe_instance.initialize_payment(amount=20, currency="eur")
    # params = {"amount": 2000, "currency": "eur"}
    # redirect_url = f"/verify-payment/ABCD?{urllib.parse.urlencode(params)}"
    redirect_url = f"/make-payment/ABCD"
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stripe_instance": stripe_instance,
            # "secret_key": client_secret,
            "redirect_url": redirect_url,
            "return_url": "https://tuteria.localtunnel.me/return-url",
        },
    )
