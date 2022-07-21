from crypt import methods
from email.message import Message
from flask import Flask, render_template,redirect ,request, session, url_for
from errors import checkpass, checkmail, checkexistance,deleteaccount,insertdetails,check_login_details,recover_password, trovalabs, book_lab,findrangedate
import datetime
from random import randint
from flask_mail import Mail, Message
from mailsender import mailtemplate, recover_template
import time
from minifuctions import date_arr

app = Flask(__name__)

app.config['SECRET_KEY'] = "prenota123"

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pillomad45@gmail.com'
app.config['MAIL_PASSWORD'] = 'qliwmssokwhfjbhx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

error = ""
email = ""
pass1 = ""
nome = ""
aula =""
aulaex = "no"
calendario = []


def sess_cheker():
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))

def codegenerator():
    date = datetime.datetime.now()
    code = ""
    matt = [
        ['a','x','d','e','f','g'],
        ['m','s','!','@','3','5'],
        ['n','d','E','T','r','*'],
        ['M','O','%','&','/','z'],
        ['Z','G','J','w','x','y'],
        ['Y','K','#','$','7','9'],
        ['Q','q','C','c','L','i'],
        ['L','?','-',"_","V","v"]
    ]

    for i in range(8):
        code += matt[randint(0,7)][randint(0,5)]

    return code



@app.route('/login')
def login():
    
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))
    return render_template("login.html", error=error,email=email)


@app.route("/registercheck", methods=['POST'])
def registercheck():
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))
    if request.method == "POST":
        global error,pass1,email,nome
        email = request.form['email']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']

        #check if the email is correct

        if(not checkmail(email)):
            #if the mail is not correct
            error="La mail deve essere di un insegnante delle Aldini"
            return redirect(url_for('register'))

        if(not checkpass(pass1,pass2)):
            error = "Errore nel password"
            return redirect(url_for('register'))

        nome = email.split('.')
        nome = "@".join(nome)
        nome = nome.split('@')
        
        if(not checkexistance(email)):
            error = f"{nome[0]}  {nome[1]} ha un profilo gia creato, accedi!"
            return redirect(url_for('register'))

        #send the mail 

        codice = codegenerator()
        msg = Message("Codice per completare l'iscrizione", sender='pillomad45@gmail.com', recipients = [f'{email}'])
        msg.html = mailtemplate(nome[1], nome[0],codice)
        mail.send(msg)
        
        milliseconds = int(round(time.time() * 1000))
        session['codice'] = codice
        session['target'] = str(milliseconds+82000)
        session['maintime'] = str(milliseconds)
        

        return redirect(url_for('code'))
    return redirect(url_for('register'))


@app.route('/checklogin', methods=['POST', 'GET'])
def checklogin():
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))
    if request.method == 'POST':
        global email, pass1,error,nome
        email = request.form['email']
        pass1 = request.form['pass']

        #check if the details are correct
        if(not check_login_details(email, pass1)):
            #if the details aren't found
            error = "Email o password sbagliata"
            return redirect(url_for('login'))


        nome = email.split('.')
        nome = "@".join(nome)
        nome = nome.split('@')

        session['user'] = nome[1]+" " +nome[0]
        return redirect(url_for('mainpage'))



@app.route("/code")
def code():
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))
    data = datetime.datetime.now()

    return render_template('code.html')


@app.route('/register')
def register():
    if(session.get('user') is not None):
        return redirect(url_for('mainpage'))
    return render_template("register.html", error=error)


@app.route('/', methods=['POST', 'GET'])
def mainpage():
    global error
    if request.method == 'POST':
        code = request.form['code']
        if(code == session['codice']):
            #insert data into database
            session.pop('codice', None)
            session.pop('target', None)
            session.pop('maintime', None)
            session['user'] = nome[1]+" " + nome[0]
            insertdetails(email, pass1)
        elif(code[-1] == '>' and len(code) == 9):
            error = "tempo scaduto! rifare l'iscrizione"
            return redirect(url_for('register'))
        else:
            error = "codice inserito non valido!"
            return redirect(url_for('register'))
    elif(session.get('user') is None):
        return redirect(url_for('login'))
    
    lista = trovalabs()
    aulex = ""
    return render_template("index.html", lista=lista,  email=email)



@app.route('/aula', methods=['POST','GET'])
def aula():
    global aula
    
    cal_len = ""
    if(session.get('user') is None):
        return redirect(url_for('login'))
    

    if request.method == "POST" and 'aula' in request.form:
        
        aula = request.form['aula']
        calendario.append(date_arr())
        
    elif(request.method == "POST" and 'dat' in request.form):
        data = request.form['dat']
        if data[-1] == '-':
            calendario.pop()
        else:
            data = data.split('-')
            for i in range(len(data)):
                data[i] = int(data[i])
            calendario.append(data)
    elif(aulaex == "nop"):
        print('s')
    else:
        return redirect(url_for('mainpage'))

    
    if(len(calendario) <= 1):
        cal_len = "last"
    else:
        cal_len = "more"
    

    dat = calendario[-1]
    date = datetime.datetime(dat[0], dat[1], dat[2], 0,0,0)
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    lab = "aula"+str(aula)
    prenotati = findrangedate(lab,date)

    return render_template('aula.html',data=calendario[-1],aula=aula, cal_len=cal_len,prenotati=prenotati, len=len(prenotati))

@app.route('/adding', methods=['POST','GET'])
def adding():
    if(request.method == 'POST'):
        global aulaex
        name = request.form['nome']
        datapren = request.form['date']
        lab = "aula"+str(aula)
        book_lab(str(name),str(datapren),lab)
        aulaex = "nop"
    return redirect(url_for("aula"))


@app.route("/delcookie", methods=['POST', "GET"])
def delcookie():
    if request.method == "POST":
        valore = request.form['valore']
        if(valore == "user"):
            session.pop("user", None)
    
    return redirect(url_for('mainpage'))

@app.route('/recoverpass', methods=['POST', 'GET'])
def recoverpass():
    if request.method == "POST" and "email" in request.form:
        maila = request.form['email']

        #find the email and send the psasword

        if(maila[-1] != '.'):
            nome = maila.split('.')
            nome = "@".join(nome)
            nome = nome.split('@')

            name = nome[1]+nome[0]
            password = recover_password(maila)
            msg = Message("Password sito della prenotazione laboratori", sender='pillomad45@gmail.com', recipients = [f'{maila}'])
            msg.html = recover_template(name, password)
            mail.send(msg)
        else:
            #delete the mail from database
            deleteaccount(maila[:-1])
            return redirect(url_for('register'))
    return render_template("recupera.html")



if __name__ == "__main__" : 
    app.run(host='0.0.0.0', port=80, debug=True)
