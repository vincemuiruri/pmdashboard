from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from . models import Project, Contractor, ProjectProgress, ProjectPhase
from . import utils
from django.core.paginator import Paginator


# Home page view
def index(request):
    is_admin = False
    user = request.user
    if user.is_authenticated:
        is_admin = utils.is_admin(user)
    return render(request, 'index.html', {"user": user, "is_admin":is_admin})

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
    projects_data = Project.objects.all()

    projects = []

    if projects is not None:
        for project in projects_data:

            projects.append({
                "project_name": project.name,
                "project_id": project.projectID
            })

    return render(request, 'addnewform.html', {"projects": projects})

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


    project = {
        "project_id":"",
        "project_name":""
    }
    phases = []

    try:
        contractor = Contractor.objects.filter(user=user).first()

        if contractor:
            cont_project = contractor.project

            project["project_id"] = cont_project.projectID
            project["project_name"] = cont_project.name

            project_phases = ProjectPhase.objects.filter(project=cont_project).all()

            for phase in project_phases:
                phases.append({
                    "phase_number": phase.phase_number,
                    "phase_name": phase.name
                })
    except Exception as e:
        print(f"Error: {e}")
    return render(request, 'contractors.html', {"project":project, "phases": phases})

@login_required(login_url="/auth/login")
def dashboard_view(request):
    user = request.user

    if not utils.is_admin(user):
        return HttpResponseForbidden("You are not authorized to view this page. Only for project managers")
    if request.method != "GET":
        return HttpResponse("Method not allowed.")
    
    page_number = request.GET.get("page", "1")

    # get all projects then paginate
    project_list = []
    try:
        projects = get_all_projects()

        # Sort projects by "status" in ascending order
        sorted_projects = sorted(projects, key=lambda x: x["status"], reverse=True)
        # Paginate the sorted list
        project_pg = Paginator(sorted_projects, 8 if page_number == "1" else 5)
        project_batch = project_pg.get_page(page_number)
        project_list = project_batch.object_list
    except Exception as e:
        print(f"Error: {e}")

    print(f"Project: {project_list}")
    return render(request, 'dashboard.html', {"user": user, "projects": project_list})
    
    

@login_required(login_url="/auth/login")
def table_data_view(request):
    user = request.user
    is_admin = utils.is_admin(user)

    if not is_admin:
        return HttpResponseForbidden("Not allowed to view this page")

    projects = get_all_projects()

    return render(request, 'tables-data.html', {"projects": projects})

def get_all_projects():
    projects = []

    try:
        project_data = Project.objects.prefetch_related("project_contractor", "project_progress").all()

        for project in project_data:
            
            project_contractor = project.project_contractor.first()
            status = round(compute_project_progress(project), 1)

            projects.append({
                "project_name": project.name,
                "project_id": project.projectID,
                "str_status": project.status,
                "deadline": project.deadline,
                "status": status,
                "contractor": f"{project_contractor.first_name} {project_contractor.last_name}",
                "contractor_id": project_contractor.userID
            })

    except Exception as e:
        print(f"Error: {e}")

    return projects

def compute_project_progress(project):
    try:
        project_phases = project.phases.all()

        project_progress = project.project_progress.select_related("phase").all()

        completed_phases = [
            phase for phase in project_phases 
            if any(phase.phase_number == progress_phase.phase.phase_number for progress_phase in project_progress)
        ]
        
        total_phases = project_phases.count()

        total_completed = len(completed_phases)

        
        return (total_completed / total_phases) * 100
    except Exception as e:
        print(f"Error: {e}")
        return 0
    

@login_required(login_url="/auth/login")
def users_profile_view(request):
    user = request.user

    user_id = request.GET.get("u", None)

    is_user_contractor = utils.is_contrator(user)

    if not(is_user_contractor or user_id):
        return render(request, "404.html", {"message": "User info doesn't exists"})

    contractor = None
    contractor_info = {}
    try:
        if is_user_contractor:
            contractor = user.user_contractor
            user_id = contractor.userID
        
        else:
            contractor = Contractor.objects.select_related("project").filter(userID=user_id).first()

        if not Contractor:
            return render(request, "404.html", {"message": "Contractor information not found."})
        
        is_me = contractor.user == user
        contractor_project = contractor.project

        contractor_info["first_name"] = contractor.first_name
        contractor_info["last_name"] = contractor.last_name
        contractor_info["about"] = contractor.about
        contractor_info["phone_number"] = contractor.phone_number

        project_map = {
            "project_name":  contractor_project.name,
            "status": str(round(compute_project_progress(contractor_project)))
        }
        contractor_info["project"] = project_map

    except Exception as e:
        print(f"Error: {e}")

    print(f"Contractor info: {contractor_info}")
    return render(request, 'users-profile.html', {
        "contractor": contractor_info,
        "is_me": is_me
    })

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
                
                is_admin = utils.is_admin(user)
                redirect_url = "/dashboard" if is_admin else "/project/details"
                return JsonResponse({'status': 200, 'message': 'Logged in successfully', "redirect_url": redirect_url})
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

            utils.add_user_to_group(user,"contractor")
            
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
