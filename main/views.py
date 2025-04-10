from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from . models import Project, Contractor, ProjectProgress, ProjectPhase
from . import utils
from django.core.paginator import Paginator
from django.db.models.functions import Concat
from django.db.models import Count, Q, F, DateTimeField, ExpressionWrapper, Func, Value, CharField
from django.utils.timezone import localtime
from django.db import IntegrityError
import mimetypes

# Home page view
def index(request):
    is_admin = False
    user = request.user
    if user.is_authenticated:
        is_admin = utils.is_admin(user)

    return render(request, 'index.html', {"user": user, "is_admin":is_admin})

    #return HttpResponse("Homepage")
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
        except IntegrityError as e:
            return JsonResponse({'status': 402, 'message': 'Phase already exists!'}, status=402)
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

    notification_list = []
    status, response = get_notifications()
    if status:
        notification_list = response

    return render(request, 'addnewform.html', {"projects": projects, "user": user, "is_admin": is_admin, "notifications": notification_list})

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
            file = request.FILES.get('file', None)
            image = None
            file_type = "unknown"
            if file:
                mime_type, _ = mimetypes.guess_type(file.name)
                
                if mime_type:
                    if mime_type.startswith('image/'):
                        file_type = "image"
                        image = file
                    elif mime_type == 'application/pdf':
                        file_type = "pdf"
                    else:
                        file_type = "unknown"
                else:
                    file_type = "unknown"

            print(f"Uploaded file is a {file_type}")

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
                image=image,
                file=file if file_type == "pdf" else None
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

            # project_phases = ProjectPhase.objects.filter(project=cont_project).all()
            project_progress = ProjectProgress.objects.select_related("phase").filter(project=cont_project).last()
            if not project_progress:
                next_phase = ProjectPhase.objects.filter(project=cont_project, phase_number=1).first()

            else:
                next_phase_number = project_progress.phase.phase_number + 1
                next_phase = ProjectPhase.objects.filter(project=cont_project, phase_number=next_phase_number).first()

            if next_phase:
                phases.append({
                    "phase_number": next_phase.phase_number,
                    "phase_name": next_phase.name
                })
    except Exception as e:
        print(f"Error: {e}")
    return render(request, 'contractors.html', {"project":project, "phases": phases, "user": user, "is_contractor": is_contractor})

@login_required(login_url="/auth/login")
def dashboard_view(request):
    user = request.user
    is_user_admin = utils.is_admin(user)

    if not is_user_admin:
        return HttpResponseForbidden("You are not authorized to view this page. Only for project managers")
    if request.method != "GET":
        return HttpResponse("Method not allowed.")
    
    page_number = request.GET.get("page", "1")

    # get all projects then paginate
    project_list = []
    project_progress = []
    try:
        projects = get_all_projects()

        # Paginate the sorted list
        project_pg = Paginator(projects, 8 if page_number == "1" else 5)
        project_batch = project_pg.get_page(page_number)
        project_list = project_batch.object_list
        project_progress = [
            progress["status"] for progress in project_list
        ]
    except Exception as e:
        print(f"Error: {e}")

    #print(f"Project: {project_list}")
    notification_list = []
    status, response = get_notifications()
    if status:
        notification_list = response
    return render(request, 'dashboard.html', {
        "user": user, 
        "is_admin": is_user_admin, 
        "projects": project_list,
        "progress_list": project_progress,
        "notifications": notification_list
        })
    
    

@login_required(login_url="/auth/login")
def table_data_view(request):
    user = request.user
    is_admin = utils.is_admin(user)

    if not is_admin:
        return HttpResponseForbidden("Not allowed to view this page.")
    filter = request.GET.get("filter", None)

    rq_deadline = request.GET.get('deadline', None)
    rq_status = request.GET.get("status", None)

    available_status = ["ongoing", "completed"]

    format_status = rq_status if rq_status and rq_status in available_status else None

    projects = get_all_projects(qs_filters={
        "deadline": rq_deadline,
        "status": format_status
    })

    if filter:
        return JsonResponse({
            "projects": projects
        })

    notification_list = []
    status, response = get_notifications()
    if status:
        notification_list = response

    return render(request, 'tables-data.html', {"projects": projects, "is_admin": is_admin, "user": user, "notifications": notification_list})

