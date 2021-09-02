import os  
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
#Kivy Import 
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
#Kivymd Import
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import OneLineListItem
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.toast import toast
# Others Import 
import socket,math,time,rsa,dill,os
from jnius import autoclass
from tinydb import TinyDB
from phe import paillier
from binascii import hexlify 
from plyer import filechooser
from pathlib import Path
#Config And Setting
theme_cls = ThemeManager()
theme_cls.theme_style="Dark"
theme_cls.primary_palette="Yellow" 
Window.size=(440,650)
Builder.load_file('build.kv')
(pubkey, privkey) = rsa.newkeys(512)
pub_key,priv_key=paillier.generate_paillier_keypair(n_length=128)
pkr=pub_key.n
cmd="del *x.db" if platform=='win' else  'rm *x.db'
os.system(cmd)
#Variable Declaration 
HOST = ''  # The server's hostname or IP address
PORT = ''        # The port used by the server
BS = 4096 # send 4096 bytes each time step
Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
colx=None #column list 
crypted_cols=[]# Crypted Columns list 
tabx =None # nomal Table 
Xtable=None#Table Crypté
dbname=None #crypted database 
file_name=None #file uploaded
table =None #te Table used in show datatable 
checked_ele=None # selected colummn name 
send_flag=True  # check dababase sending

class Connect(Screen):
    #_______________#
    def db_connect(self):
        
        self.Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            with self.Soc:
                global HOST,PORT
                HOST="192.168.1.107"
                #HOST="135.181.108.235"
                #HOST=self.ids.Ip.text
                PORT=65432
                #PORT=int(self.ids.Port.text)
                Soc.connect((HOST, PORT))
                pks=dill.dumps(pkr)
                Soc.send(pks)
                self.manager.current="main_screen" 
        except:
            self.ids.constat.text='Connexion failed..!'
