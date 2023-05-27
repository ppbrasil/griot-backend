from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from profiles.models import Profile

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

    def test_invalid_profile_update(self):
        data = {
            'name': '',  # Invalid because name is required
            'middle_name': 'Updated Middle Name',
            'last_name': 'Updated Last Name',
            'birth_date': '1990-01-01',
            'gender': 'other',
        }

        response = self.client.patch(self.update_profile_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    # def test_create_account_unauthenticated(self):
    #     # Log out the test user
    #     self.client.logout()

    #     # Data to be used to create an account
    #     data = {
    #         'name': 'Test Account',
    #         'description': 'This is a test account',
    #     }

    #     # Attempt to create an account
    #     response = self.client.post(self.create_url, data)

    #     # Assert that unauthenticated users cannot create an account
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
