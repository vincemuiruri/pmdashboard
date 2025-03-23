from . import views
from . import generate_pdf as pdf
from django.http import JsonResponse

def generate_projects_report(request):
    try:
        projects_list = views.get_all_projects()

        headers = [["Project", "Contractor", "Deadline", "Status"]]

        total = len(projects_list)

        empty_project = {
            "project_name": "_",
            "project_id": "_",
            "str_status": "_",
            "deadline": "_",
            "status": "_",
            "contractor": "_",
            "contractor_id": "_"
        }

        if len(projects_list) < 10:
            for i in range(10 - len(projects_list)):
                projects_list.append(empty_project)
        table_data = []
        for project in projects_list:
            is_empty_project = project == empty_project
            table_data.append(
                [
                    project.get("project_name"), 
                    project.get("contractor"), 
                    project.get("deadline"), 
                    f"{project.get("status")}" if is_empty_project else f"{project.get("status")}%"
                ]
            )

        

        data = {
            "data": table_data,
            "headers": headers,
            "type": "project",
            "total": total
        }

        is_generated, response = pdf.generate_report_pdf("Projects",data)
        if is_generated:
            return response
        
        return JsonResponse(response, status=response.get("status", 500))

    except Exception as e:
        print(f"Error: {e}")
        return False, {
            "message": "An error occurred while generating report",
            "status": 500
        }