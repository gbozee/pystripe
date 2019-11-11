import pytest
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from pystripe.frameworks.starlette import build_app
from pystripe.utils import StripeAPI


@pytest.fixture
def client():
    def _response_callback(status, order=None):
        return JSONResponse({"status": status, "order": order})

    async def _get_payment_info(order_id):
        return 20, "eur"

    def _client(
        get_payment_info=_get_payment_info,
        response_callback=_response_callback,
        path="/paystack",
    ):
        app = build_app(
            StripeAPI,
            path=path,
            webhook_secret="whsec_icv68RjYQK2MQ1Kq3O0TDxrvJJhqbEHt",
            response_callback=response_callback,
            get_payment_info=get_payment_info,
        )
        return TestClient(app)

    return _client
