from sqlalchemy import func

from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    Search,
)


__all__ = [
    # "get_user",
    "get_all_searches",
    "get_search",
    "create_search",
    "delete_search",
    "update_search",
]


# def get_user(current_session, username):
#     return query_for_user(session=current_session, username=username)

def get_search(current_session, search_id):
    return current_session.query(Search).filter_by(id=search_id).first()


def get_all_searches(current_session):
	#TODO make class Search serializable
	searches = [{"name": s.name, "id": s.id, "description": s.description, "filters": s.filter_object} for s in current_session.query(Search).filter(Search.active == True).all()]
	return {"searches": searches}


def create_search(current_session, name, description, filter_object):
    new_search = Search(name=name, filter_object=filter_object, description=description)
    current_session.add(new_search)
    current_session.flush()
    #TODO try with serialization
    return {"name": new_search.name, "id": new_search.id, "description": new_search.description, "filters": new_search.filter_object}


def update_search(current_session, search_id, name, description, filter_object):
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    if filter_object:
        data['filter_object'] = filter_object

    return (
        current_session.query(Search).filter(Search.id == search_id).update(data)
    )

 #    session.query(Table).filter_by(col=val1).update(dict(col2=val2,col3=val3))

 #    data = {'field1': 1, 'field2': 2, 'field3': 3}
	# session.query(BlogPost).filter(blog_post_id).update(data)
	# session.commit()


def delete_search(current_session, search_id):
    """
    Delete the search from the database.
    The search has to be assigned to 0 project request
    """
    search = current_session.query(Search).filter(Search.id == search_id).first()

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
    

