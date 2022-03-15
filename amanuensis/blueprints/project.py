import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
# from amanuensis.models import Application, Certificate
from amanuensis.resources.project import create, get_all
from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError
from amanuensis.schema import ProjectSchema
from cdislogging import get_logger


blueprint = flask.Blueprint("projects", __name__)

logger = get_logger(__name__)

# cache = SimpleCache()


@blueprint.route("/", methods=["GET"])
# @login_required({"user"})
def get_projetcs():
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    #TODO assign this as a resource in arborist
    approver = flask.request.args.get('approver', None)
    print(approver)

    project_schema = ProjectSchema(many=True)
    projects = project_schema.dump(get_all(logged_user_id, approver))

    return_projects = []

    for project in projects:
        tmp_project = {}
        tmp_project["id"] = project["id"]
        tmp_project["name"] = project["name"]

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
                if not status:
                    status = state["code"]

                if status == "APPROVED" or status == "REJECTED":
                    if not completed_at:
                        completed_at = request["update_date"]
                    break 
                else:
                    status = state["code"]

        tmp_project["status"] = status
        tmp_project["submitted_at"] = submitted_at
        tmp_project["completed_at"] = completed_at
        return_projects.append(tmp_project)

    return flask.jsonify(return_projects)


@blueprint.route("/", methods=["POST"])
# @debug_log
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


# @blueprint.route("/<search_id>", methods=["PUT"])
# # @admin_login_required
# # @debug_log
# def update_search(search_id):
#     """
#     Create a user on the userdatamodel database

#     Returns a json object
#     """
#     try:
#         logged_user_id = current_user.id
#     except AuthError:
#         logger.warning(
#             "Unable to load or find the user, check your token"
#         )

#     name = flask.request.get_json().get("name", None)
#     description = flask.request.get_json().get("description", None)
#     filter_object = flask.request.get_json().get("filters", None)
#     return flask.jsonify(update(logged_user_id, search_id, name, description, filter_object))


# @blueprint.route("/<search_id>", methods=["DELETE"])
# def delete_search(search_id):
#     """
#     Remove the user from the userdatamodel database and all associated storage
#     solutions.

#     Returns json object
#     """
#     try:
#         logged_user_id = current_user.id
#     except AuthError:
#         logger.warning(
#             "Unable to load or find the user, check your token"
#         )

#     response = flask.jsonify(delete(logged_user_id, search_id))
#     return response

