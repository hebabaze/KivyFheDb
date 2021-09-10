import os
from threading import local  
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
#Kivy Import 
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.image import Image
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
#Kivymd Import
import sys
sys.path.append('assets')
from filemanager import MDFileManager
from kivymd.uix.list import OneLineListItem
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.toast import toast
# Others Import 
import socket,math,time,rsa,dill,os,pysftp,paramiko,ssl
from jnius import autoclass
from tinydb import TinyDB
from phe import paillier
from binascii import hexlify 
from plyer import filechooser
from pathlib import Path
from hoverable import HoverBehavior
#Config And Setting
theme_cls = ThemeManager()
theme_cls.theme_style="Dark"
theme_cls.primary_palette="Yellow" 
Window.size=(440,650)
Builder.load_file('build.kv')
(pubkey, privkey) = rsa.newkeys(265)
pub_key,priv_key=paillier.generate_paillier_keypair(n_length=128)
pkr=pub_key.n
cmd="del *x.db" if platform=='win' else  'rm *x.db'
os.system(cmd)
#Variable Declaration 
HOST = ''  # The server's hostname or IP address
PORT = ''        # The port used by the server
user = ""
passwd = ""
Soc=""
BS = 4096 # send 4096 bytes each time step
#Soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
colx=[] #column list used in Operation[handle_selection choose_db crypt_db cryptcolumn operations upload_db ] ShowDataTable[crtab,sumf,avgf,mulru,mulog]
crypted_cols=[]# Index of crypted colonne
tabx =None # nomal Table 
Xtable=None#Table Crypté
dbname=None #crypted database 
file_name=None #file uploaded
table =None #te Table used in show datatable 
checked_ele=None # selected colummn name 
send_flag=False  # check dababase sending

