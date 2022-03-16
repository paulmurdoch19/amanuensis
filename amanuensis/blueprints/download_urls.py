import flask

from cdislogging import get_logger

from amanuensis.errors import Forbidden, InternalError, UserError, Forbidden
from amanuensis.utils import is_valid_expiration
# from amanuensis.auth.auth import check_arborist_auth


logger = get_logger(__name__)


blueprint = flask.Blueprint("download-urls", __name__)


@blueprint.route("/<project_id>", methods=["GET"])
def download_data(project_id):
    """
    Get a presigned url to download a file given a project_id.
    """

    #TODO check param is present

    #TODO get download url from project table
    storage_url = 1

    #TODO create pre-signed URL for downalod
    # result = get_signed_url_for_file("download", storage_url)
    result = "https://pcdc-gen3-dictionaries.s3.amazonaws.com/pcdc-schema-prod-20220106.json" 

    return flask.jsonify({"url": result})
