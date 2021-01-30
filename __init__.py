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
        self.saved = False
        self.berlin = pytz.timezone('Europe/Berlin')

    def getCalendars(self):
        # auf Nextcloud-Kalender durch Url zugreifen
        client = caldav.DAVClient(self.url)
        principal = client.principal()
        # alle vorhandene Kalender abholen
        calendars = principal.calendars()
        return calendars

    def searchForAppointment(self, calendar):
        """ Termin finden """
        # Es gibt noch keinen gefundenen Termin
        apmtNotExisted = True
        # ab wann der Termine gesucht werden. Hier: ab der Benutzer nach nächsten Terminen fragt
        startOfDay = datetime.now(self.berlin)
        # Intervall des Suchens. Hier ist 1 Tag
        nextDay = startOfDay + \
            timedelta(days=1)
        # Intervall wird in der Schleife geschoben bis Termine gefunden wird.
        # wenn kein Termine gefunden wird
        while(apmtNotExisted):
            # Termin wird gesucht ab 'startOfDay' bis 'nextDay' (ein Intervall)
            events = calendar.date_search(
                start=startOfDay, end=nextDay)
            # wenn Termine gefunden wird
            if len(events) > 0:
                # wenn Termine in einem Tag gefunden werden
                # dann finde den ersten Termin des Tages mit Intervall von 30 Minuten
                start = startOfDay
                end = start + timedelta(hours=0.5)
                while(apmtNotExisted):
                    event = calendar.date_search(start=start, end=end)
                    # wenn der erste Termin gefunden wird
                    if len(event) > 0:
                        # die Schleife aufhören und der Termin zurückgeben
                        apmtNotExisted = False
                        return event
                    # wenn nicht, erhöhen sich 'start' und 'end' 30 Minuten
                    start = end
                    end += timedelta(hours=0.5)
            # wenn nicht, erhöhen sich 'startOfDay' und 'nextDay' 1 Tag
            startOfDay = nextDay
            nextDay += timedelta(days=1)

    def getNextAppointmentDate(self):
        """Information von dem Termin bekommen"""
        # Information des Termin
        nextAppointment = {}
        # Kalender holen
        calendars = self.getCalendars()
        if len(calendars) > 0:
            # Erste Kalender auswählen
            calendar = calendars[0]
            # nächter Termin finden
            event = self.searchForAppointment(calendar)
            # caldav event zu ical event ändern
            nextEvent = Calendar.from_ical(event[0]._data)
            for component in nextEvent.walk():
                if component.name == "VEVENT":
                    # Name des Termin speichern
                    nextAppointment.update(
                        {'Summary': component.get('summary')})
                    if component.get('discription') != None:
                        # Beschreibung des Termin speichern
                        nextAppointment.update(
                            {'Discription': component.get('discription')})
                    # Anfangdatum des Termin speichern
                    nextAppointment.update(
                        {'Start Date': component.get('dtstart').dt.strftime('%d/%m/%Y')})
                    # Anfangstunde des Termin speichern
                    nextAppointment.update(
                        {'Start Time': component.get('dtstart').dt.astimezone(self.berlin).strftime('%H:%M')})
                    # Enddatum des Termin speichern
                    nextAppointment.update(
                        {'End Date': component.get('dtend').dt.strftime('%d/%m/%Y')})
                    # Endstunde des Termin speichern
                    nextAppointment.update(
                        {'End Time': component.get('dtend').dt.astimezone(self.berlin).strftime('%H:%M')})
        return nextAppointment

    def saveAppointment(self, apmt, apmt_timedate):
        """Einen Termin machen"""
        cal = Calendar()
        event = Event()
        myCal = self.getCalendars()
        # Information des Termin speichern
        event.add('summary', apmt)
        event.add('dtstart', apmt_timedate)
        event.add('dtend', apmt_timedate + timedelta(hours=1))
        # event in ical-Kalender erstellen
        cal.add_component(event)
        # termin in Nextcloud schreiben
        myCal[0].save_event(cal)
        self.saved = True

    def eventExisted(self, dt):
        """einen bestimmten Termin suchen"""
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            # termin am bestimmten Tag
            event = calendar.date_search(
                start=dt, end=(dt + timedelta(minutes=5)))
        return event

    def deleteAppointment(self, dt):
        """einen Termin löschen"""
        calendars = self.getCalendars()
        if len(calendars) > 0:
            calendar = calendars[0]
            # termin am bestimmten Tag
            event = calendar.date_search(
                start=dt, end=(dt + timedelta(minutes=5)))
        # termin am bestimmten Tag löschen
        event[0].delete()
        print(event[0], 'was deleted')


