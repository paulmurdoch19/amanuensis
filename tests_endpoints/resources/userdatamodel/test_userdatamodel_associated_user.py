from amanuensis.models import AssociatedUser, Project, AssociatedUserRoles, ProjectAssociatedUser
from amanuensis.resources.userdatamodel import associate_user
import pytest
from amanuensis.errors import NotFound, UserError


@pytest.fixture(scope="module")
def associated_users(session):
    associated_user_1 = AssociatedUser(
        user_id=1,
        user_source='fence',
        email='user1@example.com',
        active=True
    )

    associated_user_2 = AssociatedUser(
        user_id=2,
        user_source='fence',
        email='user2@example.com',
        active=True
    )

    associated_user_3 = AssociatedUser(
        user_id=3,
        user_source='fence',
        email='user3@example.com',
        active=True
    )

    associated_user_4 = AssociatedUser(
        user_id=4,
        user_source='fence',
        email='user4@example.com',
        active=True
    )

    project = Project(
        name='Sample Project',
        first_name='John',
        last_name='Doe',
        user_source='fence',
        institution='Sample Institution',
        description='A sample project description',
        approved_url='http://example.com/approved',
        active=True
    )

    session.add_all([associated_user_1, associated_user_2, associated_user_3, associated_user_4, project])
    session.commit()

    id_1 = session.query(AssociatedUser.id).filter(AssociatedUser.user_id == 1).first()[0]
    id_2 = session.query(AssociatedUser.id).filter(AssociatedUser.user_id == 2).first()[0]
    id_3 = session.query(AssociatedUser.id).filter(AssociatedUser.user_id == 3).first()[0]
    id_4 = session.query(AssociatedUser.id).filter(AssociatedUser.user_id == 4).first()[0]
    project_id = session.query(Project.id).filter(Project.name == 'Sample Project').first()[0]

    yield [id_1, id_2, id_3, id_4, project_id]

    session.query(ProjectAssociatedUser).delete()
    session.query(AssociatedUser).delete()
    session.query(Project).delete()
    session.commit()


def test_get_associated_user(session, associated_users):
    #test correct data
    data = associate_user.get_associated_user(session, 'user1@example.com')
    assert data.id == associated_users[0]


def test_get_associated_users(session, associated_users):
    data = associate_user.get_associated_users(session, ['user1@example.com', 'user2@example.com'])
    for user in data:
        if user.id in associated_users:
            assert True

def test_get_associated_user_by_id(session, associated_users):
    #test correct data
    data = associate_user.get_associated_user_by_id(session, associated_users[0])
    assert data.user_id == 1


def test_get_associated_users_by_id(session, associated_users):
    data = associate_user.get_associated_users_by_id(session, associated_users)
    for user in data:
        if user.user_id not in [1, 2]:
            assert False 

def test_get_associated_users_by_user_id(session, associated_users):
    data = associate_user.get_associated_user_by_user_id(session, 1)
    assert data.id == associated_users[0]

def test_update_associated_user(session, associated_users):
    user = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[2]).first()
    user.email = 'updated email0'
    user.user_id = 0
    data = associate_user.update_associated_user(session, user)
    assert data == "200"
    update_user = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[2]).first()
    assert update_user.email == 'updated email0'
    assert update_user.user_id == 0

    #test error is thrown
    fake_user = AssociatedUser(id=-1)
    with pytest.raises(NotFound) as e:
        associate_user.update_associated_user(session, fake_user)


def test_update_associated_users(session, associated_users):
    user1 = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[2]).first()
    user1.email = 'updated email-1'
    user1.user_id = -1

    user2 = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[3]).first()
    user2.email = 'updated email-2'
    user2.user_id = -2

    data = associate_user.update_associated_users(session, [user1, user2])
    assert data == "200"

    update_user1 = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[2]).first()
    assert update_user1.email == 'updated email-1'
    assert update_user1.user_id == -1

    update_user2 = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[3]).first()
    assert update_user2.email == 'updated email-2'
    assert update_user2.user_id == -2


def test_add_associated_user(session, associated_users):
    role_id = session.query(AssociatedUserRoles.id).filter(AssociatedUserRoles.code == "METADATA_ACCESS").first()[0]
    project_id = associated_users[4]
    #test incorrect
    with pytest.raises(UserError) as e:
        associate_user.add_associated_user(session, project_id, None, None, role_id)

    data = associate_user.add_associated_user(session, project_id, 'test@email.com', 5, role_id)

    project_associated_user = session.query(ProjectAssociatedUser).filter(ProjectAssociatedUser.project_id == project_id).first()

    assert data.id == project_associated_user.associated_user.id

    session.query(ProjectAssociatedUser).delete()
    session.commit()

def test_add_associated_user_to_project(session, associated_users):
    role_id = session.query(AssociatedUserRoles.id).filter(AssociatedUserRoles.code == "METADATA_ACCESS").first()[0]
    project_id = associated_users[4]
    associated_user = session.query(AssociatedUser).filter(AssociatedUser.id == associated_users[0]).first()
    
    data = associate_user.add_associated_user_to_project(session, associated_user, project_id, role_id)

    project_associated_user = session.query(ProjectAssociatedUser).filter(ProjectAssociatedUser.project_id == project_id).first()

    assert data.id == project_associated_user.associated_user.id

    session.query(ProjectAssociatedUser).delete()
    session.commit()










    



