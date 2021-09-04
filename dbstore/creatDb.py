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
  dbt = TinyDB('ISTA.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  for i in tqdm(range(1,21),unit_divisor=1,desc=f"Creating mydb.db..",colour= 'Blue'):
      tabx.insert({'id':i, 'age': i*10 ,'nom': 'Salah', 'years':1000 ,'ville' : 'Agadir' ,'phone' :'0693','cin':98 })
  logging.info(" database created : mydb.db" )
  logging.info(f"All Databases Created \n")
  return dbt

def tinyschool() :
  dbt = TinyDB('lisa.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':20.5 })
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':40.4})
  logging.info(" database created : school.db" )
  print(tabx.all())
  return dbt

L=[20.5,40.5,80.2,10.6]
P=[20,40,80,10]
def school() :
  dbt = TinyDB('ensa.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':L[0] })
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':L[1]})
  tabx.insert({'nom': 'Rajae', 'years':2500 ,'id':L[2] })
  tabx.insert({'nom': 'Rajae', 'years':2500 ,'id':L[3]})
  logging.info(" database created : school.db" )
  print(tabx.all())
  return dbt

rentable()
school()
tinyschool()

sum=0
intsum=0
mult=1
intp=1
for x in L:
    sum+=x
    intp*=int(x)
    mult*=x
print("       La somme  real est :",sum)
print("       Le produit real  est :",mult)
print("       Le produit int :",intp)