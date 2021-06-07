import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources.userdatamodel import (
    create_project,
)
from amanuensis.resources import search

from amanuensis.auth.auth import current_user


from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
# from amanuensis.jwt.utils import get_jwt_header
# from amanuensis.models import query_for_user
# from amanuensis.auth.auth import register_arborist_user
# from amanuensis.crm import hubspot


from amanuensis.models import (
    Search,
    Request,
)



logger = get_logger(__name__)


# def get_all(logged_user_id):
#     with flask.current_app.db.session as session:
#         return get_all_searches(session, logged_user_id)


# def get_by_id(logged_user_id, search_id):
#     with flask.current_app.db.session as session:
#         return get_search(session, logged_user_id, search_id)


def create(logged_user_id, description, search_ids):
    s_1 = search.get_by_id(logged_user_id, search_ids[0])
    logger.info(s_1)
    with flask.current_app.db.session as session:
        test = Search()
        test_1 = Request()
        logger.info(test)
        return create_project(session, logged_user_id, description, s_1, test_1)


# def update(logged_user_id, search_id, name, description, filter_object):
#     with flask.current_app.db.session as session:
#         return update_search(session, logged_user_id, search_id, name, description, filter_object)


# def delete(logged_user_id, search_id):
#     with flask.current_app.db.session as session:
#         return delete_search(session, logged_user_id, search_id)