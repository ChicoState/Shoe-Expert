from aggregate import Url_Paths

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect

import importlib
app1_models_module = importlib.import_module('app1.models')
app1_models_module_names = dir(app1_models_module)
app1_models_module_class_names = [name for name in app1_models_module_names if isinstance(getattr(app1_models_module, name), type)]
for name in app1_models_module_class_names:
    globals()[name] = getattr(app1_models_module, name)


# Create your views here.


def user_logout(request):
    logout(request)
    return redirect("/")


def user_login(request):
    if (request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect("/")
                else:
                    return HttpResponse("Your account is not active.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(
                    username, password))
    return render(request, 'app1/login.html', {"login_form": LoginForm})


def join(request):
    if (request.method == "POST"):
        join_form = JoinForm(request.POST)
        if (join_form.is_valid()):
            user = join_form.save()
            user.set_password(user.password)
            user.save()
            return redirect("/")
        else:
            page_data = {"join_form": join_form}
            return render(request, 'app1/join.html', page_data)
    else:
        join_form = JoinForm()
        page_data = {"join_form": join_form}
    return render(request, 'app1/join.html', page_data)


@login_required(login_url='/login/')
def home(request):
    context_list = []
    for url_path in Url_Paths:
        tmp_dict = {}
        tmp_dict['shoes'] = globals()[url_path.name.capitalize()].objects.all().order_by('?')[:3]
        tmp_dict['title'] = url_path.name.replace('_', ' ').title()
        tmp_dict['redirect'] = url_path.name.lower()
        tmp_dict['headers'] = []
        tmp_dict['fields'] = []
        for column in url_path.get_django_available_columns():
            tmp_dict['headers'].append(url_path.get_column_name(column))
            tmp_dict['fields'].append(url_path.get_column_name(column, attribute = True))
        context_list.append(tmp_dict)
    return render(request, 'app1/home.html', { 'context_list': context_list })

@login_required(login_url='/login/')
def generic_shoe(request, url_path):
    page_sizes = [5, 10, 15, 20, 30, 40, 50]
    #brands = ['All', 'Adidas', 'Nike', 'Aky']
    brands = [5, 10, 15, 20]
    brands_per_page = int(request.GET.get('brands_per_page', brands[0]))
    shoes_per_page = int(request.GET.get('shoes_per_page', page_sizes[0]))
    queryset = globals()[url_path.name.capitalize()].objects.all().order_by('shoe_name')
    paginator = Paginator(queryset, shoes_per_page)
    page = request.GET.get('page')
    brand = request.GET.get('brand')
    shoes = paginator.get_page(page)
    headers = []
    fields = []
    for column in url_path.get_django_available_columns():
        headers.append({
            'has_modal': column.has_modal(),
            'modal_body': column.get_modal_body(),
            'modal_title': url_path.get_column_name(column, display_units = False),
            'modal_id': url_path.get_column_name(column, attribute = True),
            'column_title': url_path.get_column_name(column)
        })
        fields.append(url_path.get_column_name(column, attribute = True))
    return render(request, 'app1/generic_shoe.html', {
        'shoes': shoes,
        'headers': headers,
        'fields': fields,
        'shoes_per_page': shoes_per_page,
        'page_sizes': page_sizes,
        'title': url_path.name.replace('_', ' ').title()
    })


def about(request):
    return render(request, 'app1/about.html')


@login_required(login_url='/login/')
def blog(request):
    return render(request, 'app1/blog.html')


@login_required(login_url='/login/')
def filter3(request, url_path):
    page_sizes = [5, 10, 15, 20, 30, 40, 50]
    brands = [All, Adidas, Nike, Aky]
    brands_per_page = request.GET.get('brands_per_page', brands[0])
    shoes_per_page = int(request.GET.get('shoes_per_page', page_sizes[10]))
    queryset = globals()[url_path.name.capitalize()].objects.all().order_by('shoe_name')
    paginator = Paginator(queryset, shoes_per_page, brands_per_page)
    page = request.GET.get('page')
    shoes = paginator.get_page(page)
    headers = []
    fields = []
    for column in url_path.get_django_available_columns():
        headers.append({
            'has_modal': column.has_modal(),
            'modal_body': column.get_modal_body(),
            'modal_title': url_path.get_column_name(column, display_units = False),
            'modal_id': url_path.get_column_name(column, attribute = True),
            'column_title': url_path.get_column_name(column)
        })
        fields.append(url_path.get_column_name(column, attribute = True))
    return render(request, 'app1/filter3.html', {
        'shoes': shoes,
        'headers': headers,
        'fields': fields,
        'shoes_per_page': shoes_per_page,
        'page_sizes': page_sizes,
        'title': url_path.name.replace('_', ' ').title()
    })

#@login_required(login_url='/login/')
def filter(request, userShoe):
    context_list = []
    for url_path in Url_Paths:
        tmp_dict = {}
        tmp_dict['shoes'] = globals()[url_path.name.capitalize()].objects.all().order_by('?')[:3]
        tmp_dict['title'] = url_path.name.replace('_', ' ').title()
        tmp_dict['redirect'] = url_path.name.lower()
        tmp_dict['headers'] = []
        tmp_dict['fields'] = []
        for column in url_path.get_django_available_columns():
            tmp_dict['headers'].append(url_path.get_column_name(column))
            tmp_dict['fields'].append(url_path.get_column_name(column, attribute = True))
        context_list.append(tmp_dict)
    return render(request, 'app1/filter.html', { 'context_list': context_list })

@login_required(login_url='/login/')
def filter2(request):
    if (request.method == "POST"):
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
           userShoe = filter_form.cleaned_data["Shoe"]
           return redirect(filter, userShoe)
    return render(request, 'app1/filter2.html', {'filter_form': FilterForm})

