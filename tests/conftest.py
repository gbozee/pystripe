from unittest import mock

import pytest

from pystripe.utils import StripeAPI
from pystripe import utils


class MockRequest(object):
    def __init__(self, response, **kwargs):
        self.response = response
        self.overwrite = True
        if kwargs.get("overwrite"):
            self.overwrite = True
        self.status_code = kwargs.get("status_code", 200)

    @classmethod
    def raise_for_status(cls):
        pass

    def json(self):
        if self.overwrite:
            return self.response
        return {"data": self.response}


@pytest.fixture
def stripe_api():
    return StripeAPI(
        public_key="public_key",
        secret_key="secret_key",
        webhook_secret="webhook_secret",
    )


@pytest.fixture
def headers(stripe_api: utils.StripeAPI):
    return {
        "Authorization": "Bearer {}".format(stripe_api.secret_key),
        "Content-Type": "application/json",
    }


@pytest.fixture
def get_request(mocker):
    def _get_request(*args, **kwargs):
        side_effect = kwargs.pop("side_effect", None)
        mock_get = mocker.patch("requests.get")
        if side_effect:
            mock_get.side_effect = [MockRequest(x) for x in side_effect]
        else:
            mock_get.return_value = MockRequest(*args, **kwargs)
        return mock_get

    return _get_request


@pytest.fixture
def post_request(mocker):
    def _post_request(*args, **kwargs):
        side_effect = kwargs.pop("side_effect", None)
        mock_post = mocker.patch("requests.post")
        if side_effect:
            mock_post.side_effect = [MockRequest(x) for x in side_effect]
        else:
            mock_post.return_value = MockRequest(*args, **kwargs)
        return mock_post

    return _post_request


@pytest.fixture
def put_request(mocker):
    def _put_request(*args, **kwargs):
        mock_post = mocker.patch("requests.put")
        mock_post.return_value = MockRequest(*args, **kwargs)
        return mock_post

    return _put_request


@pytest.fixture
def mock_assertion(headers, stripe_api: utils.StripeAPI):
    def _mock_assertion(mock_call, path, **kwargs):
        side_effect = kwargs.pop("stripe_apiside_effect", None)
        url = "{}{}".format(stripe_api.base_url, path)
        if side_effect:
            mock_calls = [mock.call(url, headers=headers, **x) for x in side_effect]
            mock_call.assert_has_calls(mock_calls, any_order=True)
        else:
            mock_call.assert_called_once_with(url, headers=headers, **kwargs)

    return _mock_assertion
