from flask import Flask, render_template, redirect, request, url_for
import pandas as pd
import gspread as gs 

app = Flask(__name__, static_folder="./static")
#fsisfd
#sdkjfklsdjlfsd
#oeiuwoepqvenv
#djssdjf

gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1NPK8B3CFtDfY_CaPi3BkOUvlktXQY2y3SsNFlIXqhhs/edit#gid=0')
worksheet = mainWorkSheet.get_worksheet(0)

def processRawData(dataFrame):
    dataFrame = dataFrame.dropna(thresh=10).drop_duplicates(subset = ['Team Number', 'Match Number'], keep = 'first')
    idList = ['Team Number', 'Match Number', 'Lower Cube Scored', 'Middle Cube Scored', 'Upper Cube Scored', 'Lower Cone Scored', 'Upper Cone Scored', 'Middle Cone Scored', 'Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Lower Total Score', 'Middle Total Score', 'Upper Total Score']
    for i in idList:
        string = 'dataFrame["' + i + '"] = dataFrame["' + i + '"].astype("int32", errors = "ignore")'
        exec(string)
    dataFrame['Auto Charge Station'] = 12 if 'engaged' else (8 if 'not engaged' else 0)
    dataFrame['Tele-op Charge Station'] = 10 if 'engaged' else (6 if 'not engaged' else 0)
    dataFrame['W/L'] = dataFrame['W/L'].apply(lambda x: True if x == 'true' else False)
    return dataFrame

def addRawData(dictionary):
    dataFrame = pd.DataFrame(worksheet.get_all_records())
    testData = dictionary
    dataframe = pd.DataFrame(testData, index = [0])
    dataframe = processRawData(pd.concat([dataFrame,dataframe], ignore_index = True))
    worksheet.clear()
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

def updateAutonomous():
    processData = pd.DataFrame(worksheet.get_all_records())[['Team Number','Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Auto Charge Station']]
    processData['Count'] = 1
    processData['Auto Total Score'] = processData['Lower Auto Score'] + processData['Middle Auto Score'] + processData['Upper Auto Score'] + processData['Auto Charge Station']
    processData= processData.groupby(by = 'Team Number', as_index = True).apply(lambda x: x.sum(numeric_only = True) / x['Count'].sum()).sort_values(by = 'Auto Total Score', ascending = False)
    processData.drop('Count', inplace = True, axis = 1)
    autoWordSheet = mainWorkSheet.get_worksheet(1)
    autoWordSheet.clear()
    autoWordSheet.update([processData.columns.values.tolist()] + processData.values.tolist())

    
#def updateAutonomous()


#ksjflfg
@app.route('/')
def index():
    return redirect(url_for('api'))

@app.route('/api', methods = ['GET', 'POST'])
def api():
    if request.method == 'POST':
        req = request.form.to_dict()
        print(req)
        addRawData(req)
        updateAutonomous()
    return render_template('submissionForm.html', templates='templates')


# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()