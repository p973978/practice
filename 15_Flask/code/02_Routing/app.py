from flask import Flask
app = Flask(__name__)

# route() decorator in Flask is used to bind URL to a function
# url: 127.0.0.1/hello

@app.route('/hello')
def hello_world():
   return 'hello world'
 

# default <variable> is string
# we can change <variable> into int, float, path
 
@app.route('/hello/<name>')
def hello_name(name):
   return 'Hello %s!' % name   
   

@app.route('/blog/<int:postID>')
def show_blog(postID):
   return 'Blog Number %d' % postID

@app.route('/rev/<float:revNo>')
def revision(revNo):
   return 'Revision Number %f' % revNo