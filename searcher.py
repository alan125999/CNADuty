# -*- coding: utf-8 -*-
import telnetlib
import re
import time
from icalendar import Calendar, Event, Alarm
from datetime import datetime
import pytz # timezone

def chineseNum(words):
    length = len(words)
    utf8_length = len(words.encode('utf-8'))
    return  int((utf8_length - length)/2 )

def parseToCol(allContent, table):
    for weekday in range(0, 6):
        col = []
        for line in allContent:
            if weekday == 1:
                x = 6
                y = 21
            elif weekday == 2:
                x = 21
                y = 34
            elif weekday == 3:
                x = 34
                y = 49  
            elif weekday == 4:
                x = 49
                y = 62  
            elif weekday == 5:
                x = 62
                y = 77
            else:
                x = 0
                y = 6
            col.append(line[x-chineseNum(line[0:x]):y-chineseNum(line[0:y])].strip())
        table.append(col)
        

ansiColorRemover = r"\x1B\[[0-?]*[ -/]*[@-~]"
ansi_escape = re.compile(ansiColorRemover)
timeWait = 5
# log in to homepage
tn = telnetlib.Telnet('bbs.cna.ccu.edu.tw')
content = ''
while u"您的帳號" not in content:
    content = tn.read_very_eager().decode('big5','ignore')
tn.write('guest\n'.encode('ascii'))

while u"主功能表" not in content:
    content = tn.read_very_eager().decode('big5','ignore')
    tn.write('b'.encode('ascii'))
        
# board -> duty
tn.write('b\n/CNA_Duty\n\n\n'.encode('ascii'))
time.sleep(timeWait)
while u"文章列表" not in content:
    content = tn.read_very_eager().decode('big5','ignore')
print(content)
titles = re.split('\n|\r',ansi_escape.sub('',content)) # get list


# go to previous page, and refresh 
tn.write('P\x1b[D\x1b[C\n'.encode('ascii')) 
time.sleep(timeWait)
content = ""
while len(content)<10: 
    content = tn.read_very_eager().decode('big5','ignore')
titles2 = re.split('\n|\r',ansi_escape.sub('',content)) # get list in previous page

# combine list
allTitles = []
for line in titles2[5:-1] + titles[5:-1]:
    if line.strip():
        allTitles.append(line)

name = []
schedules = []

# seek for schedule
for title in allTitles: 
    text = re.search(u'(.)(.)(月|月份)(網管)?(值班)(時間|表)?',title)
    if text:
        schedules.append(int(title[3:6]))
        if text.group(1)!=' ' or text.group(1)!=']':
            name.append(text.group(1) + text.group(2))
        else:  
            name.append(text.group(2))

# select which month
print("Choose a month ")
for i in range(len(schedules)):
    print(str(i) + ' ' + name[i] + "月值班表")

month = int(input(">>> "))

#month = len(schedules) - 3

# go into the schedule
tn.write((str(schedules[month]) + '\n\n').encode('ascii'))
content = ""
while len(content)<10: 
    content = tn.read_very_eager().decode('big5','ignore')

#fd = open("content","w")
#fd.write(content)
#fin = open("content","r")
#content = fin.read()
#fin.close()
content = re.split('\n|\r',ansi_escape.sub('', content))

# if not loaded completely
if u"闇黑國度" not in content:
    content2 = ""
    tn.write(('\x1b[C').encode('ascii'))
    while u"闇黑國度" not in content2:
        content2 = tn.read_very_eager().decode('big5','ignore')

#fd = open("content2","w")
#fd.write(content2)
#fin = open("content2","r")
#content2 = fin.read()
#fin.close()
content2 = re.split('\n|\r|--',ansi_escape.sub('', content2))  

year = int(re.search(r'([0-9]{1,})\/([0-9]{1,})\/([0-9]{1,})',content[4]).group(1)) # unsure if this always be 4
allContent = []
begin = False
for line in content[5:-1] + content2[:-1]:
    if line.strip():
        if line.strip() == "Site  中正大學˙闇黑國度 【bbs.cna.ccu.edu.tw】":
            break
        if re.search(u'(值班表)',line):
            begin = True
            continue
        if begin:
            allContent.append(line)
            print(line)

table = []
lab = False
parseToCol(allContent, table)

# create calender
cal = Calendar()
cal.add('prodid', '-//CNA Duty//mxm.dk//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '網管班表')
cal.add('x-wr-timezone', 'Asia/Taipei')

# create event and alarm
ftable = open("output_table.txt","w")
tz = pytz.timezone('Asia/Taipei')
nextRow = 0
for i in range(0,len(table[1])):
    for j in range(0,6):
        if re.search(r'([0-9]{1,})\/([0-9]{1,})', table[j][i]):
            ftable.write("\n")
            if not nextRow:
                for k in range(1,5):
                    if re.search(r'([0-9]{1,})\/([0-9]{1,})', table[j][i+k]):
                        nextRow = k
                break
    for j in range(0,6):
        if i >= len(table[j]):
            ftable.write("".ljust(15))
        else:
            ftable.write(table[j][i].ljust(15-chineseNum(table[j][i])))
            text = re.search(r'([0-9]{1,})\/([0-9]{1,})', table[j][i])
            if text:
                month = int(text.group(1))
                day = int(text.group(2))
                persons = table[j][i+1]
                for x in range(2, nextRow):
                    if table[j][i+x] != "":
                        persons += ', ' + table[j][i+x]
                event = Event()
                event.add('summary', '網管值班')
                event.add('dtstart', tz.localize(datetime(year,month,day,19,0,0)))
                event.add('dtend', tz.localize(datetime(year,month,day,22,0,0)))
                event.add('dtstamp', tz.localize(datetime.now()))
                event.add('description', "值班人員：" + persons)
                event.add('location', 'CBB')
                event.add('priority', 5)
                cal.add_component(event)
                
                
    ftable.write("\n")
f = open('example.ics', 'wb')
f.write(cal.to_ical())
f.close()

