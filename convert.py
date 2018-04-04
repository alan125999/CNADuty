from icalendar import Calendar, Event, Alarm
from datetime import datetime
import pytz # timezone

cal = Calendar()
cal.add('prodid', '-//CNA Duty//mxm.dk//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '網管班表')
cal.add('x-wr-timezone', 'Asia/Taipei')

year = 2018
month = 4
day = 4
na = "alan"
tz = pytz.timezone('Asia/Taipei')

event = Event()
event.add('summary', '網管值班')
event.add('dtstart', tz.localize(datetime(year,month,day,19,0,0)))
event.add('dtend', tz.localize(datetime(year,month,day,22,0,0)))
event.add('dtstamp', tz.localize(datetime.now()))
event.add('description', "值班人員：" + na)
event.add('location', 'CBB')
event.add('priority', 5)

'''
alarm = Alarm()
alarm.add('action', "DISPLAY")
alarm.add('description', "This is an event reminder")
alarm.add('trigger', "-P0DT0H30M0S")
'''

cal.add_component(event)
f = open('example.ics', 'wb')
f.write(cal.to_ical())
f.close()