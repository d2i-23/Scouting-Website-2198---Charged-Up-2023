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

# main driver function
if __name__ == '__main__':
    
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()