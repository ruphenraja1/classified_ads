from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Ad
from .serializers import AdSerializer
from .time_windows import boundary_for_posted_days

@api_view(['GET'])
def timewindow_ads(request):
    qs = Ad.objects.all()

    posted = request.query_params.get('posted')
    try:
        days = int(posted) if posted is not None else None
    except (TypeError, ValueError):
        days = None

    if days is not None:
        # Local midnight boundary
        boundary = boundary_for_posted_days(days)
        if boundary:
            qs = qs.filter(created_at__gte=boundary)

        # Default to oldest first within window when sort is not provided
        sort = request.query_params.get('sort')
        if not sort:
            qs = qs.order_by('created_at')
    # Sorting if provided
    sort = request.query_params.get('sort')
    if sort:
        if sort == 'newest':
            qs = qs.order_by('-created_at')
        elif sort == 'oldest':
            qs = qs.order_by('created_at')
    else:
        if days is None:
            qs = qs.order_by('-created_at')

    ser = AdSerializer(qs, many=True)
    return Response({'results': ser.data, 'count': qs.count()})
