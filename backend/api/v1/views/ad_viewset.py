from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from apps.ads.models import Ad, LOV, BlockedUser
from api.v1.serializers.ad_serializer import AdSerializer
from apps.ads.Views_Custom import check_objectionable

class AdViewSet(viewsets.ModelViewSet):
    serializer_class = AdSerializer

    def get_queryset(self):
        queryset = Ad.objects.filter(status__in=['LIVE', 'REVIEW'])

        category = self.request.query_params.get('category')
        city = self.request.query_params.get('city')
        sort = self.request.query_params.get('sort', 'newest')
        posted = self.request.query_params.get('posted')
        search = self.request.query_params.get('search')
        phone = self.request.query_params.get('phone')

        print(f"DEBUG - Query Params: category={category}, city={city}, posted={posted}, search={search}, phone={phone}")
        print(f"DEBUG - Ads count before filtering: {queryset.count()}")

        if category:
            queryset = queryset.filter(category=category.upper())
            print(f"DEBUG - After category filter: {queryset.count()}")
        if city:
            # Filter by city LIC (case-insensitive)
            queryset = queryset.filter(city__iexact=city)
            print(f"DEBUG - After city filter: {queryset.count()}")
        if posted:
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()
            days = int(posted)
            start_date = (now - timedelta(days=days - 1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            print(f"DEBUG - Posted={posted}, days={days}, start_date={start_date}, now={now}")
            queryset = queryset.filter(created_at__gte=start_date)
            print(f"DEBUG - After posted filter: {queryset.count()}")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search) | Q(phone__icontains=search)
            )
        if phone:
            queryset = queryset.filter(phone=phone)

        # Apply sorting - ensure sorting is applied correctly
        print(f"DEBUG - Sort parameter: '{sort}'")
        print(f"DEBUG - Before sorting: {list(queryset.values_list('id', 'created_at')[:3])}")

        if sort == 'price_asc':
            queryset = queryset.order_by('price')
            print("DEBUG - Applied price_asc sorting")
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
            print("DEBUG - Applied price_desc sorting")
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
            print("DEBUG - Applied oldest sorting")
        else:
            # Default to newest sorting
            queryset = queryset.order_by('-created_at')
            print("DEBUG - Applied newest sorting (default)")

        print(f"DEBUG - After sorting: {list(queryset.values_list('id', 'created_at')[:3])}")
        print(f"DEBUG - Total count: {queryset.count()}")

        return queryset

    def create(self, request, *args, **kwargs):
        # Use the custom post_ad logic for creating ads
        data = request.POST.copy()

        # Normalize phone number
        phone = ''.join(filter(str.isdigit, data.get('phone', '')))
        if phone:
            if not phone.startswith('91'):
                phone = '91' + phone
            if not phone.startswith('+91'):
                phone = '+' + phone
            data['phone'] = phone

        # Normalize whatsapp if provided
        whatsapp = ''.join(filter(str.isdigit, data.get('whatsapp', '')))
        if whatsapp:
            if not whatsapp.startswith('91'):
                whatsapp = '91' + whatsapp
            if not whatsapp.startswith('+91'):
                whatsapp = '+' + whatsapp
            data['whatsapp'] = whatsapp

        # Validate required fields
        required_fields = ['title', 'description', 'location', 'city', 'category', 'phone']
        errors = {}
        for field in required_fields:
            value = data.get(field, '').strip()
            if not value:
                errors[field] = f'{field.capitalize()} is required.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        phone = data.get('phone')

        # Check if user is blocked
        if BlockedUser.objects.filter(phone=phone, status='BLOCKED').exists():
            return Response({'error': 'User is blocked from posting ads.'}, status=status.HTTP_403_FORBIDDEN)

        # Check objectionable words
        title = data.get('title', '')
        description = data.get('description', '')
        text = f"{title} {description}"
        mod_result = check_objectionable(text)
        if mod_result['status'] == 'BLOCKED':
            ad_status = 'BLOCKED'
            BlockedUser.objects.get_or_create(phone=phone, defaults={'status': 'BLOCKED', 'reason': f"Posted {mod_result['category']} content"})
        elif mod_result['status'] == 'FLAGGED':
            ad_status = 'REVIEW'
        else:
            # Check duplicate
            duplicate = Ad.objects.filter(
                Q(title__icontains=title) | Q(description__icontains=description),
                phone=phone
            ).exists()
            if duplicate:
                ad_status = 'REVIEW'
            else:
                ad_status = 'LIVE'

        # Check if image upload is enabled
        lov = LOV.objects.filter(type='UI_CONTROL', lic='ENABLE_IMAGE_UPLOAD', is_active=True).first()
        if not lov or lov.display_name != 'Enable Image Upload':
            images = []
        else:
            images = request.FILES.getlist('images')

        # Create ad directly
        ad = Ad.objects.create(
            title=data.get('title', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            city=data.get('city', ''),
            category=data.get('category', ''),
            phone=data.get('phone', ''),
            whatsapp=data.get('whatsapp', ''),
            status=ad_status,
            images=[]
        )

        # Handle image uploads
        image_urls = []
        for image in images[:5]:
            from django.core.files.storage import default_storage
            path = default_storage.save(f'ads/{ad.id}/{image.name}', image)
            image_urls.append(f'/media/{path}')
        if image_urls:
            ad.images = image_urls
            ad.save()

        serializer = self.get_serializer(ad)
        message = "Ad is in review, it will be displayed once completed. It will take a few minutes." if ad_status != 'LIVE' else "Ad posted successfully!"
        return Response({'data': serializer.data, 'message': message}, status=status.HTTP_201_CREATED)