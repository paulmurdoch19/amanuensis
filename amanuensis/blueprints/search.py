import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
# from amanuensis.models import Application, Certificate
from amanuensis.resources.search import get_all, create, delete, update
from amanuensis.config import config




REQUIRED_CERTIFICATES = {
    "AUP_COC_NDA": "documents needed for user e-sign",
    "training_certificate": "certificate obtained from training",
}

blueprint = flask.Blueprint("cohort", __name__)



@blueprint.route("/", methods=["GET"])
# @login_required({"user"})
def get_searches():
    return flask.jsonify(get_all())


@blueprint.route("/", methods=["POST"])
# @admin_login_required
# @debug_log
def create_search():
    """
    Create a search on the userportaldatamodel database

    Returns a json object
    """
    name = flask.request.get_json().get("name", None)
    # user_id = flask.request.get_json().get("user_id", None)
    filter_object = flask.request.get_json().get("filters", None)
    description = flask.request.get_json().get("description", None)
    return flask.jsonify(create(name, description, filter_object))



@blueprint.route("/<search_id>", methods=["PUT"])
# @admin_login_required
# @debug_log
def update_search(search_id):
    """
    Create a user on the userdatamodel database

    Returns a json object
    """
    name = flask.request.get_json().get("name", None)
    description = flask.request.get_json().get("description", None)
    filter_object = flask.request.get_json().get("filters", None)
    return flask.jsonify(update(search_id, name, description, filter_object))


@blueprint.route("/<search_id>", methods=["DELETE"])
def delete_search(search_id):
    """
    Remove the user from the userdatamodel database and all associated storage
    solutions.

    Returns json object
    """
    response = flask.jsonify(delete(search_id))
    return response

