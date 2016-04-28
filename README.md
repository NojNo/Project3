Category Item Project Version 1.0 created on 28.04.2016

General Usage: 
- there are 3 usertypes: logged out visitor, logged in visitor and the owner
- logged out visitor: can visit the homepage and the item´s page of a category
- logged in visitor: can visit the homepage/the item´s page of a category and can add a category
- owner: if the user adds a category, she becomes the owner. The user is now able to create/delete/edit categories and even items.
- Sign in is possible via Google+

Table of contents

Installing
Quick start 
What´s included? 
Bugs and feature requests 
Creators + Contact 
Licence and Copyright

Installing 
The program itself does not need to be installed. However, keep in mind the program is written in Python 2.7 on a Windows machine. The whole code was executed within a Vagrant Virtual Machine and the results are displayed in a browser (in my case Chrome Version 49.0.2623.112). 
Furthermore, you need a Gmail-Account in order to create a project on the Google´s Developer Console page. 

Quick Start:

First, set up the right settings on the Google Developers Console in order to have a client ID and client secret(read more under: https://developers.google.com/identity/sign-in/web/devconsole-project). 
Keep the following settings in mind:

Authorized JavaScript origins: 
http://localhost:5000
Authorized redirect URIs: 
http://localhost:5000/gconnect
http://localhost:5000/oauth2callback
http://localhost:5000/disconnect

Now you need to enable the Google+ API (read more under: https://developers.google.com/+/web/signin/#enable_the_google_api)

Then download the JSON file and save it as: client_secret.json
This file should be in the same directory as the application.py file.

In order to run the program, Vagrant needs to be up, running and you need to be in the right directory in Vagrant. At this point type python application.py 
As the application is running on http://localhost:5000, type the URL in the broweser. 
Now you should see the application. 
In order to be able to see more than just the public pages, you need to be logged in. Currently, there is only the Google+ Sign in. If you are logged in, you can add another category. Now this category is yours/ You are the owner. You can edit/delete it or you can click on it and add items into it (and edit/delete them, as well). Only the owner has these features.

So what do you need to run the programm? 
You need to set up Python + Vagrant Virtual Machine + Google Developer Console settings (+ a Gmail-Account) + a browser(best practise here: Chrome). 

What's included

Within the download you will find the following directories and files:

catalog/ 
├── application.py
├── database_setup.py 
├── database_setup.pyc
├── lotsofitems.py
├── place your client_secret.json in here
├── static/
|	├──css/
|	|	├── bootstrap.css
|	|	├── bootstrap.min.css
|	|	├── bootstrap-theme.css
|	|	└── bootstrap-theme.min.css
|	├──fonts/
|	|	├── glyphicons-halflings-regular.eot
|	|	├── glyphicons-halflings-regular.svg
|	|	├── glyphicons-halflings-regular.ttf
|	|	├── glyphicons-halflings-regular.woff
|	|	└── glyphicons-halflings-regular.woff2
|	├──js/
|	|	├── bootstrap.js
|	|   └── bootstrap.min.js
|	├──config.json
|	└──styles.css
|
└── templates/
		├── deleteCategory.py
		├── deleteLatestItem.py
		├── editCategory.py
		├── editLatestItem.py
		├── header.py
		├── home.py
		├── index.py
		├── main.py
		├── newCategory.py
		├── newLatestItem.py
		├── publichome.py
		├── publicshowLatestItem.py
		└── showLatestItem.py

If you run application.py(is the client-program), you will access the other files. Here it is important that you do not change the position of the files and folders.

Bugs and feature requests
I have not found any. If you do so, please contact me!

Creators + Contact
Name: Nojan Nourbakhsh 
Email: nojan@hotmail.de 
Name: Udacity 
Email: review-support@udacity.com

Licence and Copyright
All rights reserved by Udacity Inc and Nojan Nourbakhsh. Category Item Project Version 1.0 and its use are subject to a licence agreement and are also subject to copyright, trademark, patent and/or other laws. For further infos, please contact Nojan Nourbakhsh.