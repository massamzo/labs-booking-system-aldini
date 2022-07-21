from unittest import result
import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host='localhost',
    user='prenotare',
    password='V7tfi!FF',
    database='prenotazione'
)

mycursor = mydb.cursor()

def checkmail(mail):
    mail = mail.lower()
    teacherstr = mail[-8:]
    if(teacherstr == "@avbo.it"):
        return True
    
    return False

def checkpass(pass1, pass2):
    if(len(pass1) >= 8 and pass1 == pass2):
        return True
    return False

def checkexistance(mail):
    mycursor.execute(f"SELECT emails FROM details WHERE emails = '{mail}'")
    result = mycursor.fetchall()
    
    if(len(result) != 0):
        return False
    return True

def insertdetails(email, pass1):
    mycursor.execute(f"INSERT INTO details(emails, pass) VALUES ('{email}','{pass1}')")
    mydb.commit()

def check_login_details(email, pass1):
    mycursor.execute(f"SELECT emails,pass FROM details WHERE emails='{email}' AND pass='{pass1}'")
    res = mycursor.fetchall()

    if(len(res) == 0):
        return False
    return True

def trovalabs():
    mycursor.execute("SELECT * from labs")
    res = mycursor.fetchall()
    lista = []
    for i in res:
        lista.append(i[0])
    return lista

def book_lab(nome, datapren,aula):
    d = datetime.datetime.now()
    now = d.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO "+aula+"(prof,datapren,data)"
    sql2 = "VALUES('%s','%s','%s')"%(str(nome), str(datapren), str(now))
    sql3 = sql+sql2
    
    mycursor.execute(sql3)
    mydb.commit()

    #delete atleast 10 

    mycursor.execute("DELETE FROM "+aula+" WHERE datapren<'%s' LIMIT 10"%(str(now)))
    mydb.commit()


def findrangedate(aula, d):
    dati = []
    
    d2 = datetime.datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S")
    d3 = d2 + datetime.timedelta(days=10)

    mycursor.execute("SELECT prof,datapren FROM "+aula+" WHERE datapren between '%s' and '%s'"%(str(d), str(d3)))
    res = mycursor.fetchall()

    for i in res:
        temp  =[]
        temp.append(i[0])
        temp.append(str(i[1]))
        dati.append(temp)

    return dati

    
def recover_password(email):
    mycursor.execute(f"SELECT pass from details WHERE emails='{email}'")

    
    res = mycursor.fetchall()
    if(len(res) != 0):
        return str(res[0][0])

def deleteaccount(email):
    mycursor.execute(f"DELETE FROM details WHERE emails='{email}'")
    mydb.commit()

recover_password("andrsssea.urso@avbo.it")