"""
Blueprints for administation of the userdatamodel database and the storage
solutions. Operations here assume the underlying operations in the interface
will maintain coherence between both systems.
"""

import functools

from flask import request, jsonify, Blueprint, current_app
from flask_sqlalchemy_session import current_session

from cdislogging import get_logger

from amanuensis.auth.auth import check_arborist_auth
from amanuensis.config import config
from amanuensis.errors import UserError

from amanuensis.resources import filterset
from amanuensis.resources import project
from amanuensis.resources import admin

from amanuensis.schema import ProjectSchema


logger = get_logger(__name__)

blueprint = Blueprint("admin", __name__)


def debug_log(function):
    """Output debug information to the logger for a function call."""
    argument_names = list(function.__code__.co_varnames)

    @functools.wraps(function)
    def write_log(*args, **kwargs):
        argument_values = (
            "{} = {}".format(arg, value)
            for arg, value in list(zip(argument_names, args)) + list(kwargs.items())
        )
        msg = function.__name__ + "\n\t" + "\n\t".join(argument_values)
        logger.debug(msg)
        return function(*args, **kwargs)

    return write_log

@blueprint.route("/update_user_authz", methods=["POST"])
# @admin_login_required
@debug_log
def update_user_authz():
    """
    run user sync to update amanuensis anf arborist DB

    Receive a JSON object with the list of resources, policies, roles, and user auth

    Returns a json object
    """

    logger.warning("IN UPDATE")
    logger.warning(request.get_json())

    sync_users(
            dbGaP=[{'info': {'host': '', 'username': '', 'password': '', 'port': 22, 'proxy': '', 'proxy_user': ''}, 'protocol': 'sftp', 'decrypt_key': '', 'parse_consent_code': True}], # dbGap
            STORAGE_CREDENTIALS={}, # storage_credential
            DB=config["DB"], # flask.current_app.db, # postgresql://fence_user:fence_pass@postgres:5432/fence_db DB
            projects=None, #project_mapping
            is_sync_from_dbgap_server=False,
            sync_from_local_csv_dir=None,
            sync_from_local_yaml_file=None, #'user.yaml',
            json_from_api=request.get_json(),
            arborist=flask.current_app.arborist,
            folder=None,
        )

    # username = request.get_json().get("name", None)
    # role = request.get_json().get("role", None)
    # email = request.get_json().get("email", None)
    # return jsonify(admin.create_user(current_session, username, role, email))
    return jsonify("test")

@blueprint.route("/states", methods=["POST"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def add_state():
    """
    Create a new state

    Returns a json object
    """

    name = request.get_json().get("name", None)
    code = request.get_json().get("code", None)

    return jsonify(admin.create_state(name, code))


@blueprint.route("/filter-sets", methods=["POST"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def create_search():
    """
    Create a search on the userportaldatamodel database

    Returns a json object
    """

    user_id = request.get_json().get("user_id", None)
    if not user_id:
        raise UserError("user does not have privileges to access this endpoint")

    name = request.get_json().get("name", None)
    filter_object = request.get_json().get("filters", None)
    description = request.get_json().get("description", None)
    ids_list = request.get_json().get("ids_list", None)
    
    return jsonify(filterset.create(user_id, True, None, name, description, filter_object, ids_list))


@blueprint.route("/projects", methods=["POST"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def create_project():
    """
    Create a search on the userportaldatamodel database

    Returns a json object
    """

    user_id = request.get_json().get("user_id", None)
    if not user_id:
        raise UserError("user does not have privileges to access this endpoint")


    name = request.get_json().get("name", None)
    description = request.get_json().get("description", None)
    institution = request.get_json().get("institution", None)
    
    filter_set_ids = request.get_json().get("filter_set_ids", None)

    project_schema = ProjectSchema()
    return jsonify(project_schema.dump(project.create(user_id, True, name, description, filter_set_ids, None, institution)))




