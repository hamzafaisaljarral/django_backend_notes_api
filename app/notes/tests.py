from django.test import TestCase, RequestFactory
from . import models, urls_name, views
from rest_framework.reverse import reverse
from rest_framework import status


# Create your tests here.
class UserTestCase(TestCase):
    """This class test the user model"""

    def setUp(self):
        """Define the test client and other tests variables"""
        self.user_email = 'foo.bar@gmail.com'
        self.user_password = 'lb/n2dcx'
        self.user_model = models.UserModel(email=self.user_email, password=self.user_password)

    def test_model_can_create_user(self):
        """Check if the model can create new users"""
        old_count = models.UserModel.objects.count()
        self.user_model.save()
        new_count = models.UserModel.objects.count()
        self.assertNotEqual(old_count, new_count)
        self.assertGreater(new_count, old_count)
        self.assertEqual(0, old_count)

    def test_model_can_retrieve_user(self):
        """Check if the user can be retrieved through his email"""
        new_user = models.UserModel(email='bar.foo@epitech.eu', password='toto')
        new_user.save()
        retrieved_new_user = models.UserModel.objects.get(email='bar.foo@epitech.eu')
        self.assertEqual(1, models.UserModel.objects.count())
        self.assertEqual('bar.foo@epitech.eu', retrieved_new_user.email)

    def test_model_can_remove_user(self):
        """Check if the user can be removed"""
        foo_bar = models.UserModel(email='foo.bar@epitech.eu', password='toto')
        bar_foo = models.UserModel(email='bar.foo@epitech.eu', password='tutu')
        other = models.UserModel(email='lala.lulu@epitech.eu', password='lalalulu')
        foo_bar.save()
        bar_foo.save()
        other.save()
        self.assertEqual(3, models.UserModel.objects.count())
        foo_bar_retrieved = models.UserModel.objects.get(email='foo.bar@epitech.eu')
        self.assertEqual('foo.bar@epitech.eu', foo_bar_retrieved.email)
        foo_bar_retrieved.delete()
        self.assertEqual(2, models.UserModel.objects.count())

    def test_model_can_update_user(self):
        """Check if model can update the user"""
        new_user = models.UserModel(email='bar.foo@epitech.eu', password='toto')
        foo_bar = models.UserModel(email='foo.bar@epitech.eu', password='toto')
        other = models.UserModel(email='lala.lulu@epitech.eu', password='lalalulu')
        new_user.save()
        foo_bar.save()
        other.save()
        self.assertEqual(3, models.UserModel.objects.count())
        queryset_new_user = models.UserModel.objects.filter(email__startswith='foo.bar@epitech')
        queryset_change_email = models.UserModel.objects.filter(email__startswith='bar.foo')
        self.assertEqual(1, queryset_new_user.count())
        self.assertEqual(1, queryset_change_email.count())
        queryset_new_user.update(is_ban=True)
        queryset_change_email.update(email='lulu.lala@epitech.eu')
        updated_email_user = models.UserModel.objects.get(email='lulu.lala@epitech.eu')
        updated_user = models.UserModel.objects.get(email='foo.bar@epitech.eu')
        self.assertEqual(True, updated_user.is_ban)
        self.assertEqual('lulu.lala@epitech.eu', updated_email_user.email)


