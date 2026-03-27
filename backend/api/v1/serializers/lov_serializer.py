from rest_framework import serializers
from apps.ads.models import LOV

class LOVSerializer(serializers.ModelSerializer):
    class Meta:
        model = LOV
        fields = '__all__'