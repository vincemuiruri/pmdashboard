from  django.contrib.auth.models import Group
import pytz
from django.conf import settings
import os

home_tz = pytz.timezone("Africa/Nairobi")


image_logo_path = os.path.join(settings.BASE_DIR, "static/assets/img/headericon.png")

def is_admin(user):
    return user.groups.filter(name="admin").exists()

def is_contrator(user):
    return user.groups.filter(name="contractor").exists()

def create_group(group_name):
    return Group.objects.get_or_create(name=group_name)

def add_user_to_group(user, group_name):
    group_name, created = create_group(group_name)
    group_name.user_set.add(user)