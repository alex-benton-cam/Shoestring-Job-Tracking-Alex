from ast import operator
from datetime import datetime
from logging import exception
from time import sleep
from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django import forms
from django.db.models import ForeignKey

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import reverse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from numpy import disp
from requests import request, session
from django.conf import settings

from .models import Operation, Job, Worker, Location, ScrapCode
import pandas as pd
from core.utils import *
from json import dumps, loads
from pprint import pprint
import re
import os
from io import BytesIO as IO
from django.utils.safestring import mark_safe


def dbprint(*args):
    print("----------")
    for arg in args:
        pprint(arg)
    print("----------")


def detail_view_exists(request, model, **kwargs):
    modelName = model.__name__
    try:
        slug = kwargs["link_slug"]
        try:
            object = model.objects.get(link_slug=slug)
            return object

        except ObjectDoesNotExist:
            messages.error(
                request, "{} {} does not exist".format(modelName, slug))
            return redirect("{}s".format(modelName.lower()))

    except:
        messages.error(request, "Failed to get operation ID from url")
        return redirect("{}s".format(modelName.lower()))


class Index(View):
    template = "_index.html"

    def get(self, request):
        return render(request, self.template)


""""""


class UploadLocs(View):

    template = "upload.html"

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        return redirect("locations")

        if "create_workers_button" in request.POST:

            csv_file = request.FILES["csv_file"]

            if not csv_file.name.endswith(".csv"):
                messages.warning(request, "A .csv file must be uploaded")
                return HttpResponseRedirect(reverse("upload"))

            def import_loc(row, model=Operation, dateCols=[], modelDict={}):

                rowDict = row.to_dict()
                obj = Location(**rowDict)
                obj.save()

            loadDF = pd.read_csv(csv_file)
            loadDF = loadDF.where(pd.notnull(loadDF), None)
            loadDF.index.rename("upload_id", inplace=True)
            loadDF.apply(import_loc, axis=1)

            return redirect("locations")


