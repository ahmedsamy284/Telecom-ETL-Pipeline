"""
Unit Test Module for CDR Data Validation.
This module uses the standard 'unittest' library to verify the correctness 
of the DataValidator class methods located in the 'utils' module.
"""

import unittest
from validation import DataValidator


class TestDataValidatorMSISDN(unittest.TestCase):
    """
    Test suite for validating the MSISDN (Caller Mobile Number) field.
    """

    def test_valid_msisdn(self):
        """Test that valid Egyptian mobile numbers return True."""
        self.assertTrue(DataValidator.is_valid_msisdn("01012345678"))
        self.assertTrue(DataValidator.is_valid_msisdn("01212345678"))
        self.assertTrue(DataValidator.is_valid_msisdn("01112345678"))
        # Test with international country code
        self.assertTrue(DataValidator.is_valid_msisdn("+201512345678"))

    def test_invalid_msisdn_wrong_prefix(self):
        """Test that numbers with invalid network prefixes (e.g., 019, 020) return False."""
        self.assertFalse(DataValidator.is_valid_msisdn("01912345678"))
        self.assertFalse(DataValidator.is_valid_msisdn("0201312345678"))
        self.assertFalse(DataValidator.is_valid_msisdn("11212345678"))

    def test_invalid_msisdn_wrong_length(self):
        """Test that numbers shorter or longer than the standard 11 digits return False."""
        self.assertFalse(DataValidator.is_valid_msisdn("0101234567"))   # 10 digits
        self.assertFalse(DataValidator.is_valid_msisdn("012123456789")) # 12 digits
        self.assertFalse(DataValidator.is_valid_msisdn("+20151234567")) # Short length with country code

    def test_invalid_msisdn_characters(self):
        """Test that numbers containing alphabetical letters or special characters return False."""
        self.assertFalse(DataValidator.is_valid_msisdn("0101234567a"))
        self.assertFalse(DataValidator.is_valid_msisdn("01212#45678"))
        self.assertFalse(DataValidator.is_valid_msisdn("+20151234!678"))

    def test_empty_or_none_msisdn(self):
        """Test that empty strings or None values are properly handled and return False."""
        self.assertFalse(DataValidator.is_valid_msisdn(""))
        self.assertFalse(DataValidator.is_valid_msisdn(None))
    

class TestDataValidatorIMSI(unittest.TestCase):
    """
    Test suite for validating the IMSI (International Mobile Subscriber Identity) field.
    """

    def test_valid_imsi(self):
        """Test that exactly 15-digit numeric strings return True."""
        self.assertTrue(DataValidator.is_valid_imsi("151353511234567"))
        self.assertTrue(DataValidator.is_valid_imsi("123456789012345"))

    def test_invalid_imsi_wrong_length(self):
        """Test that strings with lengths other than exactly 15 return False."""
        self.assertFalse(DataValidator.is_valid_imsi("15135351123456"))    # 14 digits
        self.assertFalse(DataValidator.is_valid_imsi("1513535112345678"))  # 16 digits

    def test_invalid_imsi_with_letters(self):
        """Test that 15-character strings containing letters or special symbols return False."""
        self.assertFalse(DataValidator.is_valid_imsi("15135351123456a"))
        self.assertFalse(DataValidator.is_valid_imsi("1513535112345!7"))

    def test_empty_or_none_imsi(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_imsi(""))
        self.assertFalse(DataValidator.is_valid_imsi(None))


class TestDataValidatorIMEI(unittest.TestCase):
    """
    Test suite for validating the IMEI (International Mobile Equipment Identity) field.
    """

    def test_valid_imei(self):
        """Test that exactly 15-digit numeric strings return True."""
        self.assertTrue(DataValidator.is_valid_imei("151353511234567"))
        self.assertTrue(DataValidator.is_valid_imei("123456789012345"))

    def test_invalid_imei_wrong_length(self):
        """Test that strings with lengths other than exactly 15 return False."""
        self.assertFalse(DataValidator.is_valid_imei("15135351123456"))    # 14 digits
        self.assertFalse(DataValidator.is_valid_imei("1513535112345678"))  # 16 digits

    def test_invalid_imei_with_letters(self):
        """Test that 15-character strings containing letters or special symbols return False."""
        self.assertFalse(DataValidator.is_valid_imei("15135351123456a"))
        self.assertFalse(DataValidator.is_valid_imei("1513535112345!7"))

    def test_empty_or_none_imei(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_imei(""))
        self.assertFalse(DataValidator.is_valid_imei(None))


