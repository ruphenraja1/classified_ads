from django.shortcuts import render, get_object_or_404, redirect
import re
import unicodedata
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Ad, LOV, BlockedUser
from .serializers import AdSerializer, LOVSerializer
from .Views_Custom import lov_management, delete_lov, copy_lov, ad_management, delete_ad, blockeduser_management, delete_blockeduser, verify_content, check_objectionable


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

class AdListCreate(generics.ListCreateAPIView):
    serializer_class = AdSerializer

    def create(self, request, *args, **kwargs):
        # Use the custom post_ad logic for creating ads
        from rest_framework.decorators import api_view
        from rest_framework.response import Response
        from .models import Ad, BlockedUser
        from django.db.models import Q
        
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
            return Response(errors, status=400)
        
        phone = data.get('phone')
        
        # Check if user is blocked
        if BlockedUser.objects.filter(phone=phone, status='BLOCKED').exists():
            return Response({'error': 'User is blocked from posting ads.'}, status=403)
        
        # Check objectionable words
        title = data.get('title', '')
        description = data.get('description', '')
        text = f"{title} {description}"
        mod_result = check_objectionable(text)
        if mod_result['status'] == 'BLOCKED':
            status = 'BLOCKED'
            BlockedUser.objects.get_or_create(phone=phone, defaults={'status': 'BLOCKED', 'reason': f"Posted {mod_result['category']} content"})
        elif mod_result['status'] == 'FLAGGED':
            status = 'REVIEW'
        else:
            # Check duplicate
            duplicate = Ad.objects.filter(
                Q(title__icontains=title) | Q(description__icontains=description),
                phone=phone
            ).exists()
            if duplicate:
                status = 'REVIEW'
            else:
                status = 'LIVE'
        
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
            status=status,
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
        message = "Ad is in review, it will be displayed once completed. It will take a few minutes." if status != 'LIVE' else "Ad posted successfully!"
        return Response({'data': serializer.data, 'message': message}, status=201)

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

