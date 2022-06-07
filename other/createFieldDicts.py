from core.models import *

dicts = {
    "upload_ops_complete_jobs": '''{ 
        "work_no": {"href": "abs_link"}, 
        "status": {}, 
        "company": {}, 
        "job_name": {}, 
        "quantity": {}, 
        "operation_id__op_id": {"verbose": "Current Op", "href": "operation_id__abs_link"}, 
        "operation_id__status": {"verbose": "Op Status"}, 
        "operation_id__location_id__name": {"verbose": "Current Location", "href": "operation_id__location_id__abs_link"}, 
    }''',
    "all_operations_table": '''{
        "job": {"href": "job_id__abs_link"},
        "op_no": {"href": "abs_link"},
        "name": {},
        "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "worker": {"verbose": "Operator", "href": "worker_id__abs_link"},
        "job_id__quantity": {},
    }''',
    "all_jobs_table":  '''{
        "work_no": {"href": "abs_link"},
        "status": {},
        "company": {},
        "job_name": {},
        "quantity": {},
        "operation_id__op_id": {"verbose": "Current Op", "href": "operation_id__abs_link"},
        "operation_id__status": {"verbose": "Op Status"},
        "operation_id__location_id__name": {"verbose": "Current Location", "href": "operation_id__location_id__abs_link"},
    }''',
    "all_workers_table": '''{
        "name": {"href": "abs_link"},
    }''',
    "all_locations_table": '''{
        "loc_id": {"href": "abs_link"},
        "name": {},
        "many_jobs": {},
        "worker": {"verbose": "Operator"},
    }''',

    "job_detail_main": '''{
        "work_no": {"href": "abs_link"},
        "status": {"verbose": "Job Status"},
        "operation_id__op_id": {"verbose": "Current Operation", "href": "operation_id__abs_link"},
        "operation_id__status": {"verbose": "Operation Status"},
        "location_id__name": {"verbose": "Current Location", "href": "location_id__abs_link"},
        "job_name": {},
        "company": {},
        "quantity": {},
    }''',
    "job_detail_ops": '''{
        "op_id": {"href": "abs_link"},
        "op_no": {},
        "status": {},
        "phase": {},
        "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "name": {},
        "worker": {"href": "worker_id__abs_link"},
    }''',
    "location_detail_main": '''{
        "job": {"href": "job_id__abs_link"},
        "op_no": {"href": "abs_link"},
        "status": {"verbose": "Op Status"},
        "name": {},
        "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "worker": {"href": "worker_id__abs_link"},
        "job_id__quantity": {},
    }''',
    "worker_detail_main": '''{
        "job": {"href": "job_id__abs_link"},
        "op_no": {"href": "abs_link"},
        "status": {"verbose": "Op Status"},
        "name": {},
        "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "job_id__quantity": {},
    }''',
    "op_dash_tab_1": '''{
        # "op_id": {"verbose": "Operation", "href": "abs_link"},
        "job_id__work_no": {"verbose": "Job", "href": "job_id__abs_link"},
        "job_id__job_name": {},
        "job_id__company": {},
        "worker_id__name": {"verbose": "Operator"},
        "status": {},
        "phase": {},
        "part_no": {},
        "job_id__quantity": {},
        "drg_no": {},
        "location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "num_scrap": {}
    }''',
    "op_dash_tab_2": '''{
        "start_time": {},
        "end_time": {},
        "planned_set": {"suffix": "mins"},
        "planned_run": {"suffix": "mins"},
        "actual_start_time": {},
        "actual_end_time": {},
    }''',
    "op_dash_tab_2_extra": '''{
        "actual_set": {"suffix": "mins"},
        "actual_run": {"suffix": "mins"},
        "actual_oneoff": {"suffix": "mins"},
        "actual_insp": {"suffix": "mins"},
        "actual_fullbatch": {"suffix": "mins"},
        "last_action_time": {}
    }''',
    "machine_dash": '''{
        "op_id": {},
        "job": {"href": "job_id__abs_link"},
        "op_no": {"href": "abs_link"},
        "status": {},
        "name": {},
        "job_id__location_id__name": {"verbose": "Location", "href": "location_id__abs_link"},
        "worker": {"href": "worker_id__abs_link"},
        "job_id__quantity": {},
        "start_time": {},
    }''',
}

modelNames = {
    "upload_ops_complete_jobs": "Job",
    "all_operations_table": "Operation",
    "all_jobs_table":  "Job",
    "all_workers_table": "Worker",
    "all_locations_table": "Location",
    "job_detail_main": "Job",
    "job_detail_ops": "Operation",
    "location_detail_main": "Location",
    "worker_detail_main": "Worker",
    "op_dash_tab_1": "Operation",
    "op_dash_tab_2": "Operation",
    "op_dash_tab_2_extra": "Operation",
    "machine_dash": "Operation",
}

def runmain():

    from pprint import pprint
    
    for id, fieldDict in dicts.items():
        d = {"name": " ".join(id.split("_")).title(),
            "model": modelNames[id],
            "id": id,
            "data": fieldDict}
        obj = FieldDict(**d)
        obj.save()
        print('''fieldDict = FieldDict.objects.get(id="{}").get()'''.format(id))
        print()
        

