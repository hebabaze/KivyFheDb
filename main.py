from kivy.clock import Clock
Clock.max_iteration = 20
from logging import root
import socket, os
from encryptFunctions import *
from encryptFunctions import Encrypt
encrypt=Encrypt()
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from plyer import filechooser
from kivy.core.image import Image
import json,glob,random
from pathlib import Path
from datetime import datetime
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager,Screen
Builder.load_file('design.kv')
HOST = '192.168.1.109'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
SEPARATOR = "<SEPARATOR>"
BS = 4096 # send 4096 bytes each time step
Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Connect(Screen):
    def db_connect(self):
        self.Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.Soc:
            Soc.connect((HOST, PORT))
            print(f"[+] Connecting to {HOST}:{PORT}")
            print("[+] Connected.")
            pks=dill.dumps(pkr)
            Soc.send(pks)

            #pks=dill.dumps(pkr)
            #Soc.send(pks)
            self.manager.current="main_screen"
              #while Soc:
                

class MainScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)  
        self.varx=100  

    def affiche(self,tabx):
        L=""
        for Y in tabx:
            for x,y in Y.items():
                pen=str(f" {x} : {y} "+'| ')
                L=L+pen
            L=L+"\n"
        self.ids.datashow.text= L

    def choose_db(self): # fontion de choix de fichier 
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self,selection): # fonction qui gére le choix de fichier
        chosenpath=selection[0]
        print(type(chosenpath))
        self.fname=Path(str(selection[0])).name
        print(self.fname)
        self.db = TinyDB(chosenpath)
        self.tabx=self.db.table('Hr')
        self.affiche(self.tabx)
        rdic=self.tabx.get(doc_id=1) # to check value type
        columns=list(rdic.keys())
        print(columns)        
#Add
    def crypt_db(self):

        X,self.dbname=encrypt.crypt_table(self.tabx,self.fname)
        self.ids.datashow.text=str(X)
        print(self.dbname)
    def send_db(self):

            x='3'
            Soc.send(x.encode())
            fname=self.dbname
            print("crypted db to send",fname)
            SEPARATOR = "~"
            filesize = os.path.getsize(fname)
            print("filesize",filesize)
            Soc.send(f"{encrypt.rsacrypt(fname)}{SEPARATOR}{filesize}".encode('utf-8'))
            with open(fname, "rb") as f:
                while True :
                    for i in tqdm(range(64,filesize,64),unit="Bytes",unit_divisor=64,desc=f"Sending [{fname}]",colour= 'green'):
                        bytes_read = f.read(64)
                        Soc.send(bytes_read)
                        if filesize-i < 64 :
                            bytes_read = f.read(filesize-i)
                            Soc.send(bytes_read)
                    break
    def operations(self):
        pass




class RootWidget(ScreenManager):
    pass
class MainApp(MDApp):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()