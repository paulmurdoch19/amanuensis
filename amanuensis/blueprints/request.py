import flask
from flask_sqlalchemy_session import current_session

# from amanuensis.auth import login_required, current_token
# from amanuensis.errors import Unauthorized, UserError, NotFound
# from amanuensis.models import Application, Certificate
from amanuensis.resources.request import get
from amanuensis.config import config
from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError



blueprint = flask.Blueprint("request", __name__)



@blueprint.route("/", methods=["GET"])
# @admin_login_required
# @debug_log
def get_request():
    """

    """
    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    consortium = flask.request.args.get('consortium', None)
    
    return flask.jsonify(get(logged_user_id, consortium))


