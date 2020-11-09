import json
from abc import ABC, abstractmethod
from urllib.parse import parse_qs
from columbus.models import HTTPMethod, HttpRequest
from columbus.structures import CaseInsensitiveDict


class HttpRequestParser(ABC):

    @abstractmethod
    def parse_request(self, raw_request):
        pass


class LambdaRequestParser:
    def __init__(self, event):
        self.event = event

    def get_method(self):
        return HTTPMethod[self.event['httpMethod']]

    def get_url_params(self):
        params = self.event.get('queryStringParameters')
        return params if params else {}

    @staticmethod
    def __parse_http_body(body, content_type=''):
        content_type = '' if content_type is None else content_type
        if 'application/json' in content_type:
            return json.loads(body)
        elif 'application/x-www-form-urlencoded' in content_type:
            return parse_qs(body)
        else:
            return body

    def get_body(self):
        return self.event['body']

    def get_path(self):
        return self.event['pathParameters']['path']

    def get_request(self):
        body = LambdaRequestParser.__parse_http_body(self.get_body(),
                                                     self.get_header(
                                                         'Content-Type')) if self.get_body() is not None else None
        return HttpRequest(self.event, self.get_method(), self.get_path(), self.get_url_params(), body,
                           self.get_headers())

    def get_headers(self):
        return CaseInsensitiveDict(self.event['headers'])

    def get_header(self, header):
        return self.get_headers().get(header)
