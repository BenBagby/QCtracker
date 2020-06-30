import sqlite3


conn = sqlite3.connect('LIVE06302020 test.db')
cursor = conn.cursor()

loc_sel_sql = "SELECT * FROM shrinkage WHERE location=?"
loc_updt_sql = "UPDATE shrinkage SET location=? WHERE location=?"

#old_location = 'WR 06/S HP Bulk'
#new_location = 'WR 06'

#old_location = 'WR 12/2310'
#new_location = 'WR 12'

#old_location = 'WR 10'
#new_location = 'WR 20'

old_location = 'Harper/Kona A21'
new_location = 'Harper/Kona'


cursor.execute(loc_sel_sql,(old_location,))
fetch = cursor.fetchall()
for data in fetch:
    print(data)

print('\n')


cursor.execute(loc_updt_sql,(new_location, old_location))

cursor.execute(loc_sel_sql,(new_location,))
fetch = cursor.fetchall()
for data in fetch:
    print(data)

cursor.close()
conn.commit()
conn.close()

