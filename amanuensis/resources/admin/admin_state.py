import flask
import json
from cdislogging import get_logger

from amanuensis.auth.auth import current_user
from amanuensis.resources import userdatamodel as udm
from amanuensis.config import config
from amanuensis.schema import (
    StateSchema,
    RequestSchema,
    ConsortiumDataContributorSchema,
)
from amanuensis.errors import NotFound


logger = get_logger(__name__)

__all__ = [
    "create_state",
    "get_all_states",
    "update_project_state",
    "create_consortium",
    "get_by_code",
    "override_project_date",
]


def create_state(name, code):
    with flask.current_app.db.session as session:
        state_schema = StateSchema()
        state = udm.create_state(session, name, code)
        state_schema.dump(state)
        return state


def get_all_states():
    with flask.current_app.db.session as session:
        return udm.get_all_states(session)


def get_by_code(code, session=None):
    if session:
        return udm.get_state_by_code(session, code)
    else:
        with flask.current_app.db.session as session:
            return udm.get_state_by_code(session, code)


def update_project_state(project_id, state_id):
    with flask.current_app.db.session as session:
        requests = udm.get_requests_by_project_id(session, project_id)
        if not requests:
            raise NotFound(
                "There are no requests associated to this project or there is no project. id: {}".format(
                    project_id
                )
            )

        state = udm.get_state_by_id(session, state_id)
        if not state:
            raise NotFound("The state with id {} has not been found".format(state_id))

        request_schema = RequestSchema(many=True)
        consortium_statuses = config["CONSORTIUM_STATUS"]
        requests = udm.update_project_state(
            session, requests, state, consortium_statuses, project_id
        )
        request_schema.dump(requests)
        return requests


def create_consortium(name, code):
    with flask.current_app.db.session as session:
        consortium_schema = ConsortiumDataContributorSchema()
        consortium = udm.create_consortium(session, name, code)
        consortium_schema.dump(consortium)
        return consortium


def override_project_date(project_id, new_date):
    with flask.current_app.db.session as session:
        request_schema = RequestSchema(many=True)
        requests = udm.update_project_date(session, project_id, new_date)
        request_schema.dump(requests)
        return requests
