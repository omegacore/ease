import sqlite3
import random

conn = sqlite3.connect('test.db')
c = conn.cursor()

def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS ease(empid INTEGER, name TEXT, email TEXT, access TEXT)')
	

def dynamic_entry():
	names = "MALAAK,ABDUL AATI,ABDUL NASER,ABDUL MUSLEH,BINYAMI,NARIS,YARA,SITAV,LOLAND,TILAJ,BARRAH,ABDUL NABI,ABDUL RASOOL,SUMUW,AL MAMLAKA,MALIKA,MAMLAKA,TABARAK,NARDEEN,SANDY,RAMA,MALINE,ELAINE,INAR,MALIKTINA,MAYA,LINDA,RANDA,BASMALA,JIBREEL,ABDUL MU’EEN,ABRAR,IMAN,BAYAN,BASEEL,WIREELAM,NABI,NABIYYA,AMI,TALINE,ARAM,NAREEJ,RITAL,ALICE,LAREEN,KIBRIAL,LAUREN"
	name_list = names.split(',')
	name_list.sort()
	e_type = ['@gmail.com', '@yahoo.com', '@stanford.edu', '@ucsc.edu']
	acc_type = ['admin', 'user', 'guest']
	for name in name_list:
		corr_name = ''
		eid = random.randint(1000, 9000)
		for ch in name:
			if ch == ' ':
				corr_name += '_'
			else:
				corr_name += ch
		dom = random.choice(e_type)
		mail = corr_name + dom
		acc = random.choice(acc_type)
		c.execute('INSERT INTO ease (empid, name, email, access) VALUES (?, ?, ?, ?)', (eid, name, mail, acc))
		conn.commit()
		
def read_db():
	c.execute('SELECT * FROM ease')
	for row in c.fetchall():
		print(row)


create_table()
dynamic_entry()
read_db()
c.close()
conn.close()
		
