from unittest import TestCase

from columbus.router import Router, HttpRequest


class TestRouter(TestCase):

    def test_aws_parser(self):
        event = {}
        app = Router()

        @app.get('test')
        def test_hello(req: HttpRequest):
            assert req.body == {}
            assert req.headers == {}
            assert req.params == {}

        app.get_router()(event, None)
