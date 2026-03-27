from rest_framework import serializers
from apps.ads.models import BlockedUser

class BlockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = '__all__'