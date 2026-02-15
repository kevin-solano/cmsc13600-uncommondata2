from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from datetime import datetime
from zoneinfo import ZoneInfo
# Create your views here.

def hello_xyz(request):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return render(request, 'app/index.html', {'Current Time': time_now})

def new_user(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render(request, 'app/new.html')    

def app_time(request):
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    return HttpResponse(now_cst.strftime("%H:%M"))
    
def app_sum(request):
    n1 = request.GET.get("n1", "0")
    n2 = request.GET.get("n2", "0")
    
    try: 
        result = float(n1) + float(n2)
    except ValueError:
        return HttpResponse("Invalid input")
    
    if result.is_integer():
        return HttpResponse(str(int(result)))

    return HttpResponse(str(result))

@csrf_exempt
def create_user(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(["POST required"])

    username = request.POST.get("user_name")
    password = request.POST.get("password")
    email = request.POST.get("email")
    is_curator_true = request.POST.get('is_curator')

    if not username or not password or not email:
        return HttpResponseBadRequest("missing fields")
    # duplicate email
    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"{email} email already in use")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    login(request, user)

    return HttpResponse("success", status = 201)

# endpoints for testing
def uploads(request):
    """Returns 200 for normal users, 403 for curators"""
    # Check if user is a curator (you'll need to define what makes a curator)
    # For now, let's assume users with 'curator' in their email are curators
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized")
    if request.user.is_curator:
        return HttpResponse("Forbidden")

    # 3️⃣ Otherwise (harvester) → show page
    return render(request, "uploads.html")

def dump_uploads(request):
    """Returns JSON data about uploads"""
    if not request.user.is_authenticated:
        return HttpResponse('Not authenticated')
    
    # Mock data for now
    data = {
        'uploads': [
            {'id': 1, 'filename': 'test1.txt', 'user': request.user.email},
            {'id': 2, 'filename': 'test2.txt', 'user': request.user.email},
        ]
    }
    return HttpResponse(data)