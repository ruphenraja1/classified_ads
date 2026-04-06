# backend/api/views.py
from django.http import JsonResponse

def lov(request):
    type_param = request.GET.get('type')
    language = request.GET.get('language')
    return JsonResponse({"message": f"LOV API working for {type_param} in {language}"})