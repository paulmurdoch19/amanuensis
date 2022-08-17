import flask
import json
from cdislogging import get_logger

from amanuensis.resources import userdatamodel as udm
from amanuensis.config import config
from amanuensis.schema import StateSchema, RequestSchema, ConsortiumDataContributorSchema
from amanuensis.errors import NotFound


logger = get_logger(__name__)

__all__ = [
    "update_role",
]


def update_role(project_id, user_id, email, role):
    with flask.current_app.db.session as session:  
        ret = udm.update_associated_users(session, project_id, user_id, email, role)
        return ret