from django.http import HttpResponse, JsonResponse
from . import Main_functions
from django.views.decorators.http import require_GET
import json

def getAnswer(request):
    return JsonResponse({"answer" : "Bright"})
  

def get_base64_image(request):
    # Generate the base64 image
    Interpolater = Main_functions.Interpolate()
    data = [[-11.607440, 34.295660,7328],[-13.036810, 33.481230,4356],[-13.354770, 33.918180,7362], [-15.175940, 35.297280,4726], [-9.703080, 33.274658,2642]]
    image = Interpolater.interpolate(data=data,shapefile_path=r'C:\Users\blown\OneDrive\Desktop\Malawi Data\mw_districts_pop_2008_new.shp')   
    # Return the image as a JSON response
    return JsonResponse({'image': image})

@require_GET
def krigging(request):
    data = request.GET.get("data")    
    data = json.loads(data)
    Interpolator = Main_functions.Interpolate()
    result = Interpolator.interpolate(data=data['array'],shapefile_path=r'C:\Users\blown\OneDrive\Desktop\Malawi Data\mw_districts_pop_2008_new.shp',report=data['report'],title=data['title'],model=data['model'],bins = data["neighbors"])  
    content = result["array"]
    content.append({"answer" : result["report"],"type": "report"})
    # print(result)  
    return JsonResponse(content, safe=False)
