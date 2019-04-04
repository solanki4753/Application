from typing import List

import datetime

import bson

from data.bookings import Booking
from data.machines import Machine
from data.owners import Owner
from data.jobs import Job


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_machine(active_account: Owner,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Machine:
    machine = Machine()

    machine.name = name
    machine.square_meters = meters
    machine.is_carpeted = carpeted
    machine.has_toys = has_toys
    machine.allow_dangerous_jobs = allow_dangerous
    machine.price = price

    machine.save()

    account = find_account_by_email(active_account.email)
    account.machine_ids.append(machine.id)
    account.save()

    return machine


def find_machines_for_user(account: Owner) -> List[Machine]:
    query = Machine.objects(id__in=account.machine_ids)
    machines = list(query)

    return machines


def add_available_date(machine: Machine,
                       start_date: datetime.datetime, days: int) -> Machine:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    machine = Machine.objects(id=machine.id).first()
    machine.bookings.append(booking)
    machine.save()

    return machine


def add_job(account, name, length, species, is_venomous) -> Job:
    job = Job()
    job.name = name
    job.length = length
    job.species = species
    job.is_venomous = is_venomous
    job.save()

    owner = find_account_by_email(account.email)
    owner.job_ids.append(job.id)
    owner.save()

    return job


def get_jobs_for_user(user_id: bson.ObjectId) -> List[Job]:
    owner = Owner.objects(id=user_id).first()
    jobs = Job.objects(id__in=owner.job_ids).all()

    return list(jobs)


def get_available_machines(checkin: datetime.datetime,
                        checkout: datetime.datetime, job: Job) -> List[Machine]:
    min_size = job.length / 4

    query = Machine.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if job.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    machines = query.order_by('price', '-square_meters')

    final_machines = []
    for c in machines:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.customer_job_id is None:
                final_machines.append(c)

    return final_machines


def book_machine(account, job, machine, checkin, checkout):
    booking: Booking = None

    for b in machine.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.customer_job_id is None:
            booking = b
            break

    booking.customer_owner_id = account.id
    booking.customer_job_id = job.id
    booking.booked_date = datetime.datetime.now()

    machine.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_machines = Machine.objects() \
        .filter(bookings__customer_owner_id=account.id) \
        .only('bookings', 'name')

    def map_machine_to_booking(machine, booking):
        booking.machine = machine
        return booking

    bookings = [
        map_machine_to_booking(machine, booking)
        for machine in booked_machines
        for booking in machine.bookings
        if booking.customer_owner_id == account.id
    ]

    return bookings
