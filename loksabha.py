# -*- coding: utf-8 -*-
import encodings
encodings._aliases["utf8mb4"] = "utf_8"
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import MySQLdb
import mechanize
import cookielib
import string
from BeautifulSoup import BeautifulSoup
import html2text
import re
import os
from datetime import datetime
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

db = MySQLdb.Connect("localhost","root","pass","database")
db.set_character_set('utf8mb4')
cursor = db.cursor()
cursor2 = db.cursor()
cursor.execute('SET NAMES utf8mb4;')
cursor.execute('SET CHARACTER SET utf8mb4;')
cursor.execute('SET character_set_connection=utf8mb4;')
		
table  = ['loksabha']
db.autocommit(True)

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# The site we will navigate into, handling it's session
br.open('http://164.100.24.207/LssNew/psearch/DebMemberSearch14.aspx')

page = br.open('http://164.100.24.207/LssNew/psearch/DebMemberSearch14.aspx')
soup = BeautifulSoup(page)
soup.prettify()

for select in soup.findAll('option', value=True):
	br.open('http://164.100.24.207/LssNew/psearch/DebMemberSearch14.aspx')
	# Select the first (index zero) form
	br.select_form(nr=0)
	select['value']=[select['value']]
	print select['value']
	# User credentials
	br.form['ctl00$ContPlaceHolderMain$ddlmember'] = select['value']
	br.submit() 
	br.select_form(nr=0)
	res = br.submit()
	#print res.read()
	soup = BeautifulSoup(res.read())
	#<table cellspacing="0" cellpadding="0" width="96%" align="center" border="0">
	#<table width="100%" border="0">
	link = soup.findAll('table',attrs={'width':'100%','border':'0'})

	if link:
		for lin in link:
			#link = soup.find('form')
			#link = str(link)
			lin = str(lin)
			soup2 = BeautifulSoup(lin)
			link2 = soup2.findAll('tr')
			f = open('myfile.html','w')
			f.write(str(link2))
			f.close()
			#print link2
			content = link2[1].find('a',href=True)
			cont = content['href']
			cont = br.open('http://164.100.24.207/LssNew/psearch/'+cont)
			cont = cont.read()
			#f = open('myfile.html','w')
			#f.write(str(cont))
			#f.close()
			soup3 = BeautifulSoup(cont)
			cont = soup3.find('table',attrs={'align':'center','width':'75%'})
			#print cont
			t = link2[1]
			t = t.find('a')
			title = t.text
			#print title
			
			d = link2[2]
			d = d.find('a')
			date = d.text #date
			date = datetime.strptime(date , '%d-%m-%Y')
			#print date

			p = link2[3]
			participants = strip_tags(str(p))
			#print participants
			
			k = link2[4]
			keywords = strip_tags(str(k))
			#print keywords
			cursor.execute("""INSERT IGNORE INTO loksabha (title,date,participants,keywords,content) VALUES (%s,%s,%s,%s,%s)""",(title,date,participants,keywords,cont))
			
	else:
		print "not found"
	
	
