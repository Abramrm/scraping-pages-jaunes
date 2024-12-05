# Scraping-pages-jaunes

This repository was thinked as a "Prove of concept" of a class that allows to recover informations about french companies from the website : www.pagesjaunes.fr (French Yellow Pages)

## How does it work ?

* Step 1 : Clone the repository
* Step 2 : Create your own file "secret.py" in the root directory of the repository. Add it the information : WEBPAGE_PAGESJAUNES = "XXX" with XXX the url of the page from pagesjaunes.fr that you want to recover data from
* Step 3 : Launch the script "main.py" that contains all the needed methods inside a single class
* Step 4 : Get your data inside the file "complete_file.csv" inside the folder "/output/" (it will be created automatically)

## What else ?

* Check the "requirements.txt" file to make sure you have all the packages required to use this code
* The "selenium" package uses the Google Chrome browser to navigate through the pages, so you need to have it installed on you PC