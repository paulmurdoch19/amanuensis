import pytest
import json
from mock import patch, Mock
from cdislogging import get_logger
from amanuensis.models import *
from amanuensis.schema import *

logger = get_logger(logger_name=__name__)




@pytest.fixture(scope="module", autouse=True)
def set_up_filter_set(client):
    with \
    patch('amanuensis.blueprints.filterset.current_user', id=108, username="endpoint_user_8@test.com"):
        filter_set_create_1_json = {
            "name":f"{__name__}",
            "description":"",
            "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INRG"],"isExclusion":False},"sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion":False}}},
            "gqlFilter":{"AND":[{"IN":{"consortium":["INRG"]}},{"IN":{"sex":["Male"]}}]}
        }
        filter_set_create_response = client.post(f'/filter-sets?explorerId=1', json=filter_set_create_1_json, headers={"Authorization": 'bearer 108'})
        assert filter_set_create_response.status_code == 200

        filter_set_id_1 = filter_set_create_response.json["id"]

        yield filter_set_id_1


@pytest.fixture(scope="module", autouse=True)
def set_up_project(set_up_filter_set, client, fence_get_users_mock):
    with \
    patch("amanuensis.resources.admin.admin_associated_user.fence.fence_get_users", side_effect=fence_get_users_mock), \
    patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"), \
    patch('amanuensis.resources.consortium_data_contributor.get_consortium_list', return_value=["INRG"]):
        create_project_json = {
            "user_id": 108,
            "name": f"{__name__}",
            "description": f"this is the project for {__name__}",
            "institution": "test university",
            "filter_set_ids": [set_up_filter_set],
            "associated_users_emails": []
        }
        create_project_response = client.post('/admin/projects', json=create_project_json, headers={"Authorization": 'bearer 200'})
        
        assert create_project_response.status_code == 200
    
    yield create_project_response.json['id']

def test_delete_project(client, session, set_up_project, fence_get_users_mock):
    with \
    patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"):
        
        delete_project_json = {"project_id": set_up_project}

        delete_project_response = client.delete('/admin/delete-project', json=delete_project_json, headers={"Authorization": 'bearer 200'})

        assert delete_project_response.status_code == 200
        
        #check project status changed
        # project = session.query(Project).filter(Project.id == set_up_project).first()
        # print(project)
        # assert project.active == False

        with \
        patch("amanuensis.blueprints.project.fence_get_users", side_effect=fence_get_users_mock), \
        patch('amanuensis.blueprints.project.current_user', id=108, username="endpoint_user_1@test.com"):
            response = client.get('/projects', headers={"Authorization": 'bearer 108'})

            assert set_up_project not in [project["id"] for project in response.json]
        
        with patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"):
            response = client.get(f'/admin/projects_by_users/108/admin@uchicago.edu', headers={"Authorization": 'bearer 200'})

            assert set_up_project not in [project["id"] for project in response.json]