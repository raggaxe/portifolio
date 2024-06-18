import pymysql

def connection():
    conn = pymysql.connect(host="us-cdbr-iron-east-05.cleardb.net",
                           user = '',
                           passwd = '',
                           db = '')
    c = conn.cursor()
    return c,conn
