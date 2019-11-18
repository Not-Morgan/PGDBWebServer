from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Student, PointCodes, PlistCutoff, Grade, Points, Certificates
from configuration.models import Configuration
from users.models import CustomUser
from django.template.loader import get_template
from itertools import zip_longest
import io
import xml.dom.minidom as minidom
from util.queryParse import parseQuery
from django.contrib.auth.decorators import login_required
from util.converter import wdb_convert
from threading import Thread

from axes.utils import reset
from .extra_views import *

logs = []
success = True


@login_required
def search(request):
    template = get_template('data/search.html')

    # if no query exists make an empty list
    if request.GET['query']:
        query = request.GET['query']
    else:
        return HttpResponse(template.render(None, request))

    students = parseQuery(query)

    if len(students) == 1:
        return HttpResponseRedirect(f"/data/student/{students[0].id}")
    context = {
        'student_list': students,
        'query': request.GET['query']
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def student_info(request, num):
    global success
    template = get_template('data/student_info.html')
    student = Student.objects.get(id=num)
    context = {
        'student': student,
        'plists': PlistCutoff.objects.all(),
        'config': Configuration.objects.get(),
        'current_grade': ''.join([n for n in student.homeroom if n.isdigit()]),
        'success': success,
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


@login_required
def student_submit(request, num):
    entered_by = request.user
    student = Student.objects.get(id=num)
    items = list(request.POST.items())
    anecdotes = [item for item in items if "anecdote" in item[0] != -1]
    points_list = [item for item in items if item[0].find("points") != -1 or item[0].find("code") != -1]
    scholar_fields = [item for item in items if item[0].find(" SC ") != -1]
    points_list = points_list + scholar_fields
    code_delete_buttons = [item for item in items if item[0].find("deletePoint") != -1]
    nullification = dict(item for item in items if item[0].find("nullify") != -1)
    global success
    success = True

    # anecdotes
    for n, anecdote in enumerate(anecdotes):
        # print(anecdote[1], n)
        grade = student.grade_set.get(grade=int(student.homeroom[:2]) - n)
        grade.anecdote = anecdote[1]
        if request.user.has_perm('data.change_points'):
            grade.save()

    # delete codes buttons
    for button in code_delete_buttons:
        # buttons are ['deletepoint <grade> <catagory> <code> ', 'X']
        grade, catagory, code = button[0].strip().split(' ')[1:]
        point = \
            student.grade_set.get(grade=int(grade)).points_set.filter(type__catagory=catagory).filter(type__code=code)[
                0]
        if request.user.has_perm('data.change_points') or point.entered_by == request.user:
            point.delete()
        # print(point)
        # print("button: ", grade, type, code)

    # points and codes
    if request.method == 'POST':
        # print("received POST request")
        # for k, v in request.POST.items():
        #     print(k, "|", v)

        # iterate through pairs of point amount and code
        for point_field, code_field in zip(points_list[::2], points_list[1::2]):

            # get info like grade and point type e.g. SE, AT
            info = point_field[0].split(' ')
            grade_num = int(info[0])
            type = info[1]

            # decide if it's scholar or other type
            if type == "SC":
                # scholar gets its own class from the other points
                if point_field[1] == '' and code_field[1] == '':
                    continue

                if point_field[1] == '':
                    t1 = 0
                else:
                    t1 = float(point_field[1])

                if code_field[1] == '':
                    t2 = 0
                else:
                    t2 = float(code_field[1])

                # set the scholar average
                grade = student.grade_set.get(grade=grade_num)
                scholar = grade.scholar_set.all()[0]
                scholar.term1 = t1
                scholar.term2 = t2
                success = True if (
                            request.user.has_perm('data.change_scholar') and (t1 <= 100 and t2 <= 100)) else False
                if success: scholar.save()

            else:
                if point_field[1] == '' or code_field[1] == '':
                    continue

                amount = float(point_field[1])
                code = int(code_field[1])

                # skip over invalid entries
                success = True if type == "SE" or (type == "AT" and amount <= 6) or (type == "FA" and amount <= 10) else False
                if not success: continue

                # find the point class with the same code and category
                try:
                    typeClass = PointCodes.objects.filter(catagory=type).get(code=code)
                except PointCodes.DoesNotExist as e:
                    typeClass = PointCodes(catagory=type, code=code, description=str(type) + str(code))
                    if request.user.has_perm('data.add_PointCodes'):
                        typeClass.save()

                grade = student.grade_set.get(grade=grade_num)
                grade.points_set.create(type=typeClass, amount=amount, entered_by=entered_by)

    for grade_num in range(8, int(student.homeroom[:2]) + 1):
        grade = student.grade_set.get(grade=grade_num)
        cert = grade.certificates_set.all().first()
        cert.service = ('SE' + str(grade_num).zfill(2) + ' nullify') in nullification
        cert.athletics = ('AT' + str(grade_num).zfill(2) + ' nullify') in nullification
        cert.honour = ('SC' + str(grade_num).zfill(2) + ' nullify') in nullification
        cert.fine_arts = ('FA' + str(grade_num).zfill(2) + ' nullify') in nullification
        cert.t1 = ('SC' + str(grade_num).zfill(2) + 'T1 nullify') in nullification
        cert.t2 = ('SC' + str(grade_num).zfill(2) + 'T2 nullify') in nullification
        cert.save()

    return HttpResponseRedirect(f"/data/student/{num}")


def archive(request):
    template = get_template('data/archive.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def archive_submit(request):
    global logs
    logs = []
    if request.method == "POST":
        if request.user.has_perm('data.add_student'):
            if "file" in request.FILES:
                file = ET.parse(request.FILES["file"])
                import_thread = Thread(target=import_pgdb_file, args=(file,))
                import_thread.start()
                logs.append("We will now import the file in the background")
        else:
            logs.append("Permission error: Please make sure you can import students")
    template = get_template('data/file_upload.html')
    context = {
        "logs": logs,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def archive_wdb_submit(request):
    if request.method == "POST":
        if "file" in request.FILES:
            grade = int(request.POST["grade"])
            start_year = int(request.POST["start-year"])
            pgdb_file = wdb_convert((l.decode() for l in request.FILES["file"]), grade, start_year)

            response = HttpResponse(pgdb_file, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=students.pgdb'

            return response

    return HttpResponseRedirect("/data/archive")


def archive_file(request):
    if "query" not in request.POST:
        raise Http404
    query = request.POST['query']

    print(f"query={query}")

    student_list = parseQuery(query)

    # plists from years that students being exported are in
    relevent_plists = []

    root = export_pgdb_archive(student_list, relevent_plists)

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    xml_file = io.StringIO(xml_str)

    response = HttpResponse(xml_file, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=students.pgdb'

    return response


def settings(request):
    template = get_template('data/settings.html')
    context = {
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def codes(request):
    template = get_template('data/codes.html')
    context = {
        'codes': PointCodes.objects.all()
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def plist(request):
    template = get_template('data/plist.html')
    context = {
        'plist': PlistCutoff.objects.all(),
        'year': datetime.datetime.now().year,
        'month': datetime.datetime.now().month
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def plist_submit(request):
    plist = PlistCutoff.objects.all()
    items = request.POST

    for year in plist:
        year.grade_8_T1 = items[str(year.year) + " 8 1"]
        year.grade_8_T2 = items[str(year.year) + " 8 2"]

        year.grade_9_T1 = items[str(year.year) + " 9 1"]
        year.grade_9_T2 = items[str(year.year) + " 9 2"]

        year.grade_10_T1 = items[str(year.year) + " 10 1"]
        year.grade_10_T2 = items[str(year.year) + " 10 2"]

        year.grade_11_T1 = items[str(year.year) + " 11 1"]
        year.grade_11_T2 = items[str(year.year) + " 11 2"]

        year.grade_12_T1 = items[str(year.year) + " 12 1"]
        year.grade_12_T2 = items[str(year.year) + " 12 2"]

        year.save()

    return HttpResponseRedirect("/data/settings/plist")


def autofocus_submit(request, num):
    user = CustomUser.objects.get(username=request.user.username)
    user.autofocus = num
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def codes_submit(request):
    # sort the codes into a list where each code is an item
    items = list(request.POST.items())[1:]
    args = [iter(items)] * 3
    code_info = list(zip_longest(*args))

    for code in code_info:
        if (not code[0][1]) or (not code[1][1]):
            continue

        # if there is an already existing code don't create a new one
        filter_codes = PointCodes.objects.filter(code=int(code[1][1]))
        filter_codes = filter_codes.filter(catagory=code[0][1])
        if len(filter_codes) == 1:
            entry = filter_codes[0]
        elif len(filter_codes) == 0:
            entry = PointCodes()
        else:
            print("panic!!")

        entry.code = code[1][1]
        entry.catagory = code[0][1].upper()
        entry.description = code[2][1]
        entry.save()

    return HttpResponseRedirect("/data/settings/codes")


def index(request):
    maintenance, notice = google_calendar()
    template = get_template('data/index.html')
    context = {
        'maintenance': maintenance,
        'notice': notice,
        'student_list': Student.objects.all(),
        'recent': Points.objects.all().order_by('-id')[:100],
    }
    if request.user.is_authenticated:
        reset(username=request.user.username)

    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    elif request.user.is_authenticated:
        return HttpResponseRedirect('/entry')
    else:
        return HttpResponseRedirect('/')


@login_required
def personalisation(request):
    template = get_template('data/personalisation.html')
    context = {
        'user': request.user
    }
    return HttpResponse(template.render(context, request))


@login_required
def personalisation_submit(request):
    user = request.user
    items = request.POST

    user.header_colour = items['top']
    user.page_colour = items['page']
    user.save()

    return HttpResponseRedirect('/data/personalisation')


def help(request):
    template = get_template('data/help.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')
