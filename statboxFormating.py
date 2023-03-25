import pandas as pd
import gspread as gs
import json
import os
#make this crack into a function 

gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1NPK8B3CFtDfY_CaPi3BkOUvlktXQY2y3SsNFlIXqhhs/edit#gid=0')
analysisWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(5).get_all_records()).set_index('Team Number')
comments = pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records())
comments = comments.loc[comments['Comment'] != '', ['Team Number', 'Comment']].groupby('Team Number').apply(lambda x: ','.join(x['Comment']).split(','))    #.groupby('Team Number').apply(lambda x: ','.join(x).split(','))
analysisWorksheet = pd.concat([analysisWorksheet, comments], axis = 1).rename(columns = {0: 'Comment'})
folder_path = 'jsonSaves'
files = os.listdir(folder_path)
teamListList = analysisWorksheet.index.tolist()


def updateStatBox(deleteOrNot, changedNumber = []):
    if deleteOrNot:
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print('file undeletable or no files exist')
        teamList = teamListList
    else:
        teamList = changedNumber
    for i in teamList: 
        located = analysisWorksheet.loc[i] 
        located = located.to_dict()
        try: 
            for j in range(len(located['Comment'])):
                if located['Comment'][j].find("’") > -1:
                    located['Comment'][j] = located['Comment'][j].replace("’", "`")
        except TypeError:
            pass
                    
        located['Team Number'] = i 
        with open(f'jsonSaves\\team_{i}.json', 'w') as f:
            json.dump(located, f)
    return teamListList


def createHTML():
    htmlStore = ''
    for file in files:
        listedComments = ""
        jsonFile = json.load(open(f'jsonSaves\\{file}', 'r'))   
        try:
            if len(jsonFile['Comment']) > 0:
                for i in jsonFile['Comment']:
                    listedComments += f'    <li>{i}</li>\n'
        except TypeError:
            listedComments = ""
        htmlStore += f'''
        <div id = {jsonFile['Team Number']}>
            <div class = 'statbox' >
            <p class = 'bolder' > {jsonFile['Team Number']}</p>
            <p><b>Winrate: </b>{str(round(jsonFile['Winrate']*100, 2)) + '%'}</p>
            <p><b>Position: </b>{'Offense' if jsonFile['Gameplay Position'] > 0.75 else ('Mix' if jsonFile['Gameplay Position'] > 0.5 else 'Defense')}</p>
            <p><b>Average Tele-op Charge Station: </b>{round(jsonFile['Tele-op Charge Station'],2)}</p>
            <p><b>Average Auto Charge Station: </b>{round(jsonFile['Auto Charge Station'],2)}</p>
            <p><b>Average Total Score: </b>{round(jsonFile['Overall Score'],2)}</p> 
            <p><b>{'Comments:' if listedComments != '' else ''}</b></p>
            <ul>
            {listedComments}
            </ul>
            
        </div>
        <br>
        </div>
        '''
    with open('templates\\stats.html', 'w') as s:
        s.write(htmlStore)
    #return open('stats.html', 'r')
    


#Write a program that checks if the json file are still the same 

#Write a program that stores a bunch of json file in the statis section 




