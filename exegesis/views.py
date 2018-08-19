import json
import os
import sys
import sys
import uuid
import uuid
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.db.models import Q

from annotator import settings
from exegesis.models import Project, ArtBoard, Revision, Note

ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")

translate = []
annotations = []
g_attributes = {}
defs = {}
trans_child = []


def check_for_id():
    new_id = str(uuid.uuid4())[0:8]
    return new_id


def getTranslations(transform):
    trans = []
    transx = transy = 0
    p = transform.split(')')
    for i in p:
        if i.lstrip().startswith('translate'):
            q = i.split('(')[1]
            r = q.split(',')
            trans.append(float(r[0]))
            trans.append(float(r[1]))
    for i in range(len(trans)):
        if i % 2 == 0:
            transx += trans[i]
        else:
            transy += trans[i]
    translate.append(transx)
    translate.append(transy)


def getSubChild(child):
    global trans_child
    for subchild in child:
        elm = {}
        attribute = subchild.attrib
        tag = subchild.tag.split('}')[1]
        if tag == 'g' and 'transform' in attribute.keys():
            transform = attribute['transform']
            getTranslations(transform)
            if 'translate' in transform:
                trans_child.append(subchild)

        if tag == 'rect' or tag == 'text' or tag == 'tspan' or tag == 'ellipse' or tag == 'circle':
            if translate and 'x' in attribute.keys():
                if len(translate) > 2:
                    translation = [0] * 2
                    for i in range(len(translate)):
                        if i % 2 == 0:
                            translation[0] += translate[i]
                        else:
                            translation[1] += translate[i]
                else:
                    translation = translate[:]

                attribute['x'] = float(attribute['x']) + translation[0]
                attribute['y'] = float(attribute['y']) + translation[1]
            if tag == 'tspan':
                g_attributes.clear()
                attribute['text'] = subchild.text
            attribute['type'] = tag
            if g_attributes:
                attribute.update(g_attributes)
            annotations.append(attribute)

        if tag == 'g':
            g_attributes.clear()
            for i in attribute.keys():
                if i == 'id' or i == 'transform':
                    continue
                else:
                    g_attributes[i] = attribute[i]

        if tag == 'use':
            for i in attribute.keys():
                if 'href' in i:
                    id = attribute[i]
                    del attribute[i]
                    break
            id = id.replace('#', '')
            defs_list = defs.copy()
            if 'id' in attribute.keys():
                if id in defs_list.keys():
                    defs_list[id]['id'] = attribute['id']
                    if translate and 'x' in defs_list[id].keys():
                        if len(translate) > 2:
                            translation = [0] * 2
                            for i in range(len(translate)):
                                if i % 2 == 0:
                                    translation[0] += translate[i]
                                else:
                                    translation[1] += translate[i]
                        else:
                            translation = translate[:]

                        defs_list[id]['x'] = float(defs_list[id]['x']) + translation[0]
                        defs_list[id]['y'] = float(defs_list[id]['y']) + translation[1]
                    annotations.append(defs_list[id])

        if tag == 'path':
            if 'd' in attribute.keys():
                path_data = {}
                path = attribute['d'].split(' ')
                paths = []
                if ',' in path[0]:
                    for i in path:
                        if i == 'z' or i == 'Z':
                            continue
                        point = i.split(',')
                        if not point[0].replace('.', '').isdigit():
                            point[0] = point[0][1:]
                        point[0] = float(point[0])
                        point[1] = float(point[1])
                        paths.extend(point)
                    x_array = []
                    y_array = []
                    for j in range(len(paths)):
                        if j % 2 == 0:
                            x_array.append(paths[j])
                        else:
                            y_array.append(paths[j])
                    x_max = max(x_array)
                    y_max = max(y_array)
                    x_min = min(x_array)
                    y_min = min(y_array)
                    x = x_min
                    y = y_min
                    if translate:
                        if len(translate) > 2:
                            translation = [0] * 2
                            for i in range(len(translate)):
                                if i % 2 == 0:
                                    translation[0] += translate[i]
                                else:
                                    translation[1] += translate[i]
                        else:
                            translation = translate[:]
                        y = y_min + translation[1]
                        x = x_min + translation[0]
                    height = y_max - y_min
                    width = x_max - x_min
                    del attribute['d']
                    path_data.update(attribute)
                    path_data.update(g_attributes)
                    path_data['height'] = height
                    path_data['width'] = width
                    path_data['x'] = x
                    path_data['y'] = y
                    annotations.append(path_data)

        getSubChild(subchild)
        if translate and subchild == trans_child[len(trans_child) - 1]:
            translate.pop()
            translate.pop()
            trans_child.pop()
    return annotations


