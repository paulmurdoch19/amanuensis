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

from amanuensis.schema import ProjectSchema, StateSchema, RequestSchema, ConsortiumDataContributorSchema


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

    state_schema = StateSchema()
    return jsonify(state_schema.dump(admin.create_state(name, code)))


@blueprint.route("/consortiums", methods=["POST"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def add_consortium():
    """
    Create a new state

    Returns a json object
    """

    name = request.get_json().get("name", None)
    code = request.get_json().get("code", None)

    consortium_schema = ConsortiumDataContributorSchema()
    return jsonify(consortium_schema.dump(admin.create_consortium(name, code)))


@blueprint.route("/states", methods=["GET"])
def get_states():
    """
    Create a new state

    Returns a json object
    """

    state_schema = StateSchema(many=True)
    return jsonify(state_schema.dump(admin.get_all_states()))


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
        raise UserError("You can't create a Project without specifying the user the project will be assigned to.")

    name = request.get_json().get("name", None)
    description = request.get_json().get("description", None)
    institution = request.get_json().get("institution", None)
    
    filter_set_ids = request.get_json().get("filter_set_ids", None)

    project_schema = ProjectSchema()
    return jsonify(project_schema.dump(project.create(user_id, True, name, description, filter_set_ids, None, institution)))


@blueprint.route("/projects", methods=["PUT"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def update_project():
    """
    Update a project attributes

    Returns a json object
    """
    project_id = request.get_json().get("project_id", None)
    if not project_id:
        raise UserError("A project_id is required for this endpoint.")
    
    appoved_url = request.get_json().get("appoved_url", None)
    filter_set_ids = request.get_json().get("filter_set_ids", None)

    project_schema = ProjectSchema()
    return jsonify(project_schema.dump(admin.update_project(project_id, appoved_url, filter_set_ids)))


@blueprint.route("/projects/state", methods=["POST"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def update_project_state():
    """
    Create a new state

    Returns a json object
    """
    project_id = request.get_json().get("project_id", None)
    state_id = request.get_json().get("state_id", None)

    request_schema = RequestSchema(many=True)
    return jsonify(request_schema.dump(admin.update_project_state(project_id, state_id)))





