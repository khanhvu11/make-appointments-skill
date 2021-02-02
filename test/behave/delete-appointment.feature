Feature: delete-appointment
  Scenario: delete an appointment
    Given an english speaking user
     When the user says "delete appointment for <date>"
     Then "make-appointments-skill" should reply with dialog from "confirmDelete.dialog"