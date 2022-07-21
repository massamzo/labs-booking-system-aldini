from unittest import result
import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host='localhost',
    user='prenotare',
    password='V7tfi!FF',
    database='prenotazione'
)


mycur = mydb.cursor()


lista = ["227","229","241"]

for i in lista:
    aula = "aula"+i
    mycur.execute(f"CREATE TABLE {aula}(prof VARCHAR(255), datapren DATETIME, data DATETIME)")


