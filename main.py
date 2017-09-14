from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:buildablogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(60))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Blog(db.Model):     #specific class extends object db and inherits functionality from Model class
    
    id = db.Column(db.Integer, primary_key=True) # id will function as a primary key and will associate with a specific column
    title = db.Column(db.String(80)) # a column called title will be created in sql
    body = db.Column(db.Text) # a column called body will be created in sql 

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect('/blog')   


@app.route('/blog', methods=["POST", "GET"])
def blog():

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        title_error, body_error = "", ""   #tuples 

        if not title: title_error = "What do you want to ruminate about?"
        if not body: body_error = "Please share your thoughts here."

        if not title_error and not body_error: 
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/blog?id='+str(new_blog.id))

        else: 
            return render_template('/newpost.html', page_header="Something to Ruminate About", title_error=title_error, 
            body_error=body_error, title=title, body=body)

    if request.args.get('id'):        
        blog_id = int(request.args.get('id'))
        blog = Blog.query.get(blog_id)

        if blog: 
            return render_template('/indiv_post.html', page_header="A Fresh Rumination", blog=blog)
        else: 
            return render_template('no_blog.html', page_header="Missing Thoughts")

    blogs = Blog.query.all()
    return render_template('/blog.html', page_header="All Blogs", blogs=blogs)


@app.route('/newpost')
def new_entry(): 
    return render_template('/newpost.html', page_header="Something to Ruminate About")

if __name__ == '__main__':
    app.run()
