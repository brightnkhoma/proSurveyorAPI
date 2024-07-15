from django.http import HttpResponse, JsonResponse
from . import Main_functions
from django.views.decorators.http import require_GET
import json


@require_GET
def krigging(request):
    data = request.GET.get("data")    
    data = json.loads(data)
    Interpolator = Main_functions.Interpolate()
    print(data)
    result = Interpolator.interpolate(data=data['array'],shapefile_path=r'C:\Users\blown\OneDrive\Desktop\Malawi Data\mw_districts_pop_2008_new.shp',report=data['report'],title=data['title'],model=data['model'],bins = 2)  
    content = result["array"]
    content.append({"answer" : result["report"],"type": "report"})    
    return JsonResponse(content, safe=False)
