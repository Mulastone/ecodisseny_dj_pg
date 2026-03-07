from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Poblacio


@staff_member_required
def poblacions_by_parroquia(request):
    parroquia_id = request.GET.get("parroquia_id")
    if not parroquia_id:
        return JsonResponse({"results": []})

    try:
        poblacions = Poblacio.objects.filter(parroquia_id=int(parroquia_id)).order_by("poblacio")
    except (TypeError, ValueError):
        return JsonResponse({"results": []})

    return JsonResponse(
        {
            "results": [
                {"id": p.id, "text": p.poblacio}
                for p in poblacions
            ]
        }
    )
