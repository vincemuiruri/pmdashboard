from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.contrib.auth.models import User


# Create your views here.
def index(request):
    return render(request, 'index.html', {})

@csrf_exempt
def login_request(request):
    if request.method == "POST":
        try:
            raw_body = request.body.decode('utf-8')
            body = json.loads(raw_body)
            username = body['userID']
            password = body['password']

            if not all in ([username, password]):
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid request'
                })
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                return JsonResponse({
                    'status': 200,
                    'message': 'Logged in successfully'
                })
            else:
                return JsonResponse({
                    "message": "Invalid credentials",
                    "status":401
                })
        except Exception as e:
            return JsonResponse({
                'status': 500,
                'message': f'Error parsing request: {e}'
            })

    return JsonResponse({
        'status': 400,
        'message': 'Invalid request'
    })

@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            raw_body = request.body.decode('utf-8')
            body = json.loads(raw_body)
            username = body['userID']
            first_name = body['first_name']
            last_name = body['last_name']
            project_id = body['project_id']
            project_name = body['project_name']
            password = body['password']

            if not all in ([username, first_name, last_name, project_id, project_name, password]):
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid request'
                })

            user = User.objects.create_user(
                username=username, 
                first_name=first_name, 
                last_name=last_name,
                password=password)

            user.save()
            
        except Exception as e:
            return JsonResponse({
                'status': 500,
                'message': f'Error parsing request: {e}'
            })
    return JsonResponse({
        'status': 400,
        'message': 'Invalid request'
    })

@csrf_exempt
@login_required
def logout_request(request):
    return render(request, 'logout.html', {})
