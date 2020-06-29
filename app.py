from tkinter import*
import sqlite3
from sqlite3 import Error
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import pandas as pd

import datetime
from dateutil.relativedelta import relativedelta

from Parser import ParserOCR


sql_create_shrinkage_table = """ CREATE TABLE IF NOT EXISTS `shrinkage` ( 
                                    `sample_id` TEXT NOT NULL,
                                    `sample_date` TEXT,
                                    `location` TEXT NOT NULL,
                                    `gor` REAL NOT NULL, 
                                    `shrinkage` REAL NOT NULL,
                                    `applied_average` REAL,
                                    `lower_limit` REAL,
                                    `upper_limit` REAL,  
                                    `status` REAL,
                                    `s_w` REAL,                                  
                                    PRIMARY KEY(`sample_id`)
                                    ); """


root = Tk()
root.title("Noble Shrinkage QC Tracker")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = 900
height = 500
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry('%dx%d+%d+%d' % (width, height, x, y))
root.resizable(0, 0)


def Database():
    global conn, cursor
    conn = sqlite3.connect('LIVE06232020 test.db')
    cursor = conn.cursor()
    cursor.execute(sql_create_shrinkage_table)


def Read():
    tree.delete(*tree.get_children())
    Database()
    cursor.execute("SELECT * FROM `shrinkage`")
    fetch = cursor.fetchall()
    for data in fetch:
        if data[8] == 'fail(include)':
            color_test = 'orange_flag'
        elif data[8] == 'fail(exclude)':
            color_test = 'red_flag'
        else:
            color_test = 'no_flag'
        tree.insert('', 'end', values=(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]), tags = (color_test,))
    tree.tag_configure('orange_flag', background = 'orange')
    tree.tag_configure('red_flag', background = 'red')
    cursor.close()
    conn.close()
    txt_result.config(text="Successfully read the data from database", fg="black")

def calculate_qc(folder_data):
    Database()
    
    sql_imp = "SELECT * from shrinkage WHERE location=? AND status NOT LIKE ?"
    folder_data_calc = []
    for data in folder_data:
        cursor.execute(sql_imp,(data['location'],'%'+'exclude'+'%'))
        names = [x[0] for x in cursor.description]
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=names)
        df = df.append(data,ignore_index = True)

        df['sample_date'] =pd.to_datetime(df.sample_date)
        df = df.sort_values(by='sample_date')
        df.reset_index(drop=True, inplace = True)
        df['status'] = df['status'].astype(str)

        df['status'].replace('nan', 'empty', regex = True, inplace = True)
        current_date = pd.to_datetime(data['sample_date'])

        time_series = pd.to_datetime(df['sample_date'])
        day1_time_series = time_series.apply(lambda dt: dt.replace(day = 1))
        filter3 =  day1_time_series >= (current_date + relativedelta(months=-6)).replace(day = 1)
        filter4 = time_series < current_date
        reduced_df = df.where(  pd.Series(filter3) & pd.Series(filter4) ) 
        
        applied_average = reduced_df['shrinkage'].astype(float).mean()
        lower_limit = applied_average * (1 - 0.04)
        upper_limit = applied_average * (1 + 0.04)

        if lower_limit <= float(data['shrinkage']) <= upper_limit:
            status = 'pass'
        else:
            status = 'fail(exclude)'

        #df = df.set_index('sample_id')
        #df.at[data['sample_id'], 'applied_average'] = rolling_mean2
        
        data.update({'applied_average':applied_average, 'lower_limit':lower_limit, 'upper_limit':upper_limit, 'status':status})

        folder_data_calc.append(data)
    return(folder_data_calc)

def Import():
    Database()
    dr = tkFileDialog.askdirectory()
    print(dr)
    #popup = Toplevel()
    folder_data = ParserOCR.get_folder_data(dr)
    print(folder_data)
    folder_data_calc = calculate_qc(folder_data)

    for data in folder_data_calc:
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join("`" + str(x).replace('/','_') + "`" for x in data.keys())
        values = ', '.join("'" + str(x).replace('/','/') + "'" for x in data.values())
        sql = "INSERT INTO `shrinkage` ( %s ) VALUES ( %s )" % (columns, values)
        print(sql)
        try:
            cursor.execute(sql)
        except sqlite3.IntegrityError as e:
            print("Integrity Error")
            print(e)
    cursor.close()
    conn.commit()
    conn.close()
    txt_result.config(text="Successfully imported data to database", fg="black")



def OnSelected(event):
    global mem_id
    curItem = tree.focus()
    contents =(tree.item(curItem))
    selecteditem = contents['values']
    mem_id = selecteditem[0]
    SAMPLEID.set("")
    ANALYSISDATE.set("")
    SAMPLEDATE.set("")
    LOCATION.set("")
    SHRINKAGE.set("")
    SAMPLEID.set(selecteditem[1])
    ANALYSISDATE.set(selecteditem[2])
    SAMPLEDATE.set(selecteditem[3])
    LOCATION.set(selecteditem[4])
    SHRINKAGE.set(selecteditem[5])
    btn_create.config(state=DISABLED)
    btn_read.config(state=DISABLED)
    btn_update.config(state=NORMAL)
    btn_delete.config(state=DISABLED)


#==================================VARIABLES==========================================
SAMPLEID = StringVar()
ANALYSISDATE = StringVar()
SAMPLEDATE = StringVar()
LOCATION = StringVar()
SHRINKAGE = StringVar()
STATUS = StringVar()

