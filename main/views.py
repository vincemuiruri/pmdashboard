from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from . models import Project, Contractor


# Home page view
def index(request):
    return render(request, 'index.html', {})

def add_new_form(request):
    return render(request, 'addnewform.html', {})

def contrators_form(request):
    return render(request, 'contractors.html', {})
@login_required(login_url="/auth/login")
def dashboard_view(request):
    user = request.user
    return render(request, 'dashboard.html', {"user": user})

def table_data_view(request):
    return render(request, 'tables-data.html', {})

def users_profile_view(request):
    return render(request, 'users-profile.html', {})

@csrf_exempt
def login_request(request):
    if request.method == "POST":
        try:
            raw_body = request.body.decode('utf-8').strip()
            if not raw_body:
                return JsonResponse({'status': 400, 'message': 'Empty request body'}, status=400)

            body = json.loads(raw_body)
            username = body.get('userID')
            password = body.get('password')

            if not all([username, password]):
                return JsonResponse({'status': 400, 'message': 'Invalid request'}, status=400)

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({'status': 200, 'message': 'Logged in successfully'})
            else:
                return JsonResponse({'status': 401, 'message': 'Invalid credentials'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 400, 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 500, 'message': f'Error parsing request: {e}'}, status=500)

    return render(request, "pages-login.html", {})

def signup(request):
    if request.method == "POST":
        try:
            username = request.POST.get('userID')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            project_id = request.POST.get('project_id')
            project_name = request.POST.get('project_name')
            password = request.POST.get('password')
            deadline = request.POST.get('deadline')

            if not all([username, first_name, last_name, project_id, project_name, deadline, password]):
                return JsonResponse({'status': 400, 'message': 'All fields required'}, status=400)

            user = User.objects.create_user(
                username=username, 
                first_name=first_name, 
                last_name=last_name,
                password=password
            )
            user.save()
            
            new_project = Project.objects.create(
                projectID=project_id,
                name=project_name,
                deadline=deadline
            )

            new_project.save()

            new_contractor = Contractor.objects.create(
                user=user,
                userID=username,
                project=new_project,
                first_name=first_name,
                last_name=last_name
            )

            new_contractor.save()
            return JsonResponse({'status': 201, 'message': 'User created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'status': 400, 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 500, 'message': f'Error parsing request: {e}'}, status=500)

    return render(request, "pages-register.html", {})

@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({'status': 200, 'message': 'Logged out successfully'})