#########################################################################
class MainScreen(Screen):
    selection = ListProperty([]) # define Path list type
    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager=MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.select_path,
                ext=[".py", "db",".db",".jpg"],
            )
    
    #______________************** MD Flile Manager Functions            
    def select_path(self,path):
        global file_name,tabx,colx
        print(path)
        print(type(path)  )
        listpat=path.split('\\')
        print(listpat)
        file_name=listpat[-1]
        try:
            self.db = TinyDB(path) # upload database
            tabx=self.db.table('Hr')      #upload database table 
            rdic=tabx.get(doc_id=1) # to check value type
            self.columns=list(rdic.keys())
            colx=self.columns
            self.listfil(colx) #update list with column name 
            self.ids.my_bar.value=0
            self.ids.datashow.text=f"[{file_name[:-3]}] Data base Loeded"  
        except Exception as e:
            self.ids.datashow.text=str(e)       
        self.exit_manager()
        toast(path)
    def file_manager_open(self):
        mypath = '/storage/emulated/0/' if platform == 'android' else '/'
        self.file_manager.show(mypath)
        self.manager_open = True
    def exit_manager(self):
        self.manager_open = False
        self.file_manager.close()
    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    
    #______________*************  Functions Fill Lists with column name
    def listfil(self,lista):
        try:
            self.ids.container.clear_widgets()
        except:
            pass
        for x in lista:
            self.ids.container.add_widget(OneLineListItem(text=f"{x}" , on_press=lambda x: self.listchecked(x.text)))
    def listchecked(self,x): # Function return selected element in the list 
        global checked_ele
        checked_ele=x
        self.ids.datashow.text = f" The column [ {x} ] is now Selected"
        toast(f"This Column {x} is selected")
    
    #______________************* Choose database on win env
    def choose_db(self): # fontion de choix de fichier 
        filechooser.open_file(on_selection=self.handle_selection)
    def handle_selection(self,selection): # fonction qui gére le choix de fichier
        if platform=='android':
            self.getpath()
        if not selection:
            pass
        else:
            self.selection = selection
            chosenpath=self.selection[0]
            global file_name,tabx,colx
            file_name=Path(str(self.selection[0])).name # extract db name from path
            try:
                self.db = TinyDB(chosenpath) # upload database
                tabx=self.db.table('Hr')      #upload database table 
                rdic=tabx.get(doc_id=1) # to check value type
                self.columns=list(rdic.keys())
                colx=self.columns
                self.listfil(colx) #update list with column name 
                self.ids.my_bar.value=0
                self.ids.datashow.text="Data base Loeded"
            except Exception as e:
                self.ids.datashow.text=str(e) 
    
    #______________************ Crypt Functions
    def rsacrypt(self,data):       # Fonction de Cryptage RSA
        message=data.encode()
        crypto = rsa.encrypt(message, pubkey)
        crypto = hexlify(crypto).decode()
        return crypto
    def enciph(self,y):            # get encipher text
        x=pub_key.encrypt(y)
        return x.ciphertext()
    #_______________#
    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable,dbname,file_name,tabx,checked_ele
        if dbname:
            self.ids.datashow.text=f"Warning ! ..Database [{dbname}] Aleardy Crypted"
        elif not file_name:
            self.ids.datashow.text=f"Warning ! .Choose Database !"
        else :
            try:dbname=file_name[:-3]+'x.db' # Create New DB file 
            except:self.ids.datashow.text=f"Warning ! .Choose Database !"
            dbx=TinyDB(dbname)        # Create Tinydb DB  
            Xtable = dbx.table('Dx')   # Create New Table in New DB (dbx)
            if Xtable :
                for x in colx : # if the crypted table exist try to crypt the rest of column one by one 
                    checked_ele=x
                    self.cryptcolumn()
                #tabx=Xtable 
            else :
                if tabx:
                    for x in tabx :
                        d={}
                        for a,b in x.items() :
                            if len(str(b)) >64 :
                                self.ids.datashow.text=f"The Row {a} is aleardy Crypted"
                                d[self.rsacrypt(a)]=b
                            else:
                                if str(b).isalpha():
                                    d[self.rsacrypt(a)]=self.rsacrypt(b)
                                elif not str(b).isalpha() :
                                    d[self.rsacrypt(a)]=self.enciph(int(b))
                        Xtable.insert(d)
                        self.ids.datashow.text=f"Database [{dbname}] Crypted succefully"

    def cryptcolumn(self):
        global dbname,Xtable,file_name,crypted_cols
        if not file_name :
            self.ids.datashow.text=f"Warning ! .Choose Database !"
        else:
            if not dbname:
                dbname=file_name[:-3]+'x.db' # Create New DB file
            e=colx.index(checked_ele)
            if colx[e] in crypted_cols:
                self.ids.datashow.text=f"The Row {colx[e]} is aleardy Crypted"
            else:
                dby=TinyDB(dbname) 
                if not Xtable: # intialize crypted table
                    Xtable = dby.table('Dx')                
                    for x in tabx:  
                        Xtable.insert(x)
                print("this is tabx",tabx)
                i=1 
                rdic=Xtable.get(doc_id=1) #L=[x for x in rdic if len(str(rdic[x])) > 64  ]
                if not str(rdic[colx[e]]).isalpha() :
                    print("str(rdic[colx[e]])" ,str(rdic[colx[e]]))
                    for x in Xtable:
                        Xtable.update({colx[e]:self.enciph(x[colx[e]])},doc_ids=[i])
                        i+=1
                else :
                    for x in Xtable:
                        print("Else : str(rdic[colx[e]])" ,str(rdic[colx[e]]))
                        Xtable.update({colx[e]:self.rsacrypt(x[colx[e]])},doc_ids=[i])
                        i+=1
                self.ids.datashow.text=f" Column [{checked_ele}] crypted succefully"
                #except Exception as e:self.ids.datashow.text=str(e)
             
            if colx[e] not in crypted_cols :
                crypted_cols.append(colx[e] )
        if colx==crypted_cols:
            self.ids.datashow.text=" All Columns are crypted"
        print("The crypted colonne List",crypted_cols)
    #______________************ Function to send database
    def send_db(self):
        global dbname,send_flag,HOST
        if not dbname:
            self.ids.datashow.text="Crypt Database Before"
        else :
            x='3'
            if not HOST:
                self.ids.datashow.text="U Should connected First"
            else :
                Soc.send(x.encode())
                filesize = os.path.getsize(dbname)
                Soc.send(f"{self.rsacrypt(dbname)}".encode('utf-8'))
                Soc.send(str(filesize).encode('utf-8'))
                current=self.ids.my_bar.value #initialise Pbar
                with open(dbname, "rb") as f:
                    while True :
                        for i in range(64,filesize,64):
                            bytes_read = f.read(64)
                            Soc.send(bytes_read)
                            current+=(i/filesize)*100  #increment progres bar
                            self.ids.my_bar.value=current #update Progress bar                          
                            if filesize-i < 64 :
                                bytes_read = f.read(filesize-i)
                                Soc.send(bytes_read)
                                current+=filesize-i  #increment progres bar
                                self.ids.my_bar.value=current #update Progress bar  
                        self.ids.datashow.text = f" [ { dbname } ] .. Sent Succefully ..!"   
                        send_flag=True
                        break
    #_______________************Function change Screen to operation screen 
    def operations(self):
        if send_flag:
            self.manager.current="operations_screen"
            screen3 = self.manager.get_screen('operations_screen')
            try:
                screen3.ids.container2.clear_widgets()
                for x in colx:
                    screen3.ids.container2.add_widget(OneLineListItem(text=f"{x}",on_press=lambda x: screen3.listchecked2(x.text)))   
            except:pass
        else:
            self.ids.datashow.text = f" Database not sent yet ..!"    
    #______________*************Function to show data table content
    def showdt(self) :
        global Xtable,tabx,table
        self.manager.current="show_data_table"
        screen2 = self.manager.get_screen('show_data_table')
        try:screen2.ids.sdtleft.remove_widget(table)
        except:pass
        if Xtable:
            screen2.crtab(Xtable,60)
        else:
            try:screen2.crtab(tabx,30)
            except:pass
    #______________************* Function to choose with fonction to use for uplaod db
    def upload_db(self):
        return self.choose_db() if platform=='win' else self.file_manager_open()
