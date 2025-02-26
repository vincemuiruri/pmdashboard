from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from . models import Project, Contractor, ProjectProgress, ProjectPhase
from . import utils


# Home page view
def index(request):
    return render(request, 'index.html', {})

@login_required(login_url="/auth/login")
def add_new_form(request):
    user = request.user
    is_admin = utils.is_admin(user)
    
    if not is_admin:
        return HttpResponseForbidden("You are not authorized to view this page")
    
    if request.method == "POST":
        try:
            project_id = request.POST.get('project_id')
            phase_name = request.POST.get('phase_name')
            phase_number = request.POST.get('phase_number')

            if not all([project_id, phase_name, phase_number]):
                return JsonResponse({'status': 400, 'message': 'All fields required'}, status=400)
            
            project = Project.objects.get(projectID=project_id)

            if not project:
                return JsonResponse({'status': 404, 'message': 'Project not found'}, status=404)
            
            new_project_phase = ProjectPhase.objects.create(
                project=project,
                phase_number=phase_number,
                name=phase_name
            )

            new_project_phase.save()

            return JsonResponse({'status': 201, 'message': 'Project phase added successfully'}, status=201)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return JsonResponse({'status': 400, 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 500, 'message': f'Error parsing request: {e}'}, status=500)

    return render(request, 'addnewform.html', {})

@login_required(login_url="/auth/login")
def contrators_form(request):
    user = request.user
    is_contractor = utils.is_contrator(user)

    if not is_contractor:
        return HttpResponseForbidden("You are not authorized to view this page")
    
    if request.method == "POST":
        try:
            project_id = request.POST.get('project_id')
            phase_number = request.POST.get('phase_number')
            comment = request.POST.get('comment')
            image = request.FILES.get('image')  # Get uploaded image

            if not all([project_id, phase_number, comment]):
                return JsonResponse({'status': 400, 'message': 'All fields required'}, status=400)
            
            project = Project.objects.get(projectID=project_id)

            if not project:
                return JsonResponse({'status': 404, 'message': 'Project not found'}, status=404)
            
            phase_name = ProjectPhase.objects.get(project=project, phase_number=phase_number)
            
            new_project_progress = ProjectProgress.objects.create(
                project=project,
                phase=phase_name,
                comment=comment,
                image=image
            )

            new_project_progress.save()
            return JsonResponse({'status': 201, 'message': 'Project progress added successfully'}, status=201)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return JsonResponse({'status': 400, 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 500, 'message': f'Error parsing request: {e}'}, status=500)
    
    return render(request, 'contractors.html', {})

@login_required(login_url="/auth/login")
def dashboard_view(request):
    user = request.user
    if utils.is_admin(user):
        return render(request, 'dashboard.html', {"user": user})
    
    return HttpResponseForbidden("You are not authorized to view this page. Only for project managers")

def table_data_view(request):
    return render(request, 'tables-data.html', {})

@login_required(login_url="/auth/login")
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

            utils.add_user_to_group("contractor")
            
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
