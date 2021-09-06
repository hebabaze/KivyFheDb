from tinydb import TinyDB, Query
from tqdm import tqdm
import os

#######################################################################
import logging
format="%(asctime)s.%(msecs)03d--%(levelname)s : %(message)s"
logging.basicConfig(format=format,level=logging.INFO,datefmt="%H:%M:%S")
########################################################################
cmd = 'del *.db'
cmd1 = 'del *x.db'
os.system(cmd)
os.system(cmd1)
def rentable() :
  dbt = TinyDB('wesa.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  for i in tqdm(range(1,20),unit_divisor=1,desc=f"Creating mydb.db..",colour= 'Blue'):
      tabx.insert({'id':i, 'age': i*10 ,'nom': 'Salah', 'years':1000 ,'ville' : 'Agadir' ,'phone' :693,'cin':98 })
  return dbt

def tinyschool() :
  dbt = TinyDB('maroc.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':10 })
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':20 })
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':30})
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':40})
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':50 })
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':60 })
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':70})
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':80})
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':90})
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':100})   
  return dbt

L=[100,200,300,400]
P=[20,40,80,10]
def school() :
  dbt = TinyDB('plstn.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  tabx.insert({'City': 'Haifa', 'years':1917 ,'isf':L[0],'code':313 })
  tabx.insert({'City': 'Yafa', 'years':1918 ,'isf':L[1],'code':313})
  tabx.insert({'City': 'Jenin', 'years':1948 ,'isf':L[2],'code':313 })
  tabx.insert({'City': 'Beir sab', 'years':1850 ,'isf':L[3],'code':313})
  return dbt

rentable()
school()
tinyschool()

sum=0
sump=sum=0
multp=mult=1


for x in L:
    sum+=x
    mult*=x
P=[x for x in range(10,101,10)]
print("P",P)
for x in P:
    sump+=x
    multp*=x
print(" Maroc La somme  real est :",sump)
print(" Maroc Le produit int :",multp)
print(" Plstn La somme  real est :",sum)
print(" Plstn Le produit int :",mult)