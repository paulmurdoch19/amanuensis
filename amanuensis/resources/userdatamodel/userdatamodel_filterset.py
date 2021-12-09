from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import Search, FilterSourceType

__all__ = [
    "get_filter_sets",
    "create_filter_set",
    "delete_filter_set",
    "update_filter_set",
]

def get_filter_sets(current_session, logged_user_id, filter_set_ids, explorer_id):
    '''
    Returns all, one, or multiple by id
    filter_set_id may be id(int), ids(array), or None
    '''
	#TODO make class Search serializable
    query = current_session.query(Search).filter(
        Search.active == True, 
        Search.user_id == logged_user_id,
        Search.filter_source_internal_id == explorer_id,
        Search.filter_source == FilterSourceType.explorer
    )
    if filter_set_ids:
        if not isinstance(filter_set_ids, list):
            filter_set_ids = [filter_set_ids]
        query = query.filter(Search.id.in_(filter_set_ids))

    filter_sets = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object} for s in query.all()]

    return {"filter_sets": filter_sets}


def create_filter_set(current_session, logged_user_id, explorer_id, name, description, filter_object):
    new_filter_set = Search(
        user_id=logged_user_id, 
        filter_source_internal_id=explorer_id,
        filter_source=FilterSourceType.explorer,
        user_source="fence", 
        name=name, 
        description=description, 
        filter_object=filter_object
    )
    #TODO add es_index, add dataset_version
    current_session.add(new_filter_set)
    current_session.flush()
    return {
        "name": new_filter_set.name, 
        "id": new_filter_set.id,
        "explorer_id": new_filter_set.filter_source_internal_id,
        "description": new_filter_set.description, 
        "filters": new_filter_set.filter_object
    }


def update_filter_set(current_session, logged_user_id, filter_set_id, explorer_id, name, description, filter_object):
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    if filter_object:
        data['filter_object'] = filter_object

    #TODO check that at least one has changed
    result = current_session.query(Search).filter(
        Search.id == filter_set_id, 
        Search.filter_source_internal_id == explorer_id,
        Search.filter_source == FilterSourceType.explorer,
        Search.user_id == logged_user_id
    ).update(data)
    if  result > 0:
        return  {"code": 200, "updated": filter_set_id, "explorer_id": explorer_id}
    else:
        return {"code": 500, "error": "Nothing has been updated, check the logs to see what happened during the transaction."}


def delete_filter_set(current_session, logged_user_id, filter_set_id, explorer_id):
    """
    Delete the filter_set from the database.
    The filter_set has to be assigned to 0 project request
    """
    filter_set = current_session.query(Search).filter(
        Search.id == filter_set_id, 
        Search.filter_source_internal_id == explorer_id,
        Search.filter_source == FilterSourceType.explorer,
        Search.user_id == logged_user_id
    ).first()

    if not filter_set:
        return {"code": 404, "result": "error, filter_set not found"}

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

    # current_session.delete(filter_set)
    filter_set.active = False
    return {"code": 200, "deleted": filter_set.id, "explorer_id": filter_set.filter_source_internal_id}
