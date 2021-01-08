from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder

import caldav
from caldav.elements import dav
from datetime import datetime
import json
from pytz import UTC  # timezone
from icalendar import Calendar, Event


class MyCalendar:
    def __init__(self):
        self.username = "dv029"
        self.password = "dv029admin123"

        self.url = "https://" + self.username + ":" + self.password + \
            "@next.social-robot.info/nc/remote.php/dav"

    def getCalendars(self):
        # open connection to calendar
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # get all available calendars (for this user)
        calendars = principal.calendars()
        return calendars

    def getNextAppointmentDate(self, today):
        nextAppointment = {}
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            allEvents = calendar.date_search(start=today)
            nextEvent = Calendar.from_ical(allEvents[0]._data)
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


class MakeAppointments(MycroftSkill):
    def __init__(self):
        self.myCal = MyCalendar()
        MycroftSkill.__init__(self)

    # @intent_handler('appointments.make.intent')
    # def handle_appointments_make(self, message):
    #     now = now_local.date()
    #     nextAp = myCal.getNextAppointmentDate(now)
    #     todo = nextAp['Summary']
    #     dateS = nextAp['Start Date']
    #     dateE = nextAp['End Date']
    #     timeS = nextAp['Start Time']
    #     timeE = nextAp['Start Time']
    #     if dateS = now:
    #         self.speak_dialog(
    #             'Your next appointment is on {} at {} and is entitled {}.'.format(dateS, timeS, todo))
    #     else:
    #         self.speak_dialog('You have no Appointment today')

    @intent_handler(IntentBuilder("").require("next.appointment"))
    def handle_appointments_make(self, message):
        now = datetime.now()
        nextAp = self.myCal.getNextAppointmentDate(now)
        todo = nextAp['Summary']
        dateS = nextAp['Start Date']
        dateE = nextAp['End Date']
        timeS = nextAp['Start Time']
        timeE = nextAp['Start Time']
        self.speak_dialog(
            'Your next appointment is on {} at {} and is entitled {}.'.format(dateS, timeS, todo))


def create_skill():
    return MakeAppointments()
