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
      tabx.insert({'id':i, 'age': i*10 ,'nom': 'Salah', 'years':1000 })
  logging.info(" database created : mydb.db" )
  logging.info(f"All Databases Created \n")
  return dbt




def school() :
  dbt = TinyDB('ensa.db')
  dbt.drop_table('Hr')
  tabx = dbt.table('Hr')
  tabx.insert({'nom': 'Salah', 'years':1000 ,'id':20 })
  tabx.insert({'nom': 'Ahmed', 'years':2000 ,'id':40})
  tabx.insert({'nom': 'Rajae', 'years':2500 ,'id':50 })
  tabx.insert({'nom': 'Hamid', 'years':1000 ,'id':70 })
  logging.info(" database created : school.db" )
  print(tabx.all())
  return dbt

rentable()
school()


