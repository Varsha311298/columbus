from unittest import TestCase

from columbus.parser import AWSHttpParser


class TestHttpParser(TestCase):

    def test_aws_parser(self):
        event = {}
        parser = AWSHttpParser()
        req = parser.parse_request(event)
        assert req.headers[
                   'accept'] == 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