class MakeAppointments(MycroftSkill):
    def __init__(self):
        # objekt von Klasse 'myCalendar' erstellen
        self.myCal = MyCalendar()
        MycroftSkill.__init__(self)

    @intent_handler('next.appointments.intent')
    def handle_next_appointment(self, message):
        """Frage von dem Benutzer bekommen und akustisch sie beantworten"""
        # näschter Termin gefunden durch die Funktion 'getNextAppointmentDate' von Objekt 'myCal'
        nextAp = self.myCal.getNextAppointmentDate()
        # Name des Termins
        todo = nextAp['Summary']
        # Datum des Termins
        dateS = nextAp['Start Date']
        # Uhrzeit des Termins
        timeS = nextAp['Start Time']
        # akustisch beantworten
        self.speak_dialog(
            'Your next appointment is on {} at {} and is entitled {}.'.format(dateS, timeS, todo))

    @intent_handler('make.appointment.intent')
    def add_new_appointment(self, msg=None):
        """ Handler zum Hinzufügen eines Termins mit einem Namen zu einem bestimmten Zeitpunkt. """
        # Name des Termins
        appointment = msg.data.get('appointment', None)
        # wenn kein Name da ist
        if appointment is None:
            # Rückmelden, dass kein Name gibt
            return self.unnamed_appointment(msg)
        # die Eingabe abholen
        utterance = msg.data['utterance']
        # Eine Datums- / Uhrzeitangabe wurde extrahiert
        appointment_time, _ = (extract_datetime(utterance, now_local(),
                                                self.lang,
                                                default_time=DEFAULT_TIME) or
                               (None, None))
        if appointment_time:
            # den Kalendereintrag machen
            self.myCal.saveAppointment(appointment, appointment_time)
            if self.myCal.saved:
                # bestätigen, dass den Eintrag gemacht wurde
                self.speak_dialog('appointments.make')
        else:
            # wenn kein Datum gibt, rückmelden
            self.speak_dialog('NoDate')

    @intent_handler('unnamed.appointment.intent')
    def unnamed_appointment(self, msg=None):
        """ Behandelt den Fall, in dem eine Uhrzeit angegeben wurde, aber kein Terminname hinzugefügt wurde."""
        # die Eingabe abholen
        utterance = msg.data['utterance']
        # Eine Datums- / Uhrzeitangabe wurde extrahiert
        apmt_time, _ = (extract_datetime(utterance, now_local(),
                                         self.lang,
                                         default_time=DEFAULT_TIME) or
                        (None, None))
        # nach den Terminname fragen
        response = self.get_response('AppointmentName')
        # wenn Terminname und Datum und Uhrzeit da sind
        if response and apmt_time:
            # den Kalendereintrag machen
            self.myCal.saveAppointment(response, apmt_time)
            if self.myCal.saved:
                # bestätigen, dass den Eintrag gemacht wurde
                self.speak_dialog('appointments.made')

    @intent_handler('deleteAppointment.intent')
    def remove_appointment(self, msg=None):
        """Entfernen Sie alle Termine für das angegebene Datum."""
        # Eine Datums- / Uhrzeitangabe wurde extrahiert
        if 'date' in msg.data:
            date, _ = extract_datetime(msg.data['date'], lang=self.lang)
        else:
            date, _ = extract_datetime(msg.data['utterance'], lang=self.lang)

        if date:
            if date.time():
                # schauen, ob der Termin am bestimmten Tag existiert
                if self.myCal.eventExisted(date):
                    # wenn ja, nach der Bestätigung zum Löschen fragen
                    answer = self.ask_yesno(
                        'confirmDelete', data={'date': date.strftime("%d/%m/%Y %H:%M")})
                    if answer == 'yes':
                        # wenn die Antwort 'Ja' ist, den Entrag löschen
                        self.myCal.deleteAppointment(date)
                        self.speak_dialog('Your appointment on {} was removed.'.format(
                            date.strftime("%d/%m/%Y %H:%M")))
                else:
                    # wenn kein Termin, rückmelden
                    self.speak_dialog('noAppointment', {
                                      'date': date.strftime("%d/%m/%Y %H:%M")})
        else:
            # wenn kein Datum gibt, rückmelden
            response = self.get_response('repeatDeleteDate')
            if response:
                self.remove_appointment(response)

    def stop(self):
        self.stop_beeping()

    def shutdown(self):
        pass


def create_skill():
    return MakeAppointments()
