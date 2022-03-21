import flask

from cdislogging import get_logger

from amanuensis.auth.auth import current_user
from amanuensis.errors import AuthError, UserError, NotFound, InternalError
from amanuensis.resources.project import get_by_id
from amanuensis.resources.aws.utils import get_s3_key_and_bucket

from amanuensis.config import config


logger = get_logger(__name__)

blueprint = flask.Blueprint("download-urls", __name__)


@blueprint.route("/<path:project_id>", methods=["GET"])
def download_data(project_id):
    """
    Get a presigned url to download a file given a project_id.
    """

    try:
        logged_user_id = current_user.id
    except AuthError:
        logger.warning(
            "Unable to load or find the user, check your token"
        )

    # Check param is present
    if not project_id:
        raise UserError("A project_id is needed to retrieve the correct URL")

    project = get_by_id(logged_user_id, project_id)
    if not project:
        raise NotFound("The project with id {} has not been found.".format(project_id))

    # Get download url from project table
    storage_url = project.approved_url
    if not storage_url:
        raise NotFound("The project with id {} doesn't seem to have a loaded file with approved data.".format(project_id))


    # Create pre-signed URL for downalod

    #### TODO move this in the init file or it can be part of the stored URL
    # if "DATA_DOWNLOAD_BUCKET" not in config:
    #     raise InternalError("DATA_DOWNLOAD_BUCKET has not been set in the config. There is no bucket to download the data from.")
    # s3_bucket = config["DATA_DOWNLOAD_BUCKET"]
    ####
    # TODO
    s3_info = get_s3_key_and_bucket(storage_url)
    if s3_info is None:
        raise NotFound("The S3 bucket and key information cannot be extracted from the URL {}".format(storage_url))



    result = flask.current_app.boto.presigned_url(s3_info["bucket"], s3_info["key"], "1800", {}, "get_object")
    # result = "https://pcdc-gen3-dictionaries.s3.amazonaws.com/pcdc-schema-prod-20220106.json" 

    return flask.jsonify({"download_url": result})









