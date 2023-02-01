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
    processData= processData.groupby(by = 'Team Number', as_index = True).apply(lambda x: x.sum(numeric_only = True) / x['Count'].sum()).sort_values(by = 'Tele-op Total Score', ascending = False)
    processData.drop(['Count', 'Lower Auto Score', 'Middle Auto Score', 'Upper Auto Score', 'Lower Total Score', 'Middle Total Score','Upper Total Score'], inplace = True, axis = 1)
    autoWordSheet = mainWorkSheet.get_worksheet(2)
    autoWordSheet.clear()
    autoWordSheet.update([processData.columns.values.tolist()] + processData.values.tolist())

def updateTotal():
    try: 
        autoWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(1).get_all_records())
        teleopWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(2).get_all_records())
    except: 
        autoWorksheet = pd.DataFrame()
        teleopWorksheet = pd.DataFrame()
    totalWorksheet = pd.concat([autoWorksheet, teleopWorksheet], axis = 0 )
    totalWorksheet['Lower Total Score'] = totalWorksheet['Lower Tele-op Score'] + totalWorksheet['Lower Auto Score']
    totalWorksheet['Middle Total Score'] = totalWorksheet['Middle Tele-op Score'] + totalWorksheet['Middle Auto Score']
    totalWorksheet['Upper Total Score'] = totalWorksheet['Upper Tele-op Score'] + totalWorksheet['Upper Auto Score']
    totalWorksheet['Total Charge Station'] = totalWorksheet['Tele-op Charge Station'] + totalWorksheet['Auto Charge Station']
    totalWorksheet['Total Score'] = totalWorksheet['Tele-op Total Score'] + totalWorksheet['Auto Total Score']
    newtotalWorksheet = totalWorksheet[['Lower Total Score', 'Middle Total Score', 'Upper Total Score', 'Total Charge Station', 'Total Score']]
    mainWorkSheet.get_worksheet(3).clear()
    mainWorkSheet.get_worksheet(3).update([newtotalWorksheet.columns.values.tolist()] + newtotalWorksheet.values.tolist())

def updateAnalysis():
    processData = pd.DataFrame(worksheet.get_all_records())
    processData.drop([['Match Number', 'Alliance Color', 'Comment']])
    processData1 = processData[['W/L', 'Auto Taxi', 'Gameplay Position']].groupby('Team Number', as_index=True).apply(lambda x: (len(x[x == 'TRUE']/ x.count()))*100)
    processData2 = processData.groupby[['Tele-op Charge Station', 'Auto Charge Station']]('Team Number', as_index = True).apply(lambda x: (len(x[x != 0]/ x.count()))*100)
    processData3 = processData.groupby('Team Number', as_index = True)[['Lower Total Scored', 'Middle Total Scored', 'Upper Total Scored']].apply(lambda x: (x.sum(numeric_only = True)/(x['Lower Total Scored'].sum() + x['Middle Total Scored'].sum() + x['Upper Total Scored'].sum()))*100)
    processData = pd.concat([processData1, processData2, processData3], axis = 0)
    mainWorkSheet.get_worksheet(4).clear()
    mainWorkSheet.get_worksheet(4).update([processData.columns.values.tolist()] + processData.values.tolist())

def addData(dictionary):
    try: 
        dataFrame = pd.DataFrame(worksheet.get_all_records())
    except: 
        dataFrame = pd.DataFrame()
    testData = dictionary
    dataframe = pd.DataFrame(testData, index = [0])
    dataframe = processRawData(pd.concat([dataFrame,dataframe], ignore_index = True))
    worksheet.clear()
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    updateAutonomous()
    updateTele()
    updateTotal()
    updateAnalysis()

#ksjflfg
@app.route('/')
def index():
    return redirect(url_for('api'))

@app.route('/api', methods = ['GET', 'POST'])
def api():
    if request.method == 'POST':
        req = request.form.to_dict()
        print(req)
        addData(req)
    return render_template('submissionForm.html', templates='templates')


# main driver function
if __name__ == '__main__':
    #djd
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()