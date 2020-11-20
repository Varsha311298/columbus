import json
from abc import ABC, abstractmethod
from urllib.parse import parse_qs
from columbus.models import HTTPMethod, HttpRequest
from columbus.structures import CaseInsensitiveDict


class HttpRequestParser(ABC):

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def get_method(self):
        pass

    @abstractmethod
    def get_path(self):
        pass

    @abstractmethod
    def get_mimetype(self):
        pass

    @abstractmethod
    def get_params(self):
        pass

    @abstractmethod
    def get_body(self):
        pass

    @abstractmethod
    def get_headers(self):
        pass

    def parse_request(self) -> HttpRequest:
        return HttpRequest(self.get_method(), self.get_path(), self.get_params(),
                           self.get_body(), self.get_headers(), self.get_mimetype(), self.context)


class AWSHttpParser(HttpRequestParser, ABC):
    def __init__(self, event, context):
        super().__init__(context)
        self.event = event

    def get_method(self):
        return HTTPMethod[self.event['httpMethod']]

    def get_path(self):
        return self.event['path']

    def get_headers(self):
        return CaseInsensitiveDict(self.event['headers'])

    def get_mimetype(self):
        return self.event['headers']['Content-Type'] if self.get_method() is HTTPMethod.PUT or HTTPMethod.POST else None

    def get_body(self):
        return self.__parse_body()

    def get_params(self):
        params = {}
        if self.event.get('queryStringParameters'):
            params.update(self.event.get('queryStringParameters'))
        if self.event.get('pathParameters'):
            params.update(self.event.get('pathParameters'))
        return params if params else {}

    def __parse_body(self):
        content_type = self.get_mimetype()
        body = self.event['body']
        if 'application/json' in content_type:
            return json.loads(body)
        elif 'application/x-www-form-urlencoded' in content_type:
            return parse_qs(body)
        elif 'multipart/form-data' in content_type:
            result = {}
            name = None
            filename = None
            for part in decoder.MultipartDecoder(body.encode(), content_type).parts:
                form_data = part.headers.get(b'Content-Disposition')
                key = form_data.decode('utf-8').split("; ")[1:]
                value = part.text
                if part.headers.get(b'Content-Type'):
                    if part.headers.get(b'Content-Type').decode('utf-8') == 'text/html':
                        name, filename = [x.split('=')[1].strip('/"') for x in key]
                    if part.headers.get(b'Content-Type').decode('utf-8') == 'text/plain':
                        name, filename = [x.split('=')[1].strip('/"') for x in key]
                else:
                    name = key[0].split("=")[1].strip('/"')
                result[name] = {value, filename}
            return result
        return None



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
