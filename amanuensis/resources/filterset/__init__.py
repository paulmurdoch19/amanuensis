import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources import userdatamodel as udm
from amanuensis.resources.userdatamodel import get_filter_sets, create_filter_set, delete_filter_set, update_filter_set
# from amanuensis.auth.auth import get_current_user
# from amanuensis.user import get_current_user

from amanuensis.auth.auth import current_user

from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
# from amanuensis.jwt.utils import get_jwt_header
# from amanuensis.models import query_for_user
# from amanuensis.auth.auth import register_arborist_user


logger = get_logger(__name__)


def get_all(logged_user_id, explorer_id):
    with flask.current_app.db.session as session:
        return get_filter_sets(session, logged_user_id, None, explorer_id)

def get_by_id(logged_user_id, filter_set_id, explorer_id):
    with flask.current_app.db.session as session:
        return get_filter_sets(session, logged_user_id, filter_set_id, explorer_id)

def get_by_ids(logged_user_id, filter_set_ids, explorer_id):
    with flask.current_app.db.session as session:
        return get_filter_sets(session, logged_user_id, filter_set_ids, explorer_id)


def create(logged_user_id, is_amanuensis_admin, explorer_id, name, description, filter_object):
    with flask.current_app.db.session as session:    
        return create_filter_set(session, logged_user_id, is_amanuensis_admin, explorer_id, name, description, filter_object)


def update(logged_user_id, filter_set_id, explorer_id, name, description, filter_object):
    with flask.current_app.db.session as session:
        return update_filter_set(session, logged_user_id, filter_set_id, explorer_id, name, description, filter_object)


def delete(logged_user_id, filter_set_id, explorer_id):
    with flask.current_app.db.session as session:
        return delete_filter_set(session, logged_user_id, filter_set_id, explorer_id)
