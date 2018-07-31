try:
    # for Python2
    from Tkinter import *  
except ImportError:
    # for Python3
    from tkinter import *
import tkinter as tk
import json
import os
import pymongo
from bson import json_util
from bson.json_util import loads
from pymongo import MongoClient

import urllib.request
import base64

roots = Tk() 
roots.title('Backup System') 


# get image from URL
with urllib.request.urlopen("http://res.cloudinary.com/chatbotph/image/upload/v1531710125/logo_sly4nm.png") as url:
    raw_data = url.read()
    
b64_data = base64.encodestring(raw_data)
photo = tk.PhotoImage(data=b64_data)

mongouriL = Label(roots, text='Enter MongoDB URI:')
mongouriL.grid(row=2, column=0, sticky=W)

mongouri = Entry(roots, width = 50) 
mongouri.grid(row=3, column=0, sticky=E)

collectionsL = Label(roots, text='(Optional) Enter Collections separated by (,):')
collectionsL.grid(row=4, column=0, sticky=W)

collections = Entry(roots, width = 50) 
collections.grid(row=5, column=0, sticky=E)

labelText = StringVar()
L = Label(roots, textvariable=labelText, fg = "#1ca9e5")
L.grid(row=7, column=0) 

intruction = Label(image=photo, highlightcolor="#000000")
intruction.grid(row=0, column=0, sticky=W)

def beforeBackUp():
    L.config(fg = "#1ca9e5")
    labelText.set("Backing up. Please wait.")
    roots.after(1, backUpCollections)

def beforeUpload():
    L.config(fg = "#1ca9e5")
    labelText.set("Uploading. Please wait.")
    roots.after(1, uploadCollections)    

def backUpCollections():
    if(mongouri.get() == ""):
        L.config(fg = "red")
        labelText.set("Please enter a valid uri.")
    
    uri = mongouri.get()
    client = pymongo.MongoClient(uri)
    db = client.get_default_database()
    collectionsArray = db.collection_names()
    specificCollections = collections.get()

    if(specificCollections == ""):
        for i in range(len(collectionsArray)):
            file = open(collectionsArray[i] + ".txt", "w")
            for obj in db[collectionsArray[i]].find():
                obj = json.dumps(obj, sort_keys=True, default=json_util.default)
                file.write(str(obj) + '\n')
            file.close()
    else:
        actualCollections = [x.strip() for x in specificCollections.split(',')]
        for j in range(len(actualCollections)):
            for i in range(len(collectionsArray)):
                if(actualCollections[j] == collectionsArray[i]):
                    file = open(collectionsArray[i] + ".txt", "w")
                    for obj in db[collectionsArray[i]].find():
                        obj = json.dumps(obj, sort_keys=True, default=json_util.default)
                        file.write(str(obj) + '\n')
                    file.close()
    L.config(fg = "#1ca9e5")
    labelText.set("Back-up Done.")

def uploadCollections():
    uri = mongouri.get()
    client = pymongo.MongoClient(uri)
    db = client.get_default_database()
    collectionsArray = db.collection_names()

    for i in range(len(collectionsArray)):
        if(collectionsArray[i] != "system.indexes"):
            db[collectionsArray[i]].remove({})
            file = open(collectionsArray[i] + ".txt", "r")
            for line in file:
                trueObject = loads(line)
                db[collectionsArray[i]].insert(trueObject)
            file.close()
    labelText.set("Data exported to server: \n%s" %uri)

backUpButton = Button(roots, bg="#1ca9e5", fg = "white", text="Backup", command=beforeBackUp)
backUpButton.grid(row=10, column=0, pady=(15, 1), sticky=W)
backUpButton.config(width = 42)

frontDownButton = Button(roots, bg="#1ca9e5", fg = "white", text="Upload", command=beforeUpload)
frontDownButton.grid(row=11, column=0, pady=(0, 5), sticky=W)
frontDownButton.config(width = 42)

roots.mainloop()