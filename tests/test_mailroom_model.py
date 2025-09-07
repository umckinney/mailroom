#!/usr/bin/env python
import sys
import pytest, re
from datetime import datetime
from pathlib import Path
from email_validator import validate_email, EmailNotValidError
from unittest.mock import patch  # for unit testing user inputs
from mailroom.mailroom_model import Donor
from mailroom.mailroom_model import DonorCollection
from mailroom.mailroom_model import MenuManager
from mailroom.mailroom_model import Helpers
from mailroom.mailroom_model import Validators

"""
Test Objectives:
    1. Ensure every function in mailroom_model.py has at least 1 unit test
    2. Cover both positive and as many negative unit tests as possible
"""
# IMPORT REQUIRED FUNCTIONS


# SETUP TEST FIXTURES
@pytest.fixture
def test_donor():
    return Donor("test@donor.com", "Test", "Donor")


@pytest.fixture
def test_donor2():
    return Donor("test2@donor2.com", "Test", "Donor2")


@pytest.fixture
def test_donor3():
    return Donor("test3@donor3.com", "John", "Donor3")


@pytest.fixture
def test_donor_collection():
    return DonorCollection()


####################################
# DONOR UNIT TESTS
####################################


def test_donor_initialization(test_donor):
    """test Donor initialization and __str__ value"""
    assert test_donor.email == "test@donor.com"
    assert test_donor.first_name == "Test"
    assert test_donor.last_name == "Donor"
    assert test_donor.donations == []
    assert test_donor.donation_total == 0.0
    assert test_donor.donation_count == 0
    assert test_donor.donation_average == 0.0
    assert test_donor.created is not None
    assert test_donor.deactivated[0] is False
    assert (
        str(test_donor)
        == "| test@donor.com                 | Test            | Donor           | $0.00            | 0      | $0.00            |"
    )


def test_return_donor_list_details(test_donor):
    """Validate correct values are returned (email, first, last, amount)"""
    print(test_donor.return_donor_list_details())
    assert test_donor.email in test_donor.return_donor_list_details()
    assert test_donor.first_name in test_donor.return_donor_list_details()
    assert test_donor.last_name in test_donor.return_donor_list_details()


def test_add_donation(test_donor):
    """test add_donation function explicitly, which calls donor_calculations"""
    test_donor.add_donation(100)
    assert test_donor.donations[0][0] == 100
    assert test_donor.donation_total == 100
    assert test_donor.donation_count == 1
    assert test_donor.donation_average == 100
    test_donor.add_donation(100)
    assert test_donor.donations[1][0] == 100
    assert test_donor.donation_total == 200
    assert test_donor.donation_count == 2
    assert test_donor.donation_average == 100


def test_update_donor_data(test_donor2):
    """test updating donor email, first name, and last name"""
    original_values = [
        test_donor2.email,
        test_donor2.first_name,
        test_donor2.last_name,
        test_donor2.donations,
    ]
    test_donor2.update_donor_data("email", "2test@2donor.com")
    assert test_donor2.email != original_values[0]
    assert test_donor2.first_name == original_values[1]
    assert test_donor2.last_name == original_values[2]
    assert test_donor2.donations == original_values[3]
    test_donor2.update_donor_data("first_name", "Fred")
    assert test_donor2.email != original_values[0]
    assert test_donor2.first_name != original_values[1]
    assert test_donor2.last_name == original_values[2]
    assert test_donor2.donations == original_values[3]
    test_donor2.update_donor_data("last_name", "Rogers")
    assert test_donor2.email != original_values[0]
    assert test_donor2.first_name != original_values[1]
    assert test_donor2.last_name != original_values[2]
    assert test_donor2.donations == original_values[3]
    assert (
        test_donor2.update_donor_data("Failure Test", "This Should Fail")
        == "Invalid data_type"
    )


def test_collect_donation_thank_you_details(test_donor):
    """Validate correct values are passed back for thank you note construction"""
    test_donor.add_donation(100)
    thank_you_note_content = test_donor.collect_donation_thank_you_details()
    assert thank_you_note_content["first"] == test_donor.first_name
    assert thank_you_note_content["last"] == test_donor.last_name
    assert thank_you_note_content["amount"] == test_donor.donations[0][0]
    test_donor.add_donation(1000)
    thank_you_note_content2 = test_donor.collect_donation_thank_you_details()
    assert thank_you_note_content2["amount"] == 1000


def test_collect_donation_thank_you2_details(test_donor):
    """Validate correct values are passed back for thank you note 2 construction"""
    test_donor.add_donation(100)
    thank_you_note_content = test_donor.collect_donation_thank_you2_details()
    assert thank_you_note_content["first"] == test_donor.first_name
    assert thank_you_note_content["last"] == test_donor.last_name
    assert thank_you_note_content["amount"] == 100
    test_donor.add_donation(200)
    thank_you_note2_content = test_donor.collect_donation_thank_you2_details()
    assert thank_you_note2_content["first"] == test_donor.first_name
    assert thank_you_note2_content["last"] == test_donor.last_name
    assert thank_you_note2_content["amount"] == 300


