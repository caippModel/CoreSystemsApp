# Order Form Automation
![Title](docs/title.png)
Web App to manage systems in Bioinformatics and Modeling Cores B and C.

## Setup
Install requirements with 
`pip install -r requirements.txt`   
Python version required: 3.9.*

### Mac OS
`brew install redis`
`brew services start redis`

### Ubuntu
`sudo apt-get install redis`

## Web App
The app is spearated into a few parts based on access level required and functionality.   
### Login
You have to login into your account the access the app. Each user have different roles that grant specific access.   
Login system is implemented with *flask_login* with added custom roles. The roles are:   
- Admin
- User
- Core B
- Core C
   
### Core B
This part has every system that Core B uses which are:   
- Orders
- Invoices
- PI list
   
### Core C

## Reader
Extension to read specific .csv data files.   

## PdfWriter
Extension to edit invoice PDF files.   

## General App flow
![App flow](docs/Core_App_entry_flow.png)