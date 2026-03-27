import re
import unicodedata
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import LOV, Ad, BlockedUser
from .serializers import AdSerializer, LOVSerializer
from django.core.files.storage import default_storage


# =====================================================
# API VIEWS (CLASS-BASED)
# =====================================================

class AdListCreate(generics.ListCreateAPIView):
    serializer_class = AdSerializer

    def get_queryset(self):
        queryset = Ad.objects.filter(status='LIVE')  # Only show LIVE ads
        category = self.request.query_params.get('category')
        city = self.request.query_params.get('city')
        sort = self.request.query_params.get('sort', 'newest')
        posted = self.request.query_params.get('posted')  # Changed from 'today' to 'posted'
        phone = self.request.query_params.get('phone')

        if category:
            queryset = queryset.filter(category=category.upper())
        if city:
            queryset = queryset.filter(city__iexact=city)  # Case-insensitive LIC match
        if posted:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            days = int(posted)
            # Calculate start date: N days ago at 00:00
            start_date = (now - timedelta(days=days - 1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            print(f"DEBUG - Posted={posted}, days={days}, start_date={start_date}, now={now}")
            queryset = queryset.filter(created_at__gte=start_date)
            print(f"DEBUG - After posted filter: {queryset.count()}")
        if phone:
            queryset = queryset.filter(phone=phone)

        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

class AdDetail(generics.RetrieveAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

class LOVList(generics.ListAPIView):
    serializer_class = LOVSerializer
    # Return full list for LOV lookups (no pagination)
    pagination_class = None

    def get_queryset(self):
        queryset = LOV.objects.filter(is_active=True)
        type_filter = self.request.query_params.get('type')
        language = self.request.query_params.get('language', 'en')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        queryset = queryset.filter(language=language)
        # Sort by configured order field first, then display name
        return queryset.order_by('order', 'display_name')


# =====================================================
# LOV MANAGEMENT (UNCHANGED)
# =====================================================

def lov_management(request, pk=None):
    if request.method == 'POST' and not pk:
        for lov in LOV.objects.all():
            lov_id = str(lov.id)
            if f'type_{lov_id}' in request.POST:
                lov.type = request.POST.get(f'type_{lov_id}')
                lov.lic = request.POST.get(f'lic_{lov_id}')
                lov.display_name = request.POST.get(f'display_name_{lov_id}')
                lov.language = request.POST.get(f'language_{lov_id}')
                parent_id = request.POST.get(f'parent_value_{lov_id}')
                lov.parent_value_id = int(parent_id) if parent_id and parent_id.isdigit() else None
                lov.description = request.POST.get(f'description_{lov_id}')
                lov.order = int(request.POST.get(f'order_{lov_id}') or 0)
                lov.is_active = f'is_active_{lov_id}' in request.POST
                lov.save()
        return redirect('lov_management')

    if pk == 'new':
        if request.method == 'POST':
            # Check if this is a copy operation
            is_copy_mode = request.POST.get('copy_mode') == '1'
            
            parent_value = request.POST.get('parent_value')
            parent_value_id = int(parent_value) if parent_value and parent_value.isdigit() else None
            
            if is_copy_mode:
                # In copy mode, always create a new record
                lov = LOV.objects.create(
                    type=request.POST.get('type'),
                    lic=request.POST.get('lic'),
                    language=request.POST.get('language'),
                    display_name=request.POST.get('display_name'),
                    parent_value_id=parent_value_id,
                    description=request.POST.get('description'),
                    order=int(request.POST.get('order') or 0),
                    is_active=request.POST.get('is_active') == 'on'
                )
                print(f"Created new copy LOV: {lov}")
            else:
                # In normal new mode, use get_or_create
                lov, created = LOV.objects.get_or_create(
                    type=request.POST.get('type'),
                    lic=request.POST.get('lic'),
                    language=request.POST.get('language'),
                    defaults={
                        'display_name': request.POST.get('display_name'),
                        'parent_value_id': parent_value_id,
                        'description': request.POST.get('description'),
                        'order': int(request.POST.get('order') or 0),
                        'is_active': request.POST.get('is_active') == 'on'
                    }
                )
                if not created:
                    print(f"Updated existing LOV: {lov}")
                    # Update existing
                    lov.display_name = request.POST.get('display_name')
                    lov.parent_value_id = parent_value_id
                    lov.description = request.POST.get('description')
                    lov.order = int(request.POST.get('order') or 0)
                    lov.is_active = request.POST.get('is_active') == 'on'
                    lov.save()
                else:
                    print(f"Created new LOV: {lov}")
            return redirect('lov_management')

        # Handle copy_from parameter
        copy_from_id = request.GET.get('copy_from')
        initial_data = {}
        if copy_from_id:
            try:
                source_lov = LOV.objects.get(id=copy_from_id)
                initial_data = {
                    'type': source_lov.type,
                    'lic': source_lov.lic,
                    'display_name': source_lov.display_name,
                    'language': source_lov.language,
                    'parent_value': source_lov.parent_value_id,
                    'description': source_lov.description,
                    'is_active': 'on' if source_lov.is_active else ''
                }
            except LOV.DoesNotExist:
                pass

        return render(request, 'lov_detail.html', {
            'lov': None,
            'parent_lovs': LOV.objects.all(),
            'initial': initial_data,
            'copy_mode': bool(copy_from_id)
        })

    elif pk:
        lov = get_object_or_404(LOV, pk=pk)
        if request.method == 'POST':
            parent_value = request.POST.get('parent_value')
            parent_value_id = int(parent_value) if parent_value and parent_value.isdigit() else None
            lov.type = request.POST.get('type')
            lov.lic = request.POST.get('lic')
            lov.language = request.POST.get('language')
            lov.display_name = request.POST.get('display_name')
            lov.parent_value_id = parent_value_id
            lov.description = request.POST.get('description')
            lov.order = int(request.POST.get('order') or 0)
            lov.is_active = request.POST.get('is_active') == 'on'
            lov.save()
            return redirect('lov_management')

        return render(request, 'lov_detail.html', {
            'lov': lov,
            'parent_lovs': LOV.objects.all(),
            'initial': {}
        })

    lovs = LOV.objects.all()
    # Handle query
    q_id = request.GET.get('id', '').strip()
    q_type = request.GET.get('type', '').strip()
    q_lic = request.GET.get('lic', '').strip()
    q_display_name = request.GET.get('display_name', '').strip()
    q_language = request.GET.get('language', '').strip()
    q_is_active = request.GET.get('is_active', '').strip()
    search = request.GET.get('search', '').strip()
    if q_id:
        if '*' in q_id:
            lovs = lovs.filter(id__icontains=q_id.replace('*', ''))
        else:
            lovs = lovs.filter(id=q_id)
    if q_type:
        if '*' in q_type:
            lovs = lovs.filter(type__icontains=q_type.replace('*', ''))
        else:
            lovs = lovs.filter(type=q_type)
    if q_lic:
        if '*' in q_lic:
            lovs = lovs.filter(lic__icontains=q_lic.replace('*', ''))
        else:
            lovs = lovs.filter(lic=q_lic)
    if q_display_name:
        if '*' in q_display_name:
            lovs = lovs.filter(display_name__icontains=q_display_name.replace('*', ''))
        else:
            lovs = lovs.filter(display_name=q_display_name)
    if q_language:
        lovs = lovs.filter(language=q_language)
    if q_is_active:
        lovs = lovs.filter(is_active=q_is_active == '1')
    if search:
        from django.db.models import Q
        lovs = lovs.filter(Q(type__icontains=search) | Q(display_name__icontains=search) | Q(lic__icontains=search))
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = lovs.count()
    start = (page - 1) * per_page
    end = start + per_page
    lovs_page = lovs[start:end]
    total_pages = (total + per_page - 1) // per_page
    pages = list(range(max(1, page - 2), min(total_pages + 1, page + 3)))

    return render(request, 'lov_list.html', {
        'lovs': lovs_page,
        'page': page,
        'total_pages': total_pages,
        'pages': pages,
        'total': total,
        'has_query': bool(request.GET),
        'search': search,
        'types': LOV.objects.values_list('type', flat=True).distinct(),
        'parent_lovs': LOV.objects.all()
    })


def copy_lov(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        if ids:
            try:
                lov = LOV.objects.get(id=ids[0])  # Copy the first selected
                from django.utils import timezone
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                new_lic = f"{lov.lic}_copy_{timestamp}"
                new_display_name = f"{lov.display_name} (Copy {timestamp})"
                params = {
                    'type': lov.type,
                    'lic': new_lic,
                    'display_name': new_display_name,
                    'language': lov.language,
                    'parent_value': lov.parent_value_id or '',
                    'description': lov.description,
                    'is_active': 'on' if lov.is_active else ''
                }
                from urllib.parse import urlencode
                from django.urls import reverse
                query_string = urlencode(params)
                return redirect(f'{reverse("lov_management_detail", args=["new"])}?{query_string}')
            except LOV.DoesNotExist:
                pass
    return redirect('lov_management')


def delete_lov(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        ids = [int(id) for id in ids if id.isdigit()]
        LOV.objects.filter(id__in=ids).delete()
        return redirect('lov_management')
    return redirect('lov_management')


# =====================================================
# AD MANAGEMENT (UNCHANGED)
# =====================================================

def ad_management(request, pk=None):
    if pk == 'new':
        if request.method == 'POST':
            ad = Ad(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                location=request.POST.get('location'),
                city=request.POST.get('city'),
                category=request.POST.get('category'),
                phone=request.POST.get('phone'),
                whatsapp=request.POST.get('whatsapp') or '',
                status=request.POST.get('status', 'PENDING'),
            )
            ad.save()

            images = request.FILES.getlist('images')
            ad.images = [
                f'/media/{default_storage.save(f"ads/{ad.id}/{img.name}", img)}'
                for img in images[:5]
            ]
            ad.save()
            return redirect('ad_management')

        return render(request, 'ad_detail.html', {'ad': None})

    elif pk:
        ad = get_object_or_404(Ad, pk=pk)
        if request.method == 'POST':
            for field in ['title', 'description', 'location', 'city',
                          'category', 'phone', 'status']:
                setattr(ad, field, request.POST.get(field))
            ad.whatsapp = request.POST.get('whatsapp') or ''
            ad.save()
            return redirect('ad_management')

        return render(request, 'ad_detail.html', {'ad': ad})

    ads = Ad.objects.all().order_by('-created_at')
    return render(request, 'ad_list.html', {'ads': ads})


@api_view(['POST'])
def delete_ad(request):
    Ad.objects.filter(id__in=request.data.get('ids', [])).delete()
    return Response({'success': True})


# =====================================================
# BLOCKED USER MANAGEMENT
# =====================================================

def blockeduser_management(request, pk=None):
    if pk == 'new':
        if request.method == 'POST':
            blockeduser = BlockedUser(
                phone=request.POST.get('phone'),
                status=request.POST.get('status', 'BLOCKED'),
                reason=request.POST.get('reason', ''),
            )
            blockeduser.save()
            return redirect('blockeduser_management')
        return render(request, 'blockeduser_detail.html', {'blockeduser': None})
    elif pk:
        blockeduser = get_object_or_404(BlockedUser, pk=pk)
        if request.method == 'POST':
            blockeduser.phone = request.POST.get('phone')
            blockeduser.status = request.POST.get('status')
            blockeduser.reason = request.POST.get('reason', '')
            blockeduser.save()
            return redirect('blockeduser_management')
        # Get blocked ads for this phone
        blocked_ads = Ad.objects.filter(phone=blockeduser.phone, status='BLOCKED')
        return render(request, 'blockeduser_detail.html', {'blockeduser': blockeduser, 'blocked_ads': blocked_ads})
    blockedusers = BlockedUser.objects.all().order_by('-blocked_at')
    if request.GET.get('phone'):
        blockedusers = blockedusers.filter(phone__icontains=request.GET['phone'])
    if request.GET.get('status'):
        blockedusers = blockedusers.filter(status=request.GET['status'])
    if request.GET.get('reason'):
        blockedusers = blockedusers.filter(reason__icontains=request.GET['reason'])
    return render(request, 'blockeduser_list.html', {'blockedusers': blockedusers})


@api_view(['POST'])
def delete_blockeduser(request):
    BlockedUser.objects.filter(id__in=request.data.get('ids', [])).delete()
    return Response({'success': True})


# =====================================================
# CONTENT MODERATION (FIXED + STRONG)
# =====================================================

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKC', text)

    # Replace common obfuscation characters
    text = re.sub(r'[@$!#%^&*_+=\-]', ' ', text)

    # Keep unicode letters & numbers
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)

    # Collapse repeated characters (fuuuuuck → fuuck)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def word_to_regex(word):
    """
    Converts a word into a flexible regex that matches:
    - spaced letters
    - obfuscated text
    - Tamil + English
    """
    word = normalize_text(word)

    pattern = []
    for ch in word:
        if ch.isspace():
            pattern.append(r'\s+')
        else:
            pattern.append(re.escape(ch) + r'\s*')

    return r'\b' + ''.join(pattern) + r'\b'


def check_rule_based(text):
    normalized = normalize_text(text)
    print(f"Normalized text: {normalized}")

    blocklist = {}
    lovs = LOV.objects.filter(type='BLOCKLIST', is_active=True)

    for lov in lovs:
        category = lov.lic.upper()
        words = [w.strip() for w in re.split(r'[,\n]', lov.description) if w.strip()]
        blocklist.setdefault(category, []).extend(words)

    for category, words in blocklist.items():
        for word in words:
            try:
                # REGEX-based categories
                if category.endswith('_REGEX'):
                    if re.search(word, normalized, re.IGNORECASE):
                        return {
                            'status': 'BLOCKED',
                            'reason': 'RULE_BASED',
                            'category': category.replace('_REGEX', ''),
                            'matched_word': word
                        }
                else:
                    # Exact / escaped match
                    if re.search(r'\b' + re.escape(word) + r'\b', normalized, re.IGNORECASE):
                        return {
                            'status': 'BLOCKED',
                            'reason': 'RULE_BASED',
                            'category': category,
                            'matched_word': word
                        }
            except re.error:
                continue

    return None


def classify_llm(text):
    # Placeholder for Ollama / LLM later
    return 'NORMAL'


def check_objectionable(text):
    rule_result = check_rule_based(text)
    if rule_result:
        return rule_result

    llm_label = classify_llm(text)
    return {
        'status': 'ALLOWED',
        'reason': 'LLM',
        'category': llm_label
    }


def admin_dashboard(request):
    """
    Admin dashboard showing statistics and management links
    """
    from django.db.models import Count
    
    total_ads = Ad.objects.count()
    live_ads = Ad.objects.filter(status='LIVE').count()
    review_ads = Ad.objects.filter(status='REVIEW').count()
    blocked_ads = Ad.objects.filter(status='BLOCKED').count()
    
    total_lovs = LOV.objects.count()
    active_lovs = LOV.objects.filter(is_active=True).count()
    
    total_blocked_users = BlockedUser.objects.count()
    active_blocked_users = BlockedUser.objects.filter(status='BLOCKED').count()
    
    ads_by_category = Ad.objects.values('category').annotate(count=Count('id')).order_by('-count')
    ads_by_city = Ad.objects.values('city').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'total_ads': total_ads,
        'live_ads': live_ads,
        'review_ads': review_ads,
        'blocked_ads': blocked_ads,
        'total_lovs': total_lovs,
        'active_lovs': active_lovs,
        'total_blocked_users': total_blocked_users,
        'active_blocked_users': active_blocked_users,
        'ads_by_category': ads_by_category[:10],
        'ads_by_city': ads_by_city[:10],
    }
    
    return render(request, 'admin_dashboard.html', context)


def verify_content(request):
    message = None
    text = ''

    if request.method == 'POST':
        text = request.POST.get('text', '')
        result = check_objectionable(text)

        if result['status'] == 'BLOCKED':
            message = f"Blocked ({result['category']}): {result['matched_word']}"
        else:
            message = "Allowed"

    return render(request, 'verify.html', {
        'message': message,
        'text': text
    })


@api_view(['POST'])
def import_lov(request):
    """
    Import LOV records from CSV data
    Expected CSV format: type, lic, display_name, language, description, order, is_active
    (Column names are case-insensitive and order-independent)
    """
    import csv
    from io import StringIO
    
    csv_data = request.data.get('csv_data', '')
    
    if not csv_data:
        return Response({'success': False, 'error': 'No CSV data provided'}, status=400)
    
    try:
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        # Normalize column names to lowercase for flexibility
        if reader.fieldnames:
            reader.fieldnames = [field.lower().strip() for field in reader.fieldnames]
        
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Normalize row keys to lowercase
                row = {k.lower().strip(): v for k, v in row.items()}
                
                type_val = row.get('type', '').strip()
                order = row.get('order', '').strip()
                description = row.get('description', '').strip()
                lic = row.get('lic', '').strip()
                language = row.get('language', '').strip()
                display_name = row.get('display_name', '').strip()
                is_active = row.get('is_active', 'false').lower() == 'true'
                
                if not all([type_val, lic, display_name, language]):
                    error_count += 1
                    errors.append(f"Row {row_num}: Missing required fields (type, lic, display_name, language)")
                    continue
                
                # Upsert: use update_or_create for idempotent behavior
                lov, created = LOV.objects.update_or_create(
                    type=type_val,
                    lic=lic,
                    display_name=display_name,
                    language=language,
                    is_active=is_active,
                    defaults={
                        'order': int(order) if order else 0,
                        'description': description,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        return Response({
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'error_details': errors[:10]
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)