class NotesModelTest(TestCase):
    """This class test the model of a notes"""

    def setUp(self):
        """Setup the tests"""
        self.user = models.UserModel(email='test.test@gmail.com', password='password')
        self.user.save()
        self.std_notes = models.Notes(title='first notes to be tested',
                                             body='description of the tested notes', tags='created', owner=self.user)

    def test_model_can_filter_and_read_notes(self):
        """Check if we can retrieve notes from the model"""
        note_custom = models.Notes(title='Simple notes', body='simple notes', tags='created', owner=self.user)
        note_custom2 = models.Notes(title='custom notes', body='custom notes', tags='done', owner=self.user)
        note_custom.save()
        note_custom2.save()
        notes_queryset = models.Notes.objects.filter(tags__contains='created')
        notes_queryset_owner = models.Notes.objects.filter(owner__email='test.test@gmail.com')
        self.assertEqual(1, notes_queryset.count())
        self.assertEqual(2, notes_queryset_owner.count())

    def test_model_can_create_notes(self):
        """Test if we can insert notes inside the database"""
        self.assertEqual(0, models.Notes.objects.count())
        self.std_notes.save()
        self.assertEqual(1, models.Notes.objects.count())
        registered_notes = models.Notes.objects.get()
        self.assertEqual(self.std_notes.id, registered_notes.id)
        self.assertEqual(self.std_notes.title, registered_notes.title)
        self.assertEqual(self.std_notes.body, registered_notes.body)
        self.assertEqual(self.std_notes.tags, registered_notes.tags)


class AuthTest(TestCase):
    """Test case used to test the authentication and registration"""

    def setUp(self):
        """Setup the tests"""
        self.user = models.UserModel(email='toto.titi@epitech.eu', password='toto')
        self.banned_user = models.UserModel(email='titi.toto@epitech.eu', password='test', is_ban=True)

    def test_api_can_signin_user(self):
        """Test if the user can authenticate with the api"""
        self.user.save()
        self.banned_user.save()
        response = self.client.post(reverse(urls_name.LOGIN_NAME),
                                    {'email': self.user.email, 'password': self.user.password})
        response_is_ban = self.client.post(reverse(urls_name.LOGIN_NAME),
                                           {'email': self.banned_user.email, 'password': self.banned_user.password})
        response_unknown_user = self.client.post(reverse(urls_name.LOGIN_NAME),
                                                 {'email': 'unknown.user@epitech.eu', 'password': 'unknown'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_is_ban.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_unknown_user.status_code)

    def test_api_can_register_user(self):
        """Test if the API can register an user"""
        self.user.save()

        response = self.client.post(reverse(urls_name.REGISTER_NAME),
                                    {'email': 'test.register@gmail.com', 'password': 'test-password'})
        response_user_already_exist = self.client.post(reverse(urls_name.REGISTER_NAME),
                                                       {'email': self.user.email, 'password': self.user.password})
        response_user_email_invalid = self.client.post(reverse(urls_name.REGISTER_NAME),
                                                       {'email': 'bad-email', 'password': 'unknown'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_user_already_exist.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_user_email_invalid.status_code)

    def test_api_can_logout_user(self):
        """Test the logout action of the API"""
        self.user.save()

        login_response = self.client.post(reverse(urls_name.LOGIN_NAME),
                                          {'email': self.user.email, 'password': self.user.password})
        response_logout = self.client.get(reverse(urls_name.LOGOUT_NAME))
        response_logout_without_auth = self.client.get(reverse(urls_name.LOGOUT_NAME))

        self.assertEqual(status.HTTP_200_OK, login_response.status_code)
        self.assertEqual(status.HTTP_200_OK, response_logout.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_logout_without_auth.status_code)


class NotesListView(TestCase):
    """Test case used to test the notes list view"""

    def __execute_get_request(self, user):
        """
            Execute a get request and return the response
            :param user: The user used inside the request
            :return: An http response
        """
        request_get = self.request_factory.get(reverse(urls_name.NOTES_LIST_NAME))
        request_get.user = user
        notesListView = views.ListNotes.as_view()
        response = notesListView(request_get)
        return response

    def __execute_post_request(self, requestUser, jsonTodo):
        """
            Execute a post request and return the response
            :param requestUser: The user used during the post request
            :param jsonTodo: The notes used during the post request
            :return: An Http response
        """
        request_post = self.request_factory.post(reverse(urls_name.NOTES_LIST_NAME), jsonTodo)
        request_post._dont_enforce_csrf_checks = True
        request_post.user = requestUser
        notesListView = views.ListNotes.as_view()
        response = notesListView(request_post)
        return response

    def setUp(self):
        """Setup the test"""
        self.request_factory = RequestFactory()
        self.user = models.UserModel(email='toto.titi-list-view-test@epitech.eu', password='toto')
        self.admin = models.UserModel(email='admin.admin-list-view-test@gmail.com', password='admin', is_superuser=True)
        self.banned_user = models.UserModel(email='banned.banned-list-view-test@gmail.com', password='banned',
                                            is_ban=True)
        self.admin.save()
        self.user.save()
        self.banned_user.save()

    def test_api_can_get_notes(self):
        """Api can get the notes from the database"""
        response = self.__execute_get_request(None)
        user_response = self.__execute_get_request(self.user)
        admin_response = self.__execute_get_request(self.admin)
        banned_repsonse = self.__execute_get_request(self.banned_user)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, banned_repsonse.status_code)
        self.assertEqual(status.HTTP_200_OK, admin_response.status_code)
        self.assertEqual(status.HTTP_200_OK, user_response.status_code)

    def test_api_can_post_nodes(self):
        """Api can post a nodes by being connected"""
        self.admin.save()
        self.user.save()
        self.banned_user.save()
        response_forbidden = self.__execute_post_request(None, {'title': 'test', 'body': 'test',
                                                                'tags': 'created'})
        response_forbidden_banned_user = self.__execute_post_request(self.banned_user,
                                                                     {'title': 'test', 'body': 'test',
                                                                      'tags': 'created'})
        response_admin_ok = self.__execute_post_request(self.admin, {'title': 'test', 'body': 'test',
                                                                     'tags': 'created'})
        response_ok = self.__execute_post_request(self.user, {'title': 'test', 'body': 'test',
                                                              'tags': 'created'})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response_forbidden.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_forbidden_banned_user.status_code)
        self.assertEqual(status.HTTP_201_CREATED, response_ok.status_code)
        self.assertEqual(status.HTTP_201_CREATED, response_admin_ok.status_code)


