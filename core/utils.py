from datetime import datetime
from dateutil.parser import parse
from django.db.models.base import ModelBase
from django.apps import apps
from json import dumps
from django.contrib import messages


def get_job_log(job):
    log = job.entry_set.all().order_by("-id")
    
    displayLog = []
    for entry in log:
        op_id = entry.operation.op_id if entry.operation else "-"
        displayLog.append([stdDateTime(entry.dt), entry.message, op_id] )
    
    return displayLog

def create_confirm_modal(request, name="confirm_modal", title="Title", message="Message", message_bottom="", table=None, data=None, action="Confirm"):

    modalDict = {
        "name": name,
        "message": message,
        "title": title,
        "table": table,
        "data": dumps(data),
        "message_bottom": message_bottom,
        "action": action
    }
    messages.info(request, dumps(modalDict), extra_tags="modal_confirm")


def stdDateTime(dt=None):
    if dt == None or dt == "now":
        dt = datetime.now()
    elif isinstance(dt, str):
        dt = parse(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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


def get_datatable(fieldDict, query, model):
    for field_str in fieldDict.keys():
        if "verbose" not in fieldDict[field_str]:
            fieldDict[field_str]["verbose"] = get_verbose(model, field_str)

    linkFields = [v.get("href") for v in fieldDict.values() if v.get("href")]
    queryFields = list(fieldDict.keys()) + linkFields

    queryData = list(query.values(*[f for f in queryFields if "__" not in f]))

    for i in range(len(queryData)):
        for field in [f for f in queryFields if "__" in f]:
            queryData[i][field] = get_value(query[i], field)

        for field in queryData[i].keys():
            if type(queryData[i][field]) is datetime:
                queryData[i][field] = stdDateTime(queryData[i][field])

    return fieldDict, queryData
