from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    Search,
)


__all__ = [
    "get_all_searches",
    "get_search",
    "create_search",
    "delete_search",
    "update_search",
]



def get_search(current_session, logged_user_id, search_id):
    search = current_session.query(Search).filter_by(id=search_id).filter_by(user_id=logged_user_id).first()
    return search


def get_all_searches(current_session, logged_user_id):
	#TODO make class Search serializable
	searches = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object} for s in current_session.query(Search).filter(Search.active == True, Search.user_id == logged_user_id).all()]
	return {"searches": searches}


def create_search(current_session, logged_user_id, name, description, filter_object):
    new_search = Search(user_id=logged_user_id, 
                        user_source="fence", 
                        name=name, 
                        description=description, 
                        filter_object=filter_object)
    #TODO add es_index, add dataset_version
    current_session.add(new_search)
    current_session.flush()
    #TODO try with serialization
    return {"name": new_search.name, "id": new_search.id, "description": new_search.description, "filters": new_search.filter_object}


def update_search(current_session, logged_user_id, search_id, name, description, filter_object):
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    if filter_object:
        data['filter_object'] = filter_object

    #TODO check that at least one has changed
    result = current_session.query(Search).filter(Search.id == search_id, Search.user_id == logged_user_id).update(data)
    if  result > 0:
        return  {"code": 200, "updated": search_id}
    else:
        return {"code": 500, "error": "Nothing has been updated, check the logs to see what happened during the transaction."}


def delete_search(current_session, logged_user_id, search_id):
    """
    Delete the search from the database.
    The search has to be assigned to 0 project request
    """
    search = current_session.query(Search).filter(Search.id == search_id, Search.user_id == logged_user_id).first()

    if not search:
        return {"code": 404, "result": "error, search not found"}

    #TODO
    # proj_request = (
    #     current_session.query(ProjectToBucket)
    #     .filter(ProjectToBucket.project_id == proj.id)
    #     .first()
    # )

    # if proj_request:
    #     msg = (
    #         "error, project still has buckets associated with it. Please"
    #         " remove those first and then retry."
    #     )
    #     return {"result": msg}

    # current_session.delete(search)
    search.active = False
    return {"code": 200, "deleted": search.id}
    

