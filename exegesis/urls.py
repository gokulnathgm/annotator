from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from exegesis import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^projects/$', views.projects, name='projects'),
]
