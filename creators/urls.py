from django.urls import path
from . import views
urlpatterns = [
    path('add_creator/', views.add_creator, name='add_creator'),
    ]