from ast import operator
from datetime import datetime
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
from django.core.exceptions import ObjectDoesNotExist
from numpy import disp

from .models import Operation, Job, Worker, Location
import pandas as pd
from core.utils import stdDateTime
from json import dumps, loads


from django.db.models.base import ModelBase
from django.apps import apps


def get_verbose(model, field_str, app="core"):
    try:
        if "__" in field_str:
            parent_str, field_str = field_str.split("__", 1)
            parent_model = apps.get_model(app, parent_str.replace("_id", ""))
            return get_verbose(parent_model, field_str, app="core")
        else:
            return model._meta.get_field(field_str).verbose_name
    except:
        return "views.get_verbose error"


def get_value(object, field_str):
    try:
        if "__" in field_str:
            parent_str, field_str = field_str.split("__", 1)
            # parent = job_id, field = "quantity"
            parentObj = getattr(object, parent_str.replace("_id", ""))
            return get_value(parentObj, field_str)
        else:
            return getattr(object, field_str)
    except AttributeError:
        return "-"


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class Index(View):
    template = "_index.html"

    def get(self, request):
        return render(request, self.template)


def uploadOps(request):
    data = {}
    template = "upload.html"

    if request.method == "GET":
        return render(request, template)

    elif request.method == "POST":

        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.warning(request, "The wrong file type was uploaded")
            return HttpResponseRedirect(reverse("upload"))

        def import_op(row, dateCols=[]):

            rowDict = row.to_dict()
            jobFields = ["work_no", "company", "job_name", "quantity"]

            try:
                # Get job object
                parentJob = Job.objects.get(work_no=rowDict[jobFields[0]])
            except ObjectDoesNotExist:
                # Create Job object if not already existing
                jobDict = {key: rowDict[key] for key in jobFields}
                parentJob = Job(**jobDict)
                parentJob.job_log = dumps({stdDateTime(): "Job uploaded to website"})
                parentJob.save()

            # Change op dict to reflect job creation
            rowDict["job"] = parentJob
            rowDict["op_id"] = (
                str(rowDict["work_no"])
                + "/"
                + str(rowDict["issue_no"])
                + str(rowDict["op_no"])
            )
            for field in jobFields:
                rowDict.pop(field, None)

            if rowDict["worker"]:
                try:
                    parentWorker = Worker.objects.get(name=rowDict["worker"])
                    rowDict["worker"] = parentWorker
                except ObjectDoesNotExist:
                    messages.warning(
                        request, "Worker '" + rowDict["worker"] + "' does not Exist"
                    )
                    rowDict["worker"] = None

            if rowDict["location"]:
                try:
                    parentLocation = Location.objects.get(name=rowDict["location"])
                    rowDict["location"] = parentLocation
                except ObjectDoesNotExist:
                    messages.warning(
                        request, "Location '" + rowDict["location"] + "' does not Exist"
                    )
                    rowDict["location"] = None

            for col in dateCols:
                rowDict[col] = stdDateTime(rowDict[col]) if rowDict[col] else None
            obj = Operation(**rowDict)
            obj.save()

        loadDF = pd.read_csv(csv_file)
        loadDF = loadDF.where(pd.notnull(loadDF), None)
        loadDF.index.rename("upload_id", inplace=True)

        loadDF.apply(import_op, axis=1, dateCols=["start_time", "end_time"])

        return render(request, template, data)


def uploadLocs(request):
    data = {}
    template = "upload.html"

    if request.method == "GET":
        return render(request, template)

    elif request.method == "POST":

        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.warning(request, "The wrong file type was uploaded")
            return HttpResponseRedirect(reverse("upload"))

        def import_loc(row, model=Operation, dateCols=[], modelDict={}):

            rowDict = row.to_dict()
            obj = Location(**rowDict)
            obj.save()

        loadDF = pd.read_csv(csv_file)
        loadDF = loadDF.where(pd.notnull(loadDF), None)
        loadDF.index.rename("upload_id", inplace=True)
        loadDF.apply(import_loc, axis=1)

        return render(request, template, data)


