# Chat-bot-final
 The final chat-bot created for IIS project by group 6

#TODO
    Clean the whole database naming and file naming.

This chatbot is made for a locally hosted database, the database may be easilly changed to work on a server hosted one with support for local data storage, currently it assume a local database of mongoDB is hosted on the port: mongodb://localhost:27018 (the database part requires some cleaning but can be easily done with just a different location of storing database memory)


To run this chatbot you need to have the database hosted on mongodb://localhost:27018. The database is in the redo_main/redo/medical_app and the host using the mongoDB hosting instruction provided here: https://www.geeksforgeeks.org/how-to-start-mongodb-local-server/

The link for the mongoDB config: https://drive.google.com/file/d/1FuEM_cCJ0CgeqE_ID3Mioryc4fM0rQWD/view?usp=sharing, 
Take this file and add your paths as required.


Steps after the mongoDB server has been setup (and the required libraries has been installed): 
1st) cd to the folder with temp.py 
2nd) run py temp.py 
