from rest_framework import serializers
from apps.ads.models import Ad

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'

    def create(self, validated_data):
        print(f"SERIALIZER DEBUG - Creating ad with validated_data: {validated_data}")
        print(f"SERIALIZER DEBUG - Status in validated_data: {validated_data.get('status', 'NOT FOUND')}")
        ad = super().create(validated_data)
        print(f"SERIALIZER DEBUG - Ad created with status: {ad.status}")
        return ad