class NotesAPIView(TestCase):
    """Test case used to test the notes update,delete and search view"""

    def __execute_update_request(self, notes, modification, user):
        """
            Execute a put request and return the response
            :param notes: The note used for the request
            :param user: The user used for the request
            :return: The Http reponse
        """
        request_put = self.request_factory.put(reverse(urls_name.NOTES_UPDATE, kwargs={'pk': notes.id}),
                                               modification, content_type='application/json')
        request_put.user = user
        request_put._dont_enforce_csrf_checks = True
        detail = views.UpdateAPIView.as_view()
        return detail(request_put, pk=notes.id)

    def __execute_delete_command(self, notes, user):
        """
            Execute a delete command and return the response
            :param notes: The notes used for the request
            :param user: The user used for the request
        """
        request_delete = self.request_factory.delete(reverse(urls_name.NOTES_DELETE, kwargs={'pk': notes.id}))
        request_delete.user = user
        request_delete._dont_enforce_csrf_checks = True
        detail = views.DestroyAPIView.as_view()
        return detail(request_delete, pk=notes.id)

    def __execute_search_command(self, search, user):
        """
            Execute a search command and return the response
            :param search: The search keywords
            :param user: The user used for the request
        """
        request_search = self.request_factory.get(urls_name.FILTER_TAGS, params={'search':search})
        request_search.user = user
        request_search._dont_enforce_csrf_checks = True
        detail = views.FilterAPIView.as_view()
        return detail(request_search, tags=search)

    def setUp(self):
        """Setup the test"""
        self.request_factory = RequestFactory()
        self.user = models.UserModel(email='toto.titi@tutu.com', password='test')
        self.user_banned = models.UserModel(email='banned.user@gmail.com', password='test', is_ban=True)
        self.admin = models.UserModel(email='admin.api@test.com', password='admin', is_superuser=True)
        self.admin.save()
        self.user.save()
        self.user_banned.save()
        self.notes = models.Notes(title='notes', body='test description', owner=self.user)
        self.admin_notes = models.Notes(title='admin notes test', body='admin notes test description',
                                               owner=self.admin)
        self.banned_notes = models.Notes(title='todo made by a banned user',
                                                body='todo made by a banned user', owner=self.user_banned)
        self.notes.save()
        self.admin_notes.save()
        self.banned_notes.save()

    def test_api_can_delete_notes(self):
        """Test case that check if we can delete the nodes"""
        notes_by_user = models.Notes(title='test to remove', body='test descritpion to remove',
                                            owner=self.user)
        notes_by_user_removed_by_admin = models.Notes(title='test to remove',
                                                             body='test descritpion to remove', owner=self.user)
        notes_by_admin = models.Notes(title='test to remove', body='todo from the admin to remove',
                                             owner=self.admin)
        notes_by_banned_user = models.Notes(title='test to remove', body='todo from the admin to remove',
                                                   owner=self.admin)
        notes_by_user.save()
        notes_by_user_removed_by_admin.save()
        notes_by_admin.save()
        notes_by_banned_user.save()

        removed_user_notes = self.__execute_delete_command(notes=notes_by_user, user=self.user)
        removed_admin_notes_forbidden = self.__execute_delete_command(notes=notes_by_admin, user=self.user)
        removed_admin_notes_user = self.__execute_delete_command(notes=notes_by_user_removed_by_admin, user=self.admin)
        removed_task_by_banned_user_forbidden = self.__execute_delete_command(notes=notes_by_banned_user,
                                                                              user=self.user_banned)
        removed_non_existent_notes = self.__execute_delete_command(notes=notes_by_user, user=self.user)

        self.assertEqual(status.HTTP_204_NO_CONTENT, removed_user_notes.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, removed_admin_notes_forbidden.status_code)
        self.assertEqual(status.HTTP_204_NO_CONTENT, removed_admin_notes_user.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, removed_task_by_banned_user_forbidden.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, removed_non_existent_notes.status_code)


    def test_api_can_update_detail_of_a_notes(self):
        """Test if we can update detail of a notes"""
        user_modification_response = self.__execute_update_request(self.notes, {'title': 'Modified by user',
                                                                            'body': self.notes.body},
                                                                self.user)
        user_modification_ill_formed_response = self.__execute_update_request(self.notes, {'title': 'Modified by user'},
                                                                           self.user)
        user_modification_on_another_task = self.__execute_update_request(self.admin_notes, {'title': 'Modified by user',
                                                                                         'body': 'Description modified by user'},
                                                                       self.user)
        admin_modification_response = self.__execute_update_request(self.notes, {'title': 'Modified by the admin',
                                                                             'body': 'Description modified by the admin'},
                                                                 self.admin)
        banned_forbidden_modification = self.__execute_update_request(self.banned_notes,
                                                                   {'title': 'modified by a banned user',
                                                                    'body': self.banned_notes.body},
                                                                   self.user_banned)

        self.assertEqual(status.HTTP_200_OK, user_modification_response.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, user_modification_ill_formed_response.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, user_modification_on_another_task.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, banned_forbidden_modification.status_code)
        self.assertEqual(status.HTTP_200_OK, admin_modification_response.status_code)


    def test_api_can_search_tags_of_a_notes(self):
        """Test if we can search  of a notes"""
        user_search_response = self.__execute_search_command(search = 'created',user=self.user)
        admin_search_response = self.__execute_search_command(search = 'created',user=self.admin)

        self.assertEqual(status.HTTP_200_OK, user_search_response.status_code)
        self.assertEqual(status.HTTP_200_OK, admin_search_response.status_code)


