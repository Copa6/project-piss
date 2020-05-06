from rest_framework.pagination import PageNumberPagination
from project_piss import settings


class ReviewsPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = 'page_size'
    max_page_size = 1000