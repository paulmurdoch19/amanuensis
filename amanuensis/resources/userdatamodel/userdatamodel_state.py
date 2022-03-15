from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    State
)

__all__ = [
    "create_state",
    "get_all_states",
]


def create_state(current_session, name, code):
    """
    Creates a consortium
    """
    new_state = State(code=code, name=name)

    current_session.add(new_state)
    current_session.commit()
    
    return new_state


def get_all_states(current_session):
    return current_session.query(State).all()



