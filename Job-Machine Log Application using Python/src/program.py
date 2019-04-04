from colorama import Fore
import program_customers
import program_workers
import data.mongo_setup as mongo_setup


def main():
    mongo_setup.global_init()

    print_header()

    try:
        while True:
            if find_user_intent() == 'job_booking':
                program_customers.run()
            else:
                program_workers.run()
    except KeyboardInterrupt:
        return


def print_header():
    print(Fore.WHITE + '****************Job_log**********************')
    print(Fore.GREEN + '*********************************************')
    print(Fore.WHITE + '*********************************************')
    print()
    print("Welcome to Job_log!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g]uest: Book a machine for your job")
    print("[w]orker: Offer extra machine space")
    print()
    choice = input("Are you a [g]uest or [w]orker? ")
    if choice == 'w':
        return 'Add_machine'

    return 'job_booking'


if __name__ == '__main__':
    main()
