import flask
from flask_sqlalchemy_session import current_session

from amanuensis.auth import require_auth_header
from amanuensis.blueprints.storage_creds.api import AccessKey, ApiKey, ApiKeyList
from amanuensis.blueprints.storage_creds.google import GoogleCredentialsList
from amanuensis.blueprints.storage_creds.google import GoogleCredentials
from amanuensis.resources.storage import get_endpoints_descriptions
from amanuensis.restful import RestfulApi
from amanuensis.config import config

ALL_RESOURCES = {
    "/api": "access to CDIS APIs",
    "/ceph": "access to Ceph storage",
    "/cleversafe": "access to cleversafe storage",
    "/aws-s3": "access to AWS S3 storage",
    "/google": "access to Google storage",
}


def make_creds_blueprint():
    blueprint = flask.Blueprint("credentials", __name__)
    blueprint_api = RestfulApi(blueprint)

    blueprint_api.add_resource(GoogleCredentialsList, "/google", strict_slashes=False)
    blueprint_api.add_resource(
        GoogleCredentials, "/google/<access_key>", strict_slashes=False
    )

    # TODO: REMOVE DEPRECATED /cdis ENDPOINTS
    # temporarily leaving them here to give time for users to make switch
    blueprint_api.add_resource(ApiKeyList, "/api", "/cdis", strict_slashes=False)
    blueprint_api.add_resource(
        ApiKey, "/api/<access_key>", "/cdis/<access_key>", strict_slashes=False
    )
    blueprint_api.add_resource(
        AccessKey, "/api/access_token", "/cdis/access_token", strict_slashes=False
    )



    return blueprint
