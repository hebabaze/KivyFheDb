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
HOST = '192.168.1.105'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
SEPARATOR = "<SEPARATOR>"
BS = 4096 # send 4096 bytes each time step
Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pkr=pub_key.n
colx=""
tabx =""
Xtable=""
class Connect(Screen):
    def db_connect(self):
        self.Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.Soc:
            Soc.connect((HOST, PORT))
            print(f"[+] Connecting to {HOST}:{PORT}")
            print("[+] Connected.")
            pks=dill.dumps(pkr)
            Soc.send(pks)
            self.manager.current="main_screen"                

class MainScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)    

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
        global tabx
        tabx=self.db.table('Hr')
        self.affiche(tabx)
        rdic=tabx.get(doc_id=1) # to check value type
        columns=list(rdic.keys())
        print(columns) 
        global colx
        colx=columns
             

    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable
        Xtable,self.dbname=encrypt.crypt_table(tabx,self.fname)
        self.ids.datashow.text=str(Xtable.all())
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
        self.manager.current="operations_screen"
        screen2 = self.manager.get_screen('operations_screen')
        screen2.ids.idinsert.hint_text = f" choose colonne to crypt {colx}"

###############################################################################
class OperationsScreen(Screen):
    def sumf(self):
        chosen_col=self.ids.idinsert.text
        if chosen_col not in colx:
            print("Choose a valid column name! ")
        else :
            x='4'
            Soc.send(x.encode())
            idc=colx.index(chosen_col)
            Soc.send(str(idc).encode())
            sum=Soc.recv(BS)
            sum=dill.loads(sum)
            sum=priv_key.decrypt(sum)
            print(f" [+] Resultat de la somme est [{sum}]")

    def mulru(self):
        print("XTABLE TYPE ",Xtable)
        print("XTABLE TYPE ",type(Xtable))
        #print("ALL XTABLE VALUE ",Xtable.all())
        print("pkr ",pkr)
        print(" Type pkr",type(pkr))
        print("Mul=====>",colx,type(colx))
        x='60'
        Soc.send(x.encode())
        #def RussMul(s,pub_key,pkr,BS,tabp):
        chosen_col=self.ids.idinsert.text
        idd=colx.index(chosen_col)
        print(" id To Calculate ",idd)
        L=[] # Pour Stocker Les Valeurs à calculer 
        pkp = paillier.PaillierPublicKey(int(pkr)) #pkr=pub_key.n pour reconstruire le ciphertext
        print("pkp ",pkp)
        print(" Type pkp",type(pkp))
        # Stocker les valeur à calculer 
        for y in range(1,len(Xtable)+1):
            Far=Xtable.get(doc_id=y)
            print("Far ===> ",Far)
            print("type FAR",type(Far))
            L.append(list(Far.values())[idd])
            print("Curren L",L)
        P=[paillier.EncryptedNumber(pkp, x, 0) for x in L]
        #Decrypter les valeur à traiter
        M=[priv_key.decrypt(x) for x in P]
        print("This is M=====",M)
        for x in M: # Check 0 result
            if x==0:
                print("0 Result Dectected")
                tab="End"
                tab=dill.dumps(tab)
                Soc.send(tab)
                print("Zéro Result Detected!..")
                return "Zéro Result Detected!.."
            else:
                i=0
                j=1
                m1=M[i]
                for i in range(0,len(M)-1):
                    tab=[]
                    m2=M[i+1]
                    while m1>0:
                        if m1%2==1 :
                            e2=pub_key.encrypt(m2)
                            tab.append(e2)
                        m1=m1//2
                        m2=m2*2
            ##########___Send tab
                    print(f"Sending Table n° {j} ==> {tab}")
                    j+=1
                    tab=dill.dumps(tab)
                    #tab=zlib.compress(tab)
                    Soc.send(tab)
                #############___Receiv Sum
                    result=Soc.recv(BS)
                    #result=zlib.decompress(result)
                    result=dill.loads(result)
                ##################_____Decrypt
                    result=priv_key.decrypt(result)
                    print(f"Multiplication n° {j} Result :[{result}]")
                    m1=result
            #################__BreakOut
                print(f"Final Result :[{result}]")
                tab="End"
                tab=dill.dumps(tab)
                #tab=zlib.compress(tab)
                Soc.send(tab)
                print("Task Completed")
                return "Completed Task" 


class RootWidget(ScreenManager):
    pass
class MainApp(MDApp):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()