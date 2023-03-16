from flask import Flask, render_template, redirect, request, url_for
import pandas as pd
import gspread as gs 

app = Flask(__name__, static_folder="./static")

gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1NPK8B3CFtDfY_CaPi3BkOUvlktXQY2y3SsNFlIXqhhs/edit#gid=0')
worksheet = mainWorkSheet.get_worksheet(0)

def processRawData(dataFrame):
    idList = ['Team Number', 'Match Number', 'Lower Cube Scored', 'Middle Cube Scored', 'Upper Cube Scored', 'Lower Cone Scored', 'Upper Cone Scored', 'Middle Cone Scored', 'Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Lower Total Score', 'Middle Total Score', 'Upper Total Score']
    for i in idList:
        string = 'dataFrame["' + i + '"] = dataFrame["' + i + '"].astype("int32", errors = "ignore")'
        exec(string)
    dataFrame['Auto Charge Station'] = 12 if 'engaged' else (8 if 'not engaged' else 0)
    dataFrame['Tele-op Charge Station'] = 10 if 'engaged' else (6 if 'not engaged' else 0)
    return dataFrame

def updateAutonomous():
    processData = pd.DataFrame(worksheet.get_all_records())[['Team Number','Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Auto Charge Station']]
    processData['Count'] = 1
    processData['Auto Total Score'] = processData['Lower Auto Score'] + processData['Middle Auto Score'] + processData['Upper Auto Score'] + processData['Auto Charge Station']
    processData= processData.groupby(by = 'Team Number', as_index = True).apply(lambda x: x.sum(numeric_only = True) / x['Count'].sum()).sort_values(by = 'Auto Total Score', ascending = False)
    processData.drop('Count', inplace = True, axis = 1)
    autoWordSheet = mainWorkSheet.get_worksheet(1)
    autoWordSheet.clear()
    autoWordSheet.update([processData.columns.values.tolist()] + processData.values.tolist())

def updateTele():
    processData = pd.DataFrame(worksheet.get_all_records())[['Team Number','Lower Total Score', 'Middle Total Score', 'Upper Total Score', 'Tele-op Charge Station','Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score']]
    processData['Count'] = 1
    processData['Lower Tele-op Score'] = processData['Lower Total Score'] - processData['Lower Auto Score']
    processData['Middle Tele-op Score'] = processData['Middle Total Score'] - processData['Middle Auto Score']
    processData['Upper Tele-op Score'] = processData['Upper Total Score'] - processData['Upper Auto Score']
    processData['Tele-op Total Score'] = processData['Lower Tele-op Score'] + processData['Middle Tele-op Score'] + processData['Upper Tele-op Score']
    print(processData[processData['Team Number'] == 3213])
    processData= processData.groupby(by = 'Team Number', as_index = True).apply(lambda x: x.sum(numeric_only = True) / x['Count'].sum()).sort_values(by = 'Tele-op Total Score', ascending = False)
    processData.drop(['Count', 'Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Lower Total Score', 'Middle Total Score','Upper Total Score'], inplace = True, axis = 1)
    autoWordSheet = mainWorkSheet.get_worksheet(2)
    autoWordSheet.clear()
    autoWordSheet.update([processData.columns.values.tolist()] + processData.values.tolist())

def updateTotal():
    autoWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(1).get_all_records()).set_index('Team Number')
    teleopWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(2).get_all_records()).set_index('Team Number')
    totalWorksheet = pd.concat([autoWorksheet, teleopWorksheet], axis = 1 )
    totalWorksheet['Lower Total Score'] = totalWorksheet['Lower Tele-op Score'] + totalWorksheet['Lower Auto Score']
    totalWorksheet['Middle Total Score'] = totalWorksheet['Middle Tele-op Score'] + totalWorksheet['Middle Auto Score']
    totalWorksheet['Upper Total Score'] = totalWorksheet['Upper Tele-op Score'] + totalWorksheet['Upper Auto Score']
    totalWorksheet['Total Charge Station'] = totalWorksheet['Tele-op Charge Station'] + totalWorksheet['Auto Charge Station']
    totalWorksheet['Total Score'] = totalWorksheet['Tele-op Total Score'] + totalWorksheet['Auto Total Score']
    newtotalWorksheet = totalWorksheet[['Lower Total Score', 'Middle Total Score', 'Upper Total Score', 'Total Charge Station', 'Total Score']].reset_index()
    mainWorkSheet.get_worksheet(3).clear()
    mainWorkSheet.get_worksheet(3).update([newtotalWorksheet.columns.values.tolist()] + newtotalWorksheet.values.tolist())

