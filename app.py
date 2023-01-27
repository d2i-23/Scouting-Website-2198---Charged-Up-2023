from flask import Flask, render_template

app = Flask(__name__, static_folder="./static")

@app.route('/')
def index():
    return render_template('submissionForm.html', templates='templates')




#fsisfd
#sdkjfklsdjlfsd
#oeiuwoepq
#djssdjf
#ksjflfg





@app.route('/form')
def api():
    

    #pandas code
    pass

# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()