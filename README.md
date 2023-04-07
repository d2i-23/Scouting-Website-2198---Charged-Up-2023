# Scouting-Website-2198---Charged-Up-2023
This is the scouting website for the 2023 charged up for FRC. 

To run this, you need VS code as the IDE and an internet connection. When you are in VS code, you also need to run this in the venv virtual environment. 

Before launching it however, you need to open an (empty) google spreadsheet and connect it to a g-service account. You can do this by reading here: https://robocorp.com/docs/development-guide/google-sheets/interacting-with-google-sheets

Afterwards, paste the JSON at googleService.json in order to gain permission for accessing the bot, and provide the link to the spreadsheet(make sure that the spreadsheet is accessible to the bot by giving it the necessary perms) at the updateSpreadsheet.py file at the variable spreadSheetLink as a string. With that, you should be good to go! 

