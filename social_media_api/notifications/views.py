
from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
   
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve all notifications for the authenticated user, ordered by newest first
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Optionally, mark unread notifications as read upon listing
        queryset.filter(is_read=False).update(is_read=True)
        
        return queryset.order_by('-timestamp')