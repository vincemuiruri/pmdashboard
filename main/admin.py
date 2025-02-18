from django.contrib import admin
from .models import Contractor, Project, ProjectManager, ProjectProgress
# Register your models here.
models = [Contractor, Project, ProjectManager, ProjectProgress]

admin.register(models)