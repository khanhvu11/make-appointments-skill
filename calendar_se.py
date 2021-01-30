import caldav
from caldav.elements import dav
from datetime import datetime, timedelta
import json
import pytz
from icalendar import Calendar, Event


class MyCalendar:
    def __init__(self):
        self.username = "dv029"
        self.password = "dv029admin123"

        self.url = "https://" + self.username + ":" + self.password + \
            "@next.social-robot.info/nc/remote.php/dav"
        self.apmtNotExisted = True

    def getCalendars(self):
        # open connection to calendar
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # get all available calendars (for this user)
        calendars = principal.calendars()
        print(calendars)
        return calendars

    def searchForAppointments(self, calendar):
        apmtNotExisted = True
        startOfDay = datetime.now()
        nextDay = startOfDay + \
            timedelta(days=1)
        while(apmtNotExisted):
            print('Begining: ', startOfDay)
            print('nextDay: ', nextDay)
            events = calendar.date_search(
                start=startOfDay, end=nextDay)
            if len(events) > 0:
                print('events existed')
                start = startOfDay
                end = start + timedelta(hours=0.5)
                while(apmtNotExisted):
                    print('30 minuten ...')
                    event = calendar.date_search(start=start, end=end)
                    if len(event) > 0:
                        print('1 event existed')
                        apmtNotExisted = False
                        return event
                    start = end
                    end += timedelta(hours=0.5)
            startOfDay = nextDay
            nextDay += timedelta(days=1)

    def getNextAppointmentDate(self):
        berlin = pytz.timezone('Europe/Berlin')
        nextAppointment = {}
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            # print(calendar)
            allEvents = self.searchForAppointments(calendar)
            print(allEvents)
            nextEvent = Calendar.from_ical(allEvents[0]._data)
            print('*'*30)
            print(nextEvent)
            for component in nextEvent.walk():
                if component.name == "VEVENT":
                    nextAppointment.update(
                        {'Summary': component.get('summary')})
                    if component.get('discription') != None:
                        nextAppointment.update(
                            {'Discription': component.get('discription')})
                    nextAppointment.update(
                        {'Start Date': component.get('dtstart').dt.strftime('%d/%m/%Y')})
                    print(
                        '-'*10, component.get('dtstart').dt.astimezone(berlin).strftime('%H:%M'))
                    nextAppointment.update(
                        {'Start Time': component.get('dtstart').dt.strftime('%H:%M')})
                    nextAppointment.update(
                        {'End Date': component.get('dtend').dt.strftime('%d/%m/%Y')})
                    nextAppointment.update(
                        {'End Time': component.get('dtend').dt.strftime('%H:%M')})
        return nextAppointment

    def saveAppointment(self, apmt, apmt_timedate):
        cal = Calendar()
        event = Event()
        myCal = self.getCalendars()
        event.add('summary', apmt)
        event.add('dtstart', apmt_timedate)
        event.add('dtend', apmt_timedate + timedelta(hours=1))
        # event.add('description',
        # f'{awesomeEvent.description} - {awesomeEvent.url}')
        # event.add('location', awesomeEvent.location)
        cal.add_component(event)
        myCal[0].save_event(cal)
        print('saved!')

    def deleteAppointment(self, dt):
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            allEvents = calendar.date_search(
                start=dt, end=(dt + timedelta(minutes=5)))
            allEvents[0].delete()
            print(allEvents[0], 'was deleted')


myCal = MyCalendar()
# dt = datetime(2021, 1, 19, 23, 0)
# myCal.deleteAppointment(dt)
nextAp = myCal.getNextAppointmentDate()
print(datetime.now())
print(nextAp)
