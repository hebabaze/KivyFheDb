from kivy.clock import Clock
Clock.max_iteration = 20
from logging import root
import socket, os,math
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
colx="" #list des colonne 
tabx ="" # Table en claire
Xtable=""#Table Crypté
class Connect(Screen):
    #_______________#
    def db_connect(self):
        self.Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.Soc:
            Soc.connect((HOST, PORT))
            print(f"[+] Connecting to {HOST}:{PORT}")
            print("[+] Connected.")
            pks=dill.dumps(pkr)
            Soc.send(pks)
            self.manager.current="main_screen"                
#########################################################################
class MainScreen(Screen):
    #_______________#
    def __init__(self, **kw):
        super().__init__(**kw)    
    #_______________#
    def affiche(self,tabx):
        L=""
        for Y in tabx:
            for x,y in Y.items():
                pen=str(f" {x} : {y} "+'| ')
                L=L+pen
            L=L+"\n"
        self.ids.datashow.text= L
    #_______________#
    def choose_db(self): # fontion de choix de fichier 
        try:
            cmd1 = 'del dbstore/*x.dbx'
            os.system(cmd1)
        except:
            print("Clean Folder")
        filechooser.open_file(on_selection=self.handle_selection)
    #_______________#
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
    #_______________#
    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable
        Xtable,self.dbname=encrypt.crypt_table(tabx,self.fname)
        self.ids.datashow.text=str(Xtable.all())
        print(self.dbname)
    #_______________#
    def send_db(self):
            x='3'
            Soc.send(x.encode())
            fname=self.dbname
            SEPARATOR = "~"
            filesize = os.path.getsize(fname)
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
    #_______________#
    def operations(self):
        self.manager.current="operations_screen"
        screen2 = self.manager.get_screen('operations_screen')
        screen2.ids.idinsert.hint_text = f" choose colonne to crypt {colx}"

###############################################################################
class OperationsScreen(Screen):
    #_______________#
    def sumf(self):
        chosen_col=self.ids.idinsert.text
        if chosen_col not in colx:
            self.ids.opresult.text = "Warning : Choose a valid column name!"
        else :
            x='4'
            Soc.send(x.encode())
            idc=colx.index(chosen_col)
            Soc.send(str(idc).encode())
            sum=Soc.recv(BS)
            sum=dill.loads(sum)
            sum=priv_key.decrypt(sum)
            self.ids.opresult.text=f" [+] Resultat de la somme est [{sum}]"
    
    def avgf(self):

        chosen_col=self.ids.idinsert.text
        if chosen_col not in colx:
            self.ids.opresult.text = "Warning : Choose a valid column name!"
        else:
            x='5'
            Soc.send(x.encode())
            idg=colx.index(chosen_col)
            Soc.send(str(idg).encode())
            avg=Soc.recv(BS)
            avg=dill.loads(avg)
            avg=priv_key.decrypt(avg)
            self.ids.opresult.text=f" [+] Resultat d'AVG {avg}"


    #_______________#
    def mulru(self):
        print("from mul PK",priv_key)
        x='60'
        Soc.send(x.encode())
        chosen_col=self.ids.idinsert.text
        idd=colx.index(chosen_col)
        T=[] # Pour Stocker Les Valeurs à calculer 
        pkp = paillier.PaillierPublicKey(int(pkr)) #pkr=pub_key.n pour reconstruire le ciphertext
        # Stocker les valeur à calculer 
        for y in range(1,len(Xtable)+1):
            Far=Xtable.get(doc_id=y)
            T.append(list(Far.values())[idd])
        P=[paillier.EncryptedNumber(pkp, x, 0) for x in T]
        print(" Russ THIS IS P",P)
        #Decrypter les valeur à traiter
        M=[priv_key.decrypt(x) for x in P]

        for x in M: # Check 0 result
            if x==0:
                self.ids.opresult.text="0 Result Dectected"
                tab="End"
                tab=dill.dumps(tab)
                Soc.send(tab)
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
                    self.ids.opresult.text=f"Sending Table n° {j} ==> {tab}"
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
                    self.ids.opresult.text=f"Multiplication n° {j} Result :[{result}]"
                    m1=result
            #################__BreakOut
                self.ids.opresult.text=f"[Task Completed] Product Reslut With Ru Methode :[{result}]"
                tab="End"
                tab=dill.dumps(tab)
                #tab=zlib.compress(tab)
                Soc.send(tab)
                return "Completed Task"
    def mulog(self):

        chosen_col=self.ids.idinsert.text
        if chosen_col not in colx:
            self.ids.opresult.text = "Warning : Choose a valid column name!"
        else :
            x='6'
            Soc.send(x.encode())
            idm=colx.index(chosen_col)
            L=[]
            pkg = paillier.PaillierPublicKey(int(pkr))
            for x in range(1,len(tabx)+1):
                Far=Xtable.get(doc_id=x)
                L.append(list(Far.values())[idm])
            P=[paillier.EncryptedNumber(pkg, x, 0) for x in L]
            print("THIS IS P",P)

            M=[]
            for p in P:
                dp=(priv_key.decrypt(p))
                M.append(dp)
                print(dp)
            print("LOG This is M",M)
            for x in M: # Check 0 result
                if x==0:
                    print(" Product equal to zéro")
                    Lprod="End"
                    Lprod=dill.dumps(Lprod)
                    Soc.send(Lprod)
                    return "Zéro Result Detected!.."
                else:
                    C=[math.log(e) for e in M]
                    Ce=[pub_key.encrypt(x) for x in C]
                    print(f"\n {Ce} \n")
                    Lprod=dill.dumps(Ce)
                    Soc.send(Lprod)
                    rprod=Soc.recv(BS)
                    rprod=dill.loads(rprod)
                    rprod=priv_key.decrypt(rprod)
                    logging.warning(f"Prod received before exp {rprod}")
                    try:
                        #709.78271 is the largest value I can compute the exp of on my machine
                        rprod=round(math.exp(rprod))
                        self.ids.opresult.text=f"[Task Completed] Product Reslut With Log Methode :[{rprod}]"
                    
                    except:
                        print("Input value is greater than allowed limit")
            Lprod="End"
            Lprod=dill.dumps(Lprod)
            Soc.send(Lprod)
            return ("Log Mul Completed")


######################################################################
class RootWidget(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()