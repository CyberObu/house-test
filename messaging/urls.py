from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('start/<int:user_id>/property/<int:property_id>/', views.start_conversation, name='start_conversation_property'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('<int:conversation_id>/poll/', views.poll_messages, name='poll_messages'),
]