class Connect(Screen):
    #_______________#
    def db_connect(self):
        global Soc
        try :
            global HOST,PORT
            #HOST="192.168.1.107"
            HOST="135.181.108.235"
            #HOST=self.ids.Ip.text
            PORT=65432
            #PORT=int(self.ids.Port.text)
            user='root' #self.ids.user.text
            passwd='' #self.ids.pswd.text
            ###########Paramiko
            client=paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(HOST,22,user,passwd)
            #stdin,stdout,stderr=client.exec_command('pkill -9 python')
            #stdin,stdout,stderr=client.exec_command('python3 FHE/main.py </dev/null &>/dev/null &')
            #print(stderr.read().decode())
            client.close()
            #####SFTP
            global sftp
            sftp=pysftp.Connection(host=HOST, username=user, password=passwd)
            #Sc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ##########SSL
            context= ssl.SSLContext()
            context.verify_mode = ssl.CERT_NONE
            Sc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Soc=context.wrap_socket(Sc)
            Soc.connect((HOST, PORT))            
            print(Soc.version())
            x='0'
            Soc.send(x.encode())
            pks=dill.dumps(pkr)
            Soc.send(pks)
            print(Soc.recv(6).decode())
            self.manager.current="main_screen" 
        except Exception as e:
            self.ids.constat.text=str(e)
            print(str(e))
            #self.ids.constat.text='Connexion failed..!'
    def onback(self):
        sys.exit(0)
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
    
    #______________************** MD Flile Manager Functions for mobile            
    def select_path(self,path):
        global file_name,tabx,colx
        try:
            cmd="del *x.db" if platform=='win' else  'rm *x.db'
        except :pass
        listpat=path.split('\\')
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
        global colx,file_name,tabx
        if not selection:
            pass
        else:
            self.selection = selection
            colx=crypted_cols=[]
            chosenpath=self.selection[0]
            cmd="del chosenpath\\..\\*x.db" if platform=='win' else  'rm chosenpath/*x.db'
            try:os.system(cmd)
            except:pass
            file_name=Path(str(self.selection[0])).name # extract db name from path
            try:
                self.db = TinyDB(chosenpath) # upload database
                tabx=self.db.table('Hr')      #upload database table 
                rdic=tabx.get(doc_id=1) # to check value type
                self.columns=list(rdic.keys())
                colx=self.columns
                self.listfil(colx) #update list with column name 
                self.ids.my_bar.value=0
                self.ids.datashow.text=f"[{file_name[:-3]}] Data base Loeded"  
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
        return str(x.ciphertext()), x.exponent
    #_______________#
    def crypt_db(self): #__Fonction de cryptage import une fonction d'autre fichier
        global Xtable,dbname,file_name,tabx,checked_ele,crypted_cols
        if not file_name:
            self.ids.datashow.text=f"Warning ! .Choose Database !"        
        elif crypted_cols==[colx.index(x) for x in colx]:
            self.ids.datashow.text=f"Warning ! ..Database [{dbname}] Aleardy Crypted"
        else :
            if Xtable :
                for x in colx : # if the crypted table exist try to crypt the rest of column one by one 
                    checked_ele=x
                    self.cryptcolumn()
                #tabx=Xtable 
            else :
                try:dbname=file_name[:-3]+'x.db' # Create New DB file 
                except:self.ids.datashow.text=f"Warning ! .Choose Database !"
                dbx=TinyDB(dbname)        # Create Tinydb DB  
                Xtable = dbx.table('Dx')   # Create New Table in New DB (dbx)
                for x in tabx :
                    d={}
                    for a,b in x.items() :
                        if str(b).isalpha():
                            d[self.rsacrypt(a)]=self.rsacrypt(b)
                        elif not str(b).isalpha() :
                            d[self.rsacrypt(a)]=self.enciph(b) #changerd line
                    Xtable.insert(d)
                    self.ids.datashow.text=f"Database [{dbname}] Crypted succefully"
                    crypted_cols=[colx.index(x) for x in colx]
    def cryptcolumn(self):
        global dbname,Xtable,file_name,crypted_cols
        crypt_temp=[]
        if not file_name :
            self.ids.datashow.text=f"Warning ! .Choose Database !"
        else:
            if not dbname:
                dbname=file_name[:-3]+'x.db' # Create New DB file
            if not checked_ele:
                self.ids.datashow.text=f"Warning ! .Choose a column !"
                return
            else :
                e=colx.index(checked_ele)
            if [colx.index(x) for x in colx]==crypted_cols:
                self.ids.datashow.text=" All Columns are crypted"
            elif e in crypted_cols:
                self.ids.datashow.text=f"The Row {colx[e]} is aleardy Crypted"
            else:
                dby=TinyDB(dbname) 
                if not Xtable: # intialize crypted table
                    Xtable = dby.table('Dx')                
                    for x in tabx:  
                        Xtable.insert(x)
                for x in Xtable:
                    temp_dict={}
                    for key,val in  x.items():
                        if key!=checked_ele:
                            temp_dict[key]=val
                        elif key==checked_ele:
                            if not str(val).isalpha() :
                                temp_dict[self.rsacrypt(key)]=self.enciph(val)
                            else :
                                temp_dict[self.rsacrypt(key)]=self.rsacrypt(val)
                            crypt_temp.append(temp_dict)
                self.ids.datashow.text=f" Column [{checked_ele}] crypted succefully"
                #except Exception as e:self.ids.datashow.text=str(e)             
                Xtable.truncate()
                for x in crypt_temp:
                    Xtable.insert(x)
                if e not in crypted_cols :
                    crypted_cols.append(e)
                    crypted_cols=sorted(crypted_cols)
    #______________************ Function to send database
    def send_db(self):
        global dbname,send_flag
        print("Soc",Soc)
        if not dbname:
            self.ids.datashow.text="Crypt Database Before"
        else :
            print(" Sending DataBase")
            x='3'
            Soc.sendall(x.encode())
            #dbname= os.path.getsize(dbname)
            print(" Dbname ",dbname)
            Soc.send((dbname).encode())
            print("Current directory **__>>" ,os.getcwd())
            localFilePath = dbname
            remoteFilePath = '/tmp/'+dbname
            sftp.put(localFilePath, remoteFilePath)            
            Acknowldgment=Soc.recv(40) .decode()
            if Acknowldgment.endswith("fully"):
                self.ids.my_bar.value=100 #update Progress bar  
                self.ids.datashow.text = f" [ { dbname[:-3] } ] .. Sent Succefully ..!"   
                send_flag=True
            else:
                self.ids.datashow.text=Acknowldgment
    
    #_______________************Function change Screen to operation screen 
    def operations(self):
        global tabx,crypted_cols
        if send_flag:
            try:
                rdic=tabx.get(doc_id=1)
                int_cols=[colx.index(x) for x in rdic if not str(rdic[x]).isalpha()]
                int_crypted_cols=[x for x in crypted_cols if x in int_cols]
            except: pass
            try:
                cmd="del *x.db" if platform=='win' else  'rm *x.db'
            except :pass
            self.manager.current="operations_screen"
            screen3 = self.manager.get_screen('operations_screen')
            try:
                screen3.ids.container2.clear_widgets()
                for x in int_crypted_cols:
                    screen3.ids.container2.add_widget(OneLineListItem(text=f"{colx[x]}",on_press=lambda x: screen3.listchecked2(x.text)))   
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
        global colx,crypted_cols,tabx,Xtable,dbname,file_name,table,send_flag
        colx=crypted_cols=[]
        tabx =Xtable=dbname=file_name=table=checked_ele =None 
        send_flag=False  # check dababase sending
        return self.choose_db() if platform=='linux' else self.file_manager_open()
    def log_out(self):
        global Soc
        Soc.send("exit".encode())
        Soc.close()
        sys.exit(0)