class TestDataValidatorCallType(unittest.TestCase):
    """
    Test suite for validating the Call Type field.
    """

    def test_valid_call_types(self):
        """Test that standard valid call types (Data, Voice, SMS) return True."""
        self.assertTrue(DataValidator.is_valid_call_type("Data"))
        self.assertTrue(DataValidator.is_valid_call_type("Voice"))
        self.assertTrue(DataValidator.is_valid_call_type("SMS"))
      
    def test_valid_call_types_with_case_insensitive_and_whitespace(self):
        """Test that valid call types handle mixed cases and leading/trailing spaces correctly."""
        self.assertTrue(DataValidator.is_valid_call_type("  daTA  "))
        self.assertTrue(DataValidator.is_valid_call_type("  VoIcE  "))
        self.assertTrue(DataValidator.is_valid_call_type("  sMs  "))

    def test_invalid_call_types(self):
        """Test that unrecognized call types return False."""
        self.assertFalse(DataValidator.is_valid_call_type("Video"))
        self.assertFalse(DataValidator.is_valid_call_type("CALL"))
        self.assertFalse(DataValidator.is_valid_call_type("MMS"))

    def test_empty_or_none_call_type(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_call_type(""))
        self.assertFalse(DataValidator.is_valid_call_type(None))


class DataValidatorCallDuration(unittest.TestCase):
    """
    Test suite for validating the Call Duration field.
    """

    def test_valid_call_duration(self):
        """Test that positive numeric strings and zero return True."""
        self.assertTrue(DataValidator.is_valid_call_duration("120"))
        self.assertTrue(DataValidator.is_valid_call_duration("0"))
        self.assertTrue(DataValidator.is_valid_call_duration("9999"))

    def test_invalid_call_duration_negative(self):
        """Test that negative durations return False."""
        self.assertFalse(DataValidator.is_valid_call_duration("-1"))
        self.assertFalse(DataValidator.is_valid_call_duration("-100"))

    def test_invalid_call_duration_non_numeric(self):
        """Test that strings containing non-numeric characters return False."""
        self.assertFalse(DataValidator.is_valid_call_duration("abc"))
        self.assertFalse(DataValidator.is_valid_call_duration("12.5d"))
        self.assertFalse(DataValidator.is_valid_call_duration("!@#"))

    def test_empty_or_none_call_duration(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_call_duration(""))
        self.assertFalse(DataValidator.is_valid_call_duration(None))


class DataValidatorTimestamp(unittest.TestCase):
    """
    Test suite for validating the Call Timestamp field formats.
    """

    def test_valid_timestamp(self):
        """Test that correctly formatted datetime strings return True."""
        self.assertTrue(DataValidator.is_valid_timestamp("2023-01-01 12:00:00"))
        self.assertTrue(DataValidator.is_valid_timestamp("2023-12-31 23:59:59"))
        self.assertTrue(DataValidator.is_valid_timestamp("01-01-2023 12:00:00"))
        self.assertTrue(DataValidator.is_valid_timestamp("2023/01/01 12:00:00"))

    def test_invalid_timestamp_format(self):
        """Test that incorrectly formatted or out-of-bounds datetime strings return False."""
        self.assertFalse(DataValidator.is_valid_timestamp("01-15-2023 12:00:00"))  # Wrong month format
        self.assertFalse(DataValidator.is_valid_timestamp("2023 01 01 12:00:00"))  # Missing separators
        self.assertFalse(DataValidator.is_valid_timestamp("2023-01-01T12:00:00"))  # ISO format

    def test_empty_or_none_timestamp(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_timestamp(""))
        self.assertFalse(DataValidator.is_valid_timestamp(None))


