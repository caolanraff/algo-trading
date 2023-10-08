import psycopg2

conn = psycopg2.connect(
   database="algo_trading", user='postgres', password='postgres', host='localhost', port= '5432'
)

cursor = conn.cursor()


def query_ticks(sql):
    cursor.execute(sql)
    data = cursor.fetchall()
    return data


# should be able to load the goog.sql file and create the database first
# maybe send some data from the pickle files
# conn.commit() after


SQL = '''SELECT
    dt,high,low,open,close,volume,adj_close
    FROM "GOOG"
    WHERE dt BETWEEN "2016-11-08" AND "2016-11-09"
    ORDER BY dt
    LIMIT 100;'''

print(query_ticks(SQL))