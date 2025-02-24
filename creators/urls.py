from django.urls import path
from . import views
urlpatterns = [
    path('add_creator/', views.add_creator, name='add_creator'),
    path('02a10962-b38b-4d7a-a62c-4f22e2a32e46/', views.whatsappWebhook, name='whatsapp-webhook'),
    ]