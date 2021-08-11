from tinydb import TinyDB
from binascii import hexlify , unhexlify
from phe import paillier
import rsa
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
    
    
    def paillierEncr(self,x):      #Crypter les colonnes de types int
        def transform(self,doc):
            doc[x]=self.enciph(int(doc[x]))
        return transform

    def rsaEncr(self,x):    #Crypter les colonnes de types String
 
        def transform(self,doc):
            doc[x]=self.rsacrypt(doc[x])
        return transform
    def crypt_table(self,tabx,fname):
        dbname=fname[:-3]+'x.db'
        dbx=TinyDB(dbname)
        tabrx = dbx.table('Dx')
        for x in tabx :
            d={}
            for a,b in x.items() :
                if str(b).isalpha():
                    d[self.rsacrypt(a)]=self.rsacrypt(b)
                elif not str(b).isalpha() :
                    d[self.rsacrypt(a)]=self.enciph(int(b))
            tabrx.insert(d)
        return(tabrx.all(),dbname)
    