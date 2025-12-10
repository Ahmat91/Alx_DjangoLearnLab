
from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer 

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    # Since target is a GenericForeignKey, we serialize just enough info
    target_type = serializers.SerializerMethodField()
    target_id = serializers.ReadOnlyField(source='target_object_id')

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor', 'verb', 'timestamp', 'is_read',
            'target_type', 'target_id'
        ]
        read_only_fields = fields

    def get_target_type(self, obj):
        if obj.target:
            return obj.target.__class__.__name__
        return None