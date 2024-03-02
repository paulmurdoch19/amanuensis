import flask
import jwt
import smtplib
import json
from cdislogging import get_logger
from gen3authz.client.arborist.errors import ArboristError

from amanuensis.resources.userdatamodel import (
    create_project,
    get_all_projects,
    get_project_by_consortium,
    get_project_by_user,
    get_project_by_id,
    update_project,
    associate_user,
    update_request_state,
    get_state_by_code
)
from amanuensis.resources import filterset, consortium_data_contributor, admin
from amanuensis.resources.request import get_request_state
from amanuensis.resources.userdatamodel.userdatamodel_request import (
    get_requests_by_project_id,
)
from amanuensis.resources.userdatamodel.userdatamodel_state import get_latest_request_state_by_id

from amanuensis.config import config
from amanuensis.errors import NotFound, Unauthorized, UserError, InternalError, Forbidden
from amanuensis.utils import get_consortium_list
from amanuensis.resources.fence import fence_get_users

from amanuensis.models import (
    Request,
    ConsortiumDataContributor,
    AssociatedUser,
    RequestState
)

from amanuensis.schema import ProjectSchema



logger = get_logger(__name__)


def get_all(logged_user_id, logged_user_email, special_user):
    project_schema = ProjectSchema(many=True)
    with flask.current_app.db.session as session:
        if special_user:
            if special_user == "admin":
                projects = get_all_projects(session)
                project_schema.dump(projects)
                return projects

            # #TODO check if the user is part of a EC commettee, if so get the one submitted to the consortium
            # #Get consortium
            # isEcMember = True
            # consortium = "INRG"
            # if isEcMember and consortium:
            #     projects = get_project_by_consortium(session, consortium, logged_user_id)
            #     project_schema.dump(projects)
            #     return projects
            # else:
            #     raise NotFound(
            #         "User role and consortium not matching or user {} is not assigned to the Executive Commettee in the system. Consortium: {}".format(
            #                 logged_user_id,
            #                 consortium
            #             )
            #         )

        projects = get_project_by_user(session, logged_user_id, logged_user_email)
        project_schema.dump(projects)
        return projects


def get_by_id(logged_user_id, project_id):
    project_schema = ProjectSchema()
    with flask.current_app.db.session as session:
        project = get_project_by_id(session, logged_user_id, project_id)
        project_schema.dump(project)
        return project

def get_all_associated_users(emails):
    with flask.current_app.db.session as session:
        associated_users = associate_user.get_associated_users(session, emails)
        return associated_users


def create(logged_user_id, is_amanuensis_admin, name, description, filter_set_ids, explorer_id, institution, associated_users_emails):
    # retrieve all the filter_sets associated with this project
    filter_sets = filterset.get_by_ids(logged_user_id, is_amanuensis_admin, filter_set_ids, explorer_id)
    # example filter_sets - [{"id": 4, "user_id": 1, "name": "INRG_1", "description": "", "filter_object": {"race": {"selectedValues": ["Black or African American"]}, "consortium": {"selectedValues": ["INRG"]}, "data_contributor_id": {"selectedValues": ["COG"]}}}]

    path = 'http://pcdcanalysistools-service/tools/stats/consortiums'
    consortiums = []
    for s in filter_sets:
        # Get a list of consortiums the cohort of data is from
        # example or retuned values - consoritums = ['INRG']
        # s.filter_object - you can use getattr to get the value or implement __getitem__ - https://stackoverflow.com/questions/11469025/how-to-implement-a-subscriptable-class-in-python-subscriptable-class-not-subsc
        consortiums.extend(get_consortium_list(path, s.graphql_object, s.ids_list))    
    consortiums = list(set(consortiums))
    # Defaulst state is SUBMITTED
    default_state = admin.get_by_code("IN_REVIEW")

    #TODO make sure to populate the consortium table
    # insert into consortium_data_contributor ("code", "name") values ('INRG','INRG'), ('INSTRUCT', 'INSTRuCT');
    requests = []
    for consortia in consortiums:
        # get consortium's ID
        consortium = consortium_data_contributor.get(code=consortia.upper())
        if consortium is None:
            raise NotFound(
                "Consortium with code {} not found.".format(
                    consortia
                )
            )
        req = Request()
        req.consortium_data_contributor = consortium
        req.states.append(default_state)
        requests.append(req)


    with flask.current_app.db.session as session:
        project_schema = ProjectSchema()
        project = create_project(session, logged_user_id, description, name, institution, filter_sets, requests)
        associated_users = []
        for email in associated_users_emails:
            associated_users.append({"project_id": project.id, "email": email})
        associated_users.append({"project_id": project.id, "id": logged_user_id})
        admin.add_associated_users(associated_users)
        project_schema.dump(project)
        return project