class Dashboard(View):
    template = "dashboard.html"

    def get(self, request):
        return render(request, self.template, {"jobs": Job.objects.all()})


class ModelView(View):

    model = None
    template = "_datatable_populated.html"

    def get_object(self, queryset=None):
        return queryset.get(model=self.model)

    def get(self, request):
        
        query = None
        
        if self.model == Operation:
            query = Operation.objects.all()
            fieldDict = {
                "job": {"href": "job_id__abs_link"},
                "op_no": {"href": "abs_link"},
                "op_name": {},
                "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
                "worker": {"href": "worker_id__abs_link"},
                "job_id__quantity": {},
            }

        elif self.model == Job:
            fieldDict = {
                "work_no": {"href": "abs_link"},
                "company": {},
                "job_name": {},
                "quantity": {},
                "location": {},
            }
            
        elif self.model == Worker:
            fieldDict = {
                "name": {"href": "abs_link"},
            }
            
        elif self.model == Location:
            fieldDict = {
                "loc_id": {"href": "abs_link"},
                "name": {},
                "machine": {},
                "worker": {},
            }
        
        else:
            displayFields = [
                f.name
                for f in self.model._meta.get_fields()
                if hasattr(self.model._meta.get_field(f.name), "verbose_name")
                and f.name != "link_slug"
            ]
            fieldDict = {k: {} for k in displayFields}
            
        query = query if query is not None else self.model.objects.all()

        for field_str in fieldDict.keys():
            fieldDict[field_str]["verbose"] = get_verbose(self.model, field_str)
        linkFields = [v.get("href") for v in fieldDict.values() if v.get("href")]

        queryData = query.values(*fieldDict.keys(), *linkFields)
        return render(
            request, self.template, {"fieldDict": fieldDict, "queryData": queryData}
        )


class Cards(View):
    template = "_cards.html"

    def get(self, request):
        return render(request, self.template)


class OperatorDash(View):
    template = "operator.html"

    def get(self, request):
        return render(request, self.template)


class OpDetail(View):
    template = "_operator.html"
    model = Operation
    
    def template_args(self, link):
        
        fieldDict = {
            "op_id": {},
            "op_name": {},
            "job_id__company": {},
            "job_id__job_name": {},
            "part_no": {},
            "job_id__quantity": {},
            "drg_no": {},
            "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        }

        operation = Operation.objects.get(link_slug=link)
        linkFields = [v.get("href") for v in fieldDict.values() if v.get("href")]
        opData = {f: get_value(operation, f) for f in list(fieldDict.keys()) + linkFields}
        
        for field_str in fieldDict.keys():
            if "verbose" not in fieldDict[field_str]:
                fieldDict[field_str]["verbose"] = get_verbose(self.model, field_str)
        
        
        jobLog = loads(get_value(operation, "job_id__job_log"))
        displayLog = {k: jobLog[k] for k in sorted(jobLog, reverse=True)}
                
        return {"fieldDict": fieldDict, "opData": dict(opData), "jobLog": displayLog}
    
    
    def get(self, request, *args, **kwargs):
        
        context = self.template_args(kwargs["op"])
        context["submit"] = "get"
        
        return render(request, self.template, context)
    
    def post(self, request, *args, **kwargs):
        
        operation = Operation.objects.get(link_slug=kwargs["op"])
        job = operation.job
         
        if "advance_to_next_button" in request.POST:
            jobLogJson = loads(job.job_log)
            jobLogJson[stdDateTime()] = "Query Submitted " + str(operation)
            job.job_log = dumps(jobLogJson)
            job.save()
        elif "undo_last_button" in request.POST:
            jobLogJson = loads(job.job_log)
            
            popped = jobLogJson.pop(max(jobLogJson.keys()))
            print(popped)
            
            job.job_log = dumps(jobLogJson)
            job.save()
            
             
        context = self.template_args(kwargs["op"])
        context["submit"] = "post"

        return render(request, self.template, context)
        
        


"""
class Login(View):
    template = 'login.html'
    
    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template, {'form': form})
"""
