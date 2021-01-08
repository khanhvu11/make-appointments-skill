from mycroft import MycroftSkill, intent_file_handler
from adapt.intent import IntentBuilder
from mycroft.util.time import now_local
import calendar_se as myCal


class MakeAppointments(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('appointments.make.intent')
    def handle_appointments_make(self, message):
        now = now_local.date()
        nextAp = myCal.getNextAppointmentDate(now)
        todo = nextAp['Summary']
        dateS = nextAp['Start Date']
        dateE = nextAp['End Date']
        timeS = nextAp['Start Time']
        timeE = nextAp['Start Time']
        self.speak_dialog(
            'Your next appointment is on {} at {} and is entitled {}.'.format(dateS, timeS, todo))


def create_skill():
    return MakeAppointments()