def get_all_projects(qs_filters={}):
    projects = []

    try:
        filters = {}

        rq_status = None
        qs_deadline =qs_filters.get("deadline", None)

        if qs_deadline and qs_deadline is not None:
            filters["deadline"] = qs_deadline

        qs_status =qs_filters.get("status", None)

        if qs_status and qs_status is not None:
            rq_status = qs_status
        
        project_data = Project.objects.prefetch_related("project_contractor", "project_progress").filter(**filters)

        for project in project_data:
            
            project_contractor = project.project_contractor.first()
            status = round(compute_project_progress(project), 1)

            if rq_status:
                if rq_status == "completed" and not status >= 100:
                    continue
                elif rq_status == "ongoing" and not status < 100:
                    continue
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

    sorted_projects = sorted(projects, key=lambda x: x["status"], reverse=True)
    return sorted_projects

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
    is_admin=utils.is_admin(user)
    if not(is_user_contractor or user_id):
        return render(request, "404.html", {"message": "User info doesn't exists"})

    contractor = None
    contractor_info = {}
    messages = []
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

        project_progress = ProjectProgress.objects.filter(project=contractor_project).all()

        messages = [
            {
                "message": progress.comment,
                "date": progress.date
            } for progress in project_progress
        ] if project_progress.exists() else []

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
        "is_me": is_me,
        "user": user,
        "is_contractor": is_user_contractor,
        "is_admin": is_admin,
        "messages": messages
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
    
def logout_request(request):
    logout(request)
    return  redirect("/")


def get_notifications():
    try:
        project_progress = ProjectProgress.objects.select_related("project").filter(is_read=False)
        if not project_progress:
            print("No new notifications")
            return False, {
                "message": "No new messages",
                "status": 200
            }
        unread_progress_project = [
            project for project in project_progress if len(project.comment) > 0
        ]
        projects = [
            project.project for project in unread_progress_project
        ]
        contractors = Contractor.objects.filter(project__in=projects)

        unread_messages = [
            {
                "message": progress.comment,
                "contractor":  (contractors.filter(project=progress.project).annotate(full_name=Concat("first_name",Value(" "),"last_name"))
                                .values("full_name").first()).get("full_name"),
                "image": progress.image,
                "date": str(localtime(progress.date).strftime("%b %d at %H:%m")),
                "pdf": progress.file
            } for progress in unread_progress_project
        ]
        # print(f"Unread messages: {unread_messages}")
        if len(unread_messages) > 0:
            sorted_message = sorted(unread_messages, key=lambda x: x["date"], reverse=True)
            print(f"Sorted messages: {sorted_message}")
            unread_messages = sorted_message
        return True, unread_messages

    except Exception as e:
        print(f"Error: {e}")
        return False, {
            "message": "Something went wrong.",
            "status": 500
        }
    
@login_required(login_url="/auth/login")
def change_password_view(request):
    r_user = request.user
    username = r_user.username

    if request.method == "GET":
        return JsonResponse({
            "message": "Method not allowed",
            "status":400
        }, status=400)
    current_p = request.POST.get("currentPassword", None)
    new_pasword =  request.POST.get("newPassword", None)

    if not(current_p and new_pasword):
        return JsonResponse({
            "message": "All fields required",
            "status": 400
        }, status=400)
    
    try:
        user = authenticate(request=request, username=username, password=current_p)
        if not user:
            return JsonResponse({
                "message": "Incorrect current password.",
                "status": 401
            }, status=401)
        
        user.set_password(new_pasword)

        user.save()
        return JsonResponse({
            "message": "Password changed successfully!",
            "status": 200
        }, status=200)
    
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({
            "message": f"Error: {e}",
            "status": 500
        }, status=500)

def project_update(request):
    id = request.GET.get("id", None)

    if not id:
        return JsonResponse({
            "message":"No project sepecified",
            "status":400
        })
    
    try:
        project = Project.objects.get(projectID=id)
        project.delete()
        return JsonResponse({
            "message":"Project deleted",
            "status": 200
        }, status=200)
    except Project.DoesNotExist:
        return JsonResponse({
            "message":"Project does not exist",
            "status": 404
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "message": f"Error: {e}",
            "status": 500
        }, status=500)