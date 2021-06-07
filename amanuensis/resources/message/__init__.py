import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources import userdatamodel as udm
from amanuensis.resources.userdatamodel import get_all_messages, get_messages_by_request, send_message

from amanuensis.models import (
    Message,
    Receiver
)

from amanuensis.schema import MessageSchema

# from amanuensis.auth.auth import get_current_user
# from amanuensis.user import get_current_user
from amanuensis.auth.auth import current_user

from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
# from amanuensis.jwt.utils import get_jwt_header
# from amanuensis.models import query_for_user
# from amanuensis.auth.auth import register_arborist_user
# from amanuensis.crm import hubspot


logger = get_logger(__name__)


def get_all_messages(logged_user_id):
    with flask.current_app.db.session as session:
        msgs = udm.get_all_messages(session, logged_user_id)
        message_schema = MessageSchema(many=True)
        return message_schema.dump(msgs)


def get_messages_by_request(logged_user_id, request_id):
    with flask.current_app.db.session as session:
        search = udm.get_messages_by_request(session, logged_user_id, request_id)
        message_schema = MessageSchema(many=True)
        return message_schema.dump(search)



def send_message(logged_user_id, request_id, body):
    with flask.current_app.db.session as session:    
        #TODO get receivers from consorium EC members list
        receivers = [Receiver(receiver_id=r_id) for r_id in [1,2]]
        msg = udm.send_message(session, logged_user_id, request_id, body, receivers)

        message_schema = MessageSchema()

        return message_schema.dump(msg)


