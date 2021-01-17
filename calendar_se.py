import caldav
from caldav.elements import dav
from datetime import datetime, timedelta
import json
from pytz import UTC  # timezone
from icalendar import Calendar, Event


class MyCalendar:
    def __init__(self):
        self.username = "dv029"
        self.password = "dv029admin123"

        self.url = "https://" + self.username + ":" + self.password + \
            "@next.social-robot.info/nc/remote.php/dav"
        self.apmtNotExisted = True
        self.startOfRequest = datetime.now()
        self.nextHalfHour = self.startOfRequest + \
            timedelta(hours=0.5)

    def getCalendars(self):
        # open connection to calendar
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # get all available calendars (for this user)
        calendars = principal.calendars()
        print(calendars)
        return calendars

    def searchForAppointments(self, calendar):
        self.timeDelta = 0
        while(self.apmtNotExisted):
            print('Begining: ', self.startOfRequest)
            print('nextHalfHour: ', self.nextHalfHour)
            events = calendar.date_search(
                start=self.startOfRequest, end=self.nextHalfHour)
            if len(events) > 0:
                print('events existed')
                self.apmtNotExisted = False
                return events
            self.timeDelta += 0.5
            self.startOfRequest = self.nextHalfHour
            self.nextHalfHour += timedelta(hours=self.timeDelta)

    def getNextAppointmentDate(self):
        nextAppointment = {}
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            # print(calendar)
            allEvents = self.searchForAppointments(calendar)
            print(allEvents)
            nextEvent = Calendar.from_ical(allEvents[1]._data)
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


myCal = MyCalendar()
nextAp = myCal.getNextAppointmentDate()
print(datetime.now())
print(nextAp)
