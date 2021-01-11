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
        self.nextDay = self.startOfRequest + \
            timedelta(days=1)

    def getCalendars(self):
        # open connection to calendar
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # get all available calendars (for this user)
        calendars = principal.calendars()
        return calendars

    def searchForAppointments(self, calendar):
        self.timeDelta = 0
        while(self.apmtNotExisted):
            self.startOfRequest += timedelta(days=self.timeDelta)
            print('Start: ', self.startOfRequest)
            self.nextDay += timedelta(days=self.timeDelta)
            print('nextDay: ', self.nextDay)
            events = calendar.date_search(
                start=self.startOfRequest, end=self.nextDay)
            if len(events) > 0:
                print('events existed')
                self.apmtNotExisted = False
                return events
            self.timeDelta += 1

    def getNextAppointmentDate(self, today):
        nextAppointment = {}
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            # print(calendar)
            allEvents = self.searchForAppointments(calendar)
            print(allEvents[0])
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
                    nextAppointment.update(
                        {'Start Time': component.get('dtstart').dt.strftime('%H:%M')})
                    nextAppointment.update(
                        {'End Date': component.get('dtend').dt.strftime('%d/%m/%Y')})
                    nextAppointment.update(
                        {'End Time': component.get('dtend').dt.strftime('%H:%M')})
        return nextAppointment


myCal = MyCalendar()
nextAp = myCal.getNextAppointmentDate(datetime.now())
print(nextAp)