def updateAnalysis():
    processData = pd.DataFrame(worksheet.get_all_records())
    processData = processData.drop(['Match Number', 'Alliance Color', 'Comment'], axis = 1)
    processData1 = processData[['Team Number', 'W/L', 'Auto Taxi', 'Gameplay Position']].groupby('Team Number', as_index = True).apply(lambda x: (x[x == 'TRUE']).count()/x.count())[['W/L', 'Auto Taxi', 'Gameplay Position']]
    processData2 = processData[['Team Number', 'Tele-op Charge Station', 'Auto Charge Station']].groupby('Team Number', as_index = True).apply(lambda x: (x[x > 0]).count()/x.count())[['Tele-op Charge Station', 'Auto Charge Station']]
    processData['Total Score'] = processData['Lower Total Score'] + processData['Middle Total Score'] + processData['Upper Total Score']
    processData3 = processData[['Team Number', 'Lower Total Score', 'Middle Total Score', 'Upper Total Score', 'Total Score']].groupby('Team Number', as_index = True).apply(lambda x: x.sum()/x['Total Score'].sum())[['Lower Total Score', 'Upper Total Score', 'Middle Total Score']]
    processData = pd.concat([processData1, processData2, processData3], axis = 1).reset_index().fillna(0)
    mainWorkSheet.get_worksheet(4).clear()
    mainWorkSheet.get_worksheet(4).update([processData.columns.values.tolist()] + processData.values.tolist())

def updateFinalWorksheet():
    winRateResults = pd.DataFrame(mainWorkSheet.get_worksheet(4).get_all_records())[['Team Number', 'W/L']].sort_values(by = 'Team Number').set_index('Team Number')
    teleOpStats = pd.DataFrame(mainWorkSheet.get_worksheet(2).get_all_records())[['Team Number', 'Tele-op Charge Station', 'Tele-op Total Score']].sort_values(by = 'Team Number').set_index('Team Number')
    autoStats =  pd.DataFrame(mainWorkSheet.get_worksheet(1).get_all_records())[['Team Number', 'Auto Charge Station', 'Auto Total Score']].sort_values(by = 'Team Number').set_index('Team Number')

    finalWorksheet = pd.concat([winRateResults,teleOpStats,autoStats], ignore_index=False, axis = 1).reset_index()

    finalWorksheet['Overall Score'] = finalWorksheet['Tele-op Charge Station'] + finalWorksheet['Auto Charge Station'] + finalWorksheet['Auto Total Score'] + finalWorksheet['Tele-op Total Score']

    finalWorksheet = finalWorksheet.sort_values(by = 'Overall Score').reset_index().rename(columns = {'index': 'Ranking', 'W/L': 'Winrate'})
    mainWorkSheet.get_worksheet(5).clear()
    mainWorkSheet.get_worksheet(5).update([finalWorksheet.columns.values.tolist()] + finalWorksheet.values.tolist())

def addData(dictionary):
    dataFrame = pd.DataFrame(worksheet.get_all_records())
    dataframe = pd.DataFrame()
    for i in dictionary:
        testData = pd.DataFrame(i, index = [0])
        dataframe  = pd.concat([dataframe, testData], ignore_index = True)
    dataframe = processRawData(dataframe)
    dataframe = pd.concat([dataFrame, dataframe], ignore_index=True)
    dataframe = dataframe.dropna(thresh=5).drop_duplicates(subset = ['Team Number', 'Match Number'], keep = 'first')
    worksheet.clear()
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    updateAutonomous()
    updateTele()
    updateTotal()
    updateAnalysis()
    updateFinalWorksheet()
    
storedRequest = []

@app.route('/')
def index():
    return redirect(url_for('api'))

@app.route('/api', methods = ['GET', 'POST'])
def api():
    if request.method == 'POST':
        global storedRequest
        req = request.form.to_dict()
        storedRequest.append(req)
        if len(storedRequest) > 3:
            addData(storedRequest)
            storedRequest = []
    return render_template('submissionForm.html', templates='templates')

@app.route('/data')
def data():
    return render_template('spreadSheetData.html', templates = 'template')

# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()