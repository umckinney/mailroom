#!/usr/bin/env python3
import sys
from mailroom_model import Donor
from mailroom_model import DonorCollection
from mailroom_model import MenuManager
from mailroom_model import Helpers
from mailroom_model import Validators


##########################################################
# UI CLASSES                                             #
##########################################################
class View:
    """Base View class"""

    def __init__(self, view_name):
        self.view_name = view_name

    def newline(self):
        print("\n")

    def pause_screen(self):
        """Pause the screen"""
        return input("Press ENTER to continue")

    def clear_screen(self):
        """Clear the screen"""
        print("\033c", end="")

    def print_title(self):
        """Print the title to screen"""
        print(f"Donation Manager - {self.view_name}")

    def print_content(self, content):
        """Print the content to screen"""
        print(content)

    def collect_user_input(self, collection_string):
        """Collect user input"""
        return input(collection_string + " >>> ")


class Menu(View):
    def print_content(self, content):
        """Prints menu values based on the selected menu type"""
        for key, value in content.items():
            print(f"{key} - {value.__name__.replace('_', ' ').title()}")


class Report(View):
    def print_content(self, content):
        for i in content:
            print(i)


##########################################################
# PROGRAM FLOW                                           #
##########################################################
def main():
    """Start mailroom program flow"""
    program_running = True
    while program_running:
        main_menu_view()


def main_menu_view():
    """Construct and manage main program menu"""
    valid = False
    while not valid:
        main_view = Menu("Main Menu")
        main_view.clear_screen()
        main_view.print_title()
        main_view.newline()
        main_view.print_content(program_main_menu)
        main_view.newline()
        menu_selection = main_view.collect_user_input("Select an item from the menu")
        menu_manager = MenuManager(menu_selection)
        selected_function = menu_manager.selection_handler(program_main_menu)
        if callable(selected_function):
            selected_function()


def add_donation():
    """Record a new donation for new or existing donor"""
    add_donation_view = View("Add Donation")
    add_donation_view.clear_screen()
    add_donation_view.print_title()
    add_donation_view.newline()
    valid = False
    while not valid:
        donor_email = add_donation_view.collect_user_input(
            "Enter the donor's email address"
        )
        valid = Validators().validate_donor_email(donor_email)
    donor_found = donor_collection.select_donor(donor_email, "email")
    if donor_found:
        donor = donor_found[0]
    else:
        first_name = collect_name(add_donation_view, "first")
        last_name = collect_name(add_donation_view, "last")
        donor = donor_collection.add_new_donor(donor_email, first_name, last_name)
        add_donation_view.print_content(
            f"{first_name} {last_name} added to Donor Collection"
        )
    valid = False
    while not valid:
        donation_amount = add_donation_view.collect_user_input(
            "Enter the donation amount"
        )
        valid = Validators().validate_donation_amount(donation_amount)
    donor.add_donation(float(donation_amount))
    add_donation_view.newline()
    thank_you_details = donor.collect_donation_thank_you_details()
    add_donation_view.print_content(
        donor.thank_you_template().format(**thank_you_details)
    )
    add_donation_view.newline()
    add_donation_view.pause_screen()
    main_menu_view()


def collect_name(view, name_type):
    valid = False
    while not valid:
        name = view.collect_user_input(f"Enter the donor's {name_type} name").title()
        valid = Validators().validate_value_exists(name)
    return name


def list_of_donors():
    """Present a list of all donors in donor_collection"""
    donor_list = donor_collection.generate_donor_list()
    donor_list_view = Report("Donor Report")
    donor_list_view.clear_screen()
    donor_list_view.print_title()
    donor_list_view.newline()
    donor_list_view.print_content(donor_list)
    donor_list_view.newline()
    donor_list_view.pause_screen()
    main_menu_view()


def donor_report():
    """Present donor report for all donors in donor_collection"""
    report = donor_collection.generate_donor_report()
    donor_report_view = Report("Donor Report")
    donor_report_view.clear_screen()
    donor_report_view.print_title()
    donor_report_view.newline()
    donor_report_view.print_content(report)
    donor_report_view.newline()
    donor_report_view.pause_screen()
    main_menu_view()


def create_thank_you_letters_for_donors():
    """Generate thank you letters for all donors in parent folder on Desktop"""
    thank_you_view = View("Create Thank You Letters for Donors")
    thank_you_view.clear_screen()
    thank_you_view.print_title()
    thank_you_view.newline()
    donors_list = donor_collection.select_donor()
    for donor in donors_list:
        thank_you_details = donor.collect_donation_thank_you2_details()
        thank_you_letter = donor.thank_you_template2().format(**thank_you_details)
        Helpers().save_thank_you_message(
            donor.first_name, donor.last_name, thank_you_letter
        )
        thank_you_view.print_content(
            f"Thank you letter saved for {donor.first_name} {donor.last_name}"
        )
    thank_you_view.newline()
    thank_you_view.pause_screen()
    main_menu_view()


def exit_program():
    """End program"""
    print("Program Ended Successfully")
    sys.exit()


##########################################################
# INITIALIZE MAILROOM PROGRAM                            #
##########################################################
donor_collection = DonorCollection()
seed_donors = Helpers().generate_seed_donors(donor_collection)
program_main_menu = {
    "A": add_donation,
    "L": list_of_donors,
    "D": donor_report,
    "C": create_thank_you_letters_for_donors,
    "E": exit_program,
}

if __name__ == "__main__":
    donor_collection = DonorCollection()
    seed_donors = Helpers().generate_seed_donors(donor_collection)
    main()
