import sqlite3
import csv

conn = sqlite3.connect('database copy 2.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM shrinkage")

with open("export.csv", "w") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)



