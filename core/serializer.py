from rest_framework import serializers
from .models import UploadData

class UploadDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadData
        # Specify the fields to include, excluding password and password_protected
        fields = ['created_on', 'video', 'photo', 'recording', 'is_assigned', 'slug']