class MgSetup(View):
    template = "mg_Setup.html"
    models = [Location, Worker, ScrapCode]

    def import_row(self, row, mod, request):

        try:
            rowDict = row.to_dict()
            obj = mod(**rowDict)
            obj.save()
            return False
        except Exception as e:
            messages.error(
                request, "Upload failed at row <{}> - -  Error message: <{}>".format(str(list(row)), str(e)))
            return True

    def get(self, request):

        context = []

        def CCtoString(str):
            return(" ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)))

        for model in self.models:
            contextDict = {
                "name": model.__name__,
                "friendly": CCtoString(model.__name__),
                "lower": CCtoString(model.__name__).lower(),
                "example_fp": "{}assets/{}_example.csv".format(settings.STATIC_URL, model.__name__.lower()).lstrip("/"),
                "count": model.objects.count(),
            }
            context.append(contextDict)

        return render(request, self.template, {"context": context})

    def post(self, request):

        dbprint(request.POST)
        try:
            type = [p for p in ["download", "upload",
                                "example"] if p in request.POST][0]
            model = [m for m in self.models if m.__name__ in request.POST[type]][0]
            dbprint(type, model)

            if type == "example":

                path = os.path.join(settings.BASE_DIR,
                                    request.POST["filepath"])
                try:

                    with open(path, 'rb') as fh:
                        response = HttpResponse(
                            fh.read(), content_type="text/csv", charset="utf-8")
                        response['Content-Disposition'] = 'attachment; filename=' + \
                            os.path.basename(path)
                        return response
                except:
                    messages.error(request, "Error in accessing file")
                    return redirect("mgsetup")

            elif type == "download":
                qs = model.objects.all()
                displayFields = [f.name for f in model._meta.get_fields()
                                 if hasattr(model._meta.get_field(f.name), "verbose_name")
                                 and getattr(model._meta.get_field(f.name), "editable", True)
                                 and not isinstance(model._meta.get_field(f.name), ForeignKey)]

                queryData = list(qs.values(*displayFields))
                queryDataDF = pd.DataFrame(queryData)
                csv_file = IO()
                queryDataDF.to_csv(csv_file, index=False)

                print(csv_file)
                response = HttpResponse(
                    csv_file.getvalue(), content_type="text/csv", charset="utf-8")
                response['Content-Disposition'] = 'attachment; filename=existing_{}_data.csv'.format(
                    model.__name__)
                return response.Red

            elif type == "upload":

                try:
                    csv_file = request.FILES["csv_file"]

                    if not csv_file.name.endswith(".csv"):
                        messages.warning(
                            request, "A .csv file must be uploaded")
                        return redirect("mgsetup")

                    dbprint(model)

                    loadDF = pd.read_csv(csv_file, index_col=False)
                    loadDF = loadDF.where(pd.notnull(loadDF), None)
                    #loadDF.index.rename("upload_id", inplace=True)
                    errors = loadDF.apply(
                        self.import_row, axis=1, args=(model, request))

                    if True not in list(errors):
                        messages.success(request, "Successful Upload")

                    if model == Location:
                        try:
                            for id in (Location.START, Location.END, Location.INTERIM):
                                rowDict = {"loc_id": id,
                                           "name": id, "many_jobs": True}
                                loc = Location(**rowDict)
                                loc.save()
                        except Exception as e:
                            messages.error(
                                request, "Could not add 'unreleased' and 'finished' locations " + str(e))

                    return redirect("mgsetup")

                except Exception as e:

                    messages.error(
                        request, "Upload of {} failed: {}".format(model.__name__, e))
        except Exception as e:

            messages.error(request, "Invalid post request {}".format(e))
            return redirect("mgsetup")

        return redirect("mgsetup")


class UploadOps(View):
    template = "upload.html"

    def import_op(self, row, dateCols=[]):
        rowDict = row.to_dict()
        for col in dateCols:
            rowDict[col] = stdDateTime(rowDict[col]) if rowDict[col] else None

        jobFields = ["work_no", "company", "job_name", "quantity"]

        try:
            # Get job object
            parentJob = Job.objects.get(work_no=rowDict["work_no"])

        except ObjectDoesNotExist:
            # Create Job object if not already existing
            jobDict = {key: rowDict[key] for key in jobFields}
            parentJob = Job(**jobDict)
            parentJob.save()
            parentJob.add_entry("Job uploaded to Shoestring Job Tracking")

            for i, n in enumerate([0, 99]):

                opDict = {"job": parentJob,
                          "op_no": n,
                          "name": (Location.START, Location.END)[i],
                          "active": (True, False)[i],
                          "display": False,
                          "status": (Operation.ACTIVE, Operation.PENDING)[i],
                          "issue_no": rowDict["issue_no"],
                          "location": Location.objects.get(loc_id=(Location.START, Location.END)[i])}

                obj = Operation(**opDict)
                obj.save()

                if i == 0:
                    obj.check_in(Location.objects.get(loc_id=(Location.START)))
                    # parentJob.update()

        finally:
            # Change op dict to reflect job creation
            rowDict["job"] = parentJob

            for field in jobFields:
                rowDict.pop(field, None)

        if rowDict["worker"]:
            try:
                parentWorker = Worker.objects.get(name=rowDict["worker"])
                rowDict["worker"] = parentWorker
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "Worker '" +
                    rowDict["worker"] + "' does not Exist"
                )
                rowDict["worker"] = None

        if rowDict["location"]:
            try:
                parentLocation = Location.objects.get(name=rowDict["location"])
                rowDict["location"] = parentLocation
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "Location '" +
                    rowDict["location"] + "' does not Exist"
                )
                rowDict["location"] = None

        obj = Operation(**rowDict)
        # obj.save()
        obj.phase = Operation.PENDING if obj.insp_bool else Operation.NONE
        obj.save()

        # Create interim inspection operation, based on a copy of initial obj
        if obj.insp_bool:
            obj.is_interim = True
            obj.insp_bool = False
            obj.location = Location.objects.get(loc_id=Location.INTERIM)
            obj.op_note = "Operation added automatically"
            obj.name = "Interim inspection for {}".format(str(obj.op_id))
            obj.end_time = None
            obj.start_time = None
            obj.planned_run = None
            obj.planned_set = None
            obj.worker = None
            obj.status = None
            obj.save()

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.warning(request, "A .csv file must be uploaded")
            return HttpResponseRedirect(reverse("upload"))

        loadDF = pd.read_csv(csv_file)
        loadDF = loadDF.where(pd.notnull(loadDF), None)
        loadDF.index.rename("upload_id", inplace=True)

        loadDF.apply(self.import_op, axis=1, dateCols=[
                     "start_time", "end_time"])

        return redirect("operations")


