import sqlite3
import os

def clean(filepath):
    path = os.getcwd() + '/' + filepath
    print path
    os.remove(path)

def conn_DB(db):
    # check whether db file is already existing.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    return conn, c

# implement later, according to parameters to create a table
# def cre_tbl(cursor, *args):
#     tbl_len = len(args)
#     sql_stmt = 'CREATE TABLE sim(' + '? text' * tbl_len + ')' 
#     c.execute('''CREATE TABLE sim
#              (sender text, date text, time text, value text)''')

def cre_tbl(db):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    sql = '''
    CREATE TABLE sim
    (sender text, time timestamp, value text)
    '''
    c.execute(sql)
    
def ins_DB(conn, cursor, tuple_list):
    sql_stmt = 'INSERT INTO sim VALUES (?,?,?)'
    # print 'insert : ', sql_stmt
    # print 'tuple_list : ', tuple_list
    cursor.executemany(sql_stmt, tuple_list)
    conn.commit()
    
def duration_inquery(cursor, start_datetime, end_datetime):
    sql = '''
    select * from sim where 
    time >= ? and
    time <= ?
    '''
    cursor.execute(sql, (start_datetime, end_datetime))
    return cursor.fetchall()
