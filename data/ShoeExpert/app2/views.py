from django.shortcuts import render
from django.Http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Hello App 2")
