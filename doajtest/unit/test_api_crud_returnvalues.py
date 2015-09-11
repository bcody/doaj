from doajtest.helpers import DoajTestCase
from portality import models
from portality.app import app
import json
from doajtest.fixtures import ApplicationFixtureFactory, ArticleFixtureFactory


class TestCrudReturnValues(DoajTestCase):

    def setUp(self):
        super(TestCrudReturnValues, self).setUp()

        account = models.Account.make_account(username="test",
                                              name="Tester",
                                              email="test@test.com",
                                              roles=["publisher"],
                                              associated_journal_ids=['abcdefghijk_journal'])
        account.set_password('password123')
        self.api_key = account.api_key
        account.save()

    def tearDown(self):
        super(TestCrudReturnValues, self).tearDown()

    def test_01_all_crud(self):

        # we should get a JSON 404 if we try to hit a nonexistent endpoint
        with app.test_client() as t_client:
            response = t_client.get('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

            response = t_client.post('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

            response = t_client.put('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

            response = t_client.delete('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

            response = t_client.patch('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

            response = t_client.head('/api/v1/not_valid')
            assert response.status_code == 404
            assert response.mimetype == 'application/json'

    def test_02_applications_crud(self):
        # add some data to the index with a Create
        user_data = ApplicationFixtureFactory.incoming_application()

        with app.test_client() as t_client:
            # log into the app as our user
            self.login(t_client, 'test', 'password123')

            # create a new application
            response = t_client.post('/api/v1/applications?api_key=' + self.api_key, data=json.dumps(user_data))
            assert response.status_code == 201
            assert response.mimetype == 'application/json'

            # Check it gives back a newly created application, with an ID
            new_app_id = json.loads(response.data)['id']
            new_app_loc = json.loads(response.data)['location']
            assert new_app_id is not None
            assert new_app_id in new_app_loc
            print new_app_loc

            # retrieve the same application using the location then ID
            response = t_client.get('/api/v1/application/{0}?api_key={1}'.format(new_app_id, self.api_key))
            assert response.status_code == 200
            assert response.mimetype == 'application/json'

            retrieved_application = json.loads(response.data)
            new_app_title = retrieved_application['bibjson']['title']
            assert new_app_title == ApplicationFixtureFactory.incoming_application()['bibjson']['title']


    @staticmethod
    def login(app, username, password):
        return app.post('/account/login',
                        data=dict(username=username, password=password),
                        follow_redirects=True)

    @staticmethod
    def logout(app):
        return app.get('/account/logout', follow_redirects=True)
