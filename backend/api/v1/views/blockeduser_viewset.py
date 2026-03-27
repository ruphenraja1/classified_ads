from rest_framework import viewsets
from apps.ads.models import BlockedUser
from api.v1.serializers.blockeduser_serializer import BlockedUserSerializer

class BlockedUserViewSet(viewsets.ModelViewSet):
    queryset = BlockedUser.objects.all()
    serializer_class = BlockedUserSerializer