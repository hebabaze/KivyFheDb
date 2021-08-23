import socket, os,math,time
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivymd.uix.list import MDList,OneLineListItem
from kivy.clock import Clock
Clock.max_iteration = 20
from encryptFunctions import *
from encryptFunctions import Encrypt

from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from plyer import filechooser
from pathlib import Path
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
checked_ele=""
encrypt=Encrypt()
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
    def listfil(self,lista):
        for x in lista:
            self.ids.container.add_widget(OneLineListItem(text=f"{x}" , on_press=lambda x: self.listchecked(x.text)))
    def listchecked(self,x):
        global checked_ele
        checked_ele=x
        self.ids.datashow.text = f" The column [ {x} ] is now Selected"
    def choose_db(self): # fontion de choix de fichier 
        try:
            cmd1 = 'del dbstore/*x.dbx'
            os.system(cmd1)
        except:
            print("Clean Folder")
        filechooser.open_file(on_selection=self.handle_selection)
        self.listfil(colx) #update list with column name 
        self.ids.my_bar.value=0
        #self.ids.idinsert0.hint_text = f" Colunmn to crypt {colx}"
    #_______________#
    def handle_selection(self,selection): # fonction qui gére le choix de fichier
        chosenpath=selection[0]
        self.fname=Path(str(selection[0])).name # extract db name from path
        self.db = TinyDB(chosenpath) # upload database
        global tabx
        tabx=self.db.table('Hr')      #upload database table 
        rdic=tabx.get(doc_id=1) # to check value type
        columns=list(rdic.keys())
        global colx
        colx=columns
        self.ids.datashow.text="Data base Loeded"
        

    #_______________#
    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable
        global dbname
        try:
            Xtable,dbname=encrypt.crypt_table(tabx,self.fname,Xtable,dbname)
        except:
            self.ids.datashow.text=f"Warning ! ..Database [{dbname}] Aleardy Crypted"

        self.ids.datashow.text=f"Database [{dbname}] Crypted succefully"
        print(f"--- {checked_ele}")
    def cryptcolumn(self):
        chosen_col=checked_ele
        if chosen_col not in colx :
            self.ids.datashow.text = "Warning : Choose a valid column name!"
        else :
            e=colx.index(chosen_col)
            global Xtable
            global dbname
            try:
                Xtable,dbname=encrypt.encrypt_col(tabx,colx,e,self.fname,dbname)
            except:
                self.ids.datashow.text=f"Warning !.. Column [{chosen_col} Aleardy crypted ]"
            self.ids.datashow.text=f" Column [{chosen_col}] crypted succefully"

    #_______________#
    def send_db(self):
            x='3'
            Soc.send(x.encode())
            fname=dbname
            SEPARATOR = "~"
            filesize = os.path.getsize(fname)
            Soc.send(f"{encrypt.rsacrypt(fname)}{SEPARATOR}{filesize}".encode('utf-8'))
            current=self.ids.my_bar.value
            with open(fname, "rb") as f:
                while True :
                    for i in range(64,filesize,64):
                        bytes_read = f.read(64)
                        Soc.send(bytes_read)
                        current+=i/filesize  #increment progres bar
                        self.ids.my_bar.value=current #update Progress bar                          
                        if filesize-i < 64 :
                            bytes_read = f.read(filesize-i)
                            Soc.send(bytes_read)
                            current+=filesize-i  #increment progres bar
                            self.ids.my_bar.value=current #update Progress bar  
                    self.ids.datashow.text = f" [{ fname } Sent Succefully ..!"   
                    break
    #_______________#
    def operations(self):
        self.manager.current="operations_screen"
        screen3 = self.manager.get_screen('operations_screen')
        #screen3.ids.idinsert.hint_text = f"colonne to compute {colx}"
        for x in colx:
            screen3.ids.container2.add_widget(OneLineListItem(text=f"{x}" 
            , on_press=lambda x: screen3.listchecked2(x.text)))
    def showdt(self) :
        self.manager.current="show_data_table"
        screen2 = self.manager.get_screen('show_data_table')
        try:
            screen2.ids.sdtleft.remove_widget(table)
        except:
            pass
        if Xtable:
            screen2.crtab(Xtable,60)
        else:
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
        try:
            self.ids.sdtleft.remove_widget(table)
        except:
            pass
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
    def listchecked2(self,x):
        global checked_ele
        checked_ele=x
        self.ids.showchecked.text = f" The column [ {x} ] is now Selected"
    def sumf(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx :
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        else :
            x='4'
            Soc.send(x.encode())
            idc=colx.index(chosen_col)
            Soc.send(str(idc).encode())
            sum=Soc.recv(BS)
            sum=dill.loads(sum)
            sum=priv_key.decrypt(sum)
            self.ids.lresult.text=f" [+] Sum Result : \n  [{sum}]"
        endt=(time.time() - start)*1000
        self.ids.ltime.text=f"[+] Elapsed Time : \n [{endt}] ms "
    def avgf(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx:
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        else:
            x='5'
            Soc.send(x.encode())
            idg=colx.index(chosen_col)
            Soc.send(str(idg).encode())
            avg=Soc.recv(BS)
            avg=dill.loads(avg)
            avg=priv_key.decrypt(avg)
            self.ids.lresult.text=f" [+] AVG Result : \n {avg}"
        endt=(time.time() - start)*1000
        self.ids.ltime.text=f"[+] Elapsed Time : \n [{endt}] ms "            
    #_______________#
    def mulru(self):
        chosen_col=checked_ele
        if chosen_col not in colx :
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        start=time.time()
        x='60'
        Soc.send(x.encode())
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
        print("The M list ",M)
        for x in M: # Check 0 result
            if x==0:
                self.ids.lresult.text="0 Result Dectected"
                tab="End"
                tab=dill.dumps(tab)
                Soc.send(tab)
                return "Zéro Result Detected!.."
        i=0
        m1=M[i]
        for i in range(0,len(M)-1):
            tab=[]
            m2=M[i+1]
            print("the new m2 valuer from list",m2)
            while m1>0:
                if m1%2==1 :
                    print("in While ..this m2",m2)
                    e2=pub_key.encrypt(m2)
                    tab.append(e2)
                m1=m1//2
                m2=m2+m2
    ##########___Send tab
            tab=dill.dumps(tab)
            Soc.send(tab)
        #############___Receiv Sum
            result=Soc.recv(BS)
            #result=zlib.decompress(result)
            result=dill.loads(result)
        ##################_____Decrypt
            result=priv_key.decrypt(result)
            #m1=m2
            print(f" the result for {m1} and {M[i+1]} = {result}")
            m1=result
            
    #################__BreakOut
        self.ids.lresult.text=f"Ru_mul Result : \n [{result}]"
        tab="End"
        tab=dill.dumps(tab)
        Soc.send(tab)
        endt=(time.time() - start)*1000
        self.ids.ltime.text=f"[+] Elapsed Time : \n [{endt}] ms "
        return "Completed Task"
    def mulog(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx :
            self.ids.lresult.text = "Warning : Choose a valid column name!"        
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
                    self.ids.lresult.text(" Product equal to zéro")
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
                        self.ids.lresult.text=f"Log_mul Result : \n [{rprod}]"
                    except:
                        self.ids.lresult.text("Input value is greater than allowed limit")
            Lprod="End"
            Lprod=dill.dumps(Lprod)
            Soc.send(Lprod)
            endt=(time.time() - start)*1000
            self.ids.ltime.text=f"[+] Elapsed Time : \n [{endt}] ms "
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