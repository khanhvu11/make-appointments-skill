from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_datetime
from mycroft.util.time import now_local, default_timezone

import caldav
from caldav.elements import dav
from datetime import datetime, timedelta
import json
import pytz
from icalendar import Calendar, Event

DEFAULT_TIME = now_local().replace(hour=8, minute=0, second=0)


class MyCalendar:
    def __init__(self):
        self.username = "dv029"
        self.password = "dv029admin123"

        self.url = "https://" + self.username + ":" + self.password + \
            "@next.social-robot.info/nc/remote.php/dav"
        self.apmtNotExisted = True
        self.startOfRequest = now_local(default_timezone())
        self.nextHalfHour = self.startOfRequest + \
            timedelta(hours=0.5)
        self.saved = False
        self.berlin = pytz.timezone('Europe/Berlin')

    def getCalendars(self):
        # open connection to calendar
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # get all available calendars (for this user)
        calendars = principal.calendars()
        return calendars

    def searchForAppointments(self, calendar):
        self.timeDelta = 0
        self.apmtNotExisted = True
        while(self.apmtNotExisted):
            events = calendar.date_search(
                start=self.startOfRequest, end=self.nextHalfHour)
            if len(events) > 0:
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
            allEvents = self.searchForAppointments(calendar)
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
                        {'Start Time': component.get('dtstart').dt.astimezone(self.berlin).strftime('%H:%M')})
                    nextAppointment.update(
                        {'End Date': component.get('dtend').dt.strftime('%d/%m/%Y')})
                    nextAppointment.update(
                        {'End Time': component.get('dtend').dt.astimezone(self.berlin).strftime('%H:%M')})
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
        self.saved = True

    def eventExisted(self, dt):
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            allEvents = calendar.date_search(
                start=dt, end=(dt + timedelta(minutes=5)))
        return allEvents

    def deleteAppointment(self, dt):
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            allEvents = calendar.date_search(
                start=dt, end=(dt + timedelta(minutes=5)))
        allEvents[0].delete()
        print(allEvents[0], 'was deleted')


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

    @intent_handler('next.appointments.intent')
    def handle_appointments_make(self, message):
        nextAp = self.myCal.getNextAppointmentDate()
        todo = nextAp['Summary']
        dateS = nextAp['Start Date']
        # dateE = nextAp['End Date']
        timeS = nextAp['Start Time']
        # timeE = nextAp['Start Time']
        self.speak_dialog(
            'Your next appointment is on {} at {} and is entitled {}.'.format(dateS, timeS, todo))

    @intent_handler('make.appointment.intent')
    def add_new_appointment(self, msg=None):
        """ Handler for adding  an appointment with a name at a specific time. """
        appointment = msg.data.get('appointment', None)
        if appointment is None:
            return self.unnamed_appointment(msg)
        utterance = msg.data['utterance']
        appointment_time, _ = (extract_datetime(utterance, now_local(),
                                                self.lang,
                                                default_time=DEFAULT_TIME) or
                               (None, None))
        if appointment_time:  # A datetime was extracted
            self.myCal.saveAppointment(appointment, appointment_time)
            if self.myCal.saved:
                self.speak_dialog('appointments.make')
        else:
            self.speak_dialog('NoDate')

    @intent_handler('unnamed.appointment.intent')
    def unnamed_appointment(self, msg=None):
        """ Handles the case where a time was given but no appointment
            name was added.
        """
        utterance = msg.data['timedate']
        apmt_time, _ = (extract_datetime(utterance, now_local(), self.lang))

        response = self.get_response('AppointmentName')
        if response and apmt_time:
            self.myCal.saveAppointment(response, apmt_time)
            if self.myCal.saved:
                self.speak_dialog('appointments.make')

    @intent_handler('deleteAppointment.intent')
    def remove_appointment(self, msg=None):
        """ Remove all reminders for the specified date. """
        if 'date' in msg.data:
            date, _ = extract_datetime(msg.data['date'], lang=self.lang)
        else:
            date, _ = extract_datetime(msg.data['utterance'], lang=self.lang)

        if date:
            if date.time():
                if self.myCal.eventExisted(date):
                    answer = self.ask_yesno(
                        'confirmDelete', data={'date': date.strftime("%d/%m/%Y %H:%M")})
                    if answer == 'yes':
                        self.myCal.deleteAppointment(date)
                        self.speak_dialog('Your appointment on {} was removed.'.format(
                            date.strftime("%d/%m/%Y %H:%M")))
                else:
                    self.speak_dialog('noAppointment', {
                                      'date': date.strftime("%d/%m/%Y %H:%M")})
        else:
            response = self.get_response('repeatDeleteDate')
            if response:
                self.remove_appointment(response)

    def stop(self):
        self.stop_beeping()

    def shutdown(self):
        pass


def create_skill():
    return MakeAppointments()
