import json
import sys
from django.shortcuts import render

from exegesis.models import Project


def login(request):
    try:
        return render(request, 'login.html')
    except:
        print sys.exc_info()
        return render(request, 'wrong.html')


def projects(request):
    try:
        if request.user:
            email = request.user.email
        user = request.user.first_name + ' ' + request.user.last_name
        request.session['username'] = user
        request.session['email'] = email
        request.session.modified = True
        all_projects = Project.objects.filter(user__email=email)
        proj = all_projects.values('name', 'density', 'screen', 'description')
        proj = json.dumps(list(proj))
        return render(request, 'projects.html', {'projects': all_projects, 'user': user, 'proj': proj})
    except:
        print sys.exc_info()
        return render(request, 'wrong.html')
