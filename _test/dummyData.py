import pandas as pd
from dateutil.parser import parse
headers = {
    "work_no": ["W/21704"]*5,
    "worker": ["Tim", "Greg", None, None, None],
    "location": ["Release", "T6", "Sub-Con", "Insp - Goods In", "Packing"],
    
    "issue_no": ["A"]*5,
    "op_no": [5, 10, 20, 40, 60],
    "part_no": [245, 384, 128, 243, 214],
    "company": ["Eg Inc"]*5,
    "job_name": ["Valve"]*5,
    "op_name": ["Release to Production",
               "Turn General",
               "Sub-Contract Companies",
               "Inspection at Goods In of Sub-Con Parts",
               "Packing"],    
    "quantity": [50]*5,
    "drg_no": ["120.482.04"]*5,    
    "start_time": ["28/04/2022  10:36:00",
                  "29/04/2022  13:45:37",
                  "30/04/2022  08:23:22",
                  "10/05/2022  15:22:15",
                  "11/05/2022  11:08:58"],
    "planned_set": [0, 210, None, 0, 15],
    "planned_run": [0, 1200, None, 30, 75],
    "end_time": [None, None, "08/04/2022 12:03:14", None, None],
    "insp_bool": [False, True, False, False, False],
    "op_note": ["Note " + str(i) for i in [1,2,3,4,5]]
}

dummyDF = pd.DataFrame(headers)
dummyDF.index.rename("upload_id", inplace=True)
dummyDF.to_csv(r"C:\Users\alexb\OneDrive - University of Cambridge\Long Project\DummyData.csv")


def row_to_dict(row, dateCols):
    rowDict = row.to_dict()
    for col in dateCols:
        rowDict[col] = parse(rowDict[col]).strftime("%Y-%m-%d %H:%M") if rowDict[col] else None
    print(rowDict)


loadDF = pd.read_csv(r"C:\Users\alexb\OneDrive - University of Cambridge\Long Project\DummyData.csv")
dateCols = ["start_time", "end_time"]
loadDF = loadDF.where(pd.notnull(loadDF), None)
loadDF.apply(row_to_dict, axis=1, 
             dateCols = ["start_time", "end_time"])

print(loadDF)




