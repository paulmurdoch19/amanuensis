from logging import getLogger
from sqlalchemy import func
from amanuensis.resources.aws import boto_manager
from amanuensis.auth.auth import current_user
from amanuensis.resources.message import send_message
from amanuensis.resources.userdatamodel.userdatamodel_project import get_project_by_id
from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    State,
    ConsortiumDataContributor,
    RequestState,
    Receiver,
    Project
)

__all__ = [
    "create_state",
    "get_all_states",
    "update_project_state",
    "create_consortium",
    "get_state_by_id",
    "get_state_by_code",
]

logger = getLogger(__name__)

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

def notify_user_data_delivered(request, current_session):
    """
    Notify the users when project state changes to DATA_DELIVERED.
    """
    project = get_project_by_id(current_session, request.project_id)
    email_subject = f"Project {project.name}: Data Delivered"
    email_body = f"The project f{project.name} data was delivered."

    return send_message(current_user.id, request.id, email_subject, email_body)

def update_project_state(current_session, requests, state):
    '''
    Updates the state for a project, including all requests in the project. Notifies users when the state changes to DATA_DELIVERED.
    '''

    for request in requests:
        if request.request_has_state[-1].state_id == 2 or request.request_has_state[-1].state_id == 4:
            raise UserError("Cannot change state of request {} from {} because it's a final state"\
                .format(request.id, state.code))
        elif request.request_has_state[-1].state_id == state.id:
            raise UserError("Request {} is already in state {}".format(request.id, state.code))
        else:
            request.request_has_state.append(RequestState(state_id=state.id, request_id=request.id))
            
    if state.code == "DATA_DELIVERED":
        notify_user_data_delivered(request, current_session)

    current_session.flush()
    return requests
