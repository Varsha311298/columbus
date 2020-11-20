from abc import ABC, abstractmethod
from logging import Logger
from typing import Set

from columbus.exceptions import *
from columbus.models import HTTPMethod, HttpRequest, HttpResponse
from columbus.parser import LambdaRequestParser


class Interceptor(ABC):

    @abstractmethod
    def on_request(self, request: HttpRequest):
        pass

    @abstractmethod
    def on_response(self, request: HttpRequest, response: HttpResponse):
        pass


class CORSInterceptor(Interceptor):

    def __init__(
            self,
            origin: str = '*',
            allowed_methods: Set[HTTPMethod] = frozenset(
                {HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE})
    ) -> None:
        self.origin = origin
        self.allowed_methods = allowed_methods
        self.headers = {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Methods': ', '.join([x.name for x in self.allowed_methods])
        }

    def __is_valid_request(self, request: HttpRequest):
        method = request.get_method()
        return method in self.allowed_methods

    def on_request(self, request: HttpRequest):
        if not self.__is_valid_request(request):
            raise MethodNotAllowed('%s method not allowed' % request.get_method())

    def on_response(self, request: HttpRequest, response: HttpResponse):
        response.headers.update(self.headers)


class LogInterceptor(Interceptor):
    def __init__(self, logger: Logger):
        self.log = logger

    def on_request(self, request: HttpRequest):
        self.log.info(
            '{}: {}  Params: {}'.format(request.get_method(), request.get_path(), str(request.get_all_params())))

    def on_response(self, request: HttpRequest, response: HttpResponse):
        pass

