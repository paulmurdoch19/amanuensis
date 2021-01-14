from fence.resources import institution
from flask import current_app

__all__ = [
    "update_institutions",
    "get_all_institutions",
]

def update_institutions(current_session):
    """
    Create a project with the specified auth_id and
    storage access.
    Returns a dictionary.
    """
    institutions = institution.get_all_institutions(current_session)

    ###TODO
    # pull the new companies list from hubspot

    #TODO 
    # look for differences and add the new ones.

def get_all_institutions(current_session):
	return {institutions: [{id: 1, name: "test1"},{id:2, name: "test2"}]}