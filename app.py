from flask import Flask, render_template, redirect, request 

import pandas as pd 
import gspread as gs 

app = Flask(__name__, static_folder="./static")


#fsisfd
#sdkjfklsdjlfsd
#oeiuwoepq
#djssdjf
#ksjflfg

@app.route('/api', methods = ['GET', 'POST'])
def api():
    if request.method == 'POST':
        req = request.form 
        print(req.to_dict())
        return redirect(request.url)
    else:
        return render_template('submissionForm.html', templates='templates')


# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()