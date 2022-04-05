from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    State,
    ConsortiumDataContributor
)

__all__ = [
    "create_state",
    "get_all_states",
    "update_project_state",
    "create_consortium",
    "get_state_by_id",
    "get_state_by_code",
]


def create_consortium(current_session, name, code):
    """
    Creates a consortium
    """
    new_consortium = ConsortiumDataContributor(name=name, code=code)

    current_session.add(new_consortium)
    current_session.flush()
    
    return new_consortium


def create_state(current_session, name, code):
    """
    Creates a state
    """
    new_state = State(name=name, code=code)

    current_session.add(new_state)
    # current_session.commit()
    current_session.flush()
    
    return new_state


def get_state_by_id(current_session, state_id):
    return current_session.query(State).filter(State.id == state_id).first()


def get_state_by_code(current_session, code):
    return current_session.query(State).filter(State.code == code).first()


def get_all_states(current_session):
    return current_session.query(State).all()


def update_project_state(current_session, requests, state):
    for request in requests:
        request.states.append(state)

    current_session.flush()
    return requests



