from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.

class Project(models.Model):
    projectID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    deadline = models.DateField(blank=False, null=False)
    progress = models.CharField(max_length=10, blank=False, null=False, default="0")
    status = models.CharField(max_length=20, null=False, blank=False, default="ongoing")

    def __str__(self) -> str:
        return f"{self.name}"
    
class ProjectPhase(models.Model):
    project = models.ForeignKey(Project, related_name="phases", on_delete=models.CASCADE)
    phase_number = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        unique_together = ("project", "phase_number")

    def __str__(self) -> str:
        return f"{self.project.name} - {self.name}"

class Contractor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_contractor", null=False, blank=False, unique=True)
    userID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    project = models.ForeignKey(Project, related_name="project_contractor", blank=False, null=False, on_delete=models.CASCADE)
    about = models.TextField(blank=False, null=False, default="Project Contractor")
    #avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=False, null=True, default="")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Signal to delete the User when a Contractor is deleted
@receiver(post_delete, sender=Contractor)
def delete_user_with_contractor(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()  # Deletes the associated user

class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, related_name="project_progress", on_delete=models.CASCADE)
    phase = models.ForeignKey(ProjectPhase, related_name="progress_phase", on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False, default=datetime.now)
    comment = models.TextField()
    image = models.ImageField(upload_to='project_progress_images/', null=True, blank=True)

    class Meta:
        unique_together = ("project", "phase")

    def __str__(self) -> str:
        return f"{self.project.projectID} - {self.phase.name}"

class ProjectManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_admin", null=False, blank=False, unique=True)
    userID = models.CharField(max_length=30, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

