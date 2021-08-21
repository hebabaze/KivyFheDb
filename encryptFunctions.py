import logging
format="%(asctime)s.%(msecs)03d--%(levelname)s : %(message)s"
logging.basicConfig(format=format,level=logging.INFO,datefmt="%H:%M:%S")
from tinydb import TinyDB
from tqdm import tqdm
from binascii import hexlify , unhexlify
from phe import paillier
import rsa,dill
# Security keys genration
(pubkey, privkey) = rsa.newkeys(512)
pub_key,priv_key=paillier.generate_paillier_keypair(n_length=128)

class Encrypt:

    def rsacrypt(self,data):       # Fonction de Cryptage RSA
        message=data.encode()
        crypto = rsa.encrypt(message, pubkey)
        crypto = hexlify(crypto).decode()
        return crypto
    
    def enciph(self,y):            # get encipher text
        x=pub_key.encrypt(y)
        return x.ciphertext()
    
    
    def paillierEncr(self,x):
        self.x=x      #Crypter les colonnes de types int
        def transform(self,doc):
            self.doc=doc
            self.doc[self.x]=self.enciph(int(self.doc[self.x]))
        return transform

    def rsaEncr(self,x):    #Crypter les colonnes de types String
        self.x=x 
        def transform(self,doc):
            self.doc=doc
            self.doc[self.x]=self.rsacrypt(self.doc[self.x])
        return transform

    def crypt_table(self,tabx,fname,Xtable):
        print("Crypt all Data")
        dbname=fname[:-3]+'x.db' # Create New DB file
        dbx=TinyDB(dbname)        # Create Tinydb DB   
        tabrx = dbx.table('Dx')   # Create New Table in New DB (dbx)
        if Xtable :
            tabx=Xtable
            print(" This is new TaBx",tabx)
        for x in tabx :
            d={}
            for a,b in x.items() :
                if len(str(b)) >64 :
                    print("Crypted item ",b)
                    print(f"The Row {a} is aleardy Crypted")
                    d[self.rsacrypt(a)]=b
                else:
                    if str(b).isalpha():
                        d[self.rsacrypt(a)]=self.rsacrypt(b)
                    elif not str(b).isalpha() :
                        d[self.rsacrypt(a)]=self.enciph(int(b))
            tabrx.insert(d)
        return(tabrx,dbname)
    
    def encrypt_col(self,tabx,columns,e,fname):   # crypter une colonne
        
        dbname=fname[:-3]+'x.db' # Create New DB file
        dby=TinyDB(dbname)  
        tabrx = dby.table('Dx')
        L=[]
        if not tabrx :
            for x in tabx:
                tabrx.insert(x)
        i=1
        rdic=tabrx.get(doc_id=1)
        print(f"rdic ==> {rdic}")
        L=[x for x in rdic if len(str(rdic[x])) > 64  ]
        print("Crypted Columns ",L)
        
        if columns[e] in L:
            print(f"The Row {columns[e]} is aleardy Crypted")
        elif columns[e] not in L :
            if not str(rdic[columns[e]]).isalpha() :
                for x in tabrx:
                    tabrx.update({columns[e]:self.enciph(x[columns[e]])},doc_ids=[i])
                    i+=1
            else :
                for x in tabrx:
                    tabrx.update({columns[e]:self.rsacrypt(x[columns[e]])},doc_ids=[i])
                    i+=1
        return tabrx,dbname