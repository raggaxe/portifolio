import pymysql

def connection():
    conn = pymysql.connect(host="localhost",
                           user = 'root',
                           passwd = 'rootpass',
                           db = 'portifolio')
    c = conn.cursor()
    return c,conn