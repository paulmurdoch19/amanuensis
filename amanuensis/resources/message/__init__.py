import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
from amanuensis.resources import userdatamodel as udm
from amanuensis.resources.userdatamodel import get_all_messages, get_messages_by_request, send_message
from amanuensis.resources import request
from amanuensis.auth.auth import current_user
from amanuensis.models import (
    Message,
    Receiver
)



logger = get_logger(__name__)


def get_messages(logged_user_id, request_id=None):
    with flask.current_app.db.session as session:
        if request_id:
            msgs = udm.get_messages_by_request(session, logged_user_id, request_id)
        else:
            msgs = udm.get_all_messages(session, logged_user_id)
        
        return msgs


def send_message(logged_user_id, request_id, body):
    with flask.current_app.db.session as session:    
        # TODO get receivers from consorium EC members list (connect to fence and/or hubspot)
        # 1. retrieve from Hubspot all the EC members
        # 2. query fence by username (emails) retrieved by hubspot to get the fence user ID to use in the system
        # 3. If it doesn't exist create one?? 

        # otherwise keep fence up to date

        # Get consortium
        # req = request.get(logged_user_id, None, request_id)
        # TODO Check the request exists
        # consortium = req.consortium_data_contributor

        # Get EC members emails
        ec_members = config["EXECUTIVE_COMMITTEE"]["INSTRUCT"] #consortium.code]
        print(ec_members)
        print("LUCAAAAAAAA")

        #TODO Get EC members Fence ID
        # user = get_user from fence
        #TODO get requestor email
        # if logged_user_id is commettee memeber send to other commettee members and requestor
        # otherwise send to commettee memebers

        receivers = [Receiver(receiver_id=r_id) for r_id in [1,2]]


        # TODO Trigger emails
        msg = udm.send_message(session, logged_user_id, request_id, body, receivers)

        return msg


