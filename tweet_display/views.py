from django.shortcuts import render
from django.http import HttpResponse

from rest_pandas import PandasSimpleView
import pandas as pd

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. there'll be something to see here soon.")
