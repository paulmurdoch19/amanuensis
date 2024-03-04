from logging import getLogger
from sqlalchemy import func, desc
from sqlalchemy.orm import aliased
from amanuensis.resources.message import send_admin_message
from amanuensis.resources.userdatamodel.userdatamodel_project import get_project_by_id
from amanuensis.resources.userdatamodel.userdatamodel_request import update_request_state
from amanuensis.errors import NotFound, UserError
from amanuensis.config import config
from amanuensis.models import (
    State,
    ConsortiumDataContributor,
    Transition,
    Request,
    RequestState
)

__all__ = [
    "create_state",
    "get_all_states",
    "update_project_state",
    "get_state_by_id",
    "get_state_by_code",
]

logger = getLogger(__name__)


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


# TODO move these 2 functions in the resources, there is logic here, the userdatamodel folder should contain mostly DB operation
def notify_user_project_status_update(current_session, project_id, consortiums):
    """
    Notify the users when project state changes.
    """
    project = get_project_by_id(current_session, 1, project_id)
    email_subject = f"Project {project.name}: Data Delivered"
    email_body = f"The project f{project.name} data was delivered."

    return send_admin_message(project, consortiums, email_subject, email_body)


def get_latest_request_state_by_id(current_session, request_id):
    return current_session.query(RequestState).filter(RequestState.request_id == request_id).order_by(desc(RequestState.create_date)).first()


def get_final_states(current_session):
    src_state_alias = aliased(State)
    dst_state_alias = aliased(State)

    result = (
        current_session.query(src_state_alias.code, dst_state_alias.code)
                       .join(Transition, Transition.state_src_id == src_state_alias.id)
                       .join(dst_state_alias, Transition.state_dst_id == dst_state_alias.id)
                       .all()
    )
    src = set()
    dst = set()
    for src_state, dst_state in result:
        src.add(src_state)
        dst.add(dst_state)
    return dst.difference(src)
    

def update_project_state(
    current_session, requests, state, project_id
):
    """
    Updates the state for a project, including all requests in the project. Notifies users when the state changes to DATA_DELIVERED.
    """
    updated = False
    consortiums = []
    final_states = get_final_states(current_session)
    for request in requests:
        consortium = request.consortium_data_contributor.code
        consortiums.append(consortium)
        state_code = get_latest_request_state_by_id(current_session, request.id)

        if state_code == state.code:
            logger.info(
                "Request {} is already in state {}. No need to change.".format(
                    request.id, state.code
                )
            )
        elif state_code in final_states:
            raise UserError(
                "Cannot change state of request {} from {} because it's a final state".format(
                    request.id, state.code
                )
            )
        else:
            update_request_state(current_session, request, state)

    if state.code in config["NOTIFY_STATE"] and updated:
        notify_user_project_status_update(
            current_session,
            project_id,
            consortiums
        )

    current_session.flush()
    return requests
#END TODO
