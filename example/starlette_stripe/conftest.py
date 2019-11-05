from pystripe.utils import StripeAPI
from pystripe.frameworks.starlette import build_app
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = build_app(StripeAPI)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.route("/", methods=["GET"])
def payment_page(request: Request):
    stripe_instance = app.state.stripe
    # session = stripe_instance.create_session(
    #     line_items=[
    #         {
    #             "name": "T-shirt",
    #             "description": "Comfortable cotton t-shirt",
    #             "images": ["https://example.com/t-shirt.png"],
    #             "amount": 5,
    #             "currency": "usd",
    #             "quantity": 1,
    #         }
    #     ],
    #     email="james@example.com",
    #     success_url="/success",
    #     cancel_url="/",
    # )
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stripe_instance": stripe_instance},
    )



