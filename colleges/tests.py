import json
from unittest import skip

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from rest_framework.test import APIClient

from colleges.models import College
from professors.models import Professor


class SimpleTest(TestCase):
    create_college_link = "/api/colleges/create/"
    search_college_link = "/api/colleges/search/{city_id}"
    all_cities_link = "/api/colleges/cities"

    college_data = {
        "name": "ABC College of Engineering",
        "address": "Outer Ring Road, Near Marathalli, Bellandur Main Road, Kaverappa Layout, Kadubeesanahalli, "
                   "New Delhi, Karnataka 560103, India",
        "phoneNumber": "+91 80662 97777",
        "id": "ChIJAQAAAMsTrjsRwoxxgsaWLiEKsbf",
        "websiteUri": "http://www.newhorizonindia.edu/",
        "latlng": "lat/lng: (12.933412299999999,77.69136019999999)",
        "rating": 4.2,
        "attributions": "null"
    }

    def setUp(self):
        College.objects.create(name="Test College", city="ABC", state="ABC", id="testCollege_id", google_rating=4.2,
                               city_id="test_city", latitude=1.1111, longitude=2.2222)
        College.objects.create(name="Test College", city="ABC", state="ABC", id="testCollege_id2", google_rating=4.3,
                               city_id="test_city", latitude=1.1111, longitude=2.2222)
        College.objects.create(name="Test College", city="ABC", state="ABC", id="testCollege_id3", google_rating=4.3,
                               city_id="test_city", latitude=1.1111, longitude=2.2222)
        Professor.objects.create(id=1, name="Test Prof 1", college=College.objects.get(id="testCollege_id"),
                                 previous_college=College.objects.get(id="testCollege_id2"), department="ECE")
        Professor.objects.create(id=2, name="Test Prof 2", college=College.objects.get(id="testCollege_id"),
                                 previous_college=College.objects.get(id="testCollege_id2"), department="ABC")
        Professor.objects.create(id=3, name="Test Prof 3", college=College.objects.get(id="testCollege_id"),
                                 previous_college=College.objects.get(id="testCollege_id2"), department="ABC")

        self.base_client = APIClient(enforce_csrf_checks=True)
        self.authenticated_client = APIClient(enforce_csrf_checks=True)
        self.test_user = User.objects.create(username='test', password='password')
        self.authenticated_client.force_authenticate(self.test_user)

    def test_add_college_fail_for_unauthenticated_user(self):
        response = self.base_client.post(self.create_college_link, data=json.dumps(self.college_data),
                                         content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_add_college_for_authenticated_user(self):
        response = self.authenticated_client.post(self.create_college_link, data=json.dumps(self.college_data),
                                                  content_type='application/json')
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['status'], 'success')
        self.assertEqual(response_json['college']['city'], 'New Delhi')
        self.assertEqual(response_json['college']['city_id'], 'dummy_place_id1')
        self.assertEqual(response_json['college']['longitude'], 77.69136019999999)
        self.assertEqual(response_json['college']['latitude'], 12.933412299999999)

    def test_return_college_data_on_add_if_college_exists(self):
        response = self.authenticated_client.post(self.create_college_link, data=json.dumps(self.college_data),
                                                  content_type='application/json')
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['status'], 'success')

        response = self.authenticated_client.post(self.create_college_link, data=json.dumps(self.college_data),
                                                  content_type='application/json')
        response_json = response.json()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response_json['status'], 'exists')

    @skip("Not used")
    def test_get_all_cities_list(self):
        pass

    def test_get_college_for_invalid_city(self):
        response = self.base_client.get(self.search_college_link.format(city_id='test_new_city'))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['colleges'], [])

    def test_get_college_for_valid_city(self):
        response = self.base_client.get(self.search_college_link.format(city_id='test_city'))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json['colleges']), 3)