def update(project_id, approved_url, filter_set_ids):
    # TODO retrieve all the filter_sets associated with this project
    # NOT SUPPORTED YET

    if not approved_url:
        return None

    with flask.current_app.db.session as session:
        return update_project(session, project_id, approved_url)


def update_project_searches(logged_user_id, project_id, filter_sets_id):
    project_schema = ProjectSchema()
    with flask.current_app.db.session as session:
        # Retrieve the project
        project = get_project_by_id(session, logged_user_id, project_id)
        if not project:
            raise NotFound("The project with id {} has not been found".format(project_id))

        # Retrieve all the filter_sets
        filter_sets_id = [filter_sets_id] if not isinstance(filter_sets_id, list) else filter_sets_id
        filter_sets = filterset.get_filter_sets_by_ids_f(filter_sets_id)
        not_found_filter_set_ids = set(filter_sets_id) - set(filter_set.id for filter_set in filter_sets)
        if not_found_filter_set_ids:
            raise NotFound(f"filter-set-id(s), {not_found_filter_set_ids} do not exist")

        # TODO make this a config variable in amanuensis-config.yaml
        path = 'http://pcdcanalysistools-service/tools/stats/consortiums'
        new_consortiums = set()
        for s in filter_sets:
            # s.filter_object - you can use getattr to get the value or implement __getitem__ - https://stackoverflow.com/questions/11469025/how-to-implement-a-subscriptable-class-in-python-subscriptable-class-not-subsc
            new_consortiums.update(consortium.upper() for consortium in get_consortium_list(path, s.graphql_object, s.ids_list))  
            
        # Get all the consortium involved in the existing requests
        old_consortiums = {request.consortium_data_contributor.code: request for request in project.requests}
        # Check if the consortium list is changed after changing the associated search
        remove_consortiums = old_consortiums.keys() - new_consortiums
        # Defaulst state is SUBMITTED 
        if new_consortiums:
            IN_REVIEW = admin.get_by_code("IN_REVIEW", session)
            if not IN_REVIEW:
                raise NotFound("The state with code IN_REVIEW has not been found")
            
            for new_consortium_code in new_consortiums:
                consortium = consortium_data_contributor.get(code=new_consortium_code, session=session)
                if consortium is None:
                    raise NotFound(
                        "Consortium with code {} not found.".format(
                            consortium
                        )
                    )

                if consortium.code in old_consortiums:
                    req = old_consortiums[consortium.code]
                    if get_latest_request_state_by_id(session, req.id).state.code == "IN_REVIEW":
                        continue
                else:
                    req = Request()
                    req.consortium_data_contributor = consortium
                    project.requests.append(req)
                update_request_state(session, request=req, state=IN_REVIEW)
        if remove_consortiums:
            WITHDRAWAL = admin.get_by_code("WITHDRAWAL", session)
            if not WITHDRAWAL:
                raise NotFound("The state with code WITHDRAWAL has not been found")

            for remove_consortium_code in remove_consortiums:
                req = old_consortiums[remove_consortium_code]
                update_request_state(session, request=req, state=WITHDRAWAL)


        # Update he filterset
        # session.query().filter(Institution.uid == uid).update({Institution.display_name: display_name})
        # userdatamodel project -> update_project
        project.searches = filter_sets

        session.commit()
        project_schema.dump(project)
        return project

    