########################################################### #########
class ShowDataTable(Screen):
    #_______________#
    def crtab(self,tab,mtrc):
        global table,colx
        try:
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
            self.ids.sdtleft.remove_widget(table)
        except:
            pass
        self.ids.sdtleft.add_widget(table)
        table.bind(on_check_press=self.checked)
        table.bind(on_row_press=self.row_checked)
    #function for check presses
    def checked(self,instance_table,current_row):
        #("from checked",instance_table,current_row)
        pass
    #Function for row presses
    def row_checked(self,instance_table,instance_row):
        #("from row checked",instance_table,instance_row)
        pass
    def on_row_press(self, instance_table,instance_cell_row):
        #("from row press instance_cell_row",instance_cell_row)
        pass
    def get_row_checks(instance_table):
        pass


    def onback(self):
        self.manager.current="main_screen"
###############################################################################
class OperationsScreen(Screen):
    #_______________#
    def listchecked2(self,x): #selection de clonne 
        global checked_ele
        checked_ele=x
        self.ids.showchecked.text = f"  {x} "
        self.ids.op.text='...'
        self.ids.lresult.text="..."
        self.ids.ltime.text=" ... "
    def sumf(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx or not chosen_col :
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        else :
            x='4'
            Soc.send(x.encode())
            idc=colx.index(chosen_col)
            Soc.send(str(idc).encode())
            sum=Soc.recv(BS)
            sum=dill.loads(sum)
            sum=priv_key.decrypt(sum)
            self.ids.lresult.text=f"{sum}"
        endt=(time.time() - start)*1000
        self.ids.ltime.text=f"{round(endt,2)} ms "
    def avgf(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx or not chosen_col :
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        else:
            x='5'
            Soc.send(x.encode())
            idg=colx.index(chosen_col)
            Soc.send(str(idg).encode())
            avg=Soc.recv(BS)
            avg=dill.loads(avg)
            avg=priv_key.decrypt(avg)
            self.ids.lresult.text=f"{avg}"
        endt=(time.time() - start)*1000
        self.ids.ltime.text=f"{round(endt,2)} ms "            
    #_______________#
    def mulru(self):
        chosen_col=checked_ele
        if chosen_col not in colx or not chosen_col :
            self.ids.lresult.text = "Warning : Choose a valid column name!"
        else :
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
                while m1>0:
                    if m1%2==1 :
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
                m1=result
                
        #################__BreakOut
            self.ids.lresult.text=f"{result}"
            tab="End"
            tab=dill.dumps(tab)
            Soc.send(tab)
            endt=(time.time() - start)*1000
            self.ids.ltime.text=f"{round(endt,2)} ms "
            return "Completed Task"
    def mulog(self):
        start=time.time()
        chosen_col=checked_ele
        if chosen_col not in colx or not chosen_col :
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
                    try:
                        #709.78271 is the largest value I can compute the exp of on my machine
                        rprod=round(math.exp(rprod))
                        self.ids.lresult.text=f"{rprod}"
                    except:
                        self.ids.lresult.text("Input value is greater than allowed limit")
            Lprod="End"
            Lprod=dill.dumps(Lprod)
            Soc.send(Lprod)
            endt=(time.time() - start)*1000
            self.ids.ltime.text=f"{round(endt,2)} ms "
            return ("Log Mul Completed")
    def onback(self):
         self.manager.current="main_screen"

######################################################################
class RootWidget(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        self.title= "FHEDB"
        self.theme_cls.theme_style="Light"
        self.theme_cls.primary_palette="Yellow"        
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()