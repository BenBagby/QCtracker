import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import sqlite3

#data = pd.read_csv("db/NobleQC_DB_initial3.csv")

def create_df_list(data):
    separated_tup = tuple(data.groupby('location'))
    df_list = []
    for var in separated_tup:
        for var2 in var:
            if type(var2) != str:
                df_list.append(var2)
    return df_list

def calculate_QC_params(df):

    for index, row in df.iterrows():
        df['status'].replace('nan', 'empty', regex = True, inplace = True)
        #need to replace this with a count of rows above without status X
        current_date = df.loc[index,'sample_date']
        filter0 = index == 0
        filter1 = df['status'] == 'pass' 
        filter2 = df['status'] == 'fail(include)'
        filternan = df['status'] == 'empt'
        #filter3 = pd.DatetimeIndex(df['analysis_date']).replace(day = 1) <= (current_date + relativedelta(months=-6)).replace(day = 1)
        time_series = pd.to_datetime(df['sample_date'])
        day1_time_series = time_series.apply(lambda dt: dt.replace(day = 1))
        filter3 =  day1_time_series >= (current_date + relativedelta(months=-6)).replace(day = 1)
        filter4 = df['sample_date'] < current_date
        reduced_df = df.where(  ( pd.Series(filter3) & pd.Series(filter4) & (pd.Series(filter1) | pd.Series(filter2) | pd.Series(filternan))) | pd.Series(filter0)  )
        #print(reduced_df)
        rolling_mean2 = reduced_df['shrinkage'].mean()
        gor_rolling_mean = reduced_df['gor'].mean()
        
        df.at[index, 'applied_average'] = rolling_mean2
        df.at[index, 'gor_applied_average'] = gor_rolling_mean
        
        lower_limit = df.loc[index,'applied_average'] * (1 - 0.04)
        upper_limit = df.loc[index,'applied_average'] * (1 + 0.04)
        
        df.at[index,'lower_limit'] = lower_limit
        df.at[index,'upper_limit'] = upper_limit

        if lower_limit <= df.loc[index,'shrinkage'] <= upper_limit:
            df.at[index,'status'] = 'pass'
        else:
            if index < 50:
                df.at[index,'status'] = 'fail(include)'
            else:
                df.at[index,'status'] = 'fail(exclude)'
    #print(reduced_df)
    #print(df)
    return df



if __name__ == '__main__':

    conn = sqlite3.connect('LIVE06302020 test.db')
    cursor = conn.cursor()
    data = pd.read_sql_query("SELECT * FROM shrinkage", conn)
    data['location'] = data['location'].str.extract(r'(.+?(?= \/ |$))')
    #print(data)

    df_list = create_df_list(data)
    df_out = pd.DataFrame(columns = ['sample_id', 'sample_date', 'gor', 'shrinkage', 'location', 'applied_average','lower_limit','upper_limit','status','s_w','gor_applied_average'])
    for df in df_list:
        df['sample_date'] =pd.to_datetime(df.sample_date)
        df = df.sort_values(by='sample_date')
        df.reset_index(drop=True, inplace = True)
        df['status'] = df['status'].astype(str)
        df = calculate_QC_params(df)
        df_out = df_out.append(df, ignore_index = True)
    
    print(df_out)
    
    for index, row in df_out.iterrows():
        select_query = "SELECT * FROM shrinkage WHERE sample_id = ?"
        update_query = "UPDATE shrinkage SET location=?, applied_average=?, lower_limit=?, upper_limit=?, status=?, gor_applied_average=? WHERE sample_id=?"
        cursor.execute(update_query,(row.location, row.applied_average, row.lower_limit, row.upper_limit, row.status, row.gor_applied_average, row.sample_id,))
    
    conn.commit()
    conn.close()

    

    

    






