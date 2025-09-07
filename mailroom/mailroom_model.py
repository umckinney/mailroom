#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
from email_validator import validate_email, EmailNotValidError

"""
Objectives:
    1. Model code is refactored to be Object Oriented
    2. Robust test suite exists and executes successfully
    3. Application is packaged and importable
Stretch Goals:
    A. Combine Donors and Donations dicts
    A. Add functionality to output Donors dict to json
    B. Add functionality to pick folder to save Donors json to (includes folder creation logic)
    C. Add functionality to select a json file to load for Donors data
    D. Add functionality to select output location for thank you letters
    E. Add functionality to select a saved template file for thank you letter to be created (selection from anywhere on disk)
    F. Add a localization switcher
"""


class Helpers:
    def __init__(self, *args):
        self.args = args

    def get_timestamp(self):
        now = datetime.now()
        return datetime.timestamp(now)

    def get_date(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%d %B %Y")

    def save_thank_you_message(self, first, last, thank_you_message):
        desktop_path = Path.home() / "Desktop"
        directory = f"thank_you_messages/{last}_{first}"
        path = desktop_path / directory
        path.mkdir(parents=True, exist_ok=True)
        filename = f"{last}_{first}_{str(self.get_date(self.get_timestamp()))}.txt"
        with open(f"{path}/{filename}", "w") as outfile:
            outfile.write(thank_you_message)

    def generate_seed_donors(self, seed_donor_collection):
        seed_donors = [
            ("test@test.com", "Test", "McTest"),
            ("uriah@mckinney.com", "Uriah", "McKinney"),
            ("boris@karloff.com", "Boris", "Karloff"),
            ("rick@springfield.com", "Rick", "Springfield"),
            ("bill@bailey@com", "Bill", "Bailey"),
        ]
        for seed_donor in seed_donors:
            seed_donor_collection.add_new_donor(
                seed_donor[0], seed_donor[1], seed_donor[2]
            )
        seed_donor_list = seed_donor_collection.select_donor()
        [seed_donor_list[0].add_donation(i) for i in [100]]
        [seed_donor_list[1].add_donation(i) for i in [50, 100]]
        [seed_donor_list[2].add_donation(i) for i in [10, 20, 30]]
        [seed_donor_list[3].add_donation(i) for i in [250, 100]]
        [seed_donor_list[4].add_donation(i) for i in [75, 100, 80, 25]]


class Validators:
    def __init__(self, *args):
        self.args = args

    def validate_value_exists(self, validation_value):
        return bool(validation_value)

    def validate_donation_amount(self, validation_value):
        try:
            if float(validation_value) > 0:
                return True
        except (ValueError, TypeError):
            return False

    def validate_donor_email(self, validation_value):
        try:
            validate_email(validation_value, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False


class Donor:
    """Supported actions:
    add donation, calculate donation report values, update donor details,
    generate donation thank you message
    """

    def __init__(self, email, first_name, last_name, **attributes):
        """Donations expects a 2d list with donation value + timestamp pairs"""
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.donations = []
        self.donation_total = 0.0
        self.donation_count = 0
        self.donation_average = 0.0
        self.created = Helpers().get_timestamp()
        self.deactivated = [False, self.created]
        self.donor_attributes = attributes

    def __str__(self):
        return f"| {self.email:<30} | {self.first_name:<15} | {self.last_name:<15} | ${float(self.donation_total):<15,.2f} | {self.donation_count:<6} | ${float(self.donation_average):<15,.2f} |"

    def return_donor_list_details(self):
        """Return values for list of donors view"""
        return f"{self.email:<30} | {self.first_name} {self.last_name}"

    def add_donation(self, new_donation):
        """Add a new donation value and donation timestamp to list of donations"""
        self.donations.append([new_donation, Helpers().get_timestamp()])
        self.donor_calculations()

    def donor_calculations(self):
        """Calculate/update donor values for primary report"""
        donation_value_list = []
        for donation in self.donations:
            donation_value_list.append(donation[0])
        self.donation_total = sum(donation_value_list)
        self.donation_count = len(donation_value_list)
        self.donation_average = self.donation_total / self.donation_count

    def update_donor_data(self, data_type, update_data):
        """Update method for email, first name, and last name"""
        match data_type:
            case "email":
                self.email = update_data
            case "first_name":
                self.first_name = update_data
            case "last_name":
                self.last_name = update_data
            case _:
                return "Invalid data_type"

    def collect_donation_thank_you_details(self, donation_index=-1):
        """Return donor details to populate thank you note"""
        date = Helpers().get_date(self.donations[donation_index][1])
        return {
            "date": date,
            "first": self.first_name,
            "last": self.last_name,
            "amount": self.donations[donation_index][0],
        }

    def collect_donation_thank_you2_details(self, donation_index=-1):
        """Return donor details to populate thank you note"""
        date = Helpers().get_date(self.donations[donation_index][1])
        created = Helpers().get_date(self.created)
        return {
            "date": date,
            "first": self.first_name,
            "last": self.last_name,
            "amount": self.donation_total,
            "created": created,
        }

    def deactivate_donor(self):
        self.deactivated = [True, Helpers().get_timestamp()]

    def thank_you_template(self):
        return """
        {date}

        Dear {first} {last},
        Thank you for your support to our organization and your generous donation of ${amount:,.2f}.

        Your giving helps us carry our mission forward.
        Sincerely,
        -The Team
        """

    def thank_you_template2(self):
        return """
        {date}

        Dear {first} {last},
        Since {created}, you have generously donated ${amount:,.2f} to our organization. Thank you for your support.

        Your continued giving makes our good work possible.
        Sincerely,
        -The Team
        """


class DonorCollection:
    """Supported actions:
    create a new Donor record, remove an existing Donor record,
    update Donor record, select matching donors from donor collection,
    generate Donor report
    """

    def __init__(self, limit=10, **attributes):
        self.donors = []
        self.limit = limit
        self.collection_attributes = attributes

    def add_new_donor(self, email, first_name, last_name):
        """Add new donor record to donor collection"""
        if self.select_donor(email, "email"):
            return False
        else:
            new_donor = Donor(email, first_name, last_name)
            self.donors.append(new_donor)
            return new_donor

    def select_donor(self, donor_data="*", donor_field="*"):
        """Return list of donor records based on donor_identifier value
        exact email match returns 1
        first/last name match returns N
        * (default) returns all
        Active_flag determines if query is on active or 'deactivated' records
        """
        found_donors = []
        for donor in self.donors:
            if (
                donor_field == "*"
                or (
                    donor_field == "name"
                    and (
                        donor_data == donor.first_name or donor_data == donor.last_name
                    )
                )
                or (donor_field == "email" and donor_data == donor.email)
            ):
                found_donors.append(donor)
        if found_donors:
            return found_donors
        else:
            return False

    def generate_donor_report(self):
        """TODO Generate a 3 level dict (page > page number > list of donor objects on page)"""
        report = []
        for donor in self.donors:
            report.append(donor.__str__())
        return report

    def generate_donor_list(self):
        """Generate a list of donor names and emails"""
        donor_list = []
        for donor in self.donors:
            donor_list.append(donor.return_donor_list_details())
        return donor_list


class MenuManager:
    """Manages program menus and selections"""

    def __init__(self, user_selection):
        self.user_selection = user_selection

    def selection_handler(self, menu):
        """Call the function mapped to the menu selection"""
        try:
            selected_function = menu.get(self.user_selection)
            if selected_function and callable(selected_function):
                return selected_function
            else:
                return "Invalid Selection"
        except (TypeError, ValueError):
            return "Invalid Selection"
