from logging import getLogger
from sqlalchemy import func
from amanuensis.resources.aws import boto_manager

from amanuensis.resources.userdatamodel.userdatamodel_message import send_message
from amanuensis.errors import NotFound, UserError
from amanuensis.models import State, ConsortiumDataContributor, RequestState

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


def notify_user_of_state_change(request, state, current_session):
    """
    Notify the user of a state change
    """
    email_subject = "State Change"
    email_body = "Your request has been moved to the state {}".format(state.name)
    # send_message(current_session, logged_user_id, request_id, subject, body, receivers, emails):
    # TODO change hard-coded values to be configurable
    send_message(
        current_session,
        7,
        request.id,
        email_subject,
        email_body,
        ["ferraz@uchicago.edu"],
        ["caixadonick@gmail.com"],
    )


def update_project_state(current_session, requests, state):
    for request in requests:
        """
        Comparing request.state with state won't work because the request object doesn't know about the
        RequestState object. To do this you need to either:
        1. Query the database for the RequestState object to compare
        2. Go back to the old way of using request.states.append(state) but in a way that allows you
        to have a new create_date--for some reason it seems to be using the create_date of
        the state, not the new one from the RequestState object.
        """
        if (
            request.request_has_state[-1].state_id == 2
            or request.request_has_state[-1].state_id == 4
        ):
            raise UserError(
                "Cannot change state of request {} from {} because it's a final state".format(
                    request.id, state.code
                )
            )
        elif request.request_has_state[-1].state_id == state.id:
            raise UserError(
                "Request {} is already in state {}".format(request.id, state.code)
            )
        else:
            request.request_has_state.append(
                RequestState(state_id=state.id, request_id=request.id)
            )

    current_session.flush()
    return requests
