import pandas as pd
import gspread as gs
from updateSpreadSheet import spreadSheetLink
#make this crack into a function 

gc = gs.service_account('googleService.json')
mainWorkSheet = gc.open_by_url(spreadSheetLink)
folder_path = 'jsonSaves'

def createHTML():
    htmlStore = ''
    print(pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records()).empty)
    if not pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records()).empty: 
        analysisWorksheet = pd.DataFrame(mainWorkSheet.get_worksheet(5).get_all_records()).set_index('Team Number')
        comments = pd.DataFrame(mainWorkSheet.get_worksheet(0).get_all_records())
        comments = comments.loc[comments['Comment'] != '', ['Team Number', 'Comment']].groupby('Team Number').apply(lambda x: ','.join(x['Comment']).split(','))    #.groupby('Team Number').apply(lambda x: ','.join(x).split(','))
        analysisWorksheet = pd.concat([analysisWorksheet, comments], axis = 1).rename(columns = {0: 'Comment'})
        teamListList = analysisWorksheet.index.tolist()

        for i in teamListList:
            listedComments = ""
            jsonFile =  analysisWorksheet.loc[i].to_dict() 
            try:
                if len(jsonFile['Comment']) > 0:
                    for j in jsonFile['Comment']:
                        listedComments += f'    <li>{j}</li>\n'
            except TypeError:
                listedComments = ""
            htmlStore += f'''
            <div id = {i}>
                <div class = 'statbox' >
                <p class = 'bolder' > {i}</p>
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
    else:
        teamListList = []
    with open('templates\\stats.html', 'w') as s:
        s.write(htmlStore)
        s.close()
    return teamListList




