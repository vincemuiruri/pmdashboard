from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Project(models.Model):
    projectID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    deadline = models.DateField(blank=False, null=False)
    progress = models.CharField(max_length=10,blank=False, null=False, default=0)
    status = models.CharField(max_length=20, null=False, blank=False, default="ongoing")

    def __str__(self) -> str:
        return f"{self.name}"

class Contractor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_contractor", null=False, blank=False, unique=True)
    userID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    project = models.ForeignKey(Project, related_name="project_contractor", blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, related_name="project_phase", blank=False, null=False, on_delete=models.CASCADE)
    phase = models.CharField(max_length=255, null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False, default=datetime.now())
    comment = models.TextField()

    def __str__(self) -> str:
        return f"{self.project.projectID} {self.phase}"

class ProjectManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_admin", null=False, blank=False, unique=True)
    userID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

