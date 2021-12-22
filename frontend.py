from flask import Flask, render_template, redirect, request, sessions, url_for, session, flash, current_app
import hashlib, logging, sqlite3, re, datetime, random
from urllib.parse import urlparse, urljoin
from flask_mobility import Mobility
from getprogress import get_bar
from sqlite3 import Error

app = Flask(__name__)
Mobility(app)

# app.config['ENV'] = 'production'
app.secret_key = str(random.SystemRandom())

con = sqlite3.connect('/root/code/schooltimeremaining/data.db', check_same_thread=False)

def sql_connection():
    logger = logging.getLogger(__name__)
    try:
        con = sqlite3.connect(':memory:')
        logger.info("Connection is established: Database is created in memory")
    except Error as e:
        logger.error(Error)
    finally:
        con.close()

sql_connection()

def is_safe_url(target):
    logger = logging.getLogger(__name__)
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class user :
    def getData(username) :
        logger = logging.getLogger(__name__)
        cursorObj = con.cursor() 
        cursorObj.execute(f'SELECT username, password FROM users WHERE username == {username}')
        rows = cursorObj.fetchall()
        for row in rows: print(row)
    
    def add(username, password, edusername, edpassword, acctlvl='user') :
        logger = logging.getLogger(__name__)
        cursorObj = con.cursor()
        # cursorObj.execute(f"INSERT INTO users VALUES({username}, {password}, {edusername}, {edpassword}, 'user')")
        entities = (username, user.encode.password(password), edusername, edpassword, acctlvl)
        cursorObj.execute('''INSERT INTO users (username, password, edusername, edpassword, acctlvl) VALUES(?, ?, ?, ?, ?)''', entities)
        con.commit()
    
    def exist(username) :
        logger = logging.getLogger(__name__)
        cursorObj = con.cursor()
        cursorObj.execute(f"SELECT EXISTS(SELECT * FROM users WHERE username='{username}')")
        a= cursorObj.fetchall()
        if a[0][0] == 1: 
            return True
        else : 
            return str(f'user {username} doesn\'t exist')
    
    class get :
        def password(username) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            cursorObj = con.cursor()
            cursorObj.execute(f"SELECT password FROM users WHERE username='{username}'")
            rows = cursorObj.fetchall()
            return rows[0][0]
        
        def acctlvl(username) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            cursorObj = con.cursor()
            cursorObj.execute(f"SELECT acctlvl FROM users WHERE username='{username}'")
            rows = cursorObj.fetchall()
            return rows[0][0]
        
        def edusername(username) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            cursorObj = con.cursor()
            cursorObj.execute(f"SELECT edusername FROM users WHERE username='{username}'")
            rows = cursorObj.fetchall()
            return rows[0][0]
        
        def edpassword(username) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            cursorObj = con.cursor()
            cursorObj.execute(f"SELECT edpassword FROM users WHERE username='{username}'")
            rows = cursorObj.fetchall()
            return rows[0][0]

        class all :
            def fromusername(username) :
                logger = logging.getLogger(__name__)
                if user.exist(username) != True: return 'user doesn\'t exist'
                cursorObj = con.cursor()
                cursorObj.execute(f"SELECT * FROM users WHERE username='{username}'")
                rows = cursorObj.fetchall()
                return rows[0]
            
            def all() :
                logger = logging.getLogger(__name__)
                cursorObj = con.cursor()
                cursorObj.execute(f"SELECT * FROM users")
                rows = cursorObj.fetchall()
                return rows
    
    class change :
        def password(username, newpassword, oldpassword='', Forced=False) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            if (user.check.password(username, oldpassword)) and Forced == False: return 'wrong password'
            cursorObj = con.cursor()
            logger.debug(f"UPDATE users SET password='{user.encode.password(newpassword)}' where username='{username}'")
            cursorObj.execute(f"UPDATE users SET password='{user.encode.password(newpassword)}' where username='{username}'")
            con.commit()
        
        def acctlvl(username, password, acctlvl, Forced=False) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            if (user.check.password(username, password)) and Forced == False: return 'wrong password'
            if (user.get.acctlvl(username) != 'admin') and Forced == False: return 'unauthorized'
            cursorObj = con.cursor()
            logger.debug(f"UPDATE users SET acctlvl='{acctlvl}' where username='{username}'")
            cursorObj.execute(f"UPDATE users SET acctlvl='{acctlvl}' where username='{username}'")
            con.commit()
        
        def edusername(username, password, edusername, Forced=False) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            if (user.check.password(username, password)) and Forced == False: return 'wrong password'
            cursorObj = con.cursor()
            logger.debug(f"UPDATE users SET edusername='{edusername}' where username='{username}'")
            cursorObj.execute(f"UPDATE users SET edusername='{edusername}' where username='{username}'")
            con.commit()
        
        def edpassword(username, password, edpassword, Forced=False) :
            logger = logging.getLogger(__name__)
            if user.exist(username) != True: return 'user doesn\'t exist'
            if (user.check.password(username, password)) and Forced == False: return 'wrong password'
            cursorObj = con.cursor()
            logger.debug(f"UPDATE users SET edpassword='{edpassword}' where username='{username}'")
            cursorObj.execute(f"UPDATE users SET edpassword='{edpassword}' where username='{username}'")
            con.commit()
        
    
    class check :
        def password(username, password) :
            checkagainst = user.get.password(username)
            if user.encode.password(password) == checkagainst : return True
            else : return False
    
    class encode :
        def password(password) :
            return str(hashlib.sha256(password.encode()).hexdigest())

def ismobile(useragent) :
    MOBILE_REGEX = r'/Mobile|iP(hone|od|ad)|Android|BlackBerry|BB|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune/gi'
    if re.search(pattern=MOBILE_REGEX, string=useragent) != None: return True
    else: return False

def getcss(useragent) :
    if ismobile(useragent): return '/static/mobile.css'
    else: return '/static/desktop.css'

@app.route("/")
def root(): return redirect(url_for("home"))

@app.route("/home")
def home():
    logger = logging.getLogger(__name__)
    if('user' in session and user.exist(session['user'])): 
        e = None
        edusername=user.get.edusername(session['user'])
        edpassword=user.get.edpassword(session['user'])
        width1, width2, text1, text2 = 0, 0, 'error', 'error'
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()
        year = date.strftime("%Y")
        width1, text1, width2, text2 = get_bar(username=edusername, password=edpassword, year=int(year))
        return render_template('home.html', width1=width1, width2=width2, text1=text1, text2=text2, error=e, loggedas=session['user'], css=getcss(request.headers.get('User-Agent')))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger = logging.getLogger(__name__)
    error = None
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        if user.exist(username=username) == True :
            if user.check.password(username, password) == False : 
                logger.debug(f'{username} typed the wrong password')
                if user.get.acctlvl(username) == 'admin': logger.warning(f'someone tried to login to {username} with ip: {request.remote_addr}')
                error = 'wrong password'
        else : error = user.exist(username=username)
        if error == None:
            session['user'] = username
            if user.get.acctlvl == 'admin' : logger.info(f'admin user {username} logged in at ip: {request.remote_addr}')
            return redirect(url_for('home'))
    return render_template('login.html', error=error, css=getcss(request.headers.get('User-Agent')))

@app.route('/register', methods=['GET', 'POST'])
def register():
    logger = logging.getLogger(__name__)
    error = None
    requiretoken = False
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        edusername = request.form.get("edusername")
        edpassword = request.form.get("edpassword")
        token = request.form.get("token")
        if (token != "158648234568" ) or not requiretoken: error = 'invalid token'
        elif user.exist(username) == True : error = 'username already exist'
        else:
            logger.debug(f'{username} registered with ip: {request.remote_addr}')
            user.add(username=username, password=password, edusername=edusername, edpassword=edpassword)
            return redirect(url_for('login'))
    return render_template('register.html', error=error ,requiretoken=requiretoken, css=getcss(request.headers.get('User-Agent')))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    logger = logging.getLogger(__name__)
    e = None
    if('user' in session and user.exist(session['user'])):
        if request.method == 'POST':
            edusername = request.form.get("edusername")
            edpassword = request.form.get("edpassword")
            password = request.form.get("oldpassword")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")
            if password1 != password2 : e= 'passwords doesn\'t match'
            if 'passwdchange' in request.form:
                e= user.change.password(username=session['user'], newpassword=password1, oldpassword=password, Forced=False)
            if 'edchange' in request.form:
                if 'edusername' in request.form : e= user.change.edusername(username=session['user'], password=password, edusername=edusername)
                if 'edpassword' in request.form : e= user.change.edpassword(username=session['user'], password=password, edpassword=edpassword)
        return render_template("settings.html", error=e, loggedas=session['user'], css=getcss(request.headers.get('User-Agent')))
    return render_template("loginerror.html", css=getcss(request.headers.get('User-Agent')))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    logger = logging.getLogger(__name__)
    #TODO: add user listing
    #TODO: add accont removal
    #TODO: add account change
    e = None
    if('user' in session and user.exist(session['user'])):
        if user.get.acctlvl(session['user']) == 'admin' :
            if request.method == 'POST':
                if 'adduser' in request.form: user.add(username=request.form.get('adusername'), password=request.form.get('adpassword'), edusername=request.form.get('adedusername'), edpassword=request.form.get('adedpassword'), acctlvl=request.form.get('dropdown'))
            return render_template("admin.html", error=e, loggedas=session['user'], css=getcss(request.headers.get('User-Agent')))
        return render_template("unauthorized.html", loggedas=session['user'], acctlvl=user.get.acctlvl(session['user']), required='admin', css=getcss(request.headers.get('User-Agent')))
    return render_template("loginerror.html", css=getcss(request.headers.get('User-Agent')))

@app.route('/logout')
def logout():
    logger = logging.getLogger(__name__)
    username = session['user']
    logger(f'user {username} logged out')
    session.pop('user')
    return render_template("logout.html", css=getcss(request.headers.get('User-Agent')))

#TODO: add contact page
@app.route('/about')
def about():
    return render_template("about.html", css=getcss(request.headers.get('User-Agent')))

if __name__ == "__main__":
    # now = datetime.datetime.now()
    logging._defaultFormatter = logging.Formatter(u"%(message)s")
    logging.basicConfig(filename=f'/root/code/schooltimeremaining/logs/app.log', level=logging.DEBUG,format='[%(asctime)s]: %(name)s:%(levelname)s:%(message)s') # {now.strftime("%d-%m-%Y_%H:%M:%S")}
    app.run(port=800, host='m.yapudjusowndomain.fr', debug=False)