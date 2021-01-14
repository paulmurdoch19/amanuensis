import flask_restful
from amanuensis.error_handler import get_error_response


class RestfulApi(flask_restful.Api):
    def handle_error(self, e):
        return get_error_response(e)
