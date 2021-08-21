from kivy.clock import Clock
Clock.max_iteration = 20
from logging import root
import socket, os,math
from encryptFunctions import *
from encryptFunctions import Encrypt
encrypt=Encrypt()
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from plyer import filechooser
from kivy.core.image import Image
import json,glob,random
from pathlib import Path
from datetime import datetime
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
Builder.load_file('design.kv')
HOST = ''  # The server's hostname or IP address
PORT = ''        # The port used by the server
SEPARATOR = "<SEPARATOR>"
BS = 4096 # send 4096 bytes each time step
Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pkr=pub_key.n
colx="" #list des colonne 
tabx ="" # Table en claire
Xtable=""#Table Crypté
dbname=""
table =""
#CryptColumn=[]
class Connect(Screen):
    #_______________#
    def db_connect(self):
        self.Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            with self.Soc:
                global HOST
                HOST="192.168.1.107"
                #HOST="135.181.108.235"
                #HOST=self.ids.Ip.text
                global PORT
                PORT=65432
                #PORT=int(self.ids.Port.text)
                Soc.connect((HOST, PORT))
                pks=dill.dumps(pkr)
                Soc.send(pks)
                self.manager.current="main_screen" 
        except:
            self.ids.constat.text="Connexion Field Check Server Stat Or input Value"   
     
#########################################################################
class MainScreen(Screen):

    #_______________#
    def affiche(self,tabx):
        L=""
        for Y in tabx:
            for x,y in Y.items():
                pen=str(f" {x} : {y} "+'| ')
                L=L+pen
            L=L+"\n"
        #self.ids.datashow.text= L
    #_______________#
    def choose_db(self): # fontion de choix de fichier 
        try:
            cmd1 = 'del dbstore/*x.dbx'
            os.system(cmd1)
        except:
            print("Clean Folder")
        filechooser.open_file(on_selection=self.handle_selection)
        self.ids.idinsert0.hint_text = f" Colunmn to crypt {colx}"
    #_______________#
    def handle_selection(self,selection): # fonction qui gére le choix de fichier
        chosenpath=selection[0]
        self.fname=Path(str(selection[0])).name # extract db name from path
        self.db = TinyDB(chosenpath) # upload database
        global tabx
        tabx=self.db.table('Hr')      #upload database table 
        self.affiche(tabx)
        rdic=tabx.get(doc_id=1) # to check value type
        columns=list(rdic.keys())
        global colx
        colx=columns
        """
        try:
            self.ids.sabah.remove_widget(table)
        except:
            pass
        """
        #ShowDataTable.crtab(self,tabx,30)
        self.ids.datashow.text="Data base Loeded"

    #_______________#
    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable
        global dbname
        Xtable,dbname=encrypt.crypt_table(tabx,self.fname,Xtable)
        #self.ids.datashow.text=""
        #self.ids.sabah.remove_widget(table)
        #self.crtab(Xtable,60)
        self.ids.datashow.text="Data base Crypted succefully"
        # self.ids.datashow.text=str(Xtable.all())
    def cryptcolumn(self):
        print("pub_key" ,len(str(pub_key)))
        print("priv_key" ,len(str(priv_key)))
        #def encrypt(tabx,columns):   # crypter une colonne
        chosen_col=self.ids.idinsert0.text
        if chosen_col not in colx :
            self.ids.datashow.text = "Warning : Choose a valid column name!"
        else :
            e=colx.index(chosen_col)
            global Xtable
            global dbname
            Xtable,dbname=encrypt.encrypt_col(tabx,colx,e,self.fname)
            #self.ids.sabah.remove_widget(table)
            self.crtab(Xtable,60)
            self.ids.datashow.text=f" column [{chosen_col} crypted succefully]"
            #self.ids.datashow.text=str(Xtable.all())
            
        
    #_______________#
    def send_db(self):
            x='3'
            Soc.send(x.encode())
            fname=dbname
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
        screen3 = self.manager.get_screen('operations_screen')
        screen3.ids.idinsert.hint_text = f"colonne to compute {colx}"
    def showdt(self) :
        self.manager.current="show_data_table"
        screen2 = self.manager.get_screen('show_data_table')
        screen2.crtab(tabx,30)
#############################################################################        
class ShowDataTable(Screen):
    #_______________#
    def crtab(self,tab,mtrc):
        global table
        table=MDDataTable(
            pos_hint={'center_x':0.5,'center_y':0.5},
            size_hint=(0.9,0.6),
            check=True,
            use_pagination=True,
            rows_num=4,
            pagination_menu_height='100dp',
            column_data=[(str(x),dp(mtrc))for x in colx],
            row_data=[tuple(x.values()) for x in tab]
            )
        self.ids.sdtleft.add_widget(table)
        table.bind(on_check_press=self.checked)
        table.bind(on_row_press=self.row_checked)
    #function for check presses
    def checked(self,instance_table,current_row):
        print(instance_table,current_row)
    #Function for row presses
    def row_checked(self,instance_table,instance_row):
        print(instance_table,instance_row)
        pass
    def onback(self):
        self.manager.current="main_screen"
###############################################################################
class OperationsScreen(Screen):
    #_______________#
    def sumf(self):
        chosen_col=self.ids.idinsert.text
        if chosen_col not in colx :
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
            M=[priv_key.decrypt(x) for x in P]
            for x in M: # Check 0 result
                if x==0:
                    self.ids.opresult.text(" Product equal to zéro")
                    Lprod="End"
                    Lprod=dill.dumps(Lprod)
                    Soc.send(Lprod)
                    return "Zéro Result Detected!.."
                else:
                    C=[math.log(e) for e in M]
                    Ce=[pub_key.encrypt(x) for x in C]
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
                        self.ids.opresult.text("Input value is greater than allowed limit")
            Lprod="End"
            Lprod=dill.dumps(Lprod)
            Soc.send(Lprod)
            return ("Log Mul Completed")
    def onback(self):
        self.manager.current="main_screen"

######################################################################
class RootWidget(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style="Light"
        self.theme_cls.primary_palette="BlueGray"
        return RootWidget()
if __name__ == "__main__":
    MainApp().run()