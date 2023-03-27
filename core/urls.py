from django.urls import path
from . import views
from rest_framework .authtoken.views import obtain_auth_token

urlpatterns = [
    path("", views.index),
    path('signup', views.signup),
    path('signin', views.signin),
    path('logout', views.logout),
    path('setting', views.setting),
    path('upload', views.upload),
    path('like-post', views.like_post),
    path('register', views.register.as_view()),
    path('login/', obtain_auth_token),
    path('getpost', views.getpost.as_view()),
    path('postfeed', views.postfeed.as_view()),
]