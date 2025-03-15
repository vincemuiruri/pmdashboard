from django.contrib import admin
from .models import Contractor, Project, ProjectManager, ProjectProgress, ProjectPhase
# Register your models here.
models = [Contractor, Project, ProjectManager, ProjectProgress, ProjectPhase]

admin.site.register(models)