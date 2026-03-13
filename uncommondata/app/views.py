from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse, FileResponse
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from django.conf import settings
from .models import Upload, Institution, ReportingYear, Facts, UserProfile
import subprocess
import os
import hashlib
import re

# create views here
# HW 1 - 3?
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

########## HW 4 ##########
def new_user(request):
    "redirect to URL where new user can submit new user creation form"
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render(request, 'app/new.html')    

@csrf_exempt
def create_user(request):
    "fucntion to create a new user account, all proper info submitted"
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=400)

    username = request.POST.get("user_name")
    password = request.POST.get("password")
    email = request.POST.get("email")
    is_curator_true = True if str(request.POST.get("is_curator")).lower() in ["true", "1"] else False

    if not username or not password or not email:
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
    
    UserProfile.objects.get_or_create(user=user, defaults={"is_curator": is_curator_true})
        
    login(request, user)

    return HttpResponse("success", status = 201)

######################### HW5 ###################################

def uploads(request):
    
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    if request.user.userprofile.is_curator:
        return HttpResponse(status=403, content="Forbidden if logged in as curator")
    
    uploads = Upload.objects.filter(uploader=request.user)
    return render(request, "app/uploads.html", {"uploads": uploads})

def dump_uploads(request):
    
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    try:
        profile = request.user.userprofile
        is_curator = profile.is_curator
    except UserProfile.DoesNotExist:
        is_curator = False
    
    # Curators see all uploads, regular users see only their own
    if is_curator:
        uploads = Upload.objects.all()
    else:
        uploads = Upload.objects.filter(uploader=request.user)
    
    data = []

    for u in uploads:
        data.append({
            "institution": u.institution.name,
            "reporting_year": u.reporting_year.year,
            "hash": u.hash,
            "filename": u.file.name
        })

    return JsonResponse({"uploads": data})

def dump_data(request):
    
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    if not request.user.userprofile.is_curator:
        return HttpResponse(status=403)

    facts = Facts.objects.all()

    data = {}
    
    for fact in facts:
        data[str(fact.id)] = {
            "institution": fact.institution.name,
            "year": fact.reporting_year.year,
            "key": fact.key,
            "value": fact.value,
            "updated_at": fact.updated_at,
            "updated_by": fact.updated_by.username if fact.updated_by else None,
    }

    return JsonResponse(data)

def knock_knock(request):
    "uses AI to generate a joke"
    topic = request.GET.get("topic", "banana")[:20]

    try:
        client = OpenAI(api_key= settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages= [{"role": "user",
                        "content": f"Tell a short knock knock joke about {topic}. Make sure the word '{topic}' appears in the joke."
                        }],
            timeout= 30,
        )
        joke = response.choices[0].message.content.strip()
    except Exception as e:
        print("OPENAI ERROR:", e)
        joke = f"Knock knock. Who's there? {topic}. {topic} who? {topic} jokes are the best!"
    return HttpResponse(joke)

##### HW 6 #####
"""def frontend(request):
    "end point that extracts data from specified file
    and submits to table of facts"
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    if request.user.userprofile.is_curator:
        return HttpResponse(status=403, content="Forbidden if logged in as curator")
    
    sha256 = hashlib.sha256()
    for chunk in file.chunks():
        sha256.update(chunk)
        
    filehash = sha256.hexdigest()
    upload = Upload.objects.create(
    uploader=request.user,
    institution= institution,
    reporting_year= reporting_year,
    file= file,
    hash= filehash
)"""
    
############# HW 7 ##################
def pdf_to_text(filename):
    """
    Run the shell command `pdftotext` on `filename`,
    producing `filename + ".txt"` and returning that name.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Input file not found: {filename}")

    output_filename = filename + ".txt"

    try:
        subprocess.run(
            ["pdftotext", "-layout", filename,
            output_filename], check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pdftotext failed with exit code {e.returncode}") from e

    return output_filename

@csrf_exempt
def api_upload(request):
    """..."""
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=400)
    
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    try:
        if request.user.userprofile.is_curator:
            return HttpResponse(status=403, content="Forbidden if logged in as curator")
    except (UserProfile.DoesNotExist, AttributeError):
        pass
    
    if "file" not in request.FILES:
        return JsonResponse({"error": "missing file"}, status=400)
    
    file = request.FILES["file"]
    
    file_bytes = file.read()
    filehash = hashlib.sha256(file_bytes).hexdigest()
    filename = file.name
    file.seek(0)

    inst_match = re.search(r"(UIC|EIU)", filename)
    institution_name = inst_match.group(1) if inst_match else "UNKNOWN"
    
    year_match = re.search(r"(20\d{2})", filename)
    year_value = year_match.group(1) if year_match else 0000
    
    
    institution, _ = Institution.objects.get_or_create(name=institution_name)
    reporting_year, _ = ReportingYear.objects.get_or_create(year=year_value)
    
    existing_upload = Upload.objects.filter(hash=filehash).first()
    if existing_upload:
        return JsonResponse({
            "id": existing_upload.hash,
            "note": "Using existing upload"
        }, status=200)
    
    upload = Upload(uploader=request.user,
                                   institution=institution,
                                   reporting_year=reporting_year,
                                   file=file,
                                   hash=filehash)
    
    upload.file.save(filename, file, save=True)
    
    return JsonResponse({"id": upload.hash}, status=201)

def api_download(request, ID):
    """1. lookup the uploaded file using the ID
    2. return the file so the user can download it"""
    
    try:
        upload = get_object_or_404(Upload, hash=ID)
    except Upload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    
    
    if not request.user.is_authenticated:
        return HttpResponse(status=401, content="Authentication required")
    
    is_curator = getattr(request.user.userprofile, 'is_curator', False)
    if not (is_curator or upload.uploader == request.user):
        return HttpResponse(status=403, content="Forbidden if logged in as curator")
    
    response = FileResponse(
            upload.file.open('rb'),
            as_attachment=True,
            filename=os.path.basename(upload.file.name)
        )
    return response
    

def api_process(request, ID):
    """1. lookup the uploaded file using the ID
    2. return the file so the user can download it"""
    
    upload = get_object_or_404(Upload, hash=ID)
    
    pdf_path = upload.file.path

    txt_path = pdf_to_text(pdf_path)
    
    with open(txt_path, "r") as f:
        text = f.read()

    extracted_data = {"institution": upload.institution.name,
                      "reporting_year": upload.reporting_year.year,
                      "text_length": len(text)}
    return JsonResponse(extracted_data)
