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


def create_consortium(session, name, code):
    """
    Creates a consortium
    """
    new_consortium = ConsortiumDataContributor(code=code, name=name)

    current_session.add(new_consortium)
    # current_session.commit()
    current_session.flush()
    
    return new_consortium


def create_state(current_session, name, code):
    """
    Creates a consortium
    """
    new_state = State(code=code, name=name)

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




def update_filter_set(current_session, logged_user_id, filter_set_id, explorer_id, name, description, filter_object):
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    if filter_object:
        data['filter_object'] = filter_object

    #TODO check that at least one has changed
    num_updated = current_session.query(Search).filter(
        Search.id == filter_set_id, 
        Search.filter_source_internal_id == explorer_id,
        Search.filter_source == FilterSourceType.explorer,
        Search.user_id == logged_user_id
    ).update(data)
    if  num_updated > 0:
        return  {"code": 200, "updated": int(filter_set_id), "explorer_id": int(explorer_id)}
    else:
        return {"code": 500, "error": "Nothing has been updated, check the logs to see what happened during the transaction."}




