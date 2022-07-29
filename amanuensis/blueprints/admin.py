"""
Blueprints for administation of the userdatamodel database and the storage
solutions. Operations here assume the underlying operations in the interface
will maintain coherence between both systems.
"""
import functools

from flask import request, jsonify, Blueprint, current_app
from flask_sqlalchemy_session import current_session
from datetime import datetime
from cdislogging import get_logger

from amanuensis.auth.auth import check_arborist_auth
from amanuensis.config import config
from amanuensis.errors import UserError

from amanuensis.resources import filterset
from amanuensis.resources import project
from amanuensis.resources import admin

from amanuensis.schema import (
    ProjectSchema,
    StateSchema,
    RequestSchema,
    ConsortiumDataContributorSchema,
)

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

    #TODO check it is present in fence

    if not user_id:
        raise UserError("Missing user_id in the payload")



    # get the explorer_id from the querystring
    # explorer_id = flask.request.args.get('explorerId', default=1, type=int)

    name = request.get_json().get("name", None)
    graphql_object = request.get_json().get("filters", {})
    description = request.get_json().get("description", None)
    ids_list = request.get_json().get("ids_list", None)

    return jsonify(
        filterset.create(
            user_id, True, None, name, description, None, ids_list, graphql_object
        )
    )

   
# @blueprint.route("/filter-sets", methods=["GET"])
# @check_arborist_auth(resource="/services/amanuensis", method="*")
# # @debug_log
# def get_search():
#     """
#     Create a search on the userportaldatamodel database

#     Returns a json object
#     """
#     user_id = request.get_json().get("user_id", None)
#     if not user_id:
#         raise UserError("Missing user_id in the payload")

#     admin = True
#     name = request.get_json().get("name", None)
#     search_id = request.get_json().get("search_id", None)
#     explorer_id = request.get_json().get('explorer_id', None)


#     if explorer_id:
#         if search_id:
#             filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object, "ids": s.ids_list} for s in filterset.get_by_id(user_id, search_id, explorer_id)]
#         elif name:
#             filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object, "ids": s.ids_list} for s in filterset.get_by_name(user_id, name, explorer_id)]
#     else:
#         if search_id:
#             filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object, "ids": s.ids_list} for s in filterset.get_by_id(user_id, search_id, explorer_id)]
#         elif name:
#             filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object, "ids": s.ids_list} for s in filterset.get_by_name(user_id, name, explorer_id)]

#     return jsonify({"filter_sets": filter_sets})

    
@blueprint.route("/filter-sets/user", methods=["GET"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def get_search_by_user_id():
    """
    Returns a json object
    """
    user_id = request.get_json().get("user_id", None)
    if not user_id:
        raise UserError("Missing user_id in the payload")

    is_admin = True
    # name = request.get_json().get("name", None)
    # search_id = request.get_json().get("search_id", None)
    # explorer_id = request.get_json().get('explorer_id', None)

    filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object, "ids": s.ids_list} for s in filterset.get_by_user_id(user_id, is_admin)]

    return jsonify({"filter_sets": filter_sets})


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
        raise UserError(
            "You can't create a Project without specifying the user the project will be assigned to."
        )

    statistician_emails = request.get_json().get("statistician_emails", None)
    if not statistician_emails:
        raise UserError(
            "You can't create a Project without specifying the statisticians that will access the data"
        )

    name = request.get_json().get("name", None)
    description = request.get_json().get("description", None)
    institution = request.get_json().get("institution", None)

    filter_set_ids = request.get_json().get("filter_set_ids", None)

    project_schema = ProjectSchema()
    return jsonify(
        project_schema.dump(
            project.create(
                user_id,
                True,
                name,
                description,
                filter_set_ids,
                None,
                institution,
                statistician_emails,
            )
        )
    )


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

    approved_url = request.get_json().get("approved_url", None)
    filter_set_ids = request.get_json().get("filter_set_ids", None)

    project_schema = ProjectSchema()
    return jsonify(
        project_schema.dump(project.update(project_id, approved_url, filter_set_ids))
    )


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

    if not state_id or not project_id:
        return UserError("There are missing params.")

    request_schema = RequestSchema(many=True)
    return jsonify(
        request_schema.dump(admin.update_project_state(project_id, state_id))
    )


@blueprint.route("/projects/date", methods=["PATCH"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
# @debug_log
def override_project_date():
    """
    Updates the update_date of a project.
    """

    project_id = request.get_json().get("project_id", None)
    year = request.get_json().get("year", 0)
    month = request.get_json().get("month", 0)
    day = request.get_json().get("day", 0)
    hour = request.get_json().get("hour", 0)
    minute = request.get_json().get("minute", 0)
    second = request.get_json().get("second", 0)
    microsecond = request.get_json().get("microsecond", 1)

    new_date = datetime(year, month, day, hour, minute, second, microsecond)

    if not project_id or not new_date:
        return UserError("There are missing params.")

    request_schema = RequestSchema(many=True)

    return jsonify(
        request_schema.dump(admin.override_project_date(project_id, new_date))
    )


@blueprint.route("/projects_by_users/<user_id>/<user_email>", methods=["GET"])
@check_arborist_auth(resource="/services/amanuensis", method="*")
def get_projetcs_by_user_id(user_id, user_email):
    project_schema = ProjectSchema(many=True)
    projects = project_schema.dump(project.get_all(user_id, user_email, None))
    return jsonify(projects)



