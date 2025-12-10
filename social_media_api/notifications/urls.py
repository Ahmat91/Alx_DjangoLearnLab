
from django.urls import path
from .views import NotificationListView

urlpatterns = [
    # Route for users to view their notifications
    path('', NotificationListView.as_view(), name='notification_list'), 
]