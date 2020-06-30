import sqlite3


conn = sqlite3.connect('LIVE06302020 test.db')
cursor = conn.cursor()

add_col = "ALTER TABLE shrinkage ADD COLUMN gor_applied_average REAL"
cursor.execute(add_col)


master_query = "select * from sqlite_master"
cursor.execute(master_query)
table_list = cursor.fetchall()

for table in table_list:
    print("Database Object Type: %s"%(table[0]))
    print("Database Object Name: %s"%(table[1]))
    print("Table Name: %s"%(table[2]))
    print("root Page: %s"%(table[3]))
    print("**SQL Statement**: %s"%(table[4]))