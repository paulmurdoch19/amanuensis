import flask
from flask_sqlalchemy_session import current_session

from amanuensis.resources import message as m
from amanuensis.resources.message import get_all_messages, get_messages_by_request, send_message

from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError

# from amanuensis.models import MessageScema
# from amanuensis.schema import MessageSchema



blueprint = flask.Blueprint("messages", __name__)


@blueprint.route("/", methods=["GET"])
# @login_required({"user"})
def get_all_user_messages():
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    return flask.jsonify(m.get_all_messages(logged_user_id))


@blueprint.route("/request", methods=["GET"])
# @login_required({"user"})
def get_message_by_request():
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    request_id = flask.request.get_json().get("request_id", None)

    return flask.jsonify(m.get_messages_by_request(logged_user_id, request_id))


@blueprint.route("/", methods=["POST"])
# @admin_login_required
# @debug_log
def send_message():
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

    request_id = flask.request.get_json().get("request_id", None)
    body = flask.request.get_json().get("body", None)

    # message_schema = MessageSchema()

    return flask.jsonify(m.send_message(logged_user_id, request_id, body))



