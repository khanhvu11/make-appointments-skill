Feature: next-appointment
  Scenario: my next appointment
    Given an English speaking user
     When the user says "What is my next appointment"
     Then "make-appointments-skill" should reply with "Your next appointment is on <Date> at <Time> and is entitled <Title>."
  
  Examples: appointment data
        |Date           |Time             |Title
        |22/01/2021     |09:00            |Breakfast
        |24/01/2021     |17:45            |Speech Interaction

        