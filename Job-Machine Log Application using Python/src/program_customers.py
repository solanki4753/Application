import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_workers as workers
import services.data_service as svc
from program_workers import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome customer **************** ')
    print()

    show_commands()

    while True:
        action = workers.get_action()

        with switch(action) as s:
            s.case('c', workers.create_account)
            s.case('l', workers.log_into_account)

            s.case('a', add_a_job)
            s.case('y', view_your_jobs)
            s.case('b', book_a_machine)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], workers.exit_app)

            s.default(workers.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a machine')
    print('[A]dd a job')
    print('View [y]our jobs')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_job():
    print(' ****************** Add a job **************** ')
    if not state.active_account:
        error_msg("You must log in first to add a job")
        return

    name = input("What is your job's name? ")
    if not name:
        error_msg('cancelled')
        return

    length = float(input('How long is your job (in meters)? '))
    species = input("Species? ")
    is_venomous = input("Is your job venomous [y]es, [n]o? ").lower().startswith('y')

    job = svc.add_job(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    success_msg('Created {} with id {}'.format(job.name, job.id))


def view_your_jobs():
    print(' ****************** Your jobs **************** ')
    if not state.active_account:
        error_msg("You must log in first to view your jobs")
        return

    jobs = svc.get_jobs_for_user(state.active_account.id)
    print("You have {} jobs.".format(len(jobs)))
    for s in jobs:
        print(" * {} is a {} that is {}m long and is {}venomous.".format(
            s.name,
            s.species,
            s.length,
            '' if s.is_venomous else 'not '
        ))


def book_a_machine():
    print(' ****************** Book a machine **************** ')
    if not state.active_account:
        error_msg("You must log in first to book a machine")
        return

    jobs = svc.get_jobs_for_user(state.active_account.id)
    if not jobs:
        error_msg('You must first [a]dd a job before you can book a machine.')
        return

    print("Let's start by finding available machines.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        error_msg('cancelled')
        return

    checkin = parser.parse(
        start_text
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(jobs):
        print('{}. {} (length: {}, venomous: {})'.format(
            idx + 1,
            s.name,
            s.length,
            'yes' if s.is_venomous else 'no'
        )) 
    #functuib check in list or  not 
    job = jobs[int(input('Which job do you want to book (number)')) - 1]

    machines = svc.get_available_machines(checkin, checkout, job)

    print("There are {} machines available in that time.".format(len(machines)))
    for idx, c in enumerate(machines):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            c.name,
            c.square_meters,
            'yes' if c.is_carpeted else 'no',
            'yes' if c.has_toys else 'no'))

    if not machines:
        error_msg("Sorry, no machines are available for that date.")
        return

    machine = machines[int(input('Which machine do you want to book (number)')) - 1]
    svc.book_machine(state.active_account, job, machine, checkin, checkout)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(machine.name, job.name, machine.price))


def view_bookings():
    print(' **** Your bookings(only for workers), Change Mode using M**************** ')
    if not state.active_account:
        error_msg("You must log in first to register a machine")
        return

    jobs = {s.id: s for s in svc.get_jobs_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        print(' * job: {} is booked at {} from {} for {} days.'.format(
            jobs.get(b.customer_job_id).name,
            b.machine.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
