import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

import os
import pandas as pd
import io
import psycopg2
from dotenv import load_dotenv

from utils.data import load_financial_data

load_dotenv()


# connect to postgres
conn = psycopg2.connect(
   database="algo_trading", user='postgres', password=os.getenv('POSTGRES_PW'), host='localhost', port='5432'
)

cursor = conn.cursor()

# load data
data = load_financial_data('GOOG', '2001-01-01', '2018-01-01', 'GOOG_data_large.pkl')
data = data.reset_index()
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M:%S')


# write dataframe to postgres
buffer = io.StringIO()
data.to_csv(buffer, sep='\t', index=False, header=False)
buffer.seek(0)
#cursor.copy_from(buffer, 'GOOG', null='')
#conn.commit()


# query postgres
def query_ticks(sql):
    cursor.execute(sql)
    data = cursor.fetchall()
    return data


SQL = '''SELECT
    dt,high,low,open,close,volume,adj_close
    FROM "GOOG"
    WHERE dt BETWEEN '2016-11-08' AND '2016-11-09'
    ORDER BY dt
    LIMIT 100;'''

print(query_ticks(SQL))


# close connection
cursor.close()
conn.close()