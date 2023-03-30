from flask import Flask, render_template, redirect, request, url_for
import pandas as pd
import gspread as gs 
from statboxFormating import updateStatBox, createHTML
from updateSpreadsheet import updateTele, updateAnalysis, updateAutonomous, updateFinalWorksheet, updateTotal, updateAll


app = Flask(__name__, static_folder="./static")
gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1NPK8B3CFtDfY_CaPi3BkOUvlktXQY2y3SsNFlIXqhhs/edit#gid=0')
worksheet = pd.DataFrame()
deleteOrNot = True
changedNumbers = []
fakeChangedNumber = []

def check():
    global worksheet
    worksheet = pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records())
    return not worksheet.empty

notEmpty = check()

def processRawData(dataFrame):
    idList = ['Team Number', 'Match Number', 'Lower Cube Scored', 'Middle Cube Scored', 'Upper Cube Scored', 'Lower Cone Scored', 'Upper Cone Scored', 'Middle Cone Scored', 'Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Lower Total Score', 'Middle Total Score', 'Upper Total Score']
    for i in idList:
        string = 'dataFrame["' + i + '"] = dataFrame["' + i + '"].astype("int32", errors = "ignore")'
        exec(string)
    return dataFrame

def addData(dictionary):
    global worksheet
    dataframe = pd.DataFrame()
    for i in dictionary:
        testData = pd.DataFrame(i, index = [0])
        dataframe  = pd.concat([dataframe, testData], ignore_index = True)
    dataframe = processRawData(dataframe)
    dataframe = pd.concat([worksheet, dataframe], ignore_index=True)
    dataframe = dataframe.dropna(thresh=5).drop_duplicates(subset = ['Team Number', 'Match Number'], keep = 'first')
    worksheet = dataframe
    mainWorkSheet.get_worksheet(0).clear()
    mainWorkSheet.get_worksheet(0).update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    
storedRequest = []

@app.route('/')
def index():
    return redirect(url_for('api'))

@app.route('/api', methods = ['GET', 'POST'])
def api():
    
    global deleteOrNot
    if request.method == 'POST':
       
        global storedRequest, notEmpty, fakeChangedNumber, changedNumbers
        req = request.form.to_dict()
        print(req)
        if req['Team Number'] == '' or req['Match Number'] == '' or req['Alliance Color'] == '' or req['W/L'] == '' or req['Auto Charge Station'] == '' or req['Auto Taxi'] == '' or req['Gameplay Position'] == '' or req['Tele-op Charge Station'] == '':
            #This ridiculously long if statement is to a precaution for if the form bypasses the submission requirement by refreshing the page after previously inputting something
            pass
        else:
            req['Auto Charge Station'] = 12 if req['Auto Charge Station'] == 'engaged' else (8 if req['Auto Charge Station'] == 'engaged' else 0)
            req['Tele-op Charge Station'] = 10 if req['Tele-op Charge Station'] == 'engaged' else (6 if req['Tele-op Charge Station'] == 'not engaged' else 0)
            fakeChangedNumber.append(req['Team Number'])
            print(fakeChangedNumber, req['Team Number'])
            storedRequest.append(req)
            currentCount = len(storedRequest)
            if currentCount >= 3:
                addData(storedRequest)
                storedRequest = []
                notEmpty = True 
                changedNumbers = fakeChangedNumber.copy()
                fakeChangedNumber = []
                if notEmpty:
                    updateAll()
                else:
                    check()


    return render_template('submissionForm.html', templates='templates')

@app.route('/data')
def data():
    global deleteOrNot, changedNumbers, storedRequest
    if notEmpty:
        if len(storedRequest) > 0:
            addData(storedRequest)
            storedRequest = []
        teamList = updateStatBox(deleteOrNot, changedNumbers)
        deleteOrNot = False
        changedNumbers = []
    else:
        teamList = []
    createHTML()
    return render_template('spreadSheetData.html', templates = 'template', teamList = teamList)

@app.route('/cantFindMe', methods = ['GET', 'POST'])
def portal():
    if request.method == 'POST':
        global changedNumber
        req = request.form.to_dict()
        if req['passCode'] == '21982198':
            updateAll()
            teamList = updateStatBox(True, changedNumbers)
        
        elif req['passCode'] == 'clearEverything123':
            for i in range(0,6):
                mainWorkSheet.get_worksheet(i).clear()
            updateStatBox(True, trueDelete = True)
            changedNumber = []

        elif req['passCode'] == 'resetJson067':
            teamList = updateStatBox(True, changedNumber = [])
            changedNumbers = []
            #this is for if the data had to be resetted or restored to a certain point in time 
            
    return render_template('secretPage.html', templates = 'template' )

# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()

