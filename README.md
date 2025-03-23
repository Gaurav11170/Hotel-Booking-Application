**Hotel Booking App**
![image](https://github.com/Rika290/Hotel-booking-app/assets/126352441/8603aba4-c812-433d-bfad-5a053ca89fda)


- App link :- https://hotel-booking-app-y36jbyn9ea4vcddpa5rbt9.streamlit.app/

*ABOUT*:-
- This is a web app of a fictitious travel agency called '@urDesti' which helps in choosing and booking hotels across India at comparatively low prices.


*TOOLS USED*:-
1. This app is built using Python programming language
   -  Pandas the Python library is used for viewing the data in form of data frames
   -  Streamlit, an open source framework under Python is used as an interface to create this web application
2. MySQL, an open-source Relational Database Management System (RDBMS) is used for generating the data.

*METHOD*:
1. Database creation:
- Using MySQL queries, different tables to store data on destination and hotels were created.
- Data on places, i.e, North and South were added
- Table for bookings was created which will accept the input from user
- Once saved, these tables were exported as csv files.
  
Tables:-

a. Destination tables:
 - In the MySQL Workbench, tables called North and South were created
 - Entries like States of (North India,South India), famous tourist places in theose States, along with a ID number were added
 -  In this case, the ID numbers created are unique and hence made as the primary key of both tables
 
b. Table for Hotels/Resorts
- A table called Hotels was created
- Entries like S.No,Name,Places were added
- Here, the column S.No has only unique values  and therefore is the primary key

c. Table for Booking
- A table which gets info from customers for reservation of rooms and travel
- Details like OTP,name of the customer are included
- Since OTP is unique, it is considered as the primary key
 
2.Features integrated:

a. Backend:
- The csv files are imported to Google Colab notebook
- With Pandas in python, the values from data tables can be accessed and manipulated
- OTP Generator:
   - random model was used for creating the OTP; Using smtplib and MIMEText;
   - an email containing the OTP will be sent to the mail id given by the user

b. Frontend:
- The welcome page icon and heading were setup using streamlit
- An user can navigate to Dashboard for viewing further details
- When the menu bar is accessed, user can choose any place and fill the details accordingly along with OTP
- Once all details are given correctly, the screen pops up a message - Booked successfully
- When the process is completed, the user can access the booking information by entering the OTP
- Finally, an acknowledgement mail from the company will be sent to the user

*REFERENCES*:
- https://www.makeuseof.com/otp-verification-system-python/
- https://docs.python.org/3.5/library/email.html
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
- https://docs.streamlit.io/
