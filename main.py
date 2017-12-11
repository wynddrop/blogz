from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQL_ALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title,blog_body)
        db.session.add(new_blog)
        db.session.commit()
       
    blogs = Blog.query.all()
 
    return render_template('buildablog.html',title="Build a Blog", blogs=blogs)


@app.route('/finishedpost', methods=['POST','GET'])
def individual_blog():

    if request.method =='POST':
        blog_id = int(request.form['blog-id'])
    if request.method =='GET':
       
        blog_id = int(request.args.get('blog_id'))

    blog = Blog.query.get(blog_id)
    

    return render_template('finishedpost.html',title="Build a Blog", blog=blog)

@app.route('/buildablog')
def basepage():
    blogs = Blog.query.all()
    return render_template('buildablog.html', title="Build a Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_body_error = ''
    blog_title_error = ''
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title,blog_body)

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