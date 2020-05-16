from flask import Flask, render_template, request, flash
from forms import ContactForm


app = Flask(__name__)
app.secret_key = 'development key'

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
   form = ContactForm()
   
   if request.method == 'POST':
      if form.validate():
         return render_template('success.html')
      else:         
         flash('All fields are required.')
         print('testtesttest')
         return render_template('contact.html', form = form)
   
   if request.method == 'GET':
      return render_template('contact.html', form = form)

if __name__ == '__main__':
   app.run(debug = True)