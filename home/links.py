# Links for this app
from project_piss.helpers import create_link_dict

users = {
    'default': {
        'save_details': create_link_dict('user/verify-app-status'),
        'send_activation_code': create_link_dict('auth/send-activation-code'),
        'verify_activation_code': create_link_dict('auth/verify-activation-code'),
        'verify_user_exists': create_link_dict('auth/verify-user-exists'),
        'register': create_link_dict('auth/users/create/'),
        'login': create_link_dict('login/'),
        'google_login': create_link_dict('register-by-token/google-oauth2/register'),
        },
    'authenticated': {
        'refresh_token': create_link_dict('/auth/jwt/refresh/'),
        'create_profile': create_link_dict('user/create_profile'),
        'update_profile': create_link_dict('user/update_profile', method='PUT'),
        'user': create_link_dict('auth/users/me/', method='GET')
        }
}

professors = {
    "default": {
        "get_links": create_link_dict('professors/'),
        "get_all_professor": create_link_dict('professors/search/{college_id}'),
        "get_review": create_link_dict('professors/get-reviews/{professor_id}', method='GET')
    },
    "authenticated": {
        "add_professor": create_link_dict('professors/create/'),
        "add_review": create_link_dict('professors/add-review/{professor_id}'),
        "check_if_professor_reviewed": create_link_dict('professors/check-if-reviewed/{professor_id}', method='GET'),
        "like_review": create_link_dict('professors/review/{review_id}/like', method='GET'),
        "dislike_review": create_link_dict('professors/review/{review_id}/dislike', method='GET'),
        "report_review": create_link_dict('professors/review/{review_id}/report'),
        "check_if_review_reported": create_link_dict('professors/review/{review_id}/check-if-reported', method='GET')
    }
}

colleges = {
    "default": {
        'get_links': create_link_dict('colleges/'),
        "search_college": create_link_dict("colleges/search/", method='GET'),
        'get_all': create_link_dict("colleges/get-all-colleges", method='GET')
    },
    "authenticated": {
        "add_college": create_link_dict('colleges/create/')
    }
}

links = {
    'users': users,
    'professors': professors,
    'colleges': colleges
}