class UserListTest(TestCase):
    """Test the UserList view"""

    def __execute_get_request(self, user):
        """
            Execute a get request and return the response
            :param user: The user of the get request
            :return: An Http response
        """
        request_get = self.request_factory.get(reverse(urls_name.USER_LIST_NAME))
        request_get.user = user
        request_get._dont_enforce_csrf_checks = True
        listUser = views.ListUser.as_view()
        return listUser(request_get)

    def __execute_post_request(self, user, user_to_insert):
        """
            Execute a post request and return the response
            :param user: The user of the post request
            :param user_to_insert: The user to insert inside the database
            :return: An http response
        """
        request_post = self.request_factory.post(reverse(urls_name.USER_LIST_NAME), user_to_insert)
        request_post.user = user
        request_post._dont_enforce_csrf_checks = True
        listUser = views.ListUser.as_view()
        return listUser(request_post)

    def setUp(self):
        """Setting up the test case"""
        self.normal_user = models.UserModel(email='normal-user@gmail.com', password='password')
        self.admin_user = models.UserModel(email='admin-user@gmail.com', password='password', is_superuser=True)
        self.banned_user = models.UserModel(email='banned-user@gmail.com', password='password', is_ban=True)
        self.request_factory = RequestFactory()

    def test_user_cannot_get_user(self):
        """Test if the user can retrieve users"""
        self.normal_user.save()
        response = self.__execute_get_request(user=self.normal_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_banned_user_cannot_get_users(self):
        """Test if a banned user can retrieve users"""
        self.banned_user.save()
        response = self.__execute_get_request(user=self.banned_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_admin_user_can_get_users(self):
        """Test if an admin user can retrieve users"""
        self.admin_user.save()
        response = self.__execute_get_request(user=self.admin_user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_user_cannot_post_user(self):
        """Test if a user can post a new user"""
        self.normal_user.save()
        response = self.__execute_post_request(user=self.normal_user,
                                               user_to_insert={'email': 'test@test.com', 'password': 'test'})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_banned_user_cannot_post_user(self):
        """Test if a banned user can post a new user"""
        self.banned_user.save()
        response = self.__execute_post_request(user=self.banned_user,
                                               user_to_insert={'email': 'test@test.com', 'password': 'test'})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_admin_user_can_post_user(self):
        """Test if an admin can create custom users"""
        self.admin_user.save()
        response = self.__execute_post_request(user=self.admin_user,
                                               user_to_insert={'email': 'test@test.com', 'password': 'password'})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)


class UserDetailTest(TestCase):
    """Automated test of the user detail"""

    def __execute_get_request(self, id, user):
        """
            Execute a get request and return the response
            :param id: the id of the user to retrieve
            :param user: the user that makes the request
            :return: an Http response
        """
        request_get = self.request_factory.get(reverse(urls_name.USER_DETAIL_NAME, kwargs={'pk': id}))
        request_get.user = user
        detail = views.DetailUser.as_view()
        return detail(request_get, pk=id)

    def __execute_put_request(self, id, user, data):
        """
            Execute a put request to modify the user with the speicified id
            :param id: The id of the user requested
            :param user: The user that execute the request
            :param data: Data to modify
            :return: An HTTP response
        """
        request_put = self.request_factory.patch(reverse(urls_name.USER_DETAIL_NAME, kwargs={'pk': id}), data,
                                                 content_type='application/json')
        request_put.user = user
        request_put._dont_enforce_csrf_checks = True
        detail = views.DetailUser.as_view()
        return detail(request_put, pk=id)

    def __execute_delete_request(self, id, user):
        """
            Execute a delete request
            :param id: The id of the requested user to delete
            :param user: The user that makes the request
            :return: An HTTP response
        """
        request_delete = self.request_factory.delete(reverse(urls_name.USER_DETAIL_NAME, kwargs={'pk': id}))
        request_delete.user = user
        request_delete._dont_enforce_csrf_checks = True
        detail = views.DetailUser.as_view()
        return detail(request_delete, pk=id)

    def setUp(self):
        """Setup test environnement"""
        self.request_factory = RequestFactory()
        self.normal_user = models.UserModel(email='normal.user@test.com', password='password')
        self.banned_user = models.UserModel(email='banned.user@test.com', password='password', is_ban=True)
        self.admin_user = models.UserModel(email='admin.user@test.com', password='password', is_superuser=True)
        self.normal_user.save()

    def test_user_cannot_get_detailed_user(self):
        """Check if an user cannot get another profile than itself"""
        self.admin_user.save()
        response_admin_profile = self.__execute_get_request(id=self.admin_user.id, user=self.normal_user)
        response_own_profile = self.__execute_get_request(id=self.normal_user.id, user=self.normal_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_admin_profile.status_code)
        self.assertEqual(status.HTTP_200_OK, response_own_profile.status_code)

    def test_banned_user_cannot_get_detailed_user(self):
        """Check if a banned user can get its own profile or another one"""
        self.banned_user.save()
        response_other_user = self.__execute_get_request(id=self.normal_user.id, user=self.banned_user)
        response_own_profile = self.__execute_get_request(id=self.banned_user.id, user=self.banned_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_other_user.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_own_profile.status_code)

    def test_admin_user_can_access_all_profile(self):
        """Check if an admin can access to every profile"""
        self.banned_user.save()
        self.admin_user.save()
        response_admin_profile = self.__execute_get_request(id=self.admin_user.id, user=self.admin_user)
        response_banned_profile = self.__execute_get_request(id=self.banned_user.id, user=self.admin_user)
        response_normal_user_profile = self.__execute_get_request(id=self.normal_user.id, user=self.admin_user)
        self.assertEqual(status.HTTP_200_OK, response_admin_profile.status_code)
        self.assertEqual(status.HTTP_200_OK, response_banned_profile.status_code)
        self.assertEqual(status.HTTP_200_OK, response_normal_user_profile.status_code)

    def test_user_cannot_put_other_profile(self):
        """Test if the user can update other profile"""
        self.banned_user.save()
        response_banned_user = self.__execute_put_request(id=self.banned_user.id, user=self.normal_user,
                                                          data={'is_ban': False})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_banned_user.status_code)

    def test_user_can_update_its_profile(self):
        """Test if the user can edit its own profile"""
        response_own_user = self.__execute_put_request(id=self.normal_user.id, user=self.normal_user,
                                                       data={'email': 'edited-normal-user@gmail.com'})
        self.assertEqual(status.HTTP_200_OK, response_own_user.status_code)

    def test_banned_user_can_update_its_own_profile(self):
        """Test if a banned user can edit its own profile"""
        self.banned_user.save()
        response_banned_user = self.__execute_put_request(id=self.banned_user.id, user=self.banned_user,
                                                          data={'email': 'edit-banned-user@gmail.com'})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response_banned_user.status_code)

    def test_admin_can_edit_other_profile(self):
        """Test if an admin can edit other profile"""
        self.admin_user.save()
        response_own_user = self.__execute_put_request(id=self.normal_user.id, user=self.admin_user,
                                                       data={'email': 'modified-by-admin@gmail.com', 'is_ban': True})
        self.assertEqual(status.HTTP_200_OK, response_own_user.status_code)

    def test_user_can_delete_its_own_profile(self):
        """Test if an user can delete its own profile"""
        response_own_user = self.__execute_delete_request(id=self.normal_user.id, user=self.normal_user)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response_own_user.status_code)

    def test_user_cannot_delete_other_profile(self):
        """Test if an user can delete other profile"""
        self.banned_user.save()
        response = self.__execute_delete_request(id=self.banned_user.id, user=self.normal_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_banned_user_cannot_delete_its_own_profile(self):
        """Test if a banned user can delete its own profile"""
        self.banned_user.save()
        response = self.__execute_delete_request(id=self.banned_user.id, user=self.banned_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_banned_user_cannot_delete_other_profile(self):
        """Test if a banned user can delete other profile than its own"""
        self.banned_user.save()
        response = self.__execute_delete_request(id=self.banned_user.id, user=self.banned_user)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_admin_can_delete_other_profile(self):
        """Test if an admin can delete other profile"""
        self.admin_user.save()
        response = self.__execute_delete_request(id=self.normal_user.id, user=self.admin_user)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_admin_can_delete_its_own_profile(self):
        """Test if an admin can delete its own profile"""
        self.admin_user.save()
        response = self.__execute_delete_request(id=self.admin_user.id, user=self.admin_user)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