#==================================FRAME==============================================
Top = Frame(root, width=900, height=50, bd=8, relief="raise")
Top.pack(side=TOP)
Left = Frame(root, width=300, height=500, bd=8, relief="raise")
Left.pack(side=LEFT)
Right = Frame(root, width=600, height=500, bd=8, relief="raise")
Right.pack(side=RIGHT)
Forms = Frame(Left, width=300, height=450)
Forms.pack(side=TOP)
Buttons = Frame(Left, width=300, height=100, bd=8, relief="raise")
Buttons.pack(side=BOTTOM)
RadioGroup = Frame(Forms)
Include = Radiobutton(RadioGroup, text="include", variable=STATUS, value="include", font=('arial', 16)).pack(side=LEFT)
Exclude = Radiobutton(RadioGroup, text="exclude", variable=STATUS, value="exclude", font=('arial', 16)).pack(side=LEFT)


#==================================LABEL WIDGET=======================================
txt_title = Label(Top, width=900, font=('arial', 24), text = "Noble Shrinkage QC CRUD Application")
txt_title.pack()
txt_firstname = Label(Forms, text="Sample ID:", font=('arial', 16), bd=15)
txt_firstname.grid(row=0, sticky="e")
txt_lastname = Label(Forms, text="Sample Date:", font=('arial', 16), bd=15)
txt_lastname.grid(row=1, sticky="e")
txt_gender = Label(Forms, text="Status:", font=('arial', 16), bd=15)
txt_gender.grid(row=2, sticky="e")
txt_address = Label(Forms, text="Location:", font=('arial', 16), bd=15)
txt_address.grid(row=3, sticky="e")
txt_username = Label(Forms, text="Shrinkage:", font=('arial', 16), bd=15)
txt_username.grid(row=4, sticky="e")
txt_password = Label(Forms, text="GOR:", font=('arial', 16), bd=15)
txt_password.grid(row=5, sticky="e")
txt_result = Label(Buttons)
txt_result.pack(side=TOP)


#==================================ENTRY WIDGET=======================================
firstname = Entry(Forms, textvariable=SAMPLEID, width=30)
firstname.grid(row=0, column=1)
lastname = Entry(Forms, textvariable=ANALYSISDATE, width=30)
lastname.grid(row=1, column=1)
RadioGroup.grid(row=2, column=1)
address = Entry(Forms, textvariable=SAMPLEDATE, width=30)
address.grid(row=3, column=1)
username = Entry(Forms, textvariable=LOCATION, width=30)
username.grid(row=4, column=1)
password = Entry(Forms, textvariable=SHRINKAGE, show="*", width=30)
password.grid(row=5, column=1)


#==================================BUTTONS WIDGET=====================================
btn_read = Button(Buttons, width=10, text="Read", command=Read)
btn_read.pack(side=LEFT)

btn_import = Button(Buttons, width=10, text="Import", command=Import)
btn_import.pack(side=LEFT)


#==================================LIST WIDGET========================================
column_tuple = ("sample_id", "sample_date", "location", "gor", "shrinkage", "applied_average", "lower_limit", "upper_limit", "status")
scrollbary = Scrollbar(Right, orient=VERTICAL)
scrollbarx = Scrollbar(Right, orient=HORIZONTAL)
tree = ttk.Treeview(Right, columns=("sample_id", "sample_date", "location", "gor", "shrinkage", "applied_average", "lower_limit", "upper_limit", "status"), selectmode="extended", height=500, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
scrollbary.config(command=tree.yview)
scrollbary.pack(side=RIGHT, fill=Y)
scrollbarx.config(command=tree.xview)
scrollbarx.pack(side=BOTTOM, fill=X)
tree.heading('sample_id', text="sample_id", anchor=W)
tree.heading('sample_date', text="sample_date", anchor=W)
tree.heading('location', text="location", anchor=W)
tree.heading('gor', text="gor", anchor=W)
tree.heading('shrinkage', text="shrinkage", anchor=W)
tree.heading('applied_average', text="applied_average", anchor=W)
tree.heading('lower_limit', text="lower_limit", anchor=W)
tree.heading('upper_limit', text="upper_limit", anchor=W)
tree.heading('status', text="status", anchor=W)
tree.column('#0', stretch=NO, minwidth=0, width=0)
tree.column('#1', stretch=YES, minwidth=0, width=110)
tree.column('#2', stretch=YES, minwidth=0, width=100)
tree.column('#3', stretch=NO, minwidth=0, width=75)
tree.column('#4', stretch=NO, minwidth=0, width=60)
tree.column('#5', stretch=NO, minwidth=0, width=80)
tree.column('#6', stretch=NO, minwidth=0, width=80)
tree.column('#7', stretch=NO, minwidth=0, width=80)
tree.column('#8', stretch=NO, minwidth=0, width=80)
tree.column('#9', stretch=NO, minwidth=0, width=80)
tree.pack()
tree.bind('<Double-Button-1>', OnSelected)

if __name__ == '__main__':
    #create_connection(':memory:')
    #create_connection('db/test.db')
    #Database()
    root.mainloop()
    
    '''
    df = pd.read_csv('db/NobleQC_DB_initial.csv')
    print(df)
    Database()
    df.to_sql("shrinkage",conn, if_exists = 'append', index = False)

    #cursor.execute("INSERT INTO `member` (firstname, lastname, gender, address, username, password) VALUES(?, ?, ?, ?, ?, ?)", (str(FIRSTNAME.get()), str(LASTNAME.get()), str(GENDER.get()), str(ADDRESS.get()), str(USERNAME.get()), str(PASSWORD.get())))

    '''