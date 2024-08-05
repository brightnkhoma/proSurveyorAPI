from django.http import HttpResponse, JsonResponse
from . import Main_functions
from django.views.decorators.http import require_GET
import json


@require_GET
def krigging(request):
    try:
        data = request.GET.get("data")    
        data = json.loads(data)
        Interpolator = Main_functions.Interpolate()    
        result = Interpolator.interpolate(data=data['array'],shapefile_path=r'https://firebasestorage.googleapis.com/v0/b/wews-7fc10.appspot.com/o/files%2Fblownbrian%40gmail.com%2FstudyArea.zip?alt=media&token=f0b4865d-9ef1-4e5f-b12f-7972a4271aa4',report=data['report'],title=data['title'],model=data['model'],bins = 2)  
        content = result["array"]
        content.append({"answer" : result["report"],"type": "report"})    
        return JsonResponse(content, safe=False)
    except Exception as e :
        return JsonResponse([{"answer" : "something went wrong","type" : "report"}],safe=False)
        


@require_GET
def getContent(request):
    data = request.GET.get("data")
    data = json.loads(data)
    print(data["details"])
    prompt = data["details"]
    Interpolator = Main_functions.Interpolate()
    content = Interpolator.getContent(details = f"{prompt}")
    return JsonResponse([content], safe=False)
