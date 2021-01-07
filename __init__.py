from mycroft import MycroftSkill, intent_file_handler


class MakeAppointments(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('appointments.make.intent')
    def handle_appointments_make(self, message):
        self.speak_dialog('appointments.make')


def create_skill():
    return MakeAppointments()