def getDefs(root):
    count = 0
    for child in root:
        tag = child.tag.split('}')[1]
        if tag == 'rect' or tag == 'circle' or tag == 'ellipse' or tag == 'text':
            attribute = child.attrib
            if 'id' in attribute.keys():
                id = attribute['id']
                del attribute['id']
                attribute['type'] = tag
                defs[id] = attribute
            if tag == 'text':
                for subchild in child:
                    sub_tag = subchild.tag.split('}')[1]
                    if sub_tag == 'tspan':
                        count += 1
                        sub_attrib = subchild.attrib
                        sub_text = subchild.text
                        defs[id][sub_text] = sub_attrib
    annotations.append(count)


def getChild(root):
    for child in root:
        tag = child.tag.split('}')[1]
        if len(child) > 0 and tag == 'defs':
            getDefs(child)
        else:
            annotations.append(0)
        if len(child) > 0 and tag != 'title' and tag != 'desc' and tag != 'defs':
            getSubChild(child)


def login(request):
    try:
        return render(request, 'login.html')
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def projects(request):
    try:
        if request.user:
            email = request.user.email
            print 'Logged in user ----------> ', request.user.email
        all_projects = Project.objects.filter(Q(user__email=email) | Q(shared_users__in=[request.user])).distinct()
        return render(request, 'projects.html', {'projects': all_projects})
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def create_project(request):
    try:
        project_name = request.POST.get('project-name')
        project_description = request.POST.get('project-description')
        user = request.user.first_name + ' ' + request.user.last_name
        screen = request.POST.get('screen')
        density = request.POST.get('density')
        uuid_name = uuid.uuid4()
        new_project = Project(user=request.user, name=project_name, description=project_description,
                              owner=user, screen=screen, density=density, uuid=uuid_name)
        new_project.save()
        return redirect('/exegesis/projects')
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def artboards(request):
    try:
        if request.GET.get('project'):
            project_uuid = request.GET.get('project')
        else:
            project_uuid = request.session['project_uuid']
        print 'User ---------> ', request.user.email
        print 'Project ---------> ', project_uuid
        project = Project.objects.get(uuid=project_uuid, user__email=request.user.email)
        name = project.name
        description = project.description
        owner = project.owner
        screen = project.screen
        density = project.density
        created = project.created
        last_updated = project.last_updated
        shared_members = project.shared_users.all()
        request.session['project_uuid'] = project_uuid
        request.session.modified = True
        artboards = ArtBoard.objects.filter(project=project)
        return render(request, 'artboards.html',
                      {'artboards': artboards, 'project': name, 'description': description, 'screen': screen,
                       'density': density, 'created': created, 'last_updated': last_updated, 'owner': owner,
                       'shared_members': shared_members})
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def svg_images(request):
    defs_elms = []
    arts = []
    project_uuid = request.POST.get('project-uuid')
    print 'uuid: ', project_uuid
    project = Project.objects.get(uuid=project_uuid, user=request.user)
    project_name = project.name
    redirection = '/exegesis/projects'
    artboards = ArtBoard.objects.filter(project__name__contains=project_name)
    for artboard in artboards:
        arts.append(artboard.name)
    images_path = os.path.join('exegesis', 'templates', 'uploads')
    if not os.path.exists(images_path):
        os.makedirs(images_path)
    for f in request.FILES.getlist('svgfile'):
        filename = f.name
        print 'filename: ', filename
        if filename.endswith('zip'):
            archive = zipfile.ZipFile(f)
            for file in archive.namelist():
                print 'file: ', file
                if file.endswith('svg'):
                    img_data = archive.read(file)
                    uuid_name = uuid.uuid4()
                    img_name = "%s.%s" % (uuid_name, 'svg')
                    image_path = 'uploads/' + img_name
                    url = image_path
                    with open(os.path.join(images_path, img_name), "wb") as image:
                        image.write(img_data)
                    if '/' in file:
                        file = file.split('/')[1]

                    tree = ET.parse(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
                    root = tree.getroot()
                    for child in root.iter():
                        if child.tag.split('}')[1] == 'defs':
                            for subchild in child.iter():
                                defs_elms.append(subchild)
                    for child in root.iter():
                        if child not in defs_elms:
                            attribute = child.attrib
                            if 'id' in attribute:
                                elem_id = check_for_id()
                                child.set('id', elem_id)
                            if child.tag.split('}')[1] == 'use' and 'id' not in attribute.keys() or \
                                    child.tag.split('}')[1] == 'text' and 'id' not in attribute.keys():
                                elem_id = check_for_id()
                                child.set('id', elem_id)
                    tree.write(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)

                    Project.objects.filter(name=project_name, user=request.user).update(thumbnail=url)
                    project = Project.objects.get(project=project_name, user=request.user)
                    file = file.split('.')[0]
                    if file in arts:
                        old_art = ArtBoard.objects.get(name=file, project__name__contains=project_name,
                                                       latest=True)
                        ArtBoard.objects.filter(name=file, project__name__contains=project_name).update(latest=False)
                        revision_entry = Revision(name=file, artboard=old_art)
                        revision_entry.save()
                    new_entry = ArtBoard(project=project, name=file, location=url, uuid=uuid_name, latest=True)
                    new_entry.save()
                    # TODO The last updated logic should be reviewed
                    Project.objects.filter(name=project_name).update(last_updated=datetime.now())
        else:
            img_data = f.read()
            uuid_name = uuid.uuid4()
            img_name = "%s.%s" % (uuid_name, 'svg')
            image_path = 'uploads/' + img_name
            url = image_path
            with open(os.path.join(images_path, img_name), "wb") as image:
                image.write(img_data)
            tree = ET.parse(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
            root = tree.getroot()
            for child in root.iter():
                if child.tag.split('}')[1] == 'defs':
                    for subchild in child.iter():
                        defs_elms.append(subchild)
            for child in root.iter():
                if child not in defs_elms:
                    attribute = child.attrib
                    if 'id' in child.attrib:
                        elem_id = check_for_id()
                        child.set('id', elem_id)
                    if child.tag.split('}')[1] == 'use' and 'id' not in attribute.keys() or child.tag.split('}')[
                        1] == 'text' and 'id' not in attribute.keys():
                        elem_id = check_for_id()
                        child.set('id', elem_id)
            tree.write(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
            Project.objects.filter(name=project_name, user=request.user).update(thumbnail=url)
            project = Project.objects.get(name=project_name, user=request.user)
            filename = filename.split('.')[0]
            if filename in arts:
                old_art = ArtBoard.objects.get(name=filename, project__name__contains=project_name, latest=True)
                ArtBoard.objects.filter(name=filename, project__name__contains=project_name).update(latest=False)
                revision_entry = Revision(name=filename, artboard=old_art)
                revision_entry.save()
            new_entry = ArtBoard(project=project, name=filename, location=url, uuid=uuid_name, latest=True)
            new_entry.save()
            # TODO The last updated logic should be reviewed
            Project.objects.filter(name=project_name).update(last_updated=datetime.now())
    return redirect(redirection)


def index(request):
    try:
        url = request.GET.get('url')
        global annotations
        annotations = []
        tree = ET.parse(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
        root = tree.getroot()
        getChild(root)
        artboard = ArtBoard.objects.get(location=url)
        project_name = artboard.project.name
        artboard_uuid = artboard.uuid
        artboard_name = artboard.name
        notes = Note.objects.filter(artboard__location=url)
        return render(request, 'index.html',
                      {'annotations': json.dumps(annotations), 'url': url, 'artboard': artboard_name, 'notes': notes,
                       'project': project_name, 'artboard_uuid': artboard_uuid})
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def update_artboard(request):
    try:
        defs_elms = []
        project_name = request.session['project']
        redirection = '/exegesis/artboards?project=' + project_name
        artboard_uuid = request.POST.get('artboard-uuid')
        ArtBoard.objects.filter(project__name__contains=project_name, uuid=artboard_uuid).update(latest=False)
        old_art = ArtBoard.objects.get(project__name__contains=project_name, uuid=artboard_uuid)
        revision = Revision(name=old_art.artboard, artboard=old_art)
        revision.save()
        images_path = os.path.join('exegesis', 'templates', 'uploads')
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        for f in request.FILES.getlist('svgfile'):
            filename = f.name
            print 'filename: ', filename
            img_data = f.read()
            uuid_name = uuid.uuid4()
            img_name = "%s.%s" % (uuid_name, 'svg')
            image_path = 'uploads/' + img_name
            url = image_path
            with open(os.path.join(images_path, img_name), "wb") as image:
                image.write(img_data)
            tree = ET.parse(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
            root = tree.getroot()
            for child in root.iter():
                if child.tag.split('}')[1] == 'defs':
                    for subchild in child.iter():
                        defs_elms.append(subchild)
            for child in root.iter():
                if child not in defs_elms:
                    attribute = child.attrib
                    if 'id' in child.attrib:
                        elem_id = check_for_id()
                        child.set('id', elem_id)
                    if child.tag.split('}')[1] == 'use' and 'id' not in attribute.keys() or child.tag.split('}')[
                        1] == 'text' and 'id' not in attribute.keys():
                        elem_id = check_for_id()
                        child.set('id', elem_id)
            tree.write(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
            Project.objects.filter(name=project_name, user=request.user).update(thumbnail=url)
            project = Project.objects.get(name=project_name, user=request.user)
            filename = filename.split('.')[0]
            new_entry = ArtBoard(project=project, name=filename, location=url, uuid=uuid_name, latest=True)
            new_entry.save()
            # TODO The last updated logic should be reviewed
            Project.objects.filter(project=project_name).update(last_updated=datetime.now())
            return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def delete_artboard(request):
    try:
        url = request.GET.get('artboard')
        artboard = ArtBoard.objects.get(location=url, project__user=request.user)
        project_uuid = artboard.project.uuid
        revisions = Revision.objects.filter(artboard=artboard)
        for revision in revisions:
            revision_location = revision.artboard.location
            os.remove(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + revision_location)
            ArtBoard.objects.filter(location=revision_location).delete()
        ArtBoard.objects.filter(location=url).delete()
        redirection = '/exegesis/artboards?project=' + project_uuid
        os.remove(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + url)
        return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def rename_artboard(request):
    try:
        artboard_uuid = request.POST.get('artboard')
        new_name = request.POST.get('new-name')
        project_uuid = ArtBoard.objects.get(uuid=artboard_uuid).project.uuid
        ArtBoard.objects.filter(uuid=artboard_uuid, project__user=request.user).update(name=new_name)
        redirection = '/exegesis/artboards?project=' + project_uuid
        return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def delete_project(request):
    try:
        project_uuid = request.GET.get('project')
        user = request.user
        artboards = ArtBoard.objects.filter(project__uuid=project_uuid, project__user=user)
        for artboard in artboards:
            os.remove(os.path.join(settings.BASE_DIR, 'exegesis', 'templates') + '/' + artboard.location)
        Project.objects.get(uuid=project_uuid, user=user).delete()
        redirection = '/exegesis/projects'
        return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def share_project(request):
    try:
        email = request.POST.get('email')
        if not request.POST.get('project-name'):
            project_uuid = request.session['project_uuid']
            redirection = '/exegesis/artboards?project=' + project_uuid
        else:
            project_uuid = request.POST.get('project-name')
            redirection = '/exegesis/projects'
        if not Project.objects.filter(uuid=project_uuid, shared_users__email__in=[email]):
            username = email.split('@')[0]
            new_user = User.objects.create_user(username=username, email=email)
            shared_project = Project.objects.get(uuid=project_uuid, user=request.user)
            shared_project.shared_users.add(new_user)
        return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


# TODO: Solve CairoSVG compatibility issue.
# def download_artboard(request):
#     try:
#         url = request.GET.get('artboard')
#         name = url.replace('svg', 'png')
#         cairosvg.svg2png(url=os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url,
#                          write_to=os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + name)
#
#         with open(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + name, 'rb') as png:
#             response = HttpResponse(png.read())
#             response['content_type'] = 'image/png'
#             response['Content-Disposition'] = 'attachment;filename=file.png'
#             return response
#     except Exception as e:
#         print sys.exc_info()
#         return render(request, 'wrong.html')


def revisions(request):
    try:
        artboard_name = request.GET.get('artboard')
        artboard_uuid = request.GET.get('uuid')
        project = ArtBoard.objects.get(uuid=artboard_uuid).project
        revisions = Revision.objects.filter(name=artboard_name, artboard__project=project)
        return render(request, 'revisions.html', {'revisions': revisions})
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')


def write_note(request):
    try:
        note = request.POST.get('note')
        user = request.user
        location = request.POST.get('location')
        artboard = ArtBoard.objects.get(location=location)
        new_note = Note(user=user, note=note, artboard=artboard)
        new_note.save()
        redirection = '/exegesis/svg/?url=' + location
        return redirect(redirection)
    except Exception as e:
        print sys.exc_info()
        return render(request, 'wrong.html')
