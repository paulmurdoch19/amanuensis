import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources.userdatamodel import (
    get_requests,
    get_request_by_id,
)



from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
# from amanuensis.jwt.utils import get_jwt_header
# from amanuensis.models import query_for_user
# from amanuensis.auth.auth import register_arborist_user
# from amanuensis.crm import hubspot


from amanuensis.models import (
    Request
)

from amanuensis.schema import RequestSchema



logger = get_logger(__name__)


def get(logged_user_id, consortium=None, request_id=None):
    with flask.current_app.db.session as session:
        if consortium:
        # TODO Get consortium
            print("consortium")
        elif request_id:
            print("request_id")
            request = get_request_by_id(session, logged_user_id, request_id)
            return request
            # request_schema = RequestSchema()
            # return request_schema.dump(request)
        else:
            requests = get_requests(session, logged_user_id, None)
            request_schema = RequestSchema(many=True)
            return request_schema.dump(requests)


