import unittest
import json
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app.app import create_app

class UserTestCases(unittest.TestCase):
	
	def setUp(self):

		self.app = create_app('testing').test_client()
		self.user_data = json.dumps(dict({
		            "username": "erick",
		            "email": "erick@gmail.com",
		            "password": "password"
		        }))	       


	def test_registration(self):
	        """
	        Test new user registration
	        """
	        result = self.app.post("/api/auth/register/", data=self.user_data,
	                                    content_type="application/json")
	        self.assertEqual(result.status_code, 201)

	def test_registration_without_user_email(self):
		"""
		Test that empty user email  cannot register
		"""
		unregistered = json.dumps(dict({
			"username": "erick",
			"email": "",
			"password": "password"
		}))

		result = self.app.post("/api/auth/register/", data=unregistered,
                                    content_type="application/json")
		self.assertEqual(result.status_code, 400)
	def test_registration_without_username(self):
		"""
        Test that empty user name  cannot register
        """
		test_data = json.dumps(dict({
		    "username": "",
		    "email": "erick@gmail.com",
		    "password": "password"
		}))
		result = self.app.post("/api/auth/register/", data = test_data,
		                            content_type="application/json")
		self.assertEqual(result.status_code, 400)

	def test_registration_without_user_password(self):
		"""
		Test that empty user password  cannot register
		"""
		test_data = json.dumps(dict({
			"username": "erick",
			"email": "erick@gmail.com",
			"password": ""
		}))
		result = self.app.post("/api/auth/register/", data=test_data,
	                                content_type="application/json")

		self.assertEqual(result.status_code, 400)

	def test_registration_with_special_characters(self):
		"""test that user name cannot contain special characters eg @#
		"""
		test_data = json.dumps(dict({
			"username":"@erick",
			"email": "erick@email.com",
			"password":"password"
			}))
		result = self.app.post("/api/auth/register/" ,data = test_data,
							content_type = "application/json")
		self.assertEqual(result.status_code, 400)

	def test_registration_with_invalid_email(self):
		"""test that the email supplied by the user is valid
		"""
		test_data = json.dumps(dict({
			"username":"erick",
			"email": "erick@emailcom",
			"password":"password"
			}))
		result = self.app.post("/api/auth/register/" ,data = test_data,
							content_type = "application/json")
		self.assertEqual(result.status_code, 403)

	def test_registration_with_a_short_password(self):
		"""test that the email supplied by the user is valid
		"""
		test_data = json.dumps(dict({
			"username":"erick",
			"email": "erick@emailcom",
			"password":"pass"
			}))
		result = self.app.post("/api/auth/register/" ,data = test_data,
							content_type = "application/json")
		self.assertEqual(result.status_code, 403)

	def test_register_with_a_nonexistent_url(self):
		"""
		Test registration with an invalid url
		"""
		result = self.app.post('/api/auth/regist/', data=self.user_data)
		self.assertEqual(result.status_code, 404)	
	def test_registration_with_same_email(self):
		"""
		Test that the same 
		"""
		result = self.app.post("/api/auth/register/", data=self.user_data,
		                            content_type="application/json")
		self.assertEqual(result.status_code, 201)

        # Test double registration
		user2_data = json.dumps(dict({
			"username":"johnwick",
			"email": "erick@emailcom",
			"password":"secret"}))
		second_result = self.app.post("/api/auth/register/",
		                                   data=self.user2_data,
		                                   content_type="application/json")
		self.assertEqual(second_result.status_code, 409)

	def test_successfully_getting_one_user(self):
	    """Test getting one user using the user's id"""
	    response = self.app.get('/api/v1/users/1')
	    self.assertEqual(response.status_code, 200)

	def test_login_with_a_nonexistent_url(self):
	    """
	    Test login with invalid url
	    """
	    response = self.app.post('api/auth/logon/', data=self.user_data)
	    self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