class ModelView(View):

    model = None
    template = "_datatable.html"

    def get_object(self, queryset=None):
        return queryset.get(model=self.model)

    def get(self, request):

        query = None

        if self.model == Operation:
            query = Operation.objects.filter(display=True)
            fieldDict = {
                "job": {"href": "job_id__abs_link"},
                "op_no": {"href": "abs_link"},
                "name": {},
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
                "operation_id__op_id": {"verbose": "Current Op", "href": "operation_id__abs_link"},
                "operation_id__status": {"verbose": "Op Status"},
                "operation_id__location_id__name": {"verbose": "Current Location", "href": "operation_id__location_id__abs_link"},
            }

        elif self.model == Worker:
            fieldDict = {
                "name": {"href": "abs_link"},
            }

        elif self.model == Location:
            fieldDict = {
                "loc_id": {"href": "abs_link"},
                "name": {},
                "many_jobs": {},
                "worker": {},
            }

        else:
            displayFields = [f.name for f in self.model._meta.get_fields()
                             if hasattr(self.model._meta.get_field(f.name), "verbose_name")
                             and f.name != "link_slug"]
            fieldDict = {k: {} for k in displayFields}

        query = query if query is not None else self.model.objects.all()

        fieldDict, queryData = get_datatable(fieldDict, query, self.model)

        return render(
            request, self.template, {
                "fieldDict": fieldDict, "queryData": queryData}
        )

class OpDetail(View):

    template = "op_operation.html"
    model = Operation


    def template_args(self, link):

        operation = Operation.objects.get(link_slug=link)

        fieldDict = {
            # "op_id": {"verbose": "Operation", "href": "abs_link"},
            "job_id__work_no": {"verbose": "Job", "href": "job_id__abs_link"},
            "job_id__job_name": {},
            "job_id__company": {},
            "phase": {},
            "insp_bool": {},
            "part_no": {},
            "job_id__quantity": {},
            "drg_no": {},
            "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
            "start_time": {},
            "end_time": {},
            "planned_set": {},
            "planned_run": {},
        }

        linkFields = [v.get("href")
                      for v in fieldDict.values() if v.get("href")]
        opData = {f: get_value(operation, f)
                  for f in list(fieldDict.keys()) + linkFields}

        for field_str in fieldDict.keys():
            if "verbose" not in fieldDict[field_str]:
                fieldDict[field_str]["verbose"] = get_verbose(
                    self.model, field_str)

        scrapCodes = {s.id: s.name for s in ScrapCode.objects.all()}

        return {"fieldDict": fieldDict,
                "opData": dict(opData),
                "jobLog": get_job_log(operation.job),
                "scrapCodes": scrapCodes,
                }

    def get(self, request, *args, **kwargs):
        operation = Operation.objects.get(link_slug=kwargs["link_slug"])
        context = self.template_args(operation.link_slug)
        return render(request, self.template, context)

    def post(self, request):
        messages.info(request, "POST not implemented")
        return redirect("operations")