class TestDataValidatorCalledNumber(unittest.TestCase):
    """
    Test suite for validating the Called Number (Destination) field.
    """

    def test_valid_called_number(self):
        """Test that valid destination mobile numbers return True."""
        self.assertTrue(DataValidator.is_valid_called_number("01012345678"))
        self.assertTrue(DataValidator.is_valid_called_number("01212345678"))
        self.assertTrue(DataValidator.is_valid_called_number("01112345678"))
        self.assertTrue(DataValidator.is_valid_called_number("+201512345678"))

    def test_invalid_called_number_wrong_prefix(self):
        """Test that destination numbers with invalid network prefixes return False."""
        self.assertFalse(DataValidator.is_valid_called_number("01912345678"))
        self.assertFalse(DataValidator.is_valid_called_number("0201312345678"))
        self.assertFalse(DataValidator.is_valid_called_number("11212345678"))

    def test_invalid_called_number_wrong_length(self):
        """Test that destination numbers with incorrect lengths return False."""
        self.assertFalse(DataValidator.is_valid_called_number("0101234567"))
        self.assertFalse(DataValidator.is_valid_called_number("012123456789"))
        self.assertFalse(DataValidator.is_valid_called_number("+20151234567"))

    def test_invalid_called_number_characters(self):
        """Test that destination numbers containing letters or special characters return False."""
        self.assertFalse(DataValidator.is_valid_called_number("0101234567a"))
        self.assertFalse(DataValidator.is_valid_called_number("01212#45678"))
        self.assertFalse(DataValidator.is_valid_called_number("+20151234!678"))

    def test_empty_or_none_called_number(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_called_number(""))
        self.assertFalse(DataValidator.is_valid_called_number(None))


class TestDataValidatorCallStatus(unittest.TestCase):
    """
    Test suite for validating the Call Status field.
    """

    def test_valid_call_status(self):
        """Test that recognized call status values return True, including mixed cases and spaces."""
        self.assertTrue(DataValidator.is_valid_call_status("ANSWERED"))
        self.assertTrue(DataValidator.is_valid_call_status("  DROPPED"))
        self.assertTrue(DataValidator.is_valid_call_status("busy"))
        self.assertTrue(DataValidator.is_valid_call_status("  MISSED  "))
        self.assertTrue(DataValidator.is_valid_call_status("  Blocked  "))

    def test_invalid_call_status(self):
        """Test that unrecognized or random call status strings return False."""
        self.assertFalse(DataValidator.is_valid_call_status("123"))
        self.assertFalse(DataValidator.is_valid_call_status("Unknown"))
        self.assertFalse(DataValidator.is_valid_call_status("Failed"))

    def test_empty_or_none_call_status(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_call_status(""))
        self.assertFalse(DataValidator.is_valid_call_status(None))


class TestDataValidatorCellId(unittest.TestCase):
    """
    Test suite for validating the Cell ID field.
    """

    def test_valid_cell_id(self):
        """Test that valid numeric Cell IDs between 5 and 7 digits return True."""
        self.assertTrue(DataValidator.is_valid_cell_id("12345"))
        self.assertTrue(DataValidator.is_valid_cell_id("678950"))
        self.assertTrue(DataValidator.is_valid_cell_id("6278950"))

    def test_invalid_cell_id_length(self):
        """Test that Cell IDs outside the allowed length bounds return False."""
        self.assertFalse(DataValidator.is_valid_cell_id("1234"))      # Less than 5 digits
        self.assertFalse(DataValidator.is_valid_cell_id("12345678"))  # More than 7 digits
        
    def test_invalid_cell_id_non_numeric(self):
        """Test that Cell IDs containing non-numeric characters return False."""
        self.assertFalse(DataValidator.is_valid_cell_id("abcde"))
        self.assertFalse(DataValidator.is_valid_cell_id("12a34"))
        self.assertFalse(DataValidator.is_valid_cell_id("!@#$%"))

    def test_empty_or_none_cell_id(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_cell_id(""))
        self.assertFalse(DataValidator.is_valid_cell_id(None))


class TestDataValidatorCallDirection(unittest.TestCase):
    """
    Test suite for validating the Call Direction field.
    """

    def test_valid_call_direction(self):
        """Test that recognized call directions return True, including mixed cases and spaces."""
        self.assertTrue(DataValidator.is_valid_call_direction("   INCOMING   "))
        self.assertTrue(DataValidator.is_valid_call_direction("  OUTGOING"))
        self.assertTrue(DataValidator.is_valid_call_direction("forwarded"))

    def test_invalid_call_direction(self):
        """Test that unrecognized call directions return False."""
        self.assertFalse(DataValidator.is_valid_call_direction("123"))
        self.assertFalse(DataValidator.is_valid_call_direction("Unknown"))
        self.assertFalse(DataValidator.is_valid_call_direction("Failed"))

    def test_empty_or_none_call_direction(self):
        """Test that empty strings or None values return False."""
        self.assertFalse(DataValidator.is_valid_call_direction(""))
        self.assertFalse(DataValidator.is_valid_call_direction(None))


if __name__ == '__main__':
    # Initialize the unit test runner to execute all defined tests
    unittest.main()
