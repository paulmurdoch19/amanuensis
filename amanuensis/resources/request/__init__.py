import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources.userdatamodel import (
    get_requests,
    get_request_by_id,
    get_request_by_consortium,
)

from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
from amanuensis.models import (
    Request
)

from amanuensis.schema import RequestSchema


logger = get_logger(__name__)


def get(logged_user_id, consortium=None):
    #TODO
    # Get from hubspot if User is an EC member for this specific consortium or not
    isEcMember = False
    requests = []
    with flask.current_app.db.session as session:
        if consortium and isEcMember:
            requests = get_request_by_consortium(session, logged_user_id, consortium)
        else:
            requests = get_requests(session, logged_user_id)
            
        request_schema = RequestSchema(many=True)
        request_schema.dump(requests)
        return requests


def get_by_id(logged_user_id, request_id):
    with flask.current_app.db.session as session:
        return get_request_by_id(session, logged_user_id, request_id)

