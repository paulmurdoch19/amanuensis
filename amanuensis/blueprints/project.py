import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
from amanuensis.models import State, RequestState
from amanuensis.resources.project import create, get_all
from amanuensis.resources.fence import fence_get_users
from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError, InternalError
from amanuensis.schema import ProjectSchema
from cdislogging import get_logger

blueprint = flask.Blueprint("projects", __name__)

logger = get_logger(__name__)

def get_state_id_to_code():

    with flask.current_app.db.session as session:

        # Map the State.id to the State.code in case they're in a different order than expected in the DB.

       return {int(state.id): state.code for state in session.query(State).all()}

# cache = SimpleCache()


def determine_status_code(codes):
    code = None
    if "REJECTED" in codes:
        code = "REJECTED"
    elif "DATA_DELIVERED" in codes:
        code = "DATA_DELIVERED"
    elif "IN_REVIEW" in codes:
        code = "IN_REVIEW"
    elif "APPROVED" in codes:
        code = "APPROVED"
    else:
        code = "UNKNOWN"
    return code


@blueprint.route("/", methods=["GET"])
def get_projetcs():
    STATE_ID_TO_CODE = get_state_id_to_code()
    try:
        logged_user_id = current_user.id
        logged_user_email = current_user.username
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    #TODO assign this as a resource in arborist
    approver = flask.request.args.get('approver', None)

    project_schema = ProjectSchema(many=True)
    projects = project_schema.dump(get_all(logged_user_id, logged_user_email, approver))

    return_projects = []

    for project in projects:
        tmp_project = {}
        tmp_project["id"] = project["id"]
        tmp_project["name"] = project["name"]

        requests_status_codes = []
        request_status_code = None
        project_status_code = None
        project_status_name = None
        status_date = None
        submitted_at = None
        completed_at = None

        for request in project["requests"]:
            request_state = current_session.query(RequestState).filter(RequestState.request_id == request["id"]).all()[-1]
            request_status_code = STATE_ID_TO_CODE[request_state.state_id]
            requests_status_codes.append(request_status_code)
            
            if not submitted_at:
                submitted_at = request["create_date"]

        project_status_code = determine_status_code(requests_status_codes)
        project_status_name = current_session.query(State).filter(State.code == project_status_code).first().name

        if project_status_code == "DATA_DELIVERED" or project_status_code == "REJECTED":
            if not completed_at:
                completed_at = project["update_date"]

        fence_users = fence_get_users(config=config, ids=[project["user_id"]])
        fence_users = fence_users['users'] if 'users' in fence_users else []
        logger.error("fence_users: {}".format(fence_users))
        if len(fence_users) != 1:
            raise InternalError("There can't be more or less than one user opening a project request.")

        tmp_project["researcher"] = {}
        tmp_project["researcher"]["id"] = fence_users[0]["id"]
        tmp_project["researcher"]["first_name"] = fence_users[0]["first_name"]
        tmp_project["researcher"]["last_name"] = fence_users[0]["last_name"]
        tmp_project["researcher"]["institution"] = fence_users[0]["institution"]

        tmp_project["status"] = project_status_name
        tmp_project["submitted_at"] = submitted_at
        tmp_project["completed_at"] = completed_at

        tmp_project["has_access"] = False
        if "statisticians" in project:
            for statistician in project["statisticians"]:
                if logged_user_id == statistician["user_id"] or logged_user_email == statistician["email"]:
                    tmp_project["has_access"] = True
                    break

        return_projects.append(tmp_project)

    return flask.jsonify(return_projects)


# DISABLE FOR NOW SINCE ONLY ADMIN CAN CREATE A PROJECT
@blueprint.route("/", methods=["POST"])
def create_project():
    """
    Create a search on the userportaldatamodel database

    Returns a json object
    """
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    # get the explorer_id from the querystring
    explorer_id = flask.request.args.get('explorer', default=1, type=int)

    name = flask.request.get_json().get("name", None)
    description = flask.request.get_json().get("description", None)
    
    #backward compatibility
    search_ids = flask.request.get_json().get("search_ids", None)
    filter_set_ids = flask.request.get_json().get("filter_set_ids", None)

    if search_ids and not filter_set_ids:
        filter_set_ids = search_ids

    project_schema = ProjectSchema()
    return flask.jsonify(project_schema.dump(create(logged_user_id, False, name, description, filter_set_ids, explorer_id)))