class AdDetail(generics.RetrieveAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

class LOVList(generics.ListAPIView):
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

from django.db.models import Q

@api_view(['POST'])
def post_ad(request):
    data = request.POST.copy()

    # Normalize phone number
    phone = ''.join(filter(str.isdigit, data.get('phone', '')))
    print(f"Original phone: {data.get('phone')}, digits: {phone}")
    if phone:
        if not phone.startswith('91'):
            phone = '91' + phone
        if not phone.startswith('+91'):
            phone = '+' + phone
        data['phone'] = phone
    print(f"Normalized phone: {data['phone']}")

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
        return Response(errors, status=400)

    phone = data.get('phone')

    # Check if user is blocked
    if BlockedUser.objects.filter(phone=phone, status='BLOCKED').exists():
        return Response({'error': 'User is blocked from posting ads.'}, status=403)

    # Check objectionable words
    title = data.get('title', '')
    description = data.get('description', '')
    text = f"{title} {description}"
    mod_result = check_objectionable(text)
    print(f"DEBUG - check_objectionable result: {mod_result}")
    if mod_result['status'] == 'BLOCKED':
        status = 'BLOCKED'
        BlockedUser.objects.get_or_create(phone=phone, defaults={'status': 'BLOCKED', 'reason': f"Posted {mod_result['category']} content"})
    elif mod_result['status'] == 'FLAGGED':
        status = 'REVIEW'
    else:
        # Check duplicate
        duplicate = Ad.objects.filter(
            Q(title__icontains=title) | Q(description__icontains=description),
            phone=phone
        ).exists()
        print(f"DEBUG - Duplicate check: {duplicate}")
        if duplicate:
            status = 'REVIEW'
        else:
            status = 'LIVE'
        print(f"DEBUG - Setting status to LIVE")
    
    print(f"DEBUG - Final status before save: {status}")
    
    # Check if image upload is enabled
    lov = LOV.objects.filter(type='UI_CONTROL', lic='ENABLE_IMAGE_UPLOAD', is_active=True).first()
    if not lov or lov.display_name != 'Enable Image Upload':
        images = []  # No images
    else:
        images = request.FILES.getlist('images')

    # City is already LIC

    # Create ad directly using model to bypass serializer issues
    from .models import Ad
    ad = Ad.objects.create(
        title=data.get('title', ''),
        description=data.get('description', ''),
        location=data.get('location', ''),
        city=data.get('city', ''),
        category=data.get('category', ''),
        phone=data.get('phone', ''),
        whatsapp=data.get('whatsapp', ''),
        status=status,
        images=[]
    )
    print(f"DEBUG - Ad created directly with ID: {ad.id}, status: {ad.status}")
    
    # Handle image uploads if provided
    image_urls = []
    for image in images[:5]:  # Max 5 images
        # Save to media folder
        from django.core.files.storage import default_storage
        path = default_storage.save(f'ads/{ad.id}/{image.name}', image)
        image_urls.append(f'/media/{path}')
    if image_urls:
        ad.images = image_urls
        ad.save()
    
    # Return serialized data
    serializer = AdSerializer(ad)
    message = "Ad is in review, it will be displayed once completed. It will take a few minutes." if status != 'LIVE' else "Ad posted successfully!"
    return Response({'data': serializer.data, 'message': message}, status=201)





# For compatibility, return True if BLOCKED
# But update to return the dict

@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': 'Phone number required'}, status=400)
    # Send OTP via Twilio Verify (Twilio generates and sends OTP)
    try:
        from twilio.rest import Client
        ACCOUNT_SID = "AC69cec0cd4d16a15c5d578359754c2c49"
        AUTH_TOKEN = "ea6fc7b0fbde2a2ea92ade99322eb055"
        VERIFY_SERVICE_SID = "VAd8f88f30faf220dfc7135e1ca58aa43a"
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        verification = client.verify.v2.services(VERIFY_SERVICE_SID).verifications.create(
            to=phone,
            channel="sms"
        )
        return Response({'success': True, 'sid': verification.sid})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def verify_otp(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    if not phone or not otp:
        return Response({'error': 'Phone and OTP required'}, status=400)
    try:
        from twilio.rest import Client
        ACCOUNT_SID = "AC69cec0cd4d16a15c5d578359754c2c49"
        AUTH_TOKEN = "ea6fc7b0fbde2a2ea92ade99322eb055"
        VERIFY_SERVICE_SID = "VAd8f88f30faf220dfc7135e1ca58aa43a"
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        verification_check = client.verify.v2.services(VERIFY_SERVICE_SID).verification_checks.create(
            to=phone,
            code=otp
        )
        if verification_check.status == 'approved':
            return Response({'valid': True})
        else:
            return Response({'valid': False}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)



def lov_management(request, pk=None):
    if pk == 'new':
        if request.method == 'POST':
            type_val = request.POST.get('type')
            lic_val = request.POST.get('lic')
            lang_val = request.POST.get('language')
            lov, created = LOV.objects.get_or_create(
                type=type_val,
                lic=lic_val,
                language=lang_val,
                defaults={
                    'display_name': request.POST.get('display_name'),
                    'parent_value_id': request.POST.get('parent_value'),
                    'description': request.POST.get('description'),
                    'is_active': request.POST.get('is_active') == 'on'
                }
            )
            if not created:
                lov.display_name = request.POST.get('display_name')
                lov.parent_value_id = request.POST.get('parent_value')
                lov.description = request.POST.get('description')
                lov.is_active = request.POST.get('is_active') == 'on'
                lov.save()
            return redirect('lov_management')
        parent_lovs = LOV.objects.all()
        return render(request, 'lov_detail.html', {'lov': None, 'parent_lovs': parent_lovs})
    elif pk:
        lov = get_object_or_404(LOV, pk=pk)
        if request.method == 'POST':
            lov.type = request.POST.get('type')
            lov.lic = request.POST.get('lic')
            lov.display_name = request.POST.get('display_name')
            lov.language = request.POST.get('language')
            lov.parent_value_id = request.POST.get('parent_value')
            lov.description = request.POST.get('description')
            lov.is_active = request.POST.get('is_active') == 'on'
            lov.save()
            return redirect('lov_management')
        parent_lovs = LOV.objects.all()
        return render(request, 'lov_detail.html', {'lov': lov, 'parent_lovs': parent_lovs})
    else:
        if request.method == 'POST':
            type_val = request.POST.get('type')
            lic_val = request.POST.get('lic')
            lang_val = request.POST.get('language')
            lov, created = LOV.objects.get_or_create(
                type=type_val,
                lic=lic_val,
                language=lang_val,
                defaults={
                    'display_name': request.POST.get('display_name'),
                    'parent_value_id': request.POST.get('parent_value'),
                    'description': request.POST.get('description'),
                    'is_active': request.POST.get('is_active') == 'on'
                }
            )
            if not created:
                lov.display_name = request.POST.get('display_name')
                lov.parent_value_id = request.POST.get('parent_value')
                lov.description = request.POST.get('description')
                lov.is_active = request.POST.get('is_active') == 'on'
                lov.save()
            return redirect('lov_management')
        lovs = LOV.objects.all()
        q_id = request.GET.get('id', '').strip()
        q_type = request.GET.get('type', '').strip()
        q_lic = request.GET.get('lic', '').strip()
        q_display_name = request.GET.get('display_name', '').strip()
        q_language = request.GET.get('language', '').strip()
        q_is_active = request.GET.get('is_active', '').strip()
        if q_id:
            lovs = lovs.filter(id__icontains=q_id.replace('*', '')) if '*' in q_id else lovs.filter(id=q_id)
        if q_type:
            lovs = lovs.filter(type__icontains=q_type.replace('*', '')) if '*' in q_type else lovs.filter(type=q_type)
        if q_lic:
            lovs = lovs.filter(lic__icontains=q_lic.replace('*', '')) if '*' in q_lic else lovs.filter(lic=q_lic)
        if q_display_name:
            lovs = lovs.filter(display_name__icontains=q_display_name.replace('*', '')) if '*' in q_display_name else lovs.filter(display_name=q_display_name)
        if q_language:
            lovs = lovs.filter(language=q_language)
        if q_is_active:
            lovs = lovs.filter(is_active=q_is_active == '1')
        return render(request, 'lov_list.html', {'lovs': lovs})


@api_view(['POST'])
def copy_lov(request):
    ids = request.data.get('ids', [])
    for id in ids:
        lov = LOV.objects.get(id=id)
        lov.id = None
        lov.save()
    return Response({'success': True})


@api_view(['POST'])
def delete_lov(request):
    ids = request.data.get('ids', [])
    LOV.objects.filter(id__in=ids).delete()
    return Response({'success': True})


@api_view(['POST'])
def import_lov(request):
    """
    Import LOV records from CSV data
    Expected CSV format: type,Order,Description,LIC,Language,display_name,is_active
    """
    import csv
    from io import StringIO
    
    csv_data = request.data.get('csv_data', '')
    
    if not csv_data:
        return Response({'success': False, 'error': 'No CSV data provided'}, status=400)
    
    try:
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for row_num, row in enumerate(reader, start=1):
            try:
                is_active = row.get('is_active', 'true').lower() == 'true'
                
                lov, created = LOV.objects.update_or_create(
                    type=row.get('type', '').strip(),
                    lic=row.get('LIC', '').strip(),
                    language=row.get('Language', '').strip(),
                    defaults={
                        'display_name': row.get('display_name', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'is_active': is_active,
                        'order': int(row.get('Order', 0))
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_count += 1
                continue
        
        return Response({
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'errors': error_count
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)





@api_view(['POST'])
def delete_ad(request):
    ids = request.data.get('ids', [])
    Ad.objects.filter(id__in=ids).delete()
    return Response({'success': True})


@api_view(['POST'])
def delete_blockeduser(request):
    ids = request.data.get('ids', [])
    BlockedUser.objects.filter(id__in=ids).delete()
    return Response({'success': True})


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')



