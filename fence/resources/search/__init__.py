import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from fence.resources import userdatamodel as udm
from fence.resources.userdatamodel import get_all_searches, get_search, create_search, delete_search, update_search
# from fence.auth.auth import get_current_user
# from fence.user import get_current_user

from fence.auth.auth import current_user

from fence.config import config
from fence.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
# from fence.jwt.utils import get_jwt_header
# from fence.models import query_for_user
# from fence.auth.auth import register_arborist_user
# from fence.crm import hubspot


logger = get_logger(__name__)


def get_all():
    with flask.current_app.db.session as session:
        return get_all_searches(session)


def get_by_id(search_id):
    with flask.current_app.db.session as session:
        return get_search(session, search_id)


def create(name, description, filter_object):
    with flask.current_app.db.session as session:
        # user = get_current_user()
        # username = get_current_user()
        # logger.warning(username)

        logger.warning(flask.current_app.config.get("FORCE_ISSUER"))
        logger.warning(flask.current_app.config.get("USER_API"))

        # logger.warning(current_user.id)
        # logger.warning(current_user.username)
        #TODO try to read json and make an object of it {"lastName": "test_graglia", "firstName": "test_shea", "institution": "University of Chicago"}
        return create_search(session, name, description, filter_object)


def update(search_id, name, description, filter_object):
    with flask.current_app.db.session as session:
        return update_search(session, search_id, name, description, filter_object)


def delete(search_id):
    with flask.current_app.db.session as session:
        return delete_search(session, search_id)