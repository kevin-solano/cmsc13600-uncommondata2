from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import datetime
from zoneinfo import ZoneInfo
from django.conf import settings
from openai import OpenAI
from .models import Upload, Institution, ReportingYear, Facts, UserProfile
# Create your views here.

def index(request):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return render(request, 'app/index.html', {'Current Time': time_now})

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
        return HttpResponse("Invalid input")
    
    if result.is_integer():
        return HttpResponse(str(int(result)))

    return HttpResponse(str(result))

def new_user(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render(request, 'app/new.html')    

def app_time(request):
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    return HttpResponse(now_cst.strftime("%H:%M"))

@csrf_exempt
def create_user(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(["POST required"])

    username = request.POST.get("user_name")
    password = request.POST.get("password")
    email = request.POST.get("email")
    is_curator_true = request.POST.get("is_curator")

    if not username or not password or not email or is_curator_true is None:
        return HttpResponseBadRequest("missing fields")
    # duplicate email
    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"{email} email already in use")
    # duplicate user
    if User.objects.filter(username=username).exists():
        return HttpResponseBadRequest(f"{username} username already in use")

    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password)
    
    login(request, user)

    return HttpResponse("success", status = 201)

##### HW5 ####

@login_required
def uploads_page(request):
    uploads = Upload.objects.filter(uploader=request.user)
    return render(request, "app/uploads.html", {"uploads": uploads})

#api upload
@csrf_exempt
def api_upload(request):
    if request.method != "POST":
        return HttpResponse("error: POST required", status=400)

    institution_name = request.POST.get("institution")
    year_value = request.POST.get("year")
    file = request.FILES.get("file")
    
    if not institution_name or not year_value or not file:
        return HttpResponse("error: Missing required fields", status=400)
    
    institution, _ = Institution.objects.get_or_create(name=institution_name)
    reporting_year, _ = ReportingYear.objects.get_or_create(year=year_value)

    upload = Upload.objects.create(uploader=request.user,
                                   institution=institution,
                                   reporting_year=reporting_year,
                                   file=file,
    )
    return JsonResponse({
        "success": True,
        "upload_id": upload.id
    })

def dump_uploads(request):
    try:
        profile = request.user.userprofile
        is_curator = profile.is_curator
        
    except UserProfile.DoesNotExist:
        is_curator = False
    
    if is_curator:
        uploads = Upload.objects.all()
    
    else:
        uploads = Upload.objects.filter(uploader=request.user)
    
    data = {}

    for upload in uploads:
        data[str(upload.id)] = {
            "user": upload.uploader.username,
            "institution": upload.institution.name,
            "year": upload.reporting_year.year,
            "file": upload.file.name.split("/")[-1] if upload.file else None,
        }

    return JsonResponse(data)

def dump_data(request):
    
    if UserProfile.DoesNotExist:
        return HttpResponseForbidden("401 Forbidden")
    try:
        profile = request.user.userprofile
        if not profile.is_curator:
            return HttpResponseForbidden("403 Forbidden")
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("401 Forbidden")

    facts = Facts.objects.all()

    data = {}
    
    for fact in facts:
        data[str(fact.id)] = {"institution": fact.institution.name,
                              "year": fact.reporting_year.year,
                              "key": fact.key,
                              "value": fact.value,
                              "updated_at": fact.updated_at,
                              "updated_by": fact.updated_by.username if fact.updated_by else None,
    }

    return JsonResponse(data)

def knock_knock(request):
    topic = request.GET.get("topic", "banana")[:20]

    try:
        client = OpenAI(api_key= settings.OPENAI_API_KEY)

        response = client.chat.completions.create(model="gpt-4o-mini",
                                                  messages= [{
                                                      "role": "user",
                                                      "content": f"Tell a short knock knock joke about {topic}."
                                                      }],
                                                  timeout=30,)
        joke = response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", e)
        joke = ("Knock, knock. Who’s there? Lettuce. Lettuce who? Lettuce in, it's cold out here!")

    return JsonResponse({"joke": joke})