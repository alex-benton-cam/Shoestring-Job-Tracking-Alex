from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.core import serializers

from .models import Operation, Job, Operator,Location
import pandas as pd

import datetime
import csv
from dateutil.parser import parse

from io import StringIO

from .models import Operation, Job, Operator,Location

displayFields = [f.name for f in Job._meta.get_fields() 
                         if True]

print(displayFields)