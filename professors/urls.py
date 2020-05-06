from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.get_links, name='professor_links'),
    path('create/', views.create_professor, name='create_professors'),
    path('search/<str:college_id>', views.search, name='search_professors'),
    path('search/<str:college_id>/filter', views.get_filtered_professors, name="get_filtered_professors"),
    path('check-if-reviewed/<int:professor_id>', views.check_if_professor_reviewed, name='check_if_prof_reviewed'),
    path('add-review/<int:professor_id>', views.add_review, name='add_review'),
    path('get-reviews/<int:professor_id>', views.get_reviews, name='get_reviews'),
    path('review/<int:review_id>/like', views.like_review, name='like_review'),
    path('review/<int:review_id>/dislike', views.dislike_review, name='dislike_review'),
    path('review/<int:review_id>/report', views.report_review, name='report_review'),
    path('review/<int:review_id>/check-if-reported', views.check_if_review_reported, name='check_if_review_reported')

]
