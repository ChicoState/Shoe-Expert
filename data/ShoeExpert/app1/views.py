from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from app1.forms import JoinForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from app1.models import Shoe
# Create your views here.

def user_logout(request):
    logout(request)
    return redirect("/")

def user_login(request):
    if(request.method == 'POST'):
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
                print("They used username: {} and password: {}".format(username, password))
    return render(request, 'app1/login.html', {"login_form":LoginForm})


def join(request):
    if(request.method == "POST"):
        join_form = JoinForm(request.POST)
        if(join_form.is_valid()):
            user = join_form.save()
            user.set_password(user.password)
            user.save()
            return redirect("/")
        else:
            page_data = {"join_form": join_form}
            return render(request, 'app1/join.html', page_data)
    else:
        join_form = JoinForm()
        page_data = {"join_form":join_form}
    return render(request, 'app1/join.html', page_data)


@login_required(login_url='/login/')
def home(request):
    shoes = Shoe.objects.all()
    context = {'shoes': shoes}
    return render(request, 'app1/home.html', context)

@login_required(login_url='/login/')
def about(request):
    return render(request, 'app1/about.html')

