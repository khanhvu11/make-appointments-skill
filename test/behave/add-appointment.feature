Feature: add-appointment
  Scenario: add new appointment
    Given an english speaking user
     When the user says "make appointment on <timedate> with title <appointment>"
     Then "make-appointments-skill" should reply with dialog from "appointment.made.dialog"