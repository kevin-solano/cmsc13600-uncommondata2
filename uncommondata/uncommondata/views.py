from django.http import HttpResponse
from datetime import datetime
from zoneinfo import ZoneInfo

def dummypage(request):
     if request.method == "GET": 
         return HttpResponse("No content here, sorry!")

def app_time(request):
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    return HttpResponse(now_cst.strftime("%H:%M"))
    
def app_sum(request):
    n1 = request.GET.get("n1", "0")
    n2 = request.GET.get("n2", "0")
    
    try: 
        result = float(n1) + float(n2)
    except ValueError:
        return HttpResponse("Invalid input", status = 400)
    
    if result.is_integer():
        return HttpResponse(str(int(result)))

    return HttpResponse(str(result))