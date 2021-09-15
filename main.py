import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.core.window import Window
Window.size=(440,650)
#Kivy Import 
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.image import Image
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
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
Builder.load_file('build.kv')
(pubkey, privkey) = rsa.newkeys(256)
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
sftp=None
class Connect(Screen):
    #_______________#
    def connect_db(self):
        global Soc,sftp
        try :
            global HOST,PORT
            #HOST="192.168.1.107"
            HOST="135.181.108.235"
            #HOST=self.ids.Ip.text
            PORT=443
            #PORT=int(self.ids.Port.text)
            user='root' #self.ids.user.text
            passwd= 'Takeit'
            #self.ids.pswd.text
        except Exception as e:
                self.ids.constat.text=f"Identification {str(e)}"
            ###########Paramiko
        try:
            client=paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(HOST,22,user,passwd)
            #stdin,stdout,stderr=client.exec_command('pkill -9 python')
            #stdin,stdout,stderr=client.exec_command('python3 FHE/main.py </dev/null &>/dev/null &')
            client.close()
        except Exception as e:
            self.ids.constat.text=f"PARAMIKO {str(e)}"
#__SFTP________            
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp=pysftp.Connection(host=HOST, username=user, password=passwd,cnopts=cnopts)
#__SSL_________        
        try:
            context= ssl.SSLContext()
            context.verify_mode = ssl.CERT_NONE
            Sc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Soc=context.wrap_socket(Sc)
            Soc.connect((HOST, PORT))            
            x='0'
            Soc.send(x.encode())
            pks=dill.dumps(pkr)
            Soc.send(pks)
            tm=Soc.recv(6).decode()
            self.manager.current="main_screen" 
        except Exception as e:
            self.ids.constat.text=f"SSl {str(e)}"
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
        listpat=path.split('\\')
        file_name=listpat[-1]
        dpath=path[:-len(file_name)]
        try:
            cmd="del dpath*x.db" if platform=='win' else  'rm dpath\*x.db'
        except :pass
        print(" the dpath is ",dpath)        
        try:
            cmd="del *x.db" if platform=='win' else  'rm *x.db'
        except :pass
        try:
            self.db = TinyDB(path) # upload database
            tabx=self.db.table('Hr')      #upload database table 
            rdic=tabx.get(doc_id=1) # to check value type
            self.columns=list(rdic.keys())
            colx=self.columns
            self.listfil(colx) #update list with column name 
            self.ids.my_bar.value=0
            rmtfpth=os.path.basename(file_name)
            self.ids.datashow.text=f"[{rmtfpth[:-3]}] Data Base Loaded" 
            print("________From select CWD",os.getcwd()) 
        except Exception as e:
            self.ids.datashow.text=str(e)       
        self.exit_manager()
        toast(path)
    def file_manager_open(self):
        mypath = '/storage/emulated/0/' if platform == 'android' else '/'
        self.file_manager.show(mypath)
        self.manager_open = True
        try:
            cmd="del *x.db" if platform=='win' else  'rm *x.db'
        except :pass
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

# Function return selected element in the list     
    def listchecked(self,x): 
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
    
#______________************ Crypt Functions RSA & Paillier
    def rsacrypt(self,data):       # Fonction de Cryptage RSA
        message=data.encode()
        crypto = rsa.encrypt(message, pubkey)
        crypto = hexlify(crypto).decode()
        return crypto
    def enciph(self,y):            # get encipher text
        x=pub_key.encrypt(y)
        return str(x.ciphertext()), x.exponent
#__Crypt Database Function   
    def crypt_db(self):
        global Xtable,dbname,file_name,tabx,checked_ele,crypted_cols
        if not file_name:
            self.ids.datashow.text=f"Warning ! .Choose Database !"        
        elif crypted_cols==[colx.index(x) for x in colx]:
            rmtfpth=os.path.basename(dbname)
            self.ids.datashow.text=f"Warning ! ..Database [{rmtfpth}] Aleardy Crypted"
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
                        if not str(b).isalpha() :
                            d[self.rsacrypt(a)]=self.enciph(b)
                        else:
                            d[self.rsacrypt(a)]=self.rsacrypt(b)                            
                    Xtable.insert(d)
                rmtfpth=os.path.basename(dbname)
                self.ids.datashow.text=f"Database [{rmtfpth}] Crypted succefully"
                crypted_cols=[colx.index(x) for x in colx]
