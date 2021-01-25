import flask
from flask_sqlalchemy_session import current_session

from amanuensis.errors import Unauthorized
from amanuensis.models import query_for_user
from amanuensis.config import config


def get_current_user(flask_session=None):
    flask_session = flask_session or flask.session
    username = flask_session.get("username")
    return username
