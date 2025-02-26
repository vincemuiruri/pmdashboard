from  django.contrib.auth.models import Group

def is_admin(user):
    return user.groups.filter(name="admin").exists()

def is_contrator(user):
    return user.groups.filter(name="contractor").exists()

def create_group(group_name):
    return Group.objects.get_or_create(name=group_name)

def add_user_to_group(user, group_name):
    group_name, created = create_group(group_name)
    group_name.user_set.add(user)