import json
import time

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIClient
from .models import UserActivation


class SimpleTest(TestCase):
    register_link = "/api/auth/users/create/"
    login_link = "/api/login/"
    send_activation_link = "/api/auth/send-activation-code"
    verify_activation_link = "/api/auth/verify-activation-code"

    def setUp(self):
        UserActivation.objects.create(email="test_pos@test.com", activation_code=123456, activation_status=False, num_attempts=1, attempt_datetime=1541334850.5415087)
        UserActivation.objects.create(email="test_neg@test.com", activation_code=123456, activation_status=False, num_attempts=3, attempt_datetime=time.time())
        self.base_client = APIClient(enforce_csrf_checks=True)
        self.authenticated_client = APIClient()
        self.test_user = AnonymousUser()
        self.authenticated_client.force_authenticate(self.test_user)

    def test_get_links(self):
        response = self.base_client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'users')
        self.assertContains(response, 'professors')
        self.assertContains(response, 'colleges')

    def test_register(self):
        test_user_data = {
            "username":"test@test.com",
            "email": "test@test.com",
            "password":"test_pass"
        }
        response = self.base_client.post(path=self.register_link, data=test_user_data)
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        test_user_data = {
            "username":"test@test.com",
            "password":"test_pass"
        }
        response = self.base_client.post(path=self.login_link, data=test_user_data)
        self.assertEqual(response.status_code, 400)

    def test_send_activation_max_attempts(self):
        activation_data = {
            "activation_code": "123456",
            "email": "test_neg@test.com"
        }
        reason_text = "Only 3 attempts allowed every 60 minutes. Please try after 60 minutes."
        response = self.base_client.post(self.send_activation_link, data=json.dumps(activation_data),
                                         content_type="application/json")
        self.assertEqual(response.status_code, 429)
        response_json = response.json()
        self.assertEqual(response_json['status'], "failure")
        self.assertIn(reason_text, response_json["reason"])

    def test_send_activation_link_new_mail(self):
        data = {"email": "test_new_activation@test.com"}
        response = self.base_client.post(self.send_activation_link, data=json.dumps(data),
                                         content_type="application/json")
        user_activation_details = UserActivation.objects.get(email="test_new_activation@test.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_activation_details.num_attempts, 1)

    def test_num_attempts_increment_on_send_activation_code_existing_user(self):
        data = {"email": "test_pos@test.com"}
        response = self.base_client.post(self.send_activation_link, data=json.dumps(data),
                                         content_type="application/json")
        user_activation_details = UserActivation.objects.get(email="test_pos@test.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_activation_details.num_attempts, 2)

    def test_user_activation_correct(self):
        activation_data = {
            "activation_code":"123456",
            "email": "test_pos@test.com"
        }
        response = self.base_client.post(self.verify_activation_link, data=json.dumps(activation_data),
                                         content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status")
        self.assertEqual(response.json()["status"], "verified")

    def test_user_activation_wrong_email(self):
        activation_data = {
            "activation_code": "123456",
            "email": "test_abc@test.com"
        }
        response = self.base_client.post(self.verify_activation_link, data=json.dumps(activation_data),
                                         content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "email not found")

    def test_user_activation_wrong_code(self):
        activation_data = {
            "activation_code": "111111",
            "email": "test_pos@test.com"
        }
        response = self.base_client.post(self.verify_activation_link, data=json.dumps(activation_data),
                                         content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "rejected")