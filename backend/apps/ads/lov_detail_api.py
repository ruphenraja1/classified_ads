from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LOV

@api_view(['GET','PUT','DELETE'])
def lov_detail_api(request, pk):
    try:
        lov = LOV.objects.get(pk=pk)
    except LOV.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        data = {
            'id': lov.id,
            'type': lov.type,
            'lic': lov.lic,
            'language': lov.language,
            'display_name': lov.display_name,
            'parent_value_id': lov.parent_value_id,
            'description': lov.description,
            'order': lov.order,
            'is_active': lov.is_active,
        }
        return Response(data)
    elif request.method == 'PUT':
        updatable = ['type','lic','language','display_name','parent_value_id','description','order','is_active']
        for k in updatable:
            if k in request.data:
                setattr(lov, k, request.data[k])
        lov.save()
        return Response({'status': 'updated'})
    else:
        lov.delete()
        return Response({'status': 'deleted'})
