from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.

def home(request):
    return render(request, 'app1/home.html')

def about(request)
    return render(request, 'app1/about.html')
