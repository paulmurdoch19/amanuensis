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

    approver = flask.request.args.get('approver', None)
    print(approver)

    project_schema = ProjectSchema(many=True)
    return flask.jsonify(project_schema.dump(get_all(logged_user_id, approver)))


@blueprint.route("/", methods=["POST"])
# @admin_login_required
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

    name = flask.request.get_json().get("name", None)
    description = flask.request.get_json().get("description", None)
    search_ids = flask.request.get_json().get("search_ids", None)

    project_schema = ProjectSchema()
    return flask.jsonify(project_schema.dump(create(logged_user_id, name, description, search_ids)))


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