def test_deactivate_donor(test_donor):
    assert test_donor.deactivated[0] == False
    test_donor.deactivate_donor()
    assert test_donor.deactivated[0] == True


####################################
# VALIDATION UNIT TESTS
####################################
def test_validate_value_exists():
    assert Validators().validate_value_exists("a") == True
    assert Validators().validate_value_exists("") == False


def test_validate_donation_amount():
    assert Validators().validate_donation_amount(100) == True
    assert Validators().validate_donation_amount("100") == True
    assert Validators().validate_donation_amount("a") == False
    assert Validators().validate_donation_amount("") == False
    assert Validators().validate_donation_amount(-1) == None


def test_validate_email():
    assert Validators().validate_donor_email("test@test.com") == True
    assert Validators().validate_donor_email("test@test.co.uk") == True
    assert Validators().validate_donor_email("test@test") == False
    assert Validators().validate_donor_email("@test.com") == False
    assert Validators().validate_donor_email("") == False


####################################
# DONOR COLLECTION UNIT TESTS
####################################


def test_donor_collection_initialization(test_donor_collection):
    """Validate that a fresh collection sets an empty list"""
    assert test_donor_collection.donors == []
    assert test_donor_collection.limit == 10


def test_add_new_donor(test_donor_collection):
    """Ensure donors are added, returned in order, and are kept unique"""
    assert test_donor_collection.donors == []
    test_donor_collection.add_new_donor("test1@test.com", "Test First", "Test Last")
    test_donor_collection.add_new_donor("test2@test.com", "Test First", "Test Last")
    assert test_donor_collection != []
    assert test_donor_collection.donors[0].email == "test1@test.com"
    assert test_donor_collection.donors[1].email == "test2@test.com"
    assert (
        test_donor_collection.add_new_donor(
            "test1@test.com", "Fail Test", "Failure Test"
        )
        == False
    )


def test_select_donor(test_donor_collection):
    """Ensure selecting donors works for exact email match, fuzzy name match, and all"""
    assert test_donor_collection.donors == []
    donor1 = test_donor_collection.add_new_donor(
        "test1@test.com", "Test First", "Test1 Last"
    )
    donor2 = test_donor_collection.add_new_donor(
        "test2@test.com", "Test First", "Test2 Last"
    )
    donor3 = test_donor_collection.add_new_donor(
        "test3@test.com", "Test3 First", "Test3 Last"
    )
    result1 = test_donor_collection.select_donor(donor1.email, "email")
    assert result1 == [donor1]
    result2 = test_donor_collection.select_donor(donor2.first_name, "name")
    assert result2 == [donor1, donor2]
    result3 = test_donor_collection.select_donor()
    assert result3 == [donor1, donor2, donor3]
    assert test_donor_collection.select_donor("hey@there.com", "email") == False
    assert test_donor_collection.select_donor("Test4 Last", "name") == False


def test_generate_donor_report(test_donor_collection):
    """Ensure donor report list length equals count of donors in collection"""
    assert test_donor_collection.donors == []
    assert test_donor_collection.generate_donor_report() == []
    donor1 = test_donor_collection.add_new_donor(
        "test1@test.com", "Test First", "Test1 Last"
    )
    assert test_donor_collection.donors == [donor1]
    assert test_donor_collection.generate_donor_report() == [str(donor1)]
    donor2 = test_donor_collection.add_new_donor(
        "test2@test.com", "Test First", "Test2 Last"
    )
    assert test_donor_collection.donors == [donor1, donor2]
    assert test_donor_collection.generate_donor_report() == [str(donor1), str(donor2)]
    donor3 = test_donor_collection.add_new_donor(
        "test3@test.com", "Test3 First", "Test3 Last"
    )
    assert test_donor_collection.donors == [donor1, donor2, donor3]
    assert test_donor_collection.generate_donor_report() == [
        str(donor1),
        str(donor2),
        str(donor3),
    ]


def test_generate_donor_list(test_donor_collection):
    """Ensure donor list length equals count of donors in collection"""
    assert test_donor_collection.donors == []
    assert test_donor_collection.generate_donor_list() == []
    donor1 = test_donor_collection.add_new_donor(
        "test1@test.com", "Test First", "Test1 Last"
    )
    assert test_donor_collection.generate_donor_list() == [
        donor1.return_donor_list_details()
    ]
    donor2 = test_donor_collection.add_new_donor(
        "test2@test.com", "Test First", "Test2 Last"
    )
    assert test_donor_collection.generate_donor_list() == [
        donor1.return_donor_list_details(),
        donor2.return_donor_list_details(),
    ]
    donor3 = test_donor_collection.add_new_donor(
        "test3@test.com", "Test3 First", "Test3 Last"
    )
    assert test_donor_collection.generate_donor_list() == [
        donor1.return_donor_list_details(),
        donor2.return_donor_list_details(),
        donor3.return_donor_list_details(),
    ]
