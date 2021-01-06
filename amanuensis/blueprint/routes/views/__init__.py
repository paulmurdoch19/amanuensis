"""
Provide view functions for routes in the blueprint.
"""

import uuid

import flask
from flask import current_app
import requests

from amanuensis import auth, utils
from amanuensis.utils import parse
from amanuensis.errors import AuthError, NotFoundError, UserError
from amanuensis.globals import PROGRAM_SEED, ROLES


def get_programs():
    """
    Return the available resources at the top level above programs i.e.
    registered programs.

    Summary:
        Get the programs

    Tags:
        program

    Responses:
        200 (schema_links): Success
        403: Unauthorized request.

    :reqheader Content-Type: |reqheader_Content-Type|
    :reqheader Accept: |reqheader_Accept|
    :reqheader X-Auth-Token: |reqheader_X-Auth-Token|
    :resheader Content-Type: |resheader_Content-Type|

    **Example**

    .. code-block:: http

           GET /v0/submission/ HTTP/1.1
           Host: example.com
           Content-Type: application/json
           X-Auth-Token: MIIDKgYJKoZIhvcNAQcC...
           Accept: application/json

    .. code-block:: JavaScript

        {
            "links": [
                "/v0/sumission/CGCI/",
                "/v0/sumission/TARGET/",
                "/v0/sumission/TCGA/"
            ]
        }
    """
    # if flask.current_app.config.get("AUTH_SUBMISSION_LIST", True) is True:
    #     auth.validate_request(aud={"openid"}, purpose=None)
    # with flask.current_app.db.session_scope():
    #     programs = current_app.db.nodes(models.Program.name).all()
    # links = [flask.url_for(".get_projects", program=p[0]) for p in programs]
    # return flask.jsonify({"links": links})
    return flask.jsonify({"links": "links"})


@auth.require_amanuensis_program_admin
def root_create():
    """
    Register a program.

    The content of the request is a JSON containing the information
    describing a program.  Authorization for registering programs is
    limited to administrative users.

    Summary:
        Create a program

    Tags:
        program

    Args:
        body (schema_program): input body

    Responses:
        200: Registered successfully.
        403: Unauthorized request.

    :reqheader Content-Type:
        |reqheader_Content-Type|
    :reqheader Accept:
        |reqheader_Accept|
    :reqheader X-Auth-Token:
        |reqheader_X-Auth-Token|
    :resheader Content-Type:
        |resheader_Content-Type|

    **Example:**

    .. code-block:: http

           POST /v0/submission/CGCI/ HTTP/1.1
           Host: example.com
           Content-Type: application/json
           X-Auth-Token: MIIDKgYJKoZIhvcNAQcC...
           Accept: application/json

    .. code-block:: JavaScript

        {
            "type": "program",
            "name": "CGCI",
            "dbgap_accession_number": "phs000178"
        }
    """
    # message = None
    # node_id = None
    # doc = parse.parse_request_json()
    # if not isinstance(doc, dict):
    #     raise UserError("Root endpoint only supports single documents")
    # if doc.get("type") != "program":
    #     raise UserError("Invalid type in key type='{}'".format(doc.get("type")))
    # phsid = doc.get("dbgap_accession_number")
    # program = doc.get("name")
    # if not program:
    #     raise UserError("No program specified in key 'name'")

    # # create the resource in amanuensis DB
    # with current_app.db.session_scope(can_inherit=False) as session:
    #     node = current_app.db.nodes(models.Program).props(name=program).scalar()
    #     if node:
    #         message = "Program is updated!"
    #         node_id = node.node_id
    #         node.props["dbgap_accession_number"] = phsid
    #     else:
    #         node_id = str(uuid.uuid5(PROGRAM_SEED, program))
    #         session.add(
    #             models.Program(  # pylint: disable=not-callable
    #                 node_id, name=program, dbgap_accession_number=phsid
    #             )
    #         )
    #         message = "Program registered."

    # # create the resource in arborist
    # auth.create_resource(phsid)

    # return flask.jsonify({"id": node_id, "name": program, "message": message})
    return flask.jsonify({"id": "node_id", "name": "program", "message": "message"})

