import pandas as pd
from dateutil.parser import parse
import numpy as np
from faker import Faker
fake = Faker()

valid_workers = ['Tim',
                 'Greg',
                 'Alex',
                 'Anthony',
                 'Steve Wallace',
                 'Eugene Waddlesworth',
                 'King Kong',
                 'Kylie',
                 'Tess from Accounting',
                 'Another Guy']

locations = {
    # 'Unreleased': False,
    # 'Finished': False,
    'Release': False,
    'PROGRAM': False,
    'TOOLING': False,
    'MT1': True,
    'T1 (Turn/Mill Bar Feed, Chuck)': True,
    'T2 (Turn/Mill Chuck)': True,
    'T3': True,
    'T4': True,
    'T5': True,
    'T6': True,
    'T7 (Turn/Mill Bar Feed Collet)': True,
    'T9': True,
    'G1': True,
    'G2': True,
    'G3': True,
    'MAT1': True,
    'I1 - i200': True,
    'I2 - i400': True,
    'M1 (5 AXIS)': True,
    'M2 (4 AXIS)': True,
    'M3 (4 AXIS)': True,
    'M4 (5 AXIS)': True,
    'M5 (4 AXIS)': True,
    'M6 (4 AXIS)': True,
    'M7 (4 AXIS)': True,
    'M8 (4 AXIS)': True,
    'M9 (3 AXIS)': True,
    'M10 (3 AXIS)': True,
    'M11 (4AXIS)': True,
    'M12 (MANUAL)': True,
    'DeBurr-Assy 1': False,
    'DeBurr-Assy 2': False,
    'Insp - 1': False,
    'Insp - 2': False,
    'Insp - Goods In': False,
    'Sub - Con': False,
    'Packing': False, }


companies = ["Manestical Energy Co", "Doover Industrial Systems", "Golden Triad Technology",
             "Maleo Manufacturing", "Zeus Produce Industries", "Manufacturing Corner", "Meteorite Manufacturers"]

issue_nums = ["A", "B", "C", "D", "E"]

objects = ["shawl",
           "pin",
           "harmonica",
           "controller",
           "sunglasses",
           "rock",
           "lamp shade",
           "sofa",
           "duffel bag",
           "knitting needles",
           "pickle jar",
           "soccer ball",
           "cookie tin",
           "bottle of glue",
           "cheese board",
           "boom box",
           "keyboard",
           "washing machine",
           "lock and key",
           "hand bag"]

dateFormats = ['%Y-%m-%d %H:%M:%S',
               '%Y-%m-%d %H:%M:%S.%f',
               '%Y-%m-%d %H:%M',
               '%m/%d/%Y %H:%M:%S',
               '%m/%d/%Y %H:%M:%S.%f',
               '%m/%d/%Y %H:%M',
               '%m/%d/%y %H:%M:%S',
               '%m/%d/%y %H:%M:%S.%f',
               '%m/%d/%y %H:%M']


def rand_dt(dt):
    return dt.strftime(np.random.choice(dateFormats))


make_valid_data = True
if  make_valid_data != True:
    locations += {'Invalid Loc 1': False,
                  'Invalid Loc 2': True,
                  'Invalid Loc 3': False,
                  'M10': True,
                  'Assy2': False, }


data = []

for i in range(15):  # Num jobs
    work_no = "W/" + str(np.random.randint(0, 30000))
    op_no = 0
    company = np.random.choice(companies)
    job_name = np.random.choice(objects)
    quantity = np.random.randint(1, 500)
    drg_no = str(np.random.randint(1, 500)) + "." + \
        str(np.random.randint(1, 500)) + "." + str(np.random.randint(1, 500))
    start_time = fake.date_time_this_year(before_now=True, after_now=True)
    issue_no = np.random.choice(issue_nums)

    for i in range(np.random.randint(3, 10)):
        start_time += fake.time_delta(1)
        location = np.random.choice(list(locations.keys()))
        op_no += np.random.choice([5, 10]) 
        if i == 0:
            location  = "Release"
            op_no = 5        
        planned_set = int(np.random.random() * 60) if locations[location] else np.random.choice([None, 0])
        planned_run = int(np.random.random() * 120)
        end_time = start_time + fake.time_delta(1)
        insp_bool = np.random.choice(
            [True, False]) if locations[location] else False

        rowData = {

            "work_no": work_no,
            "worker": np.random.choice(valid_workers),
            "location": location,

            "issue_no": "A",
            "op_no": op_no,
            "part_no": np.random.randint(0, 2000),
            "company": company,
            "job_name": job_name,
            "name": str(op_no) + " " + fake.sentence(nb_words=5),
            "quantity": quantity,
            "drg_no": drg_no,
            "start_time": rand_dt(start_time),
            "planned_set": planned_set,
            "planned_run": planned_run,
            "end_time": rand_dt(end_time),
            "insp_bool": insp_bool,
            "op_note": fake.sentence(nb_words=10),
        }

        data.append(rowData)


dummyDF = pd.DataFrame(data)
dummyDF.index.rename("upload_id", inplace=True)
print(dummyDF)
dummyDF.to_csv(
    r"C:\Users\alexb\OneDrive - University of Cambridge\Long Project\DummyDataRandom3.csv")
