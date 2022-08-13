import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
# from amanuensis.models import Application, Certificate
from amanuensis.resources.project import create, get_all
from amanuensis.resources.fence import fence_get_users
from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError, InternalError
from amanuensis.schema import ProjectSchema
from cdislogging import get_logger


blueprint = flask.Blueprint("projects", __name__)

logger = get_logger(__name__)

# cache = SimpleCache()


@blueprint.route("/", methods=["GET"])
def get_projetcs():
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

        status_code = None
        status = None
        status_date = None
        submitted_at = None
        completed_at = None
        for request in project["requests"]:
            # get status
            # "status": "", // string ("IN REVIEW" | "APPROVED" | "REJECTED")
            # "submitted_at": "", // string (timestamp) or null
            # "completed_at": "" // string (timestamp) or null
            if not submitted_at:
                submitted_at = request["create_date"]

            for state in request["states"]:
                if not status_code:
                    status_code = state["code"]
                    status = state["name"]


                if status_code == "DATA_DELIVERED" or status_code == "REJECTED":
                    if not completed_at:
                        completed_at = request["update_date"]
                    break 
                else:
                    status_code = state["code"]
                    status = state["name"]

        fence_users = fence_get_users(config=config, ids=[project["user_id"]])
        fence_users = fence_users['users'] if 'users' in fence_users else []
        if len(fence_users) != 1:
            raise InternalError("There can't be more or less than one user opening a project request.")

        tmp_project["researcher"] = {}
        tmp_project["researcher"]["id"] = fence_users[0]["id"]
        tmp_project["researcher"]["first_name"] = fence_users[0]["first_name"]
        tmp_project["researcher"]["last_name"] = fence_users[0]["last_name"]
        tmp_project["researcher"]["institution"] = fence_users[0]["institution"]

        tmp_project["status"] = status
        tmp_project["submitted_at"] = submitted_at
        tmp_project["completed_at"] = completed_at

        tmp_project["has_access"] = False
        if "associated_users" in project:
            for associated_user in project["associated_users"]:
                if logged_user_id == associated_user["user_id"] or logged_user_email == associated_user["email"]:
                    tmp_project["has_access"] = True
                    break

        return_projects.append(tmp_project)

    return flask.jsonify(return_projects)


# DISABLE FOR NOW SINCE ONLY ADMIN CAN CREATE A PROJECT
# @blueprint.route("/", methods=["POST"])
# def create_project():
#     """
#     Create a search on the userportaldatamodel database

#     Returns a json object
#     """
#     try:
#         logged_user_id = current_user.id
#     except AuthError:
#         logger.warning(
#             "Unable to load or find the user, check your token"
#         )

#     # get the explorer_id from the querystring
#     explorer_id = flask.request.args.get('explorer', default=1, type=int)

#     name = flask.request.get_json().get("name", None)
#     description = flask.request.get_json().get("description", None)
    
#     #backward compatibility
#     search_ids = flask.request.get_json().get("search_ids", None)
#     filter_set_ids = flask.request.get_json().get("filter_set_ids", None)

#     if search_ids and not filter_set_ids:
#         filter_set_ids = search_ids

#     project_schema = ProjectSchema()
#     return flask.jsonify(project_schema.dump(create(logged_user_id, False, name, description, filter_set_ids, explorer_id)))




