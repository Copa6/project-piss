from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

from operator import itemgetter

from colleges.models import College
from home.models import Profile
from project_piss import settings
from .pagination import ReviewsPagination
from project_piss.helpers import generate_all_links, get_data_from_request, return_unhandled_response, get_logger
from .links import links
from .models import Professor, Review, LikedReview, DislikedReview, ReportReview, DeletedReviews
from .serializers import ProfessorsSerializerPOST, ProfessorsSerializerGET, ReviewsSerializer, ReviewsSerializerGET, \
    LikedReviewSerializer, DislikedReviewSerializer, ReportReviewSerializer, ReportReviewSerializerGET

LIKE = 1
DISLIKE = 0
logger = get_logger()


def update_professor_and_college_data_on_review_add(data, professor_id, existing_review_data):
    logger.info(f"Updating professor and college number of ratings. Professor - {professor_id}")
    professor = Professor.objects.get(pk=professor_id)
    college = College.objects.get(id=professor.college.id)
    existing_review_score = existing_review_data['review_data'].get('score', 0)
    if not existing_review_data['is_reviewed']:
        logger.info("New review, increment number rating count")
        professor.num_reviews += 1
        college.number_ratings += 1
    logger.info("Updating total review score")
    professor.total_score -= existing_review_score
    college.total_rating -= existing_review_score
    professor.total_score += data['score']
    college.total_rating += data['score']

    logger.info("Save updated information to database")
    college.save()
    professor.save()


def check_like_dislike_and_increment(request, review_id, type):
    user = User.objects.get(username=request.user)
    review = Review.objects.get(pk=review_id)

    logger.info(f"User - {user.pk}\n Review - {review_id}")

    liked_review_existing = None
    is_liked = False
    disliked_review_existing = None
    is_disliked = False

    try:
        logger.info("Checking if review already liked by user")
        liked_review_existing = LikedReview.objects.get(user=user.pk, review=review_id)
        is_liked = True
        logger.info("Review has already been liked by the user")
    except LikedReview.DoesNotExist:
        logger.info("Review has not been liked by the user")
        pass

    try:
        logger.info("Checking if review already disliked by user")
        disliked_review_existing = DislikedReview.objects.get(user=user.pk, review=review_id)
        is_disliked = True
        logger.info("Review has already been disliked by the user")
    except DislikedReview.DoesNotExist:
        logger.info("Review has not been disliked by the user")
        pass

    if type == LIKE:
        logger.info("Liking review.")
        if is_liked:
            logger.info("Review already liked by user. Making no updates")
            return 0, review.like_count, review.dislike_count
        else:
            like_data = {
                'user': user.pk,
                'review': review_id
            }
            liked_review = LikedReviewSerializer(data=like_data)
            logger.info("Update like dislike count in database")
            if liked_review.is_valid():
                review.like_count += 1
                liked_review.save()
                review.save()
                logger.info("Like count updated in database")
                if is_disliked:
                    logger.info("Review has been disliked by the user. Deleting dislike")
                    remove_dislike(disliked_review_existing, review)
                return 1, review.like_count, review.dislike_count
    else:
        logger.info("Disliking review")
        if is_disliked:
            logger.info("Review already disliked by user. Making no updates")
            return 0, review.like_count, review.dislike_count
        else:
            dislike_data = {
                'user': user.pk,
                'review': review_id
            }
            disliked_review = DislikedReviewSerializer(data=dislike_data)
            logger.info("Update like dislike count in database")
            if disliked_review.is_valid():
                review.dislike_count += 1
                disliked_review.save()
                review.save()
                logger.info("Dislike count updated in database")
                if is_liked:
                    logger.info("Review has been liked by the user. Deleting like")
                    remove_like(liked_review_existing, review)
                return 1, review.like_count, review.dislike_count
    return 99, review.like_count, review.dislike_count


def remove_dislike(disliked_review_existing, review):
    disliked_review_existing.delete()
    review.dislike_count -= 1
    review.save()
    logger.info("Disliked deleted form review")


def remove_like(liked_review_existing, review):
    liked_review_existing.delete()
    review.like_count -= 1
    review.save()
    logger.info("Like deleted from review")


