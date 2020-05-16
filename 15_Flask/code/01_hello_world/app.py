from flask import Flask
app = Flask(__name__)

#app.route(rule, options)
#rule 表示該函數綁定的url
#options 是參數列表，可以傳入函數內使用

@app.route('/')
def hello_world():
   return 'Hello World'

if __name__ == '__main__':
   app.run()