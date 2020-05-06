import json
import random
from unittest import skip

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from rest_framework.test import APIClient

from colleges.models import College
from professors.models import Professor, Review, ReportReview
from professors.serializers import ReviewsSerializer


class SimpleTest(TestCase):
    search_prof_link = "/api/professors/search/{college_id}"
    create_link = "/api/professors/create/"
    add_review_link = "/api/professors/add-review/{professor_id}"
    get_reviews_link = "/api/professors/get-reviews/{professor_id}"
    check_user_review_link = "/api/professors/check-if-reviewed/{professor_id}"
    like_review_link = "/api/professors/review/{review_id}/like"
    dislike_review_link = "/api/professors/review/{review_id}/dislike"
    report_review_link = "/api/professors/review/{review_id}/report"
    check_if_review_reported_link = "/api/professors/review/{review_id}/check-if-reported"

    new_prof_data = {
        "name": "Test Prof create",
        "college": "testCollege_id",
        "previous_college": "testCollege_id2",
        "department": "ECE"
    }

    review_data = {
        "title": "Test Review",
        "score": 2,
        "review": "test review looks like this"
    }

    report_data = {
        "reason": "Test Reason"
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
        Professor.objects.create(id=3, name="Test Prof 3", college=College.objects.get(id="testCollege_id2"),
                                 previous_college=College.objects.get(id="testCollege_id"), department="ABC")

        self.base_client = APIClient(enforce_csrf_checks=True)
        self.authenticated_client = APIClient(enforce_csrf_checks=True)
        self.authenticated_client2 = APIClient(enforce_csrf_checks=True)
        self.test_user = User.objects.create(username='test', password='password')
        self.test_user2 = User.objects.create(username='test2', password='password')

        self.authenticated_client.force_authenticate(self.test_user)
        self.authenticated_client2.force_authenticate(self.test_user2)

    def test_search_professors_no_college(self):
        response = self.base_client.get(self.search_prof_link.format(college_id="testCollege_id4"))
        response_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["count"], 0)

    def test_search_professors_valid_college_no_prof(self):
        response = self.base_client.get(self.search_prof_link.format(college_id="testCollege_id3"))
        response_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["count"], 0)

    def test_search_professors_valid_college_prof(self):
        response = self.base_client.get(self.search_prof_link.format(college_id="testCollege_id"))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["count"], 3)
        self.assertEqual(len(response_json["professors"]), 2)

    def test_search_profs_using_previous_college(self):
        response = self.base_client.get(self.search_prof_link.format(college_id="testCollege_id2"))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["count"], 3)
        self.assertEqual(len(response_json["previous_professors"]), 2)
        self.assertEqual(len(response_json["professors"]), 1)

    @skip("TBD")
    def test_pagination_for_profs(self):
        pass

    def test_create_prof_non_authenticated_user(self):
        response = self.base_client.post(self.create_link, data=json.dumps(self.new_prof_data),
                                         content_type='application_json')
        self.assertEqual(response.status_code, 401)

    def test_create_prof_authenticated_user(self):
        response = self.authenticated_client.post(self.create_link, data=json.dumps(self.new_prof_data),
                                                  content_type='application_json')
        prof = Professor.objects.get(name="Test Prof create")
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["success"], 'true')
        self.assertIsNotNone(prof)

    def test_create_prof_missing_fields_error(self):
        error_data = {
            "name": "Test Prof create",
            "previous_college": "testCollege_id2",
            "department": "ECE"
        }
        response = self.authenticated_client.post(self.create_link, data=json.dumps(error_data),
                                                  content_type='application_json')
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response_json['errors'])
        self.assertEqual(response_json["success"], 'false')

    @skip("Update professor endpoint to be created")
    def test_update_prof_college_details(self):
        pass

    def test_add_review_non_auth_user_error(self):
        response = self.client.post(self.add_review_link.format(professor_id=1), data=json.dumps(self.review_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_add_review_auth_user(self):
        response = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                                  data=json.dumps(self.review_data), content_type='application/json')
        prof = Professor.objects.get(id="1")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(prof.num_reviews, 1)
        self.assertEqual(prof.total_score, 2)

    def test_prof_and_college_rating_increment_on_new_review_add(self):
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(self.review_data), content_type='application/json')
        prof = Professor.objects.get(id=1)
        coll = College.objects.get(id="testCollege_id")
        self.assertEqual(prof.num_reviews, 1)
        self.assertEqual(prof.total_score, 2)
        self.assertEqual(coll.total_rating, 2)
        self.assertEqual(coll.number_ratings, 1)
        review_score = [4, 3, 5]
        for score in review_score:
            local_authenticated_client = APIClient(enforce_csrf_checks=True)
            local_test_user = User.objects.create(username=f'test_{str(score)}', password='password')
            local_authenticated_client.force_authenticate(local_test_user)
            review_data = self.review_data
            review_data['score'] = score
            _ = local_authenticated_client.post(self.add_review_link.format(professor_id=1),
                                                data=json.dumps(review_data), content_type='application/json')
        prof = Professor.objects.get(id="1")
        coll = College.objects.get(id="testCollege_id")
        self.assertEqual(prof.num_reviews, 4)
        self.assertEqual(prof.total_score, 14)
        self.assertEqual(coll.total_rating, 14)
        self.assertEqual(coll.number_ratings, 4)


    def test_college_rating_change_on_add_review(self):
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(self.review_data), content_type='application/json')
        college = College.objects.get(id="testCollege_id")
        self.assertEqual(college.total_rating, 2)

    def test_add_review_missing_field(self):
        review_data_missing = {
            "title": "Test Review",
        }
        response = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                                  data=json.dumps(review_data_missing), content_type='application/json')
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response_json['errors'])
        self.assertEqual(response_json['success'], 'false')

    def test_add_review_no_prof_error(self):
        response = self.authenticated_client.post(self.add_review_link.format(professor_id=999999),
                                                  data=json.dumps(self.review_data), content_type='application/json')
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response_json['errors'])
        self.assertEqual(response_json['success'], 'false')

    def test_check_if_user_reviewed_prof(self):
        response = self.authenticated_client.get(self.check_user_review_link.format(professor_id=1))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['is_reviewed'], False)

        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(self.review_data), content_type='application/json')
        response = self.authenticated_client.get(self.check_user_review_link.format(professor_id=1))
        response_json = response.json()
        self.assertEqual(response_json['is_reviewed'], True)
        self.assertEqual(response_json['review_data']['title'], self.review_data['title'])
        self.assertEqual(response_json['review_data']['score'],  self.review_data['score'])
        self.assertEqual(response_json['review_data']['review'],  self.review_data['review'])

    def test_overwrite_existing_review_for_same_prof(self):
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(self.review_data), content_type='application/json')
        prof = Professor.objects.get(id=1)
        review = Review.objects.filter(added_by=self.test_user.pk, professor=prof.pk)
        serialized_review = ReviewsSerializer(review, many=True).data
        self.assertEqual(len(serialized_review), 1)
        self.assertEqual(serialized_review[0]["review"], self.review_data['review'])
        self.assertEqual(serialized_review[0]["score"], self.review_data['score'])
        self.assertEqual(prof.num_reviews, 1)
        self.assertEqual(prof.total_score, self.review_data['score'])
        review_data_2 = {
            "title": "Test Review",
            "score": 2,
            "review": "Overwritten objectstest review looks like this"
        }
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(review_data_2), content_type='application/json')
        review = Review.objects.filter(added_by=self.test_user.pk, professor=prof.pk)
        serialized_review = ReviewsSerializer(review, many=True).data
        self.assertEqual(len(serialized_review), 1)
        self.assertEqual(serialized_review[0]["review"], review_data_2['review'])
        self.assertEqual(serialized_review[0]["score"], review_data_2['score'])
        self.assertEqual(prof.num_reviews, 1)
        self.assertEqual(prof.total_score, review_data_2['score'])

    def test_do_not_overwrite_existing_review_for_different_prof(self):
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=1),
                                           data=json.dumps(self.review_data), content_type='application/json')
        prof = Professor.objects.get(id=1)
        review = Review.objects.filter(added_by=self.test_user.pk, professor=prof.pk)
        serialized_review = ReviewsSerializer(review, many=True).data
        self.assertEqual(len(serialized_review), 1)
        self.assertEqual(serialized_review[0]["review"], self.review_data['review'])
        self.assertEqual(serialized_review[0]["score"], self.review_data['score'])
        review_data_2 = {
            "title": "Test Review",
            "score": 2,
            "review": "Overwritten objects test review looks like this"
        }
        _ = self.authenticated_client.post(self.add_review_link.format(professor_id=2),
                                           data=json.dumps(review_data_2), content_type='application/json')
        prof = Professor.objects.get(id=2)
        review = Review.objects.filter(added_by=self.test_user.pk, professor=prof.pk)
        serialized_review = ReviewsSerializer(review, many=True).data
        self.assertEqual(len(serialized_review), 1)
        self.assertEqual(serialized_review[0]["review"], review_data_2['review'])
        self.assertEqual(serialized_review[0]["score"], review_data_2['score'])

    def test_get_reviews_prof_does_not_exist(self):
        response = self.authenticated_client.get(self.get_reviews_link.format(professor_id=999999))
        self.assertEqual(response.status_code, 404)

    def test_get_prof_reviews(self):
        review_score = [1,2,3,4,5]
        prof = Professor.objects.get(id=3)
        for score in review_score:
            local_authenticated_client = APIClient(enforce_csrf_checks=True)
            local_test_user = User.objects.create(username=f'test_{str(score)}_{str(random.randint(0,1))}', password='password')
            local_authenticated_client.force_authenticate(local_test_user)
            Review.objects.create(professor=prof, score=score, title="test", review="test review", added_by=local_test_user)
        response = self.authenticated_client.get(self.get_reviews_link.format(professor_id=3))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 5)
        self.assertEqual(len(response_json['results']), 5)

    def test_review_pagination(self):
        review_score = [1, 2, 3, 4, 5, 3]*3
        prof = Professor.objects.get(id=3)
        for idx,score in enumerate(review_score):
            local_authenticated_client = APIClient(enforce_csrf_checks=True)
            local_test_user = User.objects.create(username=f'test_{str(score)}_{str(idx)}',
                                                    password='password')
            local_authenticated_client.force_authenticate(local_test_user)
            Review.objects.create(professor=prof, score=score, title="test", review="test review",
                                  added_by=local_test_user)
        response = self.authenticated_client.get(self.get_reviews_link.format(professor_id=3))
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 18)
        self.assertEqual(len(response_json['results']), 5)
        response_2 = self.authenticated_client.get(response_json['next'])
        response_2_json = response_2.json()
        self.assertEqual(response_2_json['results'][0]['score'], 3)

    def test_review_like_count_increment(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        response = self.authenticated_client.get(self.like_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(review.like_count, 1)
        self.assertEqual(review.dislike_count, 0)

    def test_liked_review_re_like_no_change(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        self.authenticated_client.get(self.like_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(review.like_count, 1)
        self.assertEqual(review.dislike_count, 0)

        response = self.authenticated_client.get(self.like_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(review.like_count, 1)
        self.assertEqual(review.dislike_count, 0)

    def test_review_like_dislike_decrement(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        self.authenticated_client.get(self.like_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(review.like_count, 1)
        self.assertEqual(review.dislike_count, 0)

        response = self.authenticated_client.get(self.dislike_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(review.like_count, 0)
        self.assertEqual(review.dislike_count, 1)

    def test_review_dislike_count_increment(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        response = self.authenticated_client.get(self.dislike_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(review.like_count, 0)
        self.assertEqual(review.dislike_count, 1)

    def test_disliked_review_re_dislike_no_change(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        self.authenticated_client.get(self.dislike_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(review.like_count, 0)
        self.assertEqual(review.dislike_count, 1)

        response = self.authenticated_client.get(self.dislike_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(review.like_count, 0)
        self.assertEqual(review.dislike_count, 1)

    def test_review_dislike_like_decrement(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        self.authenticated_client.get(self.dislike_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(review.like_count, 0)
        self.assertEqual(review.dislike_count, 1)

        response = self.authenticated_client.get(self.like_review_link.format(review_id=99))
        review = Review.objects.get(pk=99)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(review.like_count, 1)
        self.assertEqual(review.dislike_count, 0)

    def test_review_reported_successfully(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        response = self.authenticated_client.post(self.report_review_link.format(review_id=99),
                                                  data=json.dumps(self.report_data),
                                                    content_type='application_json')
        reported_review = ReportReview.objects.get(review=99)
        review = Review.objects.get(pk=99)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(review.times_reported, 1)
        self.assertIsNone(reported_review.deleted_review)
        self.assertEqual(reported_review.reason, self.report_data["reason"])

    def test_report_already_exists(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        response = self.authenticated_client.post(self.report_review_link.format(review_id=99),
                                                  data=json.dumps({}),
                                                    content_type='application_json')
        response_2 = self.authenticated_client.post(self.report_review_link.format(review_id=99),
                                                  data=json.dumps(self.report_data),
                                                    content_type='application_json')

        reported_review = ReportReview.objects.get(review=99)
        response_check_report_exists = self.authenticated_client.get(self.check_if_review_reported_link.format(review_id=99))
        reported_reviews_deleted = ReportReview.objects.filter(deleted_review=1)

        check_review_json = response_check_report_exists.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_2.status_code, 302)
        self.assertEqual(response_check_report_exists.status_code, 302)
        self.assertEqual(check_review_json['reason'], self.report_data["reason"])
        self.assertIsNone(reported_review.deleted_review)
        self.assertEqual(reported_review.reason, self.report_data["reason"])
        self.assertEqual(len(reported_reviews_deleted), 0)


    def test_review_moved_and_report_updated_if_limit_crossed(self):
        professor = Professor.objects.get(pk=1)
        Review.objects.create(pk=99, professor=professor, score=2, title="test", review="test review",
                              added_by=self.test_user)
        response = self.authenticated_client.post(self.report_review_link.format(review_id=99),
                                                  data=json.dumps({}),
                                                    content_type='application_json')
        response_2 = self.authenticated_client2.post(self.report_review_link.format(review_id=99),
                                                  data=json.dumps(self.report_data),
                                                    content_type='application_json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_2.status_code, 200)

        reported_review = ReportReview.objects.filter(deleted_review=1)
        with self.assertRaises(Review.DoesNotExist):
            review = Review.objects.get(review=99)
        self.assertIsNotNone(reported_review)
        self.assertEqual(len(reported_review), 2)

