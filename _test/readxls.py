import os
import xlrd
import pandas as pd


filename = r"C:\Users\alexb\OneDrive - University of Cambridge\Long Project\From Lipco\Alex 2.xls"


book = pd.ExcelFile(filename)

"""
df = book.parse(book.sheet_names[0])
col0 = df.columns.values.tolist()[0]
print(col0)
val = df[col0].values[0]
print(val)"""
# print(df)

renameDict = {"Order No.": "work_no",
              "Part No.": "part_no",
              "Qty.": "quantity",
              "Operation Name": "name",
              "Start Time": "start_time",
              "End Time": "end_time",
              "Op. No.": "op_no"}


def row_dict(row, location):
    row["issue_no"] = row["work_no"][-1]
    row["work_no"] = row["work_no"][:-2]
    row["location"] = location
    row["company"] = "not supplied"
    row["job_name"] = "not supplied"
    row["worker"] = "Greg"
    for k in row.keys():
        if "Unnamed" in k:
            del row[k]
    del row["Product"]
    del row["Op. Progress"]
    return row

mainDF = pd.DataFrame()

for sheet in book.sheet_names:
    df = book.parse(sheet)
    col0 = df.columns.values.tolist()[0]
    location = df[col0].values[0]
    print(location)
    df2 = book.parse(sheet, header=3)
    df2.rename(columns=renameDict, inplace=True)
    print(df2)
    df3 = df2.apply(row_dict, axis=1, location=location)
    mainDF = pd.concat([mainDF, df3], axis=0)

mainDF.to_csv("LipcoOpData.csv", index=False)
exit()

dfs = [book.parse(sheet, header=3) for sheet in book.sheet_names]

for df in dfs[0:1]:
    print(df)


book = xlrd.open_workbook(filename)
for sh in book.sheets()[0:1]:
    print(sh)
    name = sh.cell_value(rowx=1, colx=0)
    print(name)
    print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
"""
print("The number of worksheets is {0}".format(book.nsheets))
print("Worksheet name(s): {0}".format(book.sheet_names()))
sh = book.sheet_by_index(0)
print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
print("Cell A2 is {0}".format(sh.cell_value(rowx=1, colx=0)))
for rx in range(sh.nrows):
    print(sh.row(rx))"""
