import pymysql

def connection():
    conn = pymysql.connect(host="us-cdbr-iron-east-05.cleardb.net",
                           user = 'b855d419d92593',
                           passwd = 'b8bb879b',
                           db = 'heroku_4a2f43692cff6c6')
    c = conn.cursor()
    return c,conn