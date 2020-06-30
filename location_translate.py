import sqlite3


conn = sqlite3.connect('LIVE06302020 test.db')
cursor = conn.cursor()

loc_sel_sql = "SELECT * FROM shrinkage WHERE location=?"
loc_updt_sql = "UPDATE shrinkage SET location=? WHERE location=?"

old_location = 'WR 06/S HP Bulk'
new_location = 'WR 06'


cursor.execute(loc_sel_sql,(old_location,))
fetch = cursor.fetchall()
for data in fetch:
    print(data)


cursor.execute(loc_updt_sql,(new_location, old_location))

cursor.execute(loc_sel_sql,(new_location,))
fetch = cursor.fetchall()
for data in fetch:
    print(data)