#__Crypt Column Function                
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
#______________************ Send database Function
    def send_db(self):
        global dbname,send_flag,sftp
        if not dbname:
            self.ids.datashow.text="Crypt Database Before"
        else :
            x='3'
            Soc.sendall(x.encode())
            Soc.send((dbname).encode())
            localFilePath = dbname
            rmtfpth=os.path.basename(dbname)
            dpath=dbname[:-len(rmtfpth)]
            remoteFilePath = '/tmp/'+rmtfpth
            sftp.put(localFilePath, remoteFilePath)            
            Acknowldgment=Soc.recv(40) .decode()
            if Acknowldgment.endswith("fully"):
                self.ids.my_bar.value=100 #update Progress bar  
                self.ids.datashow.text = f" [ { rmtfpth[:-3] } ] .. Sent Succefully ..!"   
                send_flag=True
            else:
                self.ids.datashow.text=Acknowldgment
            try:
                cmd="del dpath*x.db" if platform=='win' else  'rm dpath*x.db'
            except :pass            
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
            
        elif tabx:
            try:screen2.crtab(tabx,30)
            except:pass
        else:
            self.ids.datashow.text=f"Warning ! .Choose Database !"

#______________************* Function to choose with fonction to use for uplaod db
    def upload_db(self):
        global colx,crypted_cols,tabx,Xtable,dbname,file_name,table,send_flag
        colx=crypted_cols=[]
        tabx =Xtable=dbname=file_name=table=checked_ele =None 
        send_flag=False  # check dababase sending
        return self.file_manager_open() if platform=='win' else self.choose_db()
