from http import HTTPStatus


class HttpException(Exception):
    def __init__(self, message, status):
        super(HttpException, self).__init__(message)
        self.msg = message
        self.status = status


class BadRequest(HttpException):
    def __init__(self, message):
        super(BadRequest, self).__init__(message, HTTPStatus.BAD_REQUEST)


class UnAuthorized(HttpException):
    def __init__(self, message):
        super(UnAuthorized, self).__init__(message, HTTPStatus.UNAUTHORIZED)


class MethodNotAllowed(HttpException):
    def __init__(self, message):
        super(MethodNotAllowed, self).__init__(message, HTTPStatus.METHOD_NOT_ALLOWED)


class ResourceNotFound(HttpException):
    def __init__(self, message):
        super(ResourceNotFound, self).__init__(message, HTTPStatus.NOT_FOUND)
