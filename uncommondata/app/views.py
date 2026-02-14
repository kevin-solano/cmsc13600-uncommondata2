from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.models import User
#from django.contrib.auth import login_required, login, authenticate
import json
from django.http import HttpResponseNotAllowed

from datetime import datetime
# Create your views here.

def hello_xyz(request):
    return render(request, 'app/hello.html')

def new_user(request):
    if request.method == 'POST':
        return HttpResponseNotAllowed(['GET'])
    context = {'user_name': request.user.email if request.user.is_authenticated else None}
    return render(request, 'app/new_user.html', context)

@csrf_exempt
def create_user(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
            # Handle both JSON and form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        data = request.POST
        
    email = request.POST.get('email')
    password = request.POST.get('password')
    user_name = data.get('user_name')
            
    if not email or not password or not user_name:
        return JsonResponse({'error': 'Missing requireed fields'}, status=400)
            # Check if user exists
    if User.objects.filter(username=user_name).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
            
    user = User.objects.create_user(username=user_name,
                                    email=email,
                                    password=password)
    return JsonResponse({'message': 'User created successfully', 'id': user.id}, status=201)


def current_time(request):
    return HttpResponse(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def sum_numbers(request):
    return render(request, 'app/sum.html')