#____________************** Log OUT Function    
    def log_out(self):
        global Soc
        Soc.send("exit".encode())
        Soc.close()
        self.manager.current="connect"
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
            pos_hint={'center_x':0.5,'center_y':0.5},
            size_hint=(1,.6),
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
    
    
#______Egy Mul
#____________************* Egy Mul :
######################################### Egyptian Multiplication ##################################################
    def mulegy(self):
        #Function for finding Highest 2 power less than or equal to a given number
        def greatest2power(n,i=0):
            while int(math.pow(2,i)) <= n : i = i+1
            return int(math.pow(2,i-1))
        def splitlist(myList):
            if len(myList) == 0:
                return 0
            elif len(myList) == 1:
                return myList[0]
            half = len(myList)//2
            leftSide = myList[:half]
            rightSide = myList[half:]
            if len(leftSide)>2 or len(rightSide)>2:
                l=splitlist(leftSide)
                r=splitlist(rightSide)
                return l,r
            return leftSide,rightSide
        def egyptian(L):
            #Finding greater of two and assigning Highest to first
            
            for i in range(0,len(L)-1):
                m=L[i]
                n=L[i+1]
                if m>n : first , second = m , n
                else : first , second = n , m
                #Lists for holding two columns
                fcol , scol = [] , []
                seed = 1
            #populating two columns in the Egyptian table
                while seed <= greatest2power(first):
                    fcol.append(seed)
                    scol.append(second*seed)
                    seed = seed*2
                valid , backseed = [] , seed//2
                #computing the valid 2 powers in first column
                while backseed>=1:
                    valid.append(backseed)
                    temp = backseed
                    backseed = greatest2power(first-backseed)
                    first = first - temp
                answer = 0
            #Computing the product by adding second column elements , those mapped to valid first column
            tab=[] 
            for sol in valid:
                for a,b in zip(fcol,scol):
                    if a==sol:
                        answer = answer+b
                        tab.append(b)
            return tab
        def Long(L11,L12):
            if len(L11)==2 and len(L12)==2:
                Lx,Ly=egyptian(L11),egyptian(L12)
                Nlx=[]
                Nly=[]
                if len(Lx)>1 and len(Ly)>1:
                    sx=0
                    for i in Lx:
                        sx+=i
                    Nlx.append(sx)
                    sy=0
                    for i in Ly:
                        sy+=i
                    Nly.append(sy)
                    Nlx.extend(Nly)
                    res=egyptian(Nlx)
                elif len(Lx)>1 and len(Ly)==1:
                    sx=0
                    for i in Lx:
                        sx+=i
                    Nlx.append(sx)
                    Nlx.extend(Ly)
                    res=egyptian(Nlx)
                elif len(Lx)==1 and len(Ly)>1:
                    sy=0
                    for i in Ly:
                        sy+=i
                    Nly.append(sy)
                    Nly.extend(Lx)
                    res=egyptian(Nly)
                elif len(Lx)==1 and len(Ly)==1:
                    Lx.extend(Ly)
                    res=egyptian(Lx)
            elif len(L11)==1 and len(L12)==1:
                L11.extend(L12)
                res=egyptian(L11)
            elif len(L11)==1 and len(L12)==2:
                Lyy=egyptian(L12)
                temp=[]
                s=0
                if len(Lyy)>1:
                    for x in Lyy:
                        s+=x
                    temp.append(s)
                    temp.extend(L11)
                    res=egyptian(temp)
                elif len(Lyy)==1:
                    L11.extend(Lyy)
                    res=egyptian(L11)
            elif len(L11)==2 and len(L12)==1:
                Lxx=egyptian(L11)
                temp=[]
                s=0
                if len(Lxx)>1:
                    for x in Lxx:
                        s+=x
                    temp.append(s)
                    temp.extend(L12)
                    res=egyptian(temp)
                elif len(Lxx)==1:
                    Lxx.extend(L12)
                    res=egyptian(Lxx)
            return res
               #Fonction qui transforme une liste de plusieurs dimension a une dimension
        def flatten_list(_2d_list):
            flat_list = []
            # Iterate through the outer list
            for element in _2d_list:
                if type(element) is list:
                    # If the element is of type list, iterate through the sublist
                    for item in element:
                        flat_list.append(item)
                else:
                    flat_list.append(element)
            return flat_list
        def prodList(L):
            LY=[]
            p=1
            for x in L:
                p*=x
            LY.append(p)
            return LY 
        def folatprecision(first,second):
            m1=int(first)
            Temp=[]
            Old=[]
            rest=round((first-m1),2)
            print("rest",rest)
            Temp.append(rest)
            Temp.append(second)
            Old.append(first)
            Old.append(second)
            val=egyptian(Old)
            extra=egyptian(Temp)
            val.extend(extra)
            return val
        def numberisfloat(L):
            for i in range(0,len(L)-1):
                    m=L[i]
                    n=L[i+1]
                    if m>n : first , second = m , n
                    else : first , second = n , m
                    print("m",m)
                    print("n",n)
                    check_float = isinstance(first, float)
            return check_float
        def addfloatpart(L):
            for i in range(0,len(L)-1):
                m=L[i]
                n=L[i+1]
                if m>n : first , second = m , n
                else : first , second = n , m
                val=folatprecision(first,second)
            return val 
        chosen_col=checked_ele
        if not chosen_col :
            self.ids.showchecked.text = "Warning : Choose a column !"
        else :
            x='61'
            Soc.send(x.encode())            
            start=time.time()
            idd=colx.index(chosen_col)
            M=[] # Pour Stocker Les Valeurs à calculer 
            # Stocker les valeur à calculer 
            for y in range(1,len(tabx)+1):
                Far=tabx.get(doc_id=y)
                M.append(list(Far.values())[idd])
            for x in M: # Check 0 result
                if x==0:
                    self.ids.lresult.text="0 Result Dectected"
                    return "Zéro Result Detected!.."
            L1,L2=splitlist(M)
            if len(L1)==1 or len(L2)==1:
                res=Long(L1,L2)
                data=[pub_key.encrypt(x) for x in res]
                data=dill.dumps(data)
                Soc.send(data)
            else:
                check_float1=numberisfloat(L1)
                check_float2=numberisfloat(L2)
                if check_float1==True and check_float2==True:
                    val1=addfloatpart(L1)
                    val2=addfloatpart(L2)
                    lval1=val1
                    lval2=val2
                    if len(val1)>1:
                        s=0
                        lval1=[]
                        for x in val1:
                            s+=x
                        lval1.append(s)
                    if len(val2)>1:
                        s=0
                        lval2=[]
                        for x in val2:
                            s+=x
                        lval2.append(s)
                    lval1.extend(lval2)
                    bol=numberisfloat(lval1)
                    if bol==True:
                        v=addfloatpart(lval1)
                        data=[pub_key.encrypt(x) for x in v]
                        data=dill.dumps(data)
                        Soc.send(data)
                    else:
                        res=egyptian(lval1)
                        data=[pub_key.encrypt(x) for x in res]
                        data=dill.dumps(data)
                        Soc.send(data)
                elif check_float1==True and check_float2==False:
                    val1=addfloatpart(L1)
                    lval=val1
                    if len(val1)>1:
                        s=0
                        lval=[]
                        for x in val1:
                            s+=x
                        lval.append(s)
                    tmp=egyptian(L2)
                    ltmp=tmp
                    if len(tmp)>1:
                        s=0
                        ltmp=[]
                        for x in tmp:
                            s+=x
                        ltmp.append(s)
                    ltmp.extend(lval)
                    bol=numberisfloat(ltmp)
                    print("bol==>",bol)
                    if bol==True:
                        v=addfloatpart(ltmp)
                        data=[pub_key.encrypt(x) for x in v]
                        data=dill.dumps(data)
                        Soc.send(data)
                    res=egyptian(ltmp)                    
                    data=[pub_key.encrypt(x) for x in res]
                    data=dill.dumps(data)
                    Soc.send(data)
                elif check_float1==False and check_float2==True:
                    val2=addfloatpart(L2)
                    lval=val2
                    if len(val2)>1:
                        s=0
                        lval=[]
                        for x in val2:
                            s+=x
                        lval.append(s)
                    tmp=egyptian(L1)
                    ltmp=tmp
                    if len(tmp)>1:
                        s=0
                        ltmp=[]
                        for x in tmp:
                            s+=x
                        ltmp.append(s)
                    ltmp.extend(lval)
                    bol=numberisfloat(ltmp)
                    if bol==True:
                        v=addfloatpart(ltmp)
                        data=[pub_key.encrypt(x) for x in v]
                        data=dill.dumps(data)
                        Soc.send(data)
                    res=egyptian(ltmp)
                    data=[pub_key.encrypt(x) for x in res]
                    data=dill.dumps(data)
                    Soc.send(data)
                elif check_float1==False and check_float2==False:
                    if type(L1)==list and type(L2)==list:
                        res=Long(L1,L2)
                        data=[pub_key.encrypt(x) for x in res]
                        data=dill.dumps(data)
                        Soc.send(data)
                    elif type(L1)==tuple and type(L2)==tuple:
                        Lx1=list(L1[0])
                        Lx2=list(L1[1])
                        Lx1=flatten_list(L1[0])
                        Lx2=flatten_list(L1[1])
                        if len(Lx1)>2:
                            Lx1=prodList(Lx1)
                    
                        if len(Lx2)>2:
                            Lx2=prodList(Lx2)

                        Ly1=list(L2[0])
                        Ly2=list(L2[1])
                        Ly1=flatten_list(L2[0])
                        Ly2=flatten_list(L2[1])
                    
                        if len(Ly1)>2:
                            Ly1=prodList(Ly1)
                        if len(Ly2)>2:
                            Ly2=prodList(Ly2)
                        res1=Long(Lx1,Lx2)   
                        res2=Long(Ly1,Ly2)
                        if len(res1)>1 and len(res2)>1:
                            R1,R2=[],[]
                            s1,s2=0,0
                            for i in res1:
                                s1+=i
                            R1.append(s1)
                            for i in res2:
                                s2+=i
                            R2.append(s2)
                            R1.extend(R2)
                            res=egyptian(R1)
                            data=[pub_key.encrypt(x) for x in res]
                            data=dill.dumps(data)
                            Soc.send(data)
                        elif len(res1)==1 and len(res2)>1:
                            s=0
                            R1=[]
                            for i in res2:
                                s+=i
                            R1.append(s)
                            R1.extend(res1)
                            res=egyptian(R1)
                            data=[pub_key.encrypt(x) for x in res]
                            data=dill.dumps(data)
                            Soc.send(data)
                        elif len(res1)>1 and len(res2)==1:
                            s=0
                            R1=[]
                            for i in res1:
                                s+=i
                            R1.append(s)
                            R1.extend(res1)
                            res=egyptian(R1)
                            data=[pub_key.encrypt(x) for x in res]
                            data=dill.dumps(data)
                            Soc.send(data)
                        elif len(res1)==1 and len(res2)==1:
                            res1.extend(res2)
                            res=egyptian(res1)
                            data=[pub_key.encrypt(x) for x in res]
                            data=dill.dumps(data)
                            Soc.send(data)
            #############___Receiv Result
            result=Soc.recv(BS)
            result=dill.loads(result)
            result=priv_key.decrypt(result)
            self.ids.lresult.text=f"{round(result,2)} " 
            tab="End"
            tab=dill.dumps(tab)
            Soc.send(tab)
#_______onback    
    def onback(self):
         self.manager.current="main_screen"

######################################################################
class ImageButton(ButtonBehavior,HoverBehavior,Image):
    pass
class RootWidget(ScreenManager):
    pass
class blanks1(BoxLayout):
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
