import json
from typing import Tuple, Set
from columbus.exceptions import *
from columbus.interceptors import Interceptor
from columbus.models import *
from columbus.parser import LambdaRequestParser


class Route:
    def __init__(
            self,
            path: str,
            methods: Set[str]
    ):
        self.path = path
        self.methods = methods

    


class Router:
    def __init__(self):
        self.__filters = []
        self.routes = {}

    def with_filter(self, _filter: Interceptor):
        self.__filters.append(_filter)

    def get(self, path: str):
        return self.route(HTTPMethod.GET, path)

    def post(self, path: str):
        return self.route(HTTPMethod.POST, path)

    def delete(self, path: str):
        return self.route(HTTPMethod.DELETE, path)

    def put(self, path: str):
        return self.route(HTTPMethod.PUT, path)

    def route(self, method: HTTPMethod, path: str, ):
        def decorator(handler):
            self.routes[(method, path)] = handler
            return handler

        return decorator

    def get_handler(self, method: HTTPMethod, path: str):
        try:
            return self.routes[(method, path)]
        except KeyError:
            raise ResourceNotFound('Resource not found for : %s' % path)

    def get_router(self):
        def request_handler(event, context):
            response = HttpResponse()
            req_parser = LambdaRequestParser(event)
            request = req_parser.get_request()

            try:
                for _filter in self.__filters:
                    filter_context = _filter.filter(event, response)
                    if filter_context is not None:
                        request.add_context(*filter_context)

                handler = self.get_handler(request.get_method(), request.get_path())
                res = handler(request)

                if isinstance(res, HttpResponse):
                    response.add_headers(res.headers)
                    response.set_body(res.body)
                    response.set_status(res.status)
                else:
                    response.set_body(json.dumps(res))

            except HttpException as e:
                response = HttpResponse(body=e.msg, status=e.status)

            except Exception as e:
                response = HttpResponse(body=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)

            return response.as_dict()

        return request_handler
