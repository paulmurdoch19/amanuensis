import flask
import json
from cdislogging import get_logger

from amanuensis.resources.userdatamodel import create_state
from amanuensis.config import config

# from amanuensis.schema import State


logger = get_logger(__name__)

__all__ = [
    "create_state",
    "get_all_states"
]


def create_state(name, code):
    with flask.current_app.db.session as session:    
        return create_state(session, name, code)


def get_all_states():
	with flask.current_app.db.session as session:    
        return get_all_states(session)