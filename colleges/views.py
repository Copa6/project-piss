from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
import logging
from googleplaces import GooglePlaces

from professors.models import Professor
from professors.serializers import ProfessorsSerializerGET
from professors.views import search
from project_piss import settings
from project_piss.helpers import generate_all_links, get_data_from_request, return_unhandled_response, get_logger
from .links import links
from colleges.models import College
from .serializers import CollegesSerializerPOST, CollegesSerializerGET
from rest_framework.decorators import api_view, permission_classes
from colleges.helpers import format_college_add_data


logger = get_logger()

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_links(request):
    user = request.user

    all_links = {
        '_links': {
            'colleges': links['colleges']['default']
        }
    }

    all_links = generate_all_links(user, all_links, links, app_name='colleges')
    return Response(all_links, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_college(request):
    logger.info("Got request to add new college")
    try:
        data = get_data_from_request(request, 'added_by')
        logger.info(f"Request data - {data}")
        college_id = data["id"]

        logger.info("Checking if college exists in database")
        college_exists = College.objects.filter(id=college_id).exists()
        if college_exists:
            logger.info("College already added to database. Returning existing college data")
            college = College.objects.get(id=college_id)
            response_data = {'status':'exists'}
            college_data = CollegesSerializerGET(college).data
            response_data['college'] = college_data

            logger.info(f"Fetching professors for college - {college_id}")
            professors_data = search(request._request, college_id)

            logger.info("Got professors for college. Adding to response")
            response_data['professors'] = professors_data.data['professors']
            return Response(response_data, status=status.HTTP_302_FOUND)
        else:
            logger.info("New college. Formatting data and saving to database")
            formatted_data = format_college_add_data(data)
            logger.info("Got formatted data. Serializing to save to database")
            serializer = CollegesSerializerPOST(data=formatted_data)
            if serializer.is_valid():
                logger.info("Data successfully serialized")
                serializer.save()
                logger.info("Saved to database")
                college = College.objects.get(id=formatted_data['id'])

                logger.info("Sending serialized college data in response")
                get_serializer = CollegesSerializerGET(college)

                return Response({'status': 'success', 'college': get_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Error serializing college data - {serializer.errors}")
                return Response({'status': 'failure', 'college': {}, 'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_all_cities(request):
    logger.info("Got request to get all cities")
    try:
        cities = list(set(College.objects.all().values_list("city", flat=True)))
        logger.info(f"Found {len(cities)} cities")
        return Response({'all_cities': cities}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view((['GET']))
@permission_classes((AllowAny,))
def get_all_colleges(request):
    logger.info("Got request to get all colleges from db")
    try:
        logger.info("Fetching all collges from db")
        colleges = College.objects.all()

        logger.info("Serializing database response")
        serializer = CollegesSerializerGET(colleges, many=True)
        if len(serializer.data) == 0:
            logger.info("No college found in database. Returning empty response")
            success = False
        else:
            success = True
        return Response({'success': success, 'colleges': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_all_colleges_for_city(request, city_id):
    logger.info(f"Got request to get all colleges for city - {city_id}")
    try:
        logger.info("Fetching colleges from database")
        colleges = College.objects.filter(city_id=city_id)

        logger.info("Serializing colleges")
        serializer = CollegesSerializerGET(colleges, many=True)
        logger.info(f"Got {len(serializer.data)} colleges in response")
        if len(serializer.data) == 0:
            success = False
        else:
            success = True
        return Response({'success': success, 'colleges':serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unhandled exception occurred - {str(e)}")
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
