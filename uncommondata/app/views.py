from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
        return JsonResponse({"error": "POST required"}, status=405)
    
    data = json.loads(request.body)
    
    email = request.POST.get('email')
    password = request.POST.get('password')
    username = data.get('user_name')
            
    if not username or not password:
        return JsonResponse({'error': 'Missing fields'}, status=400)
            # Check if user exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
            
    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password)
    return JsonResponse({'message': 'User created successfully', 'id': user.id}, status=201)


def current_time(request):
    return HttpResponse(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def sum_numbers(request):
    return render(request, 'app/sum.html')

# New endpoints for the test

@login_required
def uploads(request):
    """Returns 200 for normal users, 403 for curators"""
    # Check if user is a curator (you'll need to define what makes a curator)
    # For now, let's assume users with 'curator' in their email are curators
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if 'curator' in request.user.email.lower():
        return HttpResponseForbidden("Curators cannot access uploads")
    return render(request, 'app/uploads.html')

def dump_uploads(request):
    """Returns JSON data about uploads"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    # Mock data for now
    data = {
        'uploads': [
            {'id': 1, 'filename': 'test1.txt', 'user': request.user.email},
            {'id': 2, 'filename': 'test2.txt', 'user': request.user.email},
        ]
    }
    return JsonResponse(data)

def dump_data(request):
    """Returns data for curators only"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    # Check if user is a curator
    if 'curator' not in request.user.email.lower():
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    # Mock data for curators
    data = {
        'curator_data': [
            {'id': 1, 'value': 'secret1'},
            {'id': 2, 'value': 'secret2'},
        ]
    }
    return JsonResponse(data)

def knock_knock(request):
    """Returns a knock-knock joke"""
    topic = request.GET.get('topic', '')
    
    jokes = {
        'avocado': "Avocado who? Avocado nice day, would you like to go out?",
        'lettuce': "Lettuce who? Lettuce in, it's cold out here!",
        'orange': "Orange who? Orange you glad I didn't say banana?",
    }
    
    if topic and topic in jokes:
        joke = f"Knock knock\nWho's there?\n{topic.capitalize()}\n{topic.capitalize()} who?\n{jokes[topic]}"
    else:
        # Default joke
        joke = "Knock knock\nWho's there?\nOlive\nOlive who?\nOlive you and I miss you!"
    
    return HttpResponse(joke, content_type='text/plain')