class JobDetail(View):
    template = "_job.html"

    def get(self, request, *args, **kwargs):

        result = detail_view_exists(request, Job, **kwargs)
        if not isinstance(result, Job):
            return result
        else:

            job = Job.objects.get(link_slug=kwargs["link_slug"])
            # job.update()

            fieldDict = {

                "work_no": {"href": "abs_link"},
                "operation_id__op_id": {"verbose": "Current Operation", "href": "operation_id__abs_link"},
                "location_id__name": {"verbose": "Current Location", "href": "location_id__abs_link"},
                "job_name": {},
                "company": {},
                "quantity": {},
            }

            operation = str(job.operation)

            linkFields = [v.get("href")
                          for v in fieldDict.values() if v.get("href")]
            jobData = {f: get_value(job, f)
                       for f in list(fieldDict.keys()) + linkFields}

            for field_str in fieldDict.keys():
                if "verbose" not in fieldDict[field_str]:
                    fieldDict[field_str]["verbose"] = get_verbose(
                        job, field_str)

            opFieldDict = {
                "op_id": {"href": "abs_link"},
                "op_no": {},
                "status": {},
                "phase": {},
                "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
                "name": {},
                "worker": {"href": "worker_id__abs_link"},
            }

            opQuery = job.operation_set.all()
            opFieldDict, opData = get_datatable(
                opFieldDict, opQuery, Operation)

            context = {"operation": operation,
                       "fieldDict": fieldDict,
                       "jobData": jobData,
                       "jobLog": get_job_log(job),
                       "opFieldDict": opFieldDict,
                       "opData": opData}

            return render(request, self.template, context)


class LocDetail(View):
    template = "_location.html"

    def get(self, request, *args, **kwargs):

        result = detail_view_exists(request, Location, **kwargs)
        if not isinstance(result, Location):
            return result
        else:
            location = result

        query = location.operation_set.all()
        fieldDict = {
            "job": {"href": "job_id__abs_link"},
            "op_no": {"href": "abs_link"},
            "name": {},
            "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
            "worker": {"href": "worker_id__abs_link"},
            "job_id__quantity": {},
        }
        fieldDict, data = get_datatable(fieldDict, query, Operation)
        context = {"location": location.link_slug,
                   "fieldDict": fieldDict,
                   "data": data}

        return render(request, self.template, context)


