from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:buildablogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'baby098134iscry149now238745'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(60))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



class Blog(db.Model):     #specific class extends object db and inherits functionality from Model class
    
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(80)) # a column called title will be created in sql
    body = db.Column(db.Text) # a column called body will be created in sql 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner.id



def login_validation(item):
    message = ''
    if len(item)<3 or len(item)>20 or ' ' in item:
        message = "This must be between 3-20 characters and have no spaces."
    return message
    


def login_verification(sess):
    if 'username' in sess: 
        return True
    return False



@app.before_request
def verify_logged_in():
    accessible = [ 'index', 'login', 'signup' ,'blog']

    if request.endpoint not in accessible and not login_verification(session):
        return redirect('/login')



@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, loggedin=login_verification(session), page_header="All Users")



@app.route('/blog')
def blog():
    get_blog_id = request.args.get('id')
    get_user_id = request.args.get('user')
    blogs = Blog.query.all()

    if get_blog_id: 
        blog_id = int(get_blog_id)
        this_blog = Blog.query.get(blog_id)

        if this_blog: 
            return render_template('indiv_post.html', loggedin=login_verification(session), page_header=this_blog.title, blog=this_blog)
        else: 
            return render_template('no_blog.html', loggedin=login_verification(session), page_header="Seeking Missing Thoughts")

    if get_user_id: 
        user = User.query.get(int(get_user_id))
        blogs = user.blogs
    return render_template('/blog.html', loggedin=login_verification, page_header="Fresh Ruminations", blogs=blogs )



@app.route('/newpost', methods=["POST", "GET"])
def blogz():

    if request.method == "POST":
        new_title = request.form['title']
        new_body = request.form['body']
        title_error, body_error = "", ""   #tuples 

        if not new_title: title_error = "What do you want to ruminate about?"
        if not new_body: body_error = "Please share your thoughts here."
        
        if not title_error and not body_error:
            owner = User.query.filter_by(username = session['username']).first()
            
            new_blog = Blog(new_title, new_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/blog?id='+str(new_blog.id))

        else: 
            return render_template('/newpost.html', loggedin=login_verification, page_header="Something to Ruminate About", title_error=title_error, 
            body_error=body_error, new_title=new_title, new_body=new_body)


    return render_template('/newpost.html', loggedin=login_verification, page_header="Fresh Ruminations")



@app.route('/login', methods=[ 'POST', 'GET'])
def login():
    if request.method == "POST": 
        form_username = request.form["user_name"]
        form_password = request.form["password"]

        user = User.query.filter_by(username=form_username).first()

        if user and form_password == user.password: 
            session['username'] = user.username
            return redirect('/blog?user='+str(user.id))

        else: 
            error = "This username and password don't exist."
            return render_template('/login.html', user_error=error)
    
    return render_template('login.html', loggedin=login_verification, page_header="Login")



@app.route('/signup', methods=[ 'POST', 'GET' ])
def signup(): 
    if request.method == "POST":

        form_username = request.form["user_name"]
        form_password = request.form["password"]
        verify_password = request.form["verify_password"]

        username_error = login_validation(form_username)
        password_error = login_validation(form_password)
        verify_password_error = ''

        if form_password != verify_password: verify_password_error = "Password and verify password do not match"

        if not username_error and not password_error and not verify_password_error: 
            existing_user = User.query.filter_by(username=form_username).first()

            if not existing_user:
                newuser = User(form_username, form_password)
                db.session.add(newuser)
                db.session.commit()

                session['username'] = newuser.username

                return redirect('/blog?user='+str(newuser.id))
            else: 
                username_error = "This username already exists."
                return render_template('signup.html', loggedin=login_verification(session), page_header="Sign Up", user_name = form_username, user_name_error=username_error)

        return render_template('signup.html', loggedin=login_verification(session), page_header="Sign Up", user_name=form_username, user_name_error=username_error, password_error=password_error, verify_password_error = verify_password_error)

    return render_template('signup.html', loggedin=login_verification(session), page_header="Sign Up")


@app.route('/logout')
def logout(): 
   del session['username']
   # flash( 'Logged Out' )
   return redirect('/')


if __name__ == '__main__':
    app.run()