########################################################### #########
class ShowDataTable(Screen):
    #_______________#
    def crtab(self,tab,mtrc):
        global table,colx
        #self.ids.remove_widget(table)
        def ins_value(Y):
            L=[]
            for x in list(Y.values()):
                if isinstance(x, list):
                    L.append(list(x)[0])
                else:
                    L.append(x)
            return tuple(L)
        table=MDDataTable(
            pos_hint={'center_x':0.5,'center_y':0.3},
            size_hint=(1,.8),
            check=True,
            use_pagination=True,
            rows_num=4,
            pagination_menu_height='100dp',
            column_data=[(str(x),dp(mtrc))for x in colx],
            row_data=[ins_value(x) for x in tab]
            
            )            
        self.add_widget(table)
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
        if not chosen_col  :
            self.ids.showchecked.text = "Warning : Choose a valid column name!"
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
        if not chosen_col :
            self.ids.showchecked.text = "Warning : Choose a valid column name!"
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
        if not chosen_col :
            self.ids.showchecked.text = "Warning : Choose a column !"
        else :
            start=time.time()
            x='60'
            Soc.send(x.encode())
            idd=colx.index(chosen_col)
            M=[] # Pour Stocker Les Valeurs à calculer 
            # Stocker les valeur à calculer 
            for y in range(1,len(tabx)+1):
                Far=tabx.get(doc_id=y)
                M.append(list(Far.values())[idd])
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
        if not chosen_col :
            self.ids.showchecked.text = "Warning : Choose a valid column name!"        
        else :
            x='6'
            Soc.send(x.encode())
            idm=colx.index(chosen_col)
            M=[]
            for x in range(1,len(tabx)+1):
                Far=tabx.get(doc_id=x)
                M.append(list(Far.values())[idm])
            for x in M: # Check 0 result
                if x==0:
                    self.ids.lresult.text=" Product equal to zéro"
                    Lprod="End"
                    Lprod=dill.dumps(Lprod)
                    Soc.send(Lprod)
                    return "Zéro Result Detected!.."

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
class ImageButton(ButtonBehavior,HoverBehavior,Image):
    pass
class RootWidget(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        self.title= "FHEDB"
        self.theme_cls.theme_style="Light"
        self.theme_cls.primary_palette="Yellow"
        self.icon = 'assets/ico.jpg'        
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()