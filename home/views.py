import random
import time
from threading import Thread
import logging

import pyrebase
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from home.helpers import get_user_profile_data, send_email
from home.models import Profile, UserActivation
from project_piss import settings
from project_piss.helpers import generate_all_links, get_data_from_request, return_unhandled_response, get_logger
from project_piss.settings import VERSIONS, FIREBASE
from .links import links
from .serializers import ProfileSerializer, UserPhoneDetailsSerializer, UserActivationSerializer

firebase = pyrebase.initialize_app(FIREBASE)
logger = get_logger()


def jwt_response_payload_handler(token, user=None, request=None):
    user_data = {
        'email': user.email,
        'token': token
    }
    return user_data


def test(request):
    return render(request, 'email.html', {})

@psa('social:complete')
@api_view(['POST'])
@permission_classes((AllowAny,))
def register_by_access_token(request, backend):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    logger.info("Got request to sign in user from access token")
    request_data = get_data_from_request(request)
    token = request_data.get('access_token')

    user = request.backend.do_auth(access_token=token, backend=backend)
    if user:
        logger.info("User authenticated. Generating token")
        login(request, user)
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        logger.info("Token generated successfully")
        return Response({"user": user.email,
                         "token": token}, status=status.HTTP_200_OK)
    else:
        logger.info("unable to authenticate user. Error.")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def get_links(request):
    logger.info("Get All Links called")
    user = request.user

    logger.info(f"user - {user.pk}")
    all_links = {
        'username': '',
        'email': '',
        '_links': {
            'users': links['users']['default'],
            'professors': links['professors']['default'],
            'colleges': links['colleges']['default']
        }
    }

    all_links = generate_all_links(user, all_links, links, app_name='users')

    if user.is_authenticated:
        logger.info("User is authenticated, adding links for add/edit functionality")
        user = User.objects.get(username=request.user)
        all_links['username'] = user.get_username()
        all_links['email'] = user.email

    return Response(all_links, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def send_activation_code(request):
    try:
        data = get_data_from_request(request)
        email = data['email']
        logger.info(f"Sending activation code to {email}")

        # TODO: possible to implement hashing here
        activation_code = random.randint(100000, 999999)

        logger.debug(f"Activation code - {activation_code}")
        serializer_data = {
            'email': email,
            'activation_code': activation_code,
            'activation_status': False,
        }

        try:
            logger.info("Checking if user already requested activation token.")
            existing_detail = UserActivation.objects.get(email=email)
            last_attempt_time = existing_detail.attempt_datetime
            logger.info(f"User's lask activation code request time - {last_attempt_time}")

            time_difference_between_attempts = time.time() - last_attempt_time
            logger.info(f"Time difference between consecutive attempts - {time_difference_between_attempts}")

            logger.info(f"Maximum attempts allowed in {settings.ACTIVATION_DELAY_SECONDS}seconds - "
                        f"{settings.MAX_ACTIVATION_ATTEMPTS}")
            if existing_detail.num_attempts >= settings.MAX_ACTIVATION_ATTEMPTS:
                if time_difference_between_attempts <= settings.ACTIVATION_DELAY_SECONDS:
                    logger.info("Exceeded maximum number of attempts in given time")
                    delay_minutes = int(settings.ACTIVATION_DELAY_SECONDS/60)
                    response_data = {'status': 'failure', 'reason': f"Only {settings.MAX_ACTIVATION_ATTEMPTS} attempts "
                                                                    f"allowed every {delay_minutes}"
                                                                    f" minutes. Please try after "
                                                                    f"{delay_minutes-int(time_difference_between_attempts/60)} minutes."}
                    return Response(response_data, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    logger.info("User requesting activation code after expected time difference. "
                                "Sending new activation code.")
                    serializer_data['num_attempts'] = 1
                    serializer_data['attempt_datetime'] = time.time()
                    logger.info(f"Activation code generated at - {time.time()}")
                    serializer = UserActivationSerializer(existing_detail, data=serializer_data)
            else:
                logger.info(f"Activation code request number - {existing_detail.num_attempts + 1}")
                serializer_data['num_attempts'] = existing_detail.num_attempts + 1
                logger.info(f"User requested less than {settings.MAX_ACTIVATION_ATTEMPTS} times. Sending activation code.")
                serializer = UserActivationSerializer(existing_detail, data=serializer_data)

        except UserActivation.DoesNotExist:
            logger.info("New user. Sending activation code.")
            serializer_data['num_attempts'] = 1
            serializer_data['attempt_datetime'] = time.time()
            serializer = UserActivationSerializer(data=serializer_data)

        if serializer.is_valid():
            serializer.save()
            if not settings.IS_TESTING:
                logger.info("Preparing email to be sent to the user.")
                plaintext = get_template('email.txt')
                htmltext = get_template('email.html')
                context = {'activation_code': activation_code}
                text_content = plaintext.render(context)
                html_content = htmltext.render(context)
                subject = "Welcome to PISS"
                msg = EmailMultiAlternatives(subject, text_content, to=[data["email"]])
                msg.attach_alternative(html_content, "text/html")

                logger.info("Email content generated. Sending email to user")
                send_email_thread = Thread(target=send_email, args=(msg, ))
                send_email_thread.start()
            response_data = {'status': 'success'}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.info("Error generating activation code for the user")
            logger.error(f"{serializer.errors}")
            response_data = {'status': 'failure'}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def verify_activation_code(request):
    try:
        data = get_data_from_request(request)
        logger.info(f"Verifying activation code. User - {data['user']}")
        data['activation_code'] = int(data['activation_code'])
        try:
            logger.info("Fetching user and activation code from database.")
            user_activation_object = UserActivation.objects.get(email=data['email'])
            if user_activation_object is not None:
                user_activation_serializer = UserActivationSerializer(user_activation_object)
                activation_code = user_activation_serializer.data['activation_code']
                logger.info("Matching user activation code with actual activation code")
                if activation_code == data['activation_code']:
                    logger.info("Code matched")
                    data['activation_status'] = True
                    updated_serializer = UserActivationSerializer(user_activation_object, data=data)
                    if updated_serializer.is_valid():
                        logger.info("User activation status updated. Sending Success response")
                        updated_serializer.save()
                    return Response({'status': 'verified'}, status=status.HTTP_200_OK)
                else:
                    logger.error("Activation code mismatch")
                    return Response({'status': 'rejected'}, status=status.HTTP_404_NOT_FOUND)
        except UserActivation.DoesNotExist:
            logger.info("User not found. Activation code is not generated for the user.")
            return Response({'status': 'email not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def verify_if_user_registered(request):
    data = get_data_from_request(request)
    email = data['email']
    logger.info(f"Searching for user with email {email}")
    user = get_object_or_404(User, username=email)
    return Response({'success': 'User exists'}, status=status.HTTP_302_FOUND)

@api_view(['POST'])
@permission_classes((AllowAny,))
def save_user_phone_details(request):
    try:
        logger.info("Saving user phone details")
        data = get_data_from_request(request)
        logger.info(f"Request data - {data}")
        logger.info("Validating request data")
        serializer = UserPhoneDetailsSerializer(data=data)
        response_data = {'status': 'Reject'}
        user_version_code = float(data['versionCode'])
        if serializer.is_valid():
            logger.info("User data valid. Saving to database")
            serializer.save()
            logger.info("User phone data saved")

            logger.info("Saving data to firebase db")
            db = firebase.database()
            db.child("userDevice").push(serializer.data)
            logger.info("Data saved to firebase db")

            logger.info("Checking user app version")
            if user_version_code >= float(VERSIONS['min_code']):
                logger.info(f"User version code - {user_version_code} greater than minimum required version - "
                            f"{VERSIONS['min_code']}")
                response_data['status'] = 'Later'
                if user_version_code >= float(VERSIONS['latest_code']):
                    logger.info(f"User version code - {user_version_code} satisfies latest version - "
                                f"{VERSIONS['latest_code']}")
                    response_data['status'] = 'Approved'

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            logger.info("User phone data invalid")
            return Response({'status': 'Error', 'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# user/create_profile
@api_view(['POST'])
@permission_classes((AllowAny,))
def set_profile(request):
    try:
        data = get_data_from_request(request)
        serializer = ProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":"true"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# user/update_profile
@api_view(['PUT'])
def update_profile(request):
    try:
        data = JSONParser().parse(request)
        user = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile, data=data)
        if serializer.is_valid():
            serializer.save()
            profile_data = serializer.data
            user_data = get_user_profile_data(profile_data, user)
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)