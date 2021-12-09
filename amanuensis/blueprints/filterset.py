import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
# from amanuensis.models import Application, Certificate
from amanuensis.resources.filterset import get_all, get_by_id, create, delete, update
from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError
from amanuensis.schema import SearchSchema
from cdislogging import get_logger


REQUIRED_CERTIFICATES = {
    "AUP_COC_NDA": "documents needed for user e-sign",
    "training_certificate": "certificate obtained from training",
}

logger = get_logger(__name__)

blueprint = flask.Blueprint("filter-sets", __name__)

# deprecated - remove once portal switches to the correct url

# cache = SimpleCache()

@blueprint.route("/", methods=["GET"])
# @login_required({"user"})
def get_filter_sets():
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    # get the explorer_id from the querystring
    explorer_id = flask.request.args.get('explorer', default=1, type=int)

    return flask.jsonify(get_all(logged_user_id, explorer_id))


@blueprint.route("/<filter_set_id>", methods=["GET"])
# @login_required({"user"})
def get_filter_set(filter_set_id):
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    # get the explorer_id from the querystring
    explorer_id = flask.request.args.get('explorer', default=1, type=int)

    return flask.jsonify(get_by_id(logged_user_id, filter_set_id, explorer_id))


@blueprint.route("/", methods=["POST"])
# @admin_login_required
# @debug_log
def create_search():
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
    filter_object = flask.request.get_json().get("filters", None)
    description = flask.request.get_json().get("description", None)
    # search_schema = SearchSchema()
    # return flask.jsonify(search_schema.dump(create(logged_user_id, explorer_id, name, description, filter_object)))
    return flask.jsonify(create(logged_user_id, explorer_id, name, description, filter_object))


@blueprint.route("/<filter_set_id>", methods=["PUT"])
# @admin_login_required
# @debug_log
def update_search(filter_set_id):
    """
    Create a user on the userdatamodel database

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
    filter_object = flask.request.get_json().get("filters", None)
    return flask.jsonify(update(logged_user_id, filter_set_id, explorer_id, name, description, filter_object))


@blueprint.route("/<filter_set_id>", methods=["DELETE"])
def delete_search(filter_set_id):
    """
    Remove the user from the userdatamodel database and all associated storage
    solutions.

    Returns json object
    """
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    # get the explorer_id from the querystring
    explorer_id = flask.request.args.get('explorer', default=1, type=int)

    response = flask.jsonify(delete(logged_user_id, filter_set_id, explorer_id))
    return response

