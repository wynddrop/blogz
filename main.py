from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQL_ALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcy&szP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(8))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', '/', 'allblogs', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            #TODO why login failed
            password_error = ''
            username_error = ''
            if user and user.password != password:
                password_error = 'Password did not match.  Please re-enter your password.'
                return render_template('login.html', username=username, password_error=password_error)

            if not user:
                username_error = 'Username does not exist.'
                return render_template('login.html', username_error=username_error)

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = ''
        password = ''
        verify = ''

        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        
        username_error = ''
        password_error = ''
        verify_error = ''
    

        if username.isalnum():
            a=0
        else:
            username_error = 'Username cannot be empty or have spaces in it.'
            username = ''
        
        
        if  password.isalnum():
            a=0
        else:
            password_error = 'Password cannot be empty or have spaces in it.'
            password = ''

        if  verify.isalnum():
            a=0
        else:
            verify_error = 'Field cannot be empty or have spaces in it.'
            verify = ''

        if len(username) < 3 or len(username) > 25:
            username_error = 'Username must be 3 to 25 characters long'
        

        if len(password) < 3 or len(password) > 8:
            password_error = 'Password must be 3 to 8 characters long'
        

        if password != verify:
            verify_error = 'Password and verification did not match.'
        

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = 'User found, please enter a different username.'
                return render_template('signup.html',username_error=username_error)
        else:
                return render_template('signup.html', username=username, 
                username_error=username_error,password_error=password_error, 
                verify_error=verify_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/finishedpost', methods=['POST','GET'])
def individual_blog():

    if request.method =='POST':
        blog_id = int(request.form['blog-id'])
    if request.method =='GET':
       
        blog_id = int(request.args.get('blog_id'))

    blog = Blog.query.get(blog_id)
    username = session['username']
    

    return render_template('finishedpost.html', blog=blog, username=username )

@app.route('/buildablog')
def basepage():
    username1 = User.query.filter_by(username=session['username']).first()
    username = session['username'] 
    blogs = Blog.query.filter_by(owner_id=username1.id).all()
    return render_template('buildablog.html', blogs=blogs, username=username)

@app.route('/blog', methods=['GET'])
def blog():
    
    user_id = request.args.get('userid')
    blogs = Blog.query.filter_by(owner_id=user_id).all()
    user = User.query.filter_by(id=user_id)

    return render_template('blog.html', blogs=blogs)

@app.route('/allblogs', methods=['GET'])
def blogs():
   
    blogs = Blog.query.all() 

    users = User.query.all()
    
    return render_template('allblogs.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_body_error = ''
    blog_title_error = ''
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()

        new_blog = Blog(blog_title,blog_body,owner)

        if len(blog_body) < 1 or len(blog_title) < 1:
            if len(blog_body) < 1:
                blog_body_error = "Please fill in the body"
            if len(blog_title) < 1:
                blog_title_error = "Please fill in the title"
            return render_template('newpost.html', blog_title=blog_title, 
                blog_title_error=blog_title_error,blog_body=blog_body, 
                blog_body_error=blog_body_error)
        else:
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/finishedpost?blog_id={0}'.format(blog_id))
            
    

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()