from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles.models import Profile
from accounts.models import Account
from characters.models import Character
from memories.models import Memory, Video


# User and Auth related tests
class UserCreationTestCase(APITestCase):
    def test_successful_user_creation(self):
        url = reverse('create_user') 

        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')

    def test_missing_username_field(self):
        url = reverse('create_user') 

        # Missing the 'username' field
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Assert that the response contains an appropriate error message
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'][0], 'This field is required.')
        
        # Assert that no user or profile objects are created in the database
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
    
    def test_invalid_email_format(self):
        url = reverse('create_user')
        
        # Invalid email format (missing @ symbol)
        data = {
            'username': 'testuser',
            'email': 'testuserexample.com',
            'password': 'testpassword',
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
        
    def test_password_too_short(self):
        url = reverse('create_user')
        
        # Password shorter than the required minimum length
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'pass',  # Short password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
        
    def test_missing_email_field(self):
        url = reverse('create_user')

        # Missing email field
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            # 'email' field is missing
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'This field is required.')

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
        
    def test_duplicate_email(self):
        # Create a user with a specific email to simulate a duplicate email scenario
        user1 = User.objects.create(username='existinguser', email='existinguser@example.com')
        Profile.objects.create(user=user1)

        url = reverse('create_user')
        
        # Duplicate email
        data = {
            'username': 'testuser',
            'email': 'existinguser@example.com',  # Use the existing email
            'password': 'testpassword',
        }
        
        response = self.client.post(url, data, format='json')
        
        # Depending on your implementation, you can use 400 or 409 status code for duplicate email
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT])
        
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'This email address is already in use.')
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.create_user_url = reverse('create_user')
        self.authenticate_user_url = reverse('authenticate_user')

        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        self.client.post(self.create_user_url, self.user_data, format='json')

    def test_successful_authentication(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.authenticate_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_password(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }

        response = self.client.post(self.authenticate_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_username(self):
        data = {
            'username': 'wrongtestuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.authenticate_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_credentials(self):
        data = {}

        response = self.client.post(self.authenticate_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_authentication(self):
        # Set user as inactive
        user = User.objects.get(username='testuser')
        user.is_active = False
        user.save()

        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.authenticate_user_url, data, format='json')

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

class LogoutTestCase(APITestCase):
    def setUp(self):
        self.create_user_url = reverse('create_user')
        self.authenticate_user_url = reverse('authenticate_user')
        self.logout_user_url = reverse('logout_user')

        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        self.client.post(self.create_user_url, self.user_data, format='json')
        response = self.client.post(self.authenticate_user_url, self.user_data, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_successful_logout(self):
        response = self.client.post(self.logout_user_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions as per your application's logout response.

    def test_unauthorized_logout(self):
        self.client.force_authenticate(user=None)  # Remove authentication credentials

        response = self.client.post(self.logout_user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Add additional assertions as per your application's unauthorized logout response.

    def test_missing_token_logout(self):
        self.client.credentials()  # Remove authentication credentials

        response = self.client.post(self.logout_user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Add additional assertions as per your application's missing token logout response.

# Profile related tests
class UpdateProfileTestCase(APITestCase):
    def setUp(self):
        self.create_user_url = reverse('create_user')
        self.authenticate_user_url = reverse('authenticate_user')
        self.update_profile_url = reverse('update_profile', args=[1])  # Replace `1` with the profile ID to update

        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        self.client.post(self.create_user_url, self.user_data, format='json')
        response = self.client.post(self.authenticate_user_url, self.user_data, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_successful_profile_update(self):
        data = {
            'name': 'Updated Name',
            'middle_name': 'Updated Middle Name',
            'last_name': 'Updated Last Name',
            'birth_date': '1990-01-01',
            'gender': 'other',
        }

        response = self.client.patch(self.update_profile_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions as per your application's successful profile update response.

    def test_unauthorized_profile_update(self):
        self.client.force_authenticate(user=None)  # Remove authentication credentials

        data = {
            'name': 'Updated Name',
            'middle_name': 'Updated Middle Name',
            'last_name': 'Updated Last Name',
            'birth_date': '1990-01-01',
            'gender': 'other',
        }

        response = self.client.patch(self.update_profile_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Add additional assertions as per your application's unauthorized profile update response.

# Account related tests
class AccountCreateTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            username="testuser",
            password="testpassword123"
        )
        
        Profile.objects.create(user=self.user)

        # Authenticate the test user
        self.client.force_authenticate(user=self.user)

        # URL for creating an account
        self.create_url = reverse('create_account')

    def test_create_account(self):
        # Data to be used to create an account
        data = {
            'name': 'Test Account',
        }
        
        # Create an account
        response = self.client.post(self.create_url, data)

        # Assert that the account was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Account')

        # Assert that the account is associated with the test user
        self.assertEqual(response.data['owner_user'], self.user.id)

    def test_create_account_unauthenticated(self):
        # Log out the test user
        self.client.logout()

        # Data to be used to create an account
        data = {
            'name': 'Test Account',
        }

        # Attempt to create an account
        response = self.client.post(self.create_url, data)

        # Assert that unauthenticated users cannot create an account
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AccountUpdateAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )

        Profile.objects.create(user=self.user)
        
        self.client.force_authenticate(user=self.user)

        self.account = Account.objects.create(owner_user=self.user, name='Test Account')

    def test_update_account_name(self):
        url = reverse('update_account', args=[self.account.pk]) 

        # Send a PATCH request to update only the name field
        new_name = 'Updated Account Name'
        data = {'name': new_name}
        response = self.client.patch(url, data)

        # Check the response status code and updated name value in the database
        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, new_name)

        # Ensure other fields remain unchanged
        self.assertEqual(self.account.owner_user, self.user)
        self.assertEqual(set(self.account.beloved_ones.all()), set())

    def test_update_account_owner_user(self):
        # Create a second test user
        new_user = User.objects.create_user(username='newuser', password='testpassword')
        Profile.objects.create(user=new_user)

        url = reverse('update_account', args=[self.account.pk])   # Assuming 'account-owner-update' is the endpoint for updating the owner_user field

        # Send a PATCH request to update the owner_user field
        data = {'owner_user': new_user.id}  # Try to change the owner_user to the new_user
        response = self.client.patch(url, data)

        # Check the response status code and ensure it is a failure (e.g., 4xx or 5xx)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the owner_user field remains unchanged in the database
        self.account.refresh_from_db()
        self.assertEqual(self.account.owner_user, self.user)

    def test_update_inactive_account(self):
        url = reverse('update_account', args=[self.account.pk]) 

        account = Account.objects.get(id=self.account.pk)
        account.is_active = False
        account.save()

        # Send a PATCH request to update only the name field
        new_name = 'Failing update Account Name'
        data = {'name': new_name}
        response = self.client.patch(url, data)

        # Check the response status code and updated name value in the database
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, 'Test Account')

class ListUserAccountsViewsTest(APITestCase):
    def setUp(self):
        # Create mainuser
        self.mainuser = User.objects.create_user(
            username='mainuser',
            password='testpassword'
        )
        mainuser_profile = Profile.objects.create(user=self.mainuser)

        # Create dummyuser_one
        self.dummyuser_one = User.objects.create_user(
            username='dummyuser_one',
            password='testpassword'
        )
        dummyuser_one_profile = Profile.objects.create(user=self.dummyuser_one)

        # Create dummyuser_two
        self.dummyuser_two = User.objects.create_user(
            username='dummyuser_two',
            password='testpassword'
        )
        dummyuser_two_profile = Profile.objects.create(user=self.dummyuser_two)

        # Create accounts for mainuser
        self.account1 = Account.objects.create(
            owner_user=self.mainuser,
            name='Account 1'
        )
        self.account2 = Account.objects.create(
            owner_user=self.mainuser,
            name='Account 2'
        )

        # Create an account for dummyuser_one
        self.account3 = Account.objects.create(
            owner_user=self.dummyuser_one,
            name='Account 3'
        )

        # Add mainuser as a beloved_one to dummyuser_one's account
        self.account3.beloved_ones.add(self.mainuser)

        # Authenticate mainuser
        self.client.force_authenticate(user=self.mainuser)

    def test_list_accounts(self):
        url = reverse('list_accounts')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Check if the list has two accounts as owned_accounts
        self.assertEqual(len(data['owned_accounts']), 2)

        # Check if the list has one account as beloved_accounts
        self.assertEqual(len(data['beloved_accounts']), 1)

    def test_unauthenticated_user(self):
        self.client.force_authenticate(user=None)  # Remove authentication

        url = reverse('list_accounts')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class DeleteAccountViewTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create a profile for the user
        Profile.objects.create(user=self.user)

        # Authenticate the client with the test user
        self.client.force_authenticate(user=self.user)

        # Create an account for testing
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')

    def test_delete_existing_account(self):
        url = reverse('delete_account', args=[self.account.pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert that the account was preserved in the database
        self.assertTrue(Account.objects.filter(pk=self.account.pk).exists())

        # Assert that the account was inactivated
        soft_deleted_account = Account.objects.get(pk=self.account.pk)
        self.assertFalse(soft_deleted_account.is_active)

    def test_delete_non_existing_account(self):
        non_existing_pk = 99345679  # Assuming this ID doesn't exist in the database
        url = reverse('delete_account', args=[non_existing_pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the account count in the database remains unchanged
        self.assertTrue(Account.objects.filter(pk=self.account.pk).exists())

    # def test_delete_account_with_invalid_id(self):
    #     invalid_pk = 'invalid'  # Assuming an invalid account ID
    #     url = reverse('delete_account', args=[invalid_pk])
    #     response = self.client.delete(url)

    #     # Assert the response status code
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     # Assert that the account count in the database remains unchanged
    #     self.assertTrue(Account.objects.filter(pk=self.account.pk).exists())

    def test_delete_account_authentication(self):
        # Simulate an unauthenticated user
        self.client.force_authenticate(user=None)

        url = reverse('delete_account', args=[self.account.pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Assert that the account count in the database remains unchanged
        self.assertTrue(Account.objects.filter(pk=self.account.pk).exists())

class AddBelovedOneViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        Profile.objects.create(user=self.user)
        
        self.client.force_authenticate(user=self.user)

        self.account = Account.objects.create(owner_user=self.user, name='Test Account')

    def test_add_beloved_one(self):

        beloved_one = User.objects.create_user(
            username='beloveduser', 
            password='belovedpassword'
        )

        url = reverse('add_beloved_one', kwargs={'pk': self.account.pk, 'beloved_one_id': beloved_one.pk})
        response = self.client.post(url)

        # Assert the response status code and message
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Beloved one added successfully.')

        # Refresh the account object from the database
        self.account.refresh_from_db()

        # Assert that the beloved_one is added to the account
        self.assertTrue(self.account.beloved_ones.filter(pk=beloved_one.pk).exists())

class RemoveBelovedOneToAccountViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        Profile.objects.create(user=self.user)
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.client.force_authenticate(user=self.user)
        
        self.beloved_one = User.objects.create_user(
            username='beloveduser', 
            password='belovedpassword'
        )
        Profile.objects.create(user=self.beloved_one)
        self.account.beloved_ones.add(self.beloved_one)

    def test_remove_beloved_one(self):

        # Make a POST request to remove the beloved_one from the account
        url = reverse('remove_beloved_one', kwargs={'pk': self.account.pk, 'beloved_one_id': self.beloved_one.pk})
        response = self.client.post(url)

        # Assert the response status code and message
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Beloved one removed successfully.')

        # Refresh the account object from the database
        self.account.refresh_from_db()

        # Assert that the beloved_one is removed from the account
        self.assertFalse(self.account.beloved_ones.filter(pk=self.beloved_one.pk).exists())

    def test_remove_beloved_one_not_found(self):

        # Make a POST request to remove a beloved_one not present in the account
        invalid_beloved_one_id = self.beloved_one.pk + 1
        url = reverse('remove_beloved_one', kwargs={'pk': self.account.pk, 'beloved_one_id': invalid_beloved_one_id})
        response = self.client.post(url)

        # Assert the response status code and message
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ListBelovedOneFromAccountViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        self.profile = Profile.objects.create(user=self.user, name='John')

        self.beloved_user_1 = User.objects.create_user(
            username='beloved_one', 
            password='testpassword'
        )
        self.profile_belove_1 = Profile.objects.create(user=self.beloved_user_1, name='Rita')

        self.beloved_user_2 = User.objects.create_user(
            username='beloved_two', 
            password='testpassword'
        )
        self.profile_belove_2 = Profile.objects.create(user=self.beloved_user_2, name='Ramirez')

        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.account.beloved_ones.add(self.beloved_user_1)
        self.account.beloved_ones.add(self.beloved_user_2)

    def test_list_beloved_ones(self):
        # Ensure the endpoint returns a list of beloved ones for a valid account
        url = reverse('list_beloved_ones', kwargs={'pk': self.account.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['beloved_ones']), 2)
        self.assertEqual(response.data['beloved_ones_profiles'][0]['name'], 'Rita')
        self.assertEqual(response.data['beloved_ones_profiles'][1]['name'], 'Ramirez')
        print(response.data)

    def test_list_beloved_ones_unauthenticated(self):
        # Ensure unauthenticated requests are denied access
        url = reverse('list_beloved_ones', kwargs={'pk': self.account.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_beloved_ones_invalid_account(self):
        # Ensure the endpoint returns a 404 status code for an invalid account
        url = reverse('list_beloved_ones', kwargs={'pk': 9999})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Character related tests
class CharacterCreateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.client.force_authenticate(user=self.user)

    def test_create_character(self):
        url = reverse('create_character')
        data = {
            'account': self.account.id,
            'name': 'John Doe',
            'relationship': 'friend',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Character.objects.count(), 1)
        self.assertEqual(Character.objects.first().name, 'John Doe')

    def test_create_character_unauthorized(self):
        url = reverse('create_character')
        data = {
            'account': self.account.id,
            'name': 'Jane Smith',
            'relationship': 'colleague',
        }
        self.client.force_authenticate(user=None)  # Remove authentication
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Character.objects.count(), 0)  # No new characters should be created

    def test_create_character_without_account(self):
        url = reverse('create_character')
        data = {
            'name': 'John Doe',
            'relationship': 'friend',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Character.objects.count(), 0)

class CharacterUpdateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.character = Character.objects.create(account=self.account, name='John Doe', relationship='friend')
        self.client.force_authenticate(user=self.user)

    def test_update_character(self):
        url = reverse('update_character', kwargs={'pk': self.character.pk})
        data = {
            'name': 'John Smith',
            'relationship': 'family',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.character.refresh_from_db()
        self.assertEqual(self.character.name, 'John Smith')
        self.assertEqual(self.character.relationship, 'family')

    def test_update_character_unauthorized(self):
        url = reverse('update_character', kwargs={'pk': self.character.pk})
        data = {
            'name': 'Jane Smith',
            'relationship': 'colleague',
        }
        self.client.force_authenticate(user=None)  # Remove authentication
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.character.refresh_from_db()
        self.assertEqual(self.character.name, 'John Doe')  # Name should not be updated
        self.assertEqual(self.character.relationship, 'friend')  # Relationship should not be updated

    def test_update_deactivated_character(self):      

        self.character.is_active = False
        self.character.save()

        url = reverse('update_character', kwargs={'pk': self.character.pk})
        data = {
            'name': 'New name',
            'relationship': 'other',
        }
        self.client.force_authenticate(user=None)  # Remove authentication
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.character.refresh_from_db()
        self.assertEqual(self.character.name, 'John Doe')  # Name should not be updated
        self.assertEqual(self.character.relationship, 'friend')  # Relationship should not be updated

class DeleteCharacterViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.character = Character.objects.create(account=self.account, name='John Doe', relationship='friend')
        self.client.force_authenticate(user=self.user)
    
    def test_delete_existing_character(self):
        url = reverse('delete_character', args=[self.character.pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert that the character is no longer in the database
        soft_deleted_character = Character.objects.get(pk=self.character.pk)
        self.assertFalse(soft_deleted_character.is_active)

    def test_delete_non_existing_character(self):
        non_existing_pk = 999  # Assuming this ID doesn't exist in the database
        url = reverse('delete_character', args=[non_existing_pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the character count in the database remains unchanged
        self.assertTrue(Character.objects.filter(pk=self.character.pk).exists())

    def test_delete_character_with_invalid_id(self):
        invalid_pk = 1223235
        url = reverse('delete_character', args=[invalid_pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the character count in the database remains unchanged
        self.assertTrue(Character.objects.filter(pk=self.character.pk).exists())

    def test_delete_character_authentication(self):
        # Assuming authentication is required for deleting characters
        self.client.force_authenticate(user=None)  # Simulate unauthenticated user
        url = reverse('delete_character', args=[self.character.pk])
        response = self.client.delete(url)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Assert that the character count in the database remains unchanged
        self.assertTrue(Character.objects.filter(pk=self.character.pk).exists())

# Memory related tests

class MemoryCreateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.account = Account.objects.create(owner_user=self.user, name='Test Account')
        self.client.force_authenticate(user=self.user)

    def test_create_memory(self):
        url = reverse('create_memory')
        data = {
            'account': self.account.id,
            'title': 'Test Memory',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Memory.objects.count(), 1)
        self.assertEqual(Memory.objects.first().title, 'Test Memory')
    
    def test_create_memory_unauthorized(self):
        self.client.force_authenticate(user=None)  # Unauthenticate the client
        url = reverse('create_memory')
        data = {
            'account': self.account.id,
            'title': 'Test Memory',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Memory.objects.count(), 0)

    def test_create_memory_without_account(self):
        url = reverse('create_memory')
        data = {
            'title': 'Test Memory',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Memory.objects.count(), 0)

class MemoryRetieveTestCase(APITestCase):
    pass

class MemoryUpdateTestCase(APITestCase):
    pass

class MemoryDeleteTestCase(APITestCase):
    pass

class MemoryListTestCase(APITestCase):
    pass

class MemoryAddCharacterTestCase(APITestCase):
    pass

class MemoryRemoveCharacterTestCase(APITestCase):
    pass

class VideoUploadTestCase(APITestCase):
    pass

class VideoDeleteTestCase(APITestCase):
    pass

class VideoProvideURLTestCase(APITestCase):
    pass

class VideoExpiringURLTestCase(APITestCase):
    pass