class Op_OperationDash(View):

    template = "op_operation.html"
    model = Operation
    confirm_modal = "operation_confirm_modal"

    def template_args(self, link):

        operation = Operation.objects.get(link_slug=link)

        fieldDict = {
            # "op_id": {"verbose": "Operation", "href": "abs_link"},
            "job_id__work_no": {"verbose": "Job", "href": "job_id__abs_link"},
            "job_id__job_name": {},
            "job_id__company": {},
            "phase": {},
            "insp_bool": {},
            "part_no": {},
            "job_id__quantity": {},
            "drg_no": {},
            "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
            "start_time": {},
            "end_time": {},
            "planned_set": {},
            "planned_run": {},
        }

        linkFields = [v.get("href")
                      for v in fieldDict.values() if v.get("href")]
        opData = {f: get_value(operation, f)
                  for f in list(fieldDict.keys()) + linkFields}

        for field_str in fieldDict.keys():
            if "verbose" not in fieldDict[field_str]:
                fieldDict[field_str]["verbose"] = get_verbose(
                    self.model, field_str)

        scrapCodes = {s.id: s.name for s in ScrapCode.objects.all()}

        return {"fieldDict": fieldDict,
                "opData": dict(opData),
                "jobLog": get_job_log(operation.job),
                "scrapCodes": scrapCodes,
                }

    def get(self, request, *args, **kwargs):

        try:
            location = Location.objects.get(
                loc_id=request.session['location_id'])
            dbprint(location)
            try:

                operation = location.operation_set.get(status=Operation.ACTIVE)
                context = self.template_args(operation.link_slug)
                context["submit"] = "get"
                context["op_id"] = operation.op_id
                context["loc_id"] = location.loc_id
                context["loc_name"] = location.name
                context["job_title"] = str(operation.job)
                return render(request, self.template, context)

                # print(request.session["current_operation"])
                #operation = Operation.objects.get(op_id=request.session["current_operation"])

            except:
                messages.warning(
                    request, "An operation must be checked in to first")
                return redirect("machine")

        except:
            messages.warning(request, "No machine active on device")
            return redirect("factory")

    def post(self, request, *args, **kwargs):
        post = request.POST
        dbprint(post)

        try:
            location = Location.objects.get(loc_id=post["loc_id"])
        except Exception as e:
            messages.error(request, "Can't Retrieve location " + str(e))

        try:
            operation = Operation.objects.get(op_id=post["op_id"])
            job = operation.job
        except Exception as e:
            messages.error(request, "Can't Retrieve operation " + str(e))

        if "advance_to_next_button" in post:

            if operation.phase is not None:

                if operation.phase != Operation.COMPLETE:

                    phaseNo = Operation.PHASE_LIST.index(operation.phase)
                    nextPhase = Operation.PHASE_LIST[phaseNo+1]
                    action = "Confirm"

                    if operation.phase == Operation.PENDING:
                        title = "Begin Setup"
                        message = "Confirm Setup of operation {} has begun".format(
                            operation.op_id)
                        
                    elif operation.phase == Operation.ONEOFF:
                        title = "Move to Interim Inspection"
                        message = "Confirm first off of operation {} is complete and that it is being sent to interim inspection".format(operation.op_id)
                        

                    elif operation.phase == Operation.FULLBATCH:
                        title = "Operation Complete"
                        message = "Confirm operation {} is complete".format(
                            operation.op_id)

                    else:
                        title = "Advance Operation to Next Phase"
                        message = "Confirm phase '{}' of operation {} is complete and advance to '{}'".format(
                            operation.phase, operation.op_id, nextPhase)
                        action = "Advance to {}".format(nextPhase)

                    modalDict = {
                        "name": "advance_modal",
                        "message": message,
                        "title": title,
                        "data": {"next_phase": nextPhase,
                                 "curr_phase": operation.phase,
                                 "op_id": operation.op_id,
                                 "loc_id": location.loc_id},
                        "action": action}

                    create_confirm_modal(request, **modalDict)
                    return redirect("operation")

                # phase = "Complete"
                else:
                    messages.error(
                        request, "Should not be able to advance a complete job")

            # Operation does not have interim inspection
            else:
                messages.warning(request, "Operation cannot be advanced")
                return redirect("operation")

            dbprint(operation.phase)
            dbprint([x[0] for x in Operation.PHASE_CHOICES])

            job.add_entry("Query Submitted " + str(operation))
            return redirect("operation")

        elif "undo_last_button" in post:
            latest = job.entry_set.latest("dt")
            latest.undone = True
            latest.save()
            return redirect("operation")

        elif "report_scrap_button" in post:
            dbprint(post)
            data = dumps({"scrapCode": post["scrapCode"],
                          "quantity": post["quantity"],
                          "loc_id": post["loc_id"],
                          "op_id": post["op_id"]})
            operation.add_entry("{} scrap reported ({})".format(post["quantity"], post["scrapCode"]),
                                data=data)
            return redirect("operation")

        elif "call_manager_button" in post:
            messages.info(request, "Call Manager not implemented")
            return redirect("operation")

        elif "advance_modal" in post:

            if post["next_phase"] == Operation.COMPLETE:
                operation.status = Operation.COMPLETE
                messages.success(
                    request, "Operation {} completed".format(post["op_id"]))
                
            elif post["next_phase"] == Operation.INTERIM:
                messages.success(request, "Operation {} moved to {}".format(
                    post["op_id"], post["next_phase"]))
                
                insp_op = Operation.objects.get(op_id=operation.op_id+"I")
                insp_op.status = Operation.PENDING
                insp_op.save()
                
                
            else:
                messages.success(request, "Operation {} moved to {} phase".format(
                    post["op_id"], post["next_phase"]))

            operation.phase = post["next_phase"]
            operation.save()
            operation.add_entry("{} phase begun".format(operation.phase))

            return redirect("operation")

        else:
            messages.error(request, "Invalid post request: " + str(post))
            return redirect("operation")