def check_and_hide_reported_reviews(review):
    logger.info(f"Number of times review {review.pk} reported - {review.times_reported}")
    logger.info(f"Maximum report threshold - {settings.MAX_REPORT_COUNT}")
    if review.times_reported > settings.MAX_REPORT_COUNT:
        logger.info("Review reported more than set threshold times. Soft deleting")
        professor = Professor.objects.get(pk=review.professor.pk)
        college = College.objects.get(pk=professor.college.pk)
        logger.info("Updating respective databases")

        professor.total_score -= review.score
        college.total_rating -= review.score

        professor.num_reviews -= 1
        college.number_ratings -= 1

        logger.info("Moving review to deleted database")
        deleted_review = DeletedReviews().create_from_review(review)
        ReportReview.objects.filter(review=review.pk).update(deleted_review=deleted_review.pk)
        professor.save()
        college.save()
        logger.info("Saved relarted databases - Professors and college")
        review.delete()
        logger.info("Orifinal review deleted")


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_links(request):
    try:
        user = request.user

        all_links = {
            '_links': {
                'professors': links['professors']['default']
            }
        }

        all_links = generate_all_links(user, all_links, links, app_name='professors')
        return JsonResponse(all_links, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO: Check if same prof name in same college in same department exists
@api_view(['POST'])
def create_professor(request):
    try:
        logger.info("Got request to create new professor")
        data = get_data_from_request(request, 'added_by')
        logger.info(f"Request data - {data}")
        logger.info("Validating request data")
        serializer = ProfessorsSerializerPOST(data=data)
        if serializer.is_valid():
            logger.info("Serializer valid")
            serializer.save()
            logger.info("Professor added to database")
            prof = Professor.objects.get(id=serializer.data["id"])
            serialized_prof_data = ProfessorsSerializerGET(prof)
            return Response({'success': 'true', 'professor': serialized_prof_data.data}, status=status.HTTP_201_CREATED)

        else:
            logger.info("Request data invalid. Unable to save professor to database")
            logger.error(serializer.errors)
            return Response({'success': 'false', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def search(request, college_id):
    try:
        logger.info("Got request to search for professors")
        logger.info(f"Fetching all professors from college - {college_id}")
        professors = Professor.objects.filter(college=college_id)

        logger.info(f"Fetching all professors that were previously at college - {college_id}")
        old_professors = Professor.objects.filter(previous_college=college_id)

        logger.info("Serializing professors")
        prof_serializer = ProfessorsSerializerGET(professors, many=True)
        old_prof_serializer = ProfessorsSerializerGET(old_professors, many=True)
        num_prof = len(prof_serializer.data) + len(old_prof_serializer.data)
        logger.info(f"Found {num_prof} professors")
        response_data = {
            'count': num_prof,
            'professors': prof_serializer.data,
            'previous_professors': old_prof_serializer.data
        }
        if num_prof != 0:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_filtered_professors(request, college_id):
    try:
        logger.info("Got request to filter professors")
        filter_params = get_data_from_request(request)
        logger.info(f"Filter parameters - {filter_params}")

        logger.info(f"Fetching professors with current college - {college_id}")
        professors = Professor.objects.filter(college=college_id)
        prof_serialized_data = ProfessorsSerializerGET(professors, many=True).data

        logger.info(f"Found {len(prof_serialized_data)} professors")

        if not filter_params.get("show_present_college_only", False):
            logger.info(f"Fetching professors who previously were at college = {college_id}")
            old_professors = Professor.objects.filter(previous_college=college_id)
            old_prof_serialized_data = ProfessorsSerializerGET(old_professors, many=True).data

            logger.info(f"Found {len(old_prof_serialized_data)} old professors")
        else:
            logger.info("Filtering to not show any old professors")
            old_prof_serialized_data = []

        if filter_params.get("rating_low_high", False):
            logger.info("Sort professors by rating - low to high")
            prof_serialized_data = sorted(prof_serialized_data, key=itemgetter('rating'))
            old_prof_serialized_data = sorted(old_prof_serialized_data, key=itemgetter('rating'))

        elif filter_params.get("rating_high_low", False):
            logger.info("Sort professors by rating - high to low")
            prof_serialized_data = sorted(prof_serialized_data, key=itemgetter('rating'), reverse=True)
            old_prof_serialized_data = sorted(old_prof_serialized_data, key=itemgetter('rating'), reverse=True)

        elif filter_params.get('num_reviews_low_high', False):
            logger.info("Sort professors by number of reviews - low to high")
            prof_serialized_data = sorted(prof_serialized_data, key=itemgetter('num_reviews'))
            old_prof_serialized_data = sorted(old_prof_serialized_data, key=itemgetter('num_reviews'))

        elif filter_params.get('num_reviews_high_low', False):
            logger.info("Sort professors by number of reviews - high to low")
            prof_serialized_data = sorted(prof_serialized_data, key=itemgetter('num_reviews'), reverse=True)
            old_prof_serialized_data = sorted(old_prof_serialized_data, key=itemgetter('num_reviews'), reverse=True)

        num_prof = len(prof_serialized_data) + len(old_prof_serialized_data)
        response_data = {
            'count': num_prof,
            'professors': prof_serialized_data,
            'previous_professors': old_prof_serialized_data
        }

        if num_prof != 0:
            logger.info(f"Found {num_prof} professors. Send response")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.info("Found 0 professors. Send response")
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Allow post method to let add_review api access this internally
@api_view(['GET', 'POST'])
def check_if_professor_reviewed(request, professor_id):
    logger.info("Got request to check if the professor is reviewed by the user.")
    user = User.objects.get(username=request.user)
    try:
        logger.info("Checking if professor reviewd by user")
        review = Review.objects.get(added_by=user.pk, professor=professor_id)
        serialized_review = ReviewsSerializerGET(review).data
        logger.info(f"Professor already reviewed by user. \nReview - {serialized_review}")

        logger.info("Adding id to review data")
        review_data = dict(serialized_review)
        review_data.update({'id': review.pk})

        logger.info("Sending review data in response")
        response_data = {'is_reviewed': True, 'review_data': review_data}
        return Response(response_data, status=status.HTTP_200_OK)
    except Review.DoesNotExist:
        logger.info("Professor not reviewed by the user. Return empty response")
        return Response({'is_reviewed': False, 'review_data': {}}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_review(request, professor_id):
    logger.info("Got request to add review for professor")
    try:
        data = get_data_from_request(request, 'added_by')
        data['professor'] = professor_id
        existing_review_data = check_if_professor_reviewed(request._request, professor_id).data
        if existing_review_data['is_reviewed']:
            logger.info("Found existing review. Overwriting")
            review = Review.objects.get(id=existing_review_data['review_data']['id'])
            review.title = data['title']
            review.score = data['score']
            review.review = data['review']
            logger.info("Review data updated. Saving...")
            update_professor_and_college_data_on_review_add(data, professor_id, existing_review_data)
            logger.info("Professor and college data updated")

            review.save()
            logger.info("Review saved to database")
            return Response({'success': 'Review successfully updated.'}, status=status.HTTP_201_CREATED)

        else:
            logger.info("New review found. Serialize and save to database")
            serializer = ReviewsSerializer(data=data)
            if serializer.is_valid():
                logger.info("Review serialized successfully. Update professors and college data.")
                update_professor_and_college_data_on_review_add(data, professor_id, existing_review_data)

                logger.info("Professor and college data updated. Saving review to database")
                serializer.save()
                return Response({'success': 'Review successfully added.'}, status=status.HTTP_201_CREATED)

            else:
                logger.info(f"Error serializing review. {serializer.errors}")
                return Response({'success': 'false', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_reviews(request, professor_id):
    logger.info(f"Got request to get all reviews for professor {professor_id}")
    try:
        logger.info("Fetching all reviews for professor from database")
        reviews = Review.objects.filter(professor=professor_id)

        logger.info("Initialising pagination for reviews")
        paginator = ReviewsPagination()
        if reviews.exists():
            logger.info("Found reviews for professor. Paginating and sending response")
            review_page = paginator.paginate_queryset(reviews, request)

            logger.info("Serializing reviews")
            serializer = ReviewsSerializerGET(review_page, many=True, context={'user_id': request.user.id})
            return paginator.get_paginated_response(serializer.data)
        else:
            logger.info("No reviews found for the professor.")
            return Response({'error': 'No reviews found for this Professor.'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def like_review(request, review_id):
    logger.info("Got request to like review")
    try:
        logger.info("Checking if review already liked by the user and updating like count in database")
        response_internal_code, like_count, dislike_count = check_like_dislike_and_increment(request, review_id, LIKE)
        response_data = {
            'success': False,
            'reason': 'Error',
            'like_count': like_count,
            'dislike_count': dislike_count
        }
        if response_internal_code == 0:
            logger.info("Review has already been liked by the user. No updates were made")
            response_data['reason'] = "Review  already liked by user"
            return Response(response_data, status=status.HTTP_304_NOT_MODIFIED)
        elif response_internal_code == 1:
            logger.info("Review successfully liked by user")
            response_data['success'] = True
            response_data['reason'] = 'Review liked by user.'
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.info("Unexpected error occurred while liking review.")
            logger.info(f"{response_internal_code}\n Like count - {like_count}\n Dislike count - {dislike_count}")
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def dislike_review(request, review_id):
    logger.info("Got request to dislike review")
    try:
        logger.info("Checking if review already disliked by the user and updating dislike count in database")
        response_internal_code, like_count, dislike_count = check_like_dislike_and_increment(request, review_id, DISLIKE)
        response_data = {
            'success': False,
            'reason': 'Error',
            'like_count': like_count,
            'dislike_count': dislike_count
        }
        if response_internal_code == 0:
            logger.info("Review has already been disliked by the user. No updates were made")
            response_data['reason'] = "Review  already disliked by user"
            return Response(response_data, status=status.HTTP_304_NOT_MODIFIED)
        elif response_internal_code == 1:
            logger.info("Review successfully disliked by user")
            response_data['success'] = True
            response_data['reason'] = 'Review disliked by user.'
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.info("Unexpected error occurred while disliking review.")
            logger.info(f"{response_internal_code}\n Like count - {like_count}\n Dislike count - {dislike_count}")
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_if_review_reported(request, review_id):
    logger.info("Got request to check if review was reported")
    user = User.objects.get(username=request.user)
    try:
        logger.info("Checking if review reported")
        existing_report = ReportReview.objects.get(review=review_id, reported_by=user.pk)
        logger.info("Existing report found for review. Serializing and sending response")
        serialized_report = ReportReviewSerializerGET(existing_report).data
        return Response(serialized_report, status=status.HTTP_302_FOUND)

    except ReportReview.DoesNotExist:
        logger.info("Review not reported by user")
        return Response({'success': False, 'message': 'No Report'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def report_review(request, review_id):
    logger.info("Got request to report review")
    try:
        report_data = get_data_from_request(request, 'reported_by')
        logger.info(f"Report data - {report_data}")
        report_data['review'] = review_id
        review = Review.objects.get(pk=review_id)
        response_data = {
            'success': False,
            'message': ""
        }
        logger.info("Checking if review is already reported by the user")
        try:
            existing_report = ReportReview.objects.get(review=review_id, reported_by=report_data['reported_by'])
            logger.info("Review already reported by user. No  updated required")
            is_reported = True
        except ReportReview.DoesNotExist:
            logger.info("Review not reported by the user.")
            is_reported = False

        if is_reported:
            logger.info("Review already reported by the user. Updating reason, if any")
            existing_report.reason = report_data["reason"]
            existing_report.save()
            response_data['message'] = "Report updated"
            logger.info("Database updated.")
            return Response(response_data, status=status.HTTP_302_FOUND)
        else:
            logger.info(f"Review reported by user {report_data['reported_by']} for first time. Saving to database")
            review.times_reported += 1
            serialized_report = ReportReviewSerializer(data=report_data)
            if serialized_report.is_valid():
                logger.info("Serialised request object")
                review.save()
                serialized_report.save()
                logger.info("Database successfully updated")

                response_data['success'] = True
                response_data['message'] = "Review Reported"

                logger.info("Soft delete review if reported more than threshold and returning response")
                check_and_hide_reported_reviews(review)
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error saving report - {serialized_report.errors}")
                response_data['message'] = serialized_report.errors
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
