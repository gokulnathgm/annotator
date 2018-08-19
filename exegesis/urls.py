from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from exegesis import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^create_project/', views.create_project),
    url(r'^artboards/', views.artboards),
    url(r'^svg_images/', views.svg_images),
    url(r'^svg/', views.index),
    url(r'^update_artboard/', views.update_artboard),
    url(r'^delete_artboard/', views.delete_artboard),
    url(r'^rename_artboard/', views.rename_artboard),
    url(r'^delete_project/', views.delete_project),
    url(r'^share_project/', views.share_project),
    # url(r'^download_artboard/', views.download_artboard),
    url(r'^revisions/', views.revisions),
    url(r'^write_note/', views.write_note),
]
