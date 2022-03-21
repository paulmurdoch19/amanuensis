from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    State,
    Request,
    ConsortiumDataContributor
)

__all__ = [
    "create_state",
    "get_all_states",
    "update_project_state",
    "create_consortium"
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


def get_all_states(current_session):
    return current_session.query(State).all()


def update_project_state(current_session, project_id, state_id):
    requests = current_session.query(Request).filter(
            Request.project_id == project_id
        ).all()

    state = current_session.query(State).filter(
            State.id == state_id
        ).first()

    for request in requests:
        request.states.append(state)

    current_session.flush()
    return requests



