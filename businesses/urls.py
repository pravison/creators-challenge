from django.urls import path
from . import views
urlpatterns = [
    path('add-business/', views.add_business, name='add_business'),
    path('', views.business, name='business'),
    path('<slug:slug>/', views.dashboard, name='dashboard'),
    path('<slug:slug>/add-staff', views.add_staff, name='add_staff'),
    path('<slug:slug>/create-store-Challenge/', views.create_store_challenge, name='create_store_challenge'),
    path('<slug:slug>/store-challenges/', views.store_challenges, name='store_challenges'),
    path('<slug:slug>/view-store-challenge/', views.view_store_challenge, name='view_store_challenge'),
    path('<slug:slug>/add-content-creation-job/', views.add_content_creation_job, name='add_content_creation_job'),
    path('<slug:slug>/content-creation-jobs/', views.content_creation_jobs, name='content_creation_jobs'),
    path('challenge/<int:id>/', views.submit_challenge_video_url, name='submit_video_url'),
    path('<slug:slug>/content-creation-jobs-requests/', views.content_creation_jobs_requests, name='content_creation_jobs_requests'),
]