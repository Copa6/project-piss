import time
import logging

from project_piss.helpers import get_logger

logger = get_logger()


def send_email(email_message):
    try:
        email_message.send()
        logger.info("Successfully sent email.")
    except Exception as e:
        logger.error(f"Error while sending email - {e}")


def get_user_profile_data(profile_data, user):
    user_data = {'user': user.pk, 'username': user.get_username(), 'email': user.email, 'profile': profile_data}
    return user_data
