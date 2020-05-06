from googleplaces import GooglePlaces

from project_piss import settings
import logging

from project_piss.helpers import get_logger

logger = get_logger()


def format_college_add_data(data):
    data['google_rating'] = data.get('rating', 0)

    logger.info("Converting latlong string to individual values")
    lat, lon = data.pop('latlng').split(':')[1].strip().replace("(", "").replace(")", "").split(',')
    data['latitude'] = lat
    data['longitude'] = lon

    logger.info("Formatting address lines")
    address_lines = data['address'].split(',')
    city = address_lines[-3].strip()
    data['city'] = city

    logger.info("Getting ID from city")
    data['city_id'] = get_id_from_city(city)
    state_data = address_lines[-2].split(" ")
    try:
        zipcode = int(state_data[-1].strip())
    except ValueError as e:
        zipcode = 000000
    data['zipcode'] = zipcode
    data['state'] = " ".join(state_data[:-1]).strip()
    logger.info(f"Formatted data - {data}")
    return data


def get_id_from_city(city):
    if settings.IS_TESTING:
        return "dummy_place_id1"
    else:
        logger.info("Fetching city id from google places")
        search_result = settings.google_places.text_search(query=city)
        logger.info(f"Places result - {search_result.places}")
        for place in search_result.places:
            logger.info(f"Checking if place {place.place_id} is locality or political")
            place_type = place.types
            if 'locality' in place_type or 'political' in place_type:
                logger.info(f"Place of required type found. Returning")
                return place.place_id