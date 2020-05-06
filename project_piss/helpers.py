import os

from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
import logging as l
from project_piss import settings
from google.cloud.logging.handlers import CloudLoggingHandler

# if os.getenv('GAE_APPLICATION', None):
#     logger = l.getLogger('google-cloud-logger')
# else:
logger = l.getLogger("project-piss")

def get_logger():
    if os.getenv('GAE_APPLICATION', None):
        handler = CloudLoggingHandler(settings.client)
        cloud_logger = l.getLogger("cloudLogger")
        cloud_logger.setLevel(l.INFO)
        cloud_logger.addHandler(handler)
        logger = cloud_logger
    else:
        logger = l.getLogger("project-piss")
    return logger


def create_link_dict(href, method='POST', content_type='application/json'):
    return {
        'href': href,
        'method': method,
        'content-type': content_type
    }


def generate_all_links(user, all_links, links, app_name):
    if not user.is_authenticated:
        logger.info("Generating links for non-authenticated user")
        for key in links[app_name]['authenticated']:
            all_links['_links'][app_name].pop(key, None)
    else:
        logger.info("Generating links for authenticated user")
        for key in all_links['_links']:
            all_links['_links'][key].update(links[key]['authenticated'])

    return all_links


def get_data_from_request(request, field_name='user'):
    logger.info("Parse data from request")
    data = JSONParser().parse(request)
    try:
        logger.info("Trying to get user from request")
        user = User.objects.get(username=request.user)
        logger.info(f"User found - {user.pk}")
        data[field_name] = user.pk
    except User.DoesNotExist:
        logger.info("User not found for this request")
        data[field_name] = None
    return data


def return_unhandled_response(e):
    logger.error(f"Unhandled exception occurred - {str(e)}")
    return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
