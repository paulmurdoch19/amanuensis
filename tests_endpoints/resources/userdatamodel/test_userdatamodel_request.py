import pytest 
from amanuensis.models import ConsortiumDataContributor, Project, Request, RequestState, State
from amanuensis.resources.userdatamodel import get_request_by_consortium, get_requests, get_request_by_id, get_requests_by_project_id, update_request_state
from sqlalchemy import desc


@pytest.fixture(scope="module", autouse=True)
def states(session):

    state_1 = State(name="STATE1", code="STATE1")
    state_2 = State(name="STATE2", code="STATE2")
    session.add_all(
        [
            state_1,
            state_2
        ]
    )

    session.commit()

    yield state_1, state_2

    session.query(State).filter(State.code == "STATE1").delete()
    session.query(State).filter(State.code == "STATE2").delete()

    session.commit()


@pytest.fixture(scope="module", autouse=True)
def consortiums(session):

    consortium_1 = ConsortiumDataContributor(
        code="TEST1",
        name="TEST1"
    )

    consortium_2 = ConsortiumDataContributor(
        code="TEST2",
        name="TEST2"
    )

    consortium_3 = ConsortiumDataContributor(
        code="TEST3",
        name="TEST3"
    )

    session.add_all([consortium_2, consortium_1, consortium_3])
    session.commit()

    yield consortium_1, consortium_2, consortium_3

    session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "TEST1").delete()
    session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "TEST2").delete()
    session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "TEST3").delete()
    session.commit()

@pytest.fixture(scope="module", autouse=True)
def projects(session): 
    project_1 = Project(
        name='Sample Project 1',
        first_name='John',
        last_name='Doe',
        user_source='fence',
        institution='Sample Institution 1 ',
        description='A sample project description 1 ',
        approved_url='http://example.com/approved',
        active=True,
        user_id= 1
    )

    project_2 = Project(
        name='Sample Project 2',
        first_name='John',
        last_name='Doe',
        user_source='fence',
        institution='Sample Institution',
        description='A sample project description',
        approved_url='http://example.com/approved',
        active=True,
        user_id = 1
    )
    project_3 = Project(
        name='Sample Project 3',
        first_name='John',
        last_name='Doe',
        user_source='fence',
        institution='Sample Institution',
        description='A sample project description',
        approved_url='http://example.com/approved',
        active=True,
        user_id = 2
    )

    session.add_all([project_1, project_2, project_3])

    session.commit()

    # project_1_id = session.query(Project.id).filter(Project.name == 'Sample Project 1').first()[0]
    # project_2_id = session.query(Project.id).filter(Project.name == 'Sample Project 2').first()[0]
    # project_3_id = session.query(Project.id).filter(Project.name == 'Sample Project 3').first()[0]

    # yield project_1_id, project_2_id, project_3_id

    yield project_1, project_2, project_3

    session.query(Project).delete()
    session.commit()

@pytest.fixture(scope="module", autouse=True)
def requests(session, projects, consortiums):
    request_1 = Request(project=projects[0], consortium_data_contributor=consortiums[0])
    session.add_all(
        [
            request_1,
            Request(project=projects[1], consortium_data_contributor=consortiums[0]),
            Request(project=projects[1], consortium_data_contributor=consortiums[1]),
            Request(project=projects[2], consortium_data_contributor=consortiums[0]),
            Request(project=projects[2], consortium_data_contributor=consortiums[1]),
            Request(project=projects[2], consortium_data_contributor=consortiums[2]),
        ]
    )

    session.commit()



    yield request_1 


    session.query(Request).delete()


@pytest.fixture(scope="module", autouse=True)
def requesthasstate(session, requests, states):
    req_state = RequestState(request=requests, state=states[0])
    session.add(req_state)
    session.commit()

    yield req_state

    session.query(RequestState).delete()

#current_session.query(Request).join(Request.project).filter_by(user_id=user_id).all()

def test_get_requests(session):
    data = get_requests(session, 1)
    assert len(data) == 3
    for request in data:
        assert request.project.user_id == 1
    data = get_requests(session, 2)
    assert len(data) == 3
    for request in data:
        assert request.project.user_id == 2

def test_get_requests_by_consortium(session):
    data = get_request_by_consortium(session, None, "TEST1")
    assert len(data) == 3
    for request in data:
        assert request.consortium_data_contributor.code == "TEST1"

def test_get_request_by_id(session, requests):
    data = get_request_by_id(session, 1, requests.id)
    assert data.id == requests.id


def test_get_requests_by_project_id(session, projects, requests):
    data = get_requests_by_project_id(session, projects[0].id)
    assert data[0].id == requests.id

def test_update_request_state(session, requesthasstate, states, requests):
    update_request_state(session, requests, states[1])
    data = session.query(RequestState).filter(RequestState.request == requests).order_by(desc(RequestState.create_date)).first()
    assert data.state.code == "STATE2"


#create 3 consortiums
#create 3 projects with two users 
#project one has one request with con1 and user1
#project two has two requests with con1, con2 and user1
#project three has three requests with con1, con2, con3 and user2
