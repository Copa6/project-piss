from django.urls import path, include

from rest_framework_jwt import views as jwt_views
from . import views

urlpatterns = [
    path('', views.get_links, name='home_links'),
    path('test/', views.test, name='test'),
    #Social login
    path('login/', include('rest_social_auth.urls_jwt')),
    path('login/', include('rest_social_auth.urls_session')),
    path('register-by-token/<str:backend>/register', views.register_by_access_token, name="social_register_by_access_token"),

    path('user/verify-app-status', views.save_user_phone_details, name='user_phone_details'),
    path('auth/verify-user-exists', views.verify_if_user_registered, name='verify_user_registered'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/send-activation-code', views.send_activation_code, name='send-activation-code'),
    path('auth/verify-activation-code', views.verify_activation_code, name='verify-activation-code'),
    path('login/', jwt_views.obtain_jwt_token, name='auth'),
    path('login/', include('rest_social_auth.urls_jwt'), name='social-auth'),
    path('user/create-profile', views.set_profile, name='set_profile'),
    path('user/update-profile', views.update_profile, name='update_profile')
]
