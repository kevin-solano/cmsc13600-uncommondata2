from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
# Create your views here.

def hello_xyz(request):
    return render(request, 'app/hello.html')

def new_user(request):
    context = {}
    if request.user.is_authenticated:
        context['user_name'] = request.user.email
    return render(request, 'app/new_user.html', context)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Check if user exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)
            return JsonResponse({'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def current_time(request):
    return HttpResponse(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def sum_numbers(request):
    return render(request, 'app/sum.html')