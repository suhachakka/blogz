from flask import Flask,request,redirect,render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] =True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:mynewpass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key ='secret string'


db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body =db.Column(db.String(120))
    #date = db.column(db.DateTime)
    owner_id =db.Column(db.Integer, db.ForeignKey('user.id'))
                    
    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner =owner  
       
    def __repr__(self):
        return '<Blog %r>' % self.title   

class User(db.Model):  
    id =db.Column(db.Integer,primary_key=True)
    username =db.Column(db.String(50), unique=True) 
    password =db.Column(db.String(50))
    blogs = db.relationship('Blog', backref ='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password 
    def __repr__(self):
        return '<User %r>' % self.username    

@app.route('/newpost')
def form():
    return render_template('Addblogentry.html')    

    
@app.route('/login', methods=['GET','POST']) 
def login():
    #u_error='' 
    #p_error=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '':
            flash('Invalid Username')
        if password =='':
            flash('Invalid Password') 
        if username != '' or password != '':       
  
            user = User.query.filter_by(username=username).first()
            if user == None:
                flash('Username doesnot exists')

        #print("$$$$"+user.username)

            if user and user.password == password:
                flash('User Logged in')
                session['username'] = username
                return redirect('/newpost')
            else:    
                flash('username and password invalid')
                return redirect('/login')          
    return render_template('login.html') 
@app.route('/signup', methods=['GET','POST']) 
def sign_up():
    us_error =''
    ps_error = ''  
    vps_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        v_pass = request.form['verify']
        #if not existing_user:
           
        if username == '' or username.isalpha() != True :
            us_error='That\'s not a valid Username'                

        if len(username) > 20 or len(username) <3:
            us_error='That\'s not a valid Username'
                     
        if len(password) >20  or len(password) < 3 or password == '':
            ps_error='That\'s not a valid Password'
                
        if  v_pass != password or password == '' :
            vps_error= 'password didn\'t match'
        if not us_error and not ps_error and not vps_error:
         
           existing_user = User.query.filter_by(username=username).first()
           if not existing_user:
               new_user = User(username,password)
               db.session.add(new_user)
               db.session.commit()
               session['username'] = username
               return redirect('/newpost')
           else:
                flash('A user with that Username already exists') 
                return redirect('/signup')   
    return render_template('signup.html',us_error=us_error,ps_error=ps_error,vps_error=vps_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')    

@app.route('/newpost',methods= ['GET', 'POST'])
def newpost():
    t_error ='' 
    b_error =''   
    title =request.form['title']
    body =request.form['body']    
    if title == '' or body != '':
        t_error ='please fill in the entry'
    if body == '' or title != '':
        b_error = 'please fill in the body'
    owner= User.query.filter_by(username=session['username']).first()
    #print("#$#$"+owner) 
    if title != '' and  body != '' :
        new_blog=Blog(title,body,owner)  
        db.session.add(new_blog) 
        db.session.commit() 
        #print("$$"+str(new_blog.id))
        return redirect('/blog?id='+str(new_blog.id) )       
    else:        
        return render_template('Addblogentry.html',title=title,body=body,t_error=t_error,b_error=b_error,owner=owner)

@app.route('/blog')
def blogpost():
    if request.args.get('id') != None:
        indiv_id = request.args.get('id')
        #print("$$$$$"+indiv_id)
        blogs = Blog.query.get(indiv_id)
        user_id= request.args.get('id')
        users =User.query.get(user_id)
        return render_template('Individualentrypage.html',blogs=blogs,users=users)
    if request.args.get('user') != None:
        user_name= request.args.get('user')
        print("####$"+ user_name)
        #user =User.query.get(user_name)
        user = User.query.filter_by(username=user_name).first()

        #print("####$"+ str(user.id))

        blogs =Blog.query.filter_by(owner_id=user.id).all()

        return render_template('singleuser.html',user=user,blogs=blogs)
    if request.args.get('id') == None:
        
        #blogs = Blog.query.all()

        blogs= Blog.query.order_by(Blog.id).all() #sorting the order
        users=User.query.all()

 
        return render_template('Mainblogpage.html',blogs=blogs,users=users)
        
@app.route('/')  
def index():
    if request.args.get('user') != None:
        user_name= request.args.get('user')
        user =User.query.get(user_name)
        blogs =Blog.query.get('user.id')
        return render_template('singleuser.html',user=user,blogs=blogs) 
    if request.args.get('id') == None:
        users=User.query.all()

        return render_template('index.html',users=users)

 
@app.before_request
def require_login():
    #TODO Managing login using session module
    allowed_routes = ['login', 'blogpost','index','sign_up'] 
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")    

if __name__ == '__main__':
    app.run()


