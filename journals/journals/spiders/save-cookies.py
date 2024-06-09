import json
import csv
with open('newtest.json',"r",encoding="utf-8") as json_file, open('output.csv', 'w', newline='',encoding="utf-8") as csv_file:
    data1 = json.load(json_file)
    csv_writer = csv.writer(csv_file)
    for data in data1:
        csv_writer.writerow(data.keys())
        csv_writer.writerow([data[key] for key in data])