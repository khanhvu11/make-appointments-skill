from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_datetime
from mycroft.util.time import now_local

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
        self.startOfRequest = now_local()
        self.nextHalfHour = self.startOfRequest + \
            timedelta(hours=0.5)
        self.saved = False

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

        # mogrify the response TODO: betterify!
        # appointment = (' ' + appointment).replace(' my ', ' your ').strip()
        # appointment = (' ' + appointment).replace(' our ', ' your ').strip()
        utterance = msg.data['utterance']
        appointment_time, _ = (extract_datetime(
            utterance, now_local(), self.lang))

        if appointment_time:  # A datetime was extracted
            self.myCal.saveAppointment(appointment, appointment_time)
            if self.myCal.saved:
                self.speak_dialog('appointments.make', {
                                  'appointment': appointment, 'timedate': appointment_time})
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

    def stop(self):
        self.stop_beeping()

    def shutdown(self):
        pass


def create_skill():
    return MakeAppointments()
