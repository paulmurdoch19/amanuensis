import flask
from flask_sqlalchemy_session import current_session

from amanuensis.resources import message as m

from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError



blueprint = flask.Blueprint("message", __name__)


@blueprint.route("/", methods=["GET"])
def get_messages():
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    request_id = flask.request.args.get("request_id", None)

    if request_id:
        request_id = int(request_id)

    if request_id and isinstance(request_id, int):
        return flask.jsonify(m.get_messages(logged_user_id, request_id))
    else:
        return flask.jsonify(m.get_messages(logged_user_id))



@blueprint.route("/", methods=["POST"])
# @debug_log
def send_message():
    """
    Send a message to all the users that are working on a request (requestor plu committee members)

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

    # if body is None or body == "":
    #     return 400

    return flask.jsonify(m.send_message(logged_user_id, request_id, body))