class Op_MachineView(View):

    template = None
    location = None
    confirm_modal = "machine_confirm_modal"
    buffer_modal = "confirm_buffer_modal"

    def machine_check_in(self, request, op, loc, many_jobs=False):
        request.session['current_operation'] = op.op_id
        message = "Operation '{}' checked in at '{}.'".format(
            op.op_id, loc.name)
        messages.success(request, message)
        op.check_in(loc)
        
        if many_jobs:
            return redirect("machine")
        else:        
            return redirect("operation")

    def get(self, request, *args, **kwargs):
          
        try:
            location = request.session["location_id"]
            location = Location.objects.get(loc_id=location)
        except:
            messages.warning(
                request, "A location must be selected to check in to a job")
            return redirect("factory")
        
        queryPending = location.operation_set.all().filter(status=Operation.PENDING)
        queryActive = location.operation_set.all().filter(status=Operation.ACTIVE)
        queryComplete = location.operation_set.all().filter(status=Operation.COMPLETE)

        
        fieldDict = {
            "op_id": {},
            "job": {"href": "job_id__abs_link"},
            "op_no": {"href": "abs_link"},
            "status": {},
            "name": {},
            "job_id__location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
            "worker": {"href": "worker_id__abs_link"},
            "job_id__quantity": {},
            "start_time": {},
        }

        pendFieldDict, pendData = get_datatable(
            fieldDict, queryPending, Operation)

        if queryActive:
            actFieldDict, actData = get_datatable(
                fieldDict, queryActive, Operation)
        else:
            actFieldDict, actData = (None, None)

        #fieldDict.pop("op_id")
        compFieldDict, compData = get_datatable(
            fieldDict, queryComplete, Operation)

        dbprint(compData)

        context = {"pendFieldDict": pendFieldDict,
                   "pendData": pendData,
                   "actFieldDict": actFieldDict,
                   "actData": actData,
                   "compFieldDict": compFieldDict,
                   "compData": compData,
                   "locName": location.name}
        
        if location.many_jobs:
            self.template = "op_buffer.html"
            
            
                        
        else:
            self.template = "op_machine.html"
        
        
        
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):

        #validPosts = ["check_in_button", "confirm_skip_modal"]
        if "check_in_button" in request.POST or "add_to_buffer_button" in request.POST:
            
            # Try if checked into a location            
            try:
                device_location = Location.objects.get(loc_id=request.session["location_id"])

                # If operation ID is valid
                try:
                    operation = Operation.objects.get(op_id=request.POST["operation_id"])
                
                # Try finding job if work_no provided
                except ObjectDoesNotExist:                    
                    try:    
                        job = Job.objects.get(work_no=request.POST["operation_id"])
                        
                        # Try getting operation from list of pending jobs 
                        try:
                            opsatloc = job.operation_set.filter(location=device_location)
                            pendingops = opsatloc.filter(status=Operation.PENDING)
                            operation = pendingops.order_by("op_no")[0]
                        
                        except Exception as e:
                            messages.warning(
                                request, "No pending operations from job {} at current machine. {}".format(request.POST["operation_id"]), e)
                            return redirect("machine") 
                        
                    except ObjectDoesNotExist:
                        messages.warning(
                            request, "Invalid operation or job ID: {}".format(request.POST["operation_id"]))
                        return redirect("machine")      
                
                finally:            
                    active_ops = device_location.operation_set.filter(
                        status=Operation.ACTIVE)
                    if not active_ops or device_location.many_jobs:
                        # or device_location.many_jobs == True:

                        # If trying to check into a completed job
                        if operation.status != Operation.COMPLETE:

                            skippedOps = operation.job.operation_set.filter(
                                status=Operation.PENDING, op_no__lt=operation.op_no)
                            wrongLoc = False if operation.location == device_location else True
                            
                            # Change name of modal based on adding to buffer or machine
                            modalName = self.buffer_modal if device_location.many_jobs else self.confirm_modal
                            
                            
                            
                            # Planned next operation Checked in to planned location
                            if not skippedOps and not wrongLoc:

                                return self.machine_check_in(request, operation, device_location, many_jobs=device_location.many_jobs)

                            # Check in will skip operations and set operation to a different machine
                            elif skippedOps and wrongLoc:
                                message = "By checking in operation {}, you will mark the following operations as complete".format(
                                    operation.op_id)
                                message_bottom = "The operation is also planned for a different location: {}".format(
                                    operation.location)
                                table = [[o.op_id, o.location.name, o.name]
                                        for o in skippedOps]
                                modalDict = {
                                    "name": modalName,
                                    "message": message,
                                    "message_bottom": message_bottom,
                                    "table": table,
                                    "title": "Check in will skip operations and set operation to a different machine",
                                    "data": {"op_id": operation.op_id,
                                            "location": device_location.loc_id},
                                    "action": "Confirm check in at {} and skip {} ops".format(device_location.name, len(skippedOps))
                                }
                                create_confirm_modal(request, **modalDict)
                                return redirect("machine")

                            # Check in will set operation to a different machine
                            elif not skippedOps and wrongLoc:
                                message = "Operation {} is allocated to: {}".format(
                                    str(operation), operation.location.name,)

                                modalDict = {
                                    "name": modalName,
                                    "message": message,
                                    "title": "Check in will set operation to a different machine",
                                    "data": {"op_id": operation.op_id,
                                            "location": device_location.loc_id},
                                    "action": "Confirm check in at {}".format(device_location.name)
                                }
                                create_confirm_modal(request, **modalDict)
                                return redirect("machine")

                            # Check in will skip operations
                            elif skippedOps and not wrongLoc:
                                message = "By checking in operation {}, you will mark the following operations as complete".format(
                                    operation.op_id)
                                table = [[o.op_id, o.location.loc_id, o.name]
                                        for o in skippedOps]
                                modalDict = {
                                    "name": modalName,
                                    "message": message,
                                    "table": table,
                                    "title": "Check in will skip operations",
                                    "data": {"op_id": operation.op_id,
                                            "location": device_location.loc_id},
                                    "action": "Confirm skip {} ops".format(len(skippedOps))
                                }
                                create_confirm_modal(request, **modalDict)
                                return redirect("machine")

                        else:
                            messages.warning(request,
                                            "Cannot check in to an already completed operation")
                            return redirect("machine")
                    else:
                        messages.warning(request,
                                        "There is already a job active at {}: {}.".format(device_location.name, device_location.operation_set.all()[0].op_id))

                        return redirect("operation")



                        


            except ObjectDoesNotExist:
                messages.warning(
                    request, "Location should be set before checking in to a job")
                return redirect("factory")
        
        elif "add_to_buffer_button" in request.POST:
            pass
            
        
        elif self.confirm_modal in request.POST:

            operation = Operation.objects.get(op_id=request.POST["op_id"])
            location = Location.objects.get(loc_id=request.POST["location"])

            return self.machine_check_in(request, operation, location, many_jobs=location.many_jobs)

        else:
            print(request.POST)
            messages.error(request, "Invalid post request")
            return redirect("machine")


class Op_FactoryFloor(View):

    template = "op_factory.html"

    def get(self, request, *args, **kwargs):

        query = Location.objects.all()
        fieldDict = {
            "loc_id": {"href": "abs_link"},
            "name": {},
            "worker": {},
        }
        fieldDict, queryData = get_datatable(fieldDict, query, Location)
        context = {"fieldDict": fieldDict,
                   "data": queryData}

        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):

        if "select_machine_button" in request.POST:

            try:
                location = Location.objects.get(
                    loc_id=request.POST["machine_id"])
                request.session['location_id'] = location.loc_id
                dbprint(request.session['location_id'])
                return redirect("machine")
            except:
                if request.POST["machine_id"].lower() == "clear":
                    request.session['location_id'] = None
                    messages.success(request, "Location Cookie Cleared")
                else:
                    messages.warning(
                        request, "Please enter a valid location ID")
                return redirect("factory")

        else:
            print(request.POST)
            messages.error(request, "Invalid post request")
            return(redirect("factory"))


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
