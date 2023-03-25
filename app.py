from flask import Flask, render_template, redirect, request, url_for
import pandas as pd
import gspread as gs 
from statboxFormating import updateStatBox, createHTML
from updateSpreadsheet import updateTele, updateAnalysis, updateAutonomous, updateFinalWorksheet, updateTotal, updateAll

app = Flask(__name__, static_folder="./static")

gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1NPK8B3CFtDfY_CaPi3BkOUvlktXQY2y3SsNFlIXqhhs/edit#gid=0')
worksheet = pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records())
deleteOrNot = True
changedNumbers = []


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
        global storedRequest
        req = request.form.to_dict()
        if req['Team Number'] == '' or req['Match Number'] == '' or req['Alliance Color'] == '' or req['W/L'] == '' or req['Auto Charge Station'] == '' or req['Auto Taxi'] == '' or req['Gameplay Position'] == '' or req['Tele-op Charge Station'] == '':
            #This ridiculously long if statement is to a precaution for if the form bypasses the submission requirement by refreshing the page after previously inputting something
            pass
        else:
            req['Auto Charge Station'] = 12 if req['Auto Charge Station'] == 'engaged' else (8 if req['Auto Charge Station'] == 'engaged' else 0)
            req['Tele-op Charge Station'] = 10 if req['Tele-op Charge Station'] == 'engaged' else (6 if req['Tele-op Charge Station'] == 'not engaged' else 0)
            changedNumbers.append(req['Team Number'])
            storedRequest.append(req)
            currentCount = len(storedRequest)
        if currentCount == 0:
            updateAutonomous()
            updateTele()
        elif currentCount == 1:  
            updateTotal()
            updateAnalysis()
        elif currentCount == 2:
            updateFinalWorksheet()
        elif currentCount == 3:
            addData(storedRequest)
            storedRequest = []
    return render_template('submissionForm.html', templates='templates')

@app.route('/data')
def data():
    global deleteOrNot, changedNumbers
    teamList = updateStatBox(deleteOrNot, changedNumbers)
    deleteOrNot = False
    changedNumbers = []
    createHTML()
    return render_template('spreadSheetData.html', templates = 'template', teamList = teamList)

@app.route('/cantFindMe', methods = ['GET', 'POST'])
def portal():
    if request.method == 'POST':
        req = request.form.to_dict()
        if req['passCode'] == 'hammyjammybreaks887!#':
            updateAll()
            teamList = updateStatBox(True, changedNumbers)
            return render_template('spreadSheetData.html', templates = 'template', teamList = teamList)
    return render_template('secretPage.html', templates = 'template' )

# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()

