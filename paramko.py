import paramiko
HOST="135.181.108.235"
#HOST=self.ids.Ip.text
PORT=443
user='root' #self.ids.user.text
passwd='Newlife' #self.ids.pswd.text
client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST,22,user,passwd)
#stdin,stdout,stderr=client.exec_command('pkill -9 python')
stdin,stdout,stderr=client.exec_command('ls -l')
for x in stdout:
    print(x)
stdin,stdout,stderr=client.exec_command('cat FHE/show.txt')
for x in stdout:
    print(x)
stdin,stdout,stderr=client.exec_command('mkdir help')
for x in stdout:
    print(x)
#stdin,stdout,stderr=client.exec_command('python3 FHE/main.py </dev/null &>/dev/null &')
stdin,stdout,stderr=client.exec_command('python3 FHE/main.py')
print(stderr.read().decode())
for x in stdout:
    print(x)