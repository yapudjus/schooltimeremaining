import sqlite3
from sqlite3 import Error
def sql_connection():
    try:
        con = sqlite3.connect('data.db')
        return con
    except Error:
        print(Error)

def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute("DELETE FROM users WHERE edpassword='mikado19'")
    con.commit()

con = sql_connection()
sql_table(con)