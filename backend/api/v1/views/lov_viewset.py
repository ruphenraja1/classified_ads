from rest_framework import viewsets
from apps.ads.models import LOV
from api.v1.serializers.lov_serializer import LOVSerializer

class LOVViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LOVSerializer
    pagination_class = None  # Disable pagination to return all results

    def get_queryset(self):
        queryset = LOV.objects.filter(is_active=True)
        type_filter = self.request.query_params.get('type')
        language = self.request.query_params.get('language')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if language:
            queryset = queryset.filter(language=language)

        return queryset.order_by('order', 'display_name')