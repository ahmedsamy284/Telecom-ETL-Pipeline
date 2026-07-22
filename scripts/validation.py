"""
CDR (Call Detail Record) Data Validation Utility Module.
This module provides centralized logging and data validation functions
to ensure the integrity of telecom data fields before ingestion.
"""

import re, logging, os, datetime

# Set up the current directory and the absolute path for the error log file.
current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, "Pipeline_Errors.log")


class LoggerManager:
    """
    A utility class to manage and configure the application's logging mechanism.
    """
   
    @staticmethod
    def get_logger(log_file_path=log_file_path):
        """
        Configures and retrieves the root logger for logging pipeline errors.
        
        Args:
            log_file_path (str): The absolute path where the log file will be saved.
                                 Defaults to 'Pipeline_Errors.log' in the current directory.
        
        Returns:
            logging.Logger: The configured logger instance ready to write logs.
        """
        # Configure the basic settings for the logging system
        logging.basicConfig(
            filename =log_file_path,
            filemode = "a", # Append mode to keep previous logs
            encoding = "utf-8",
            level = logging.INFO,
            format = "%(asctime)s - %(levelname)s - %(message)s",
            datefmt = "%d-%m-%Y %H:%M:%S")
        return logging.getLogger()


class DataValidator:
    """
    A collection of static methods to validate various fields of a Call Detail Record (CDR).
    Invalid fields are automatically logged using the LoggerManager.
    """

    @staticmethod
    def is_valid_msisdn(phone_number):
        """
        Validates the Mobile Station International Subscriber Directory Number (MSISDN).
        Ensures it matches the Egyptian mobile number format.
        
        Args:
            phone_number (str): The mobile number to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if phone_number is None or str(phone_number).strip() == "":
            LoggerManager.get_logger().warning(f"[MSISDN_ERROR] - Invalid MSISDN is None or empty: {phone_number}")
            return False
        
        # Regex pattern for Egyptian numbers (optional +2 or 002, followed by 010/011/012/015 and 8 digits)
        pattern = r'(002|\+2)?01[0125][0-9]{8}$'
        if re.match(pattern, phone_number) is not None:
            return True
        else:
            LoggerManager.get_logger().warning(f"[MSISDN_ERROR] - Invalid MSISDN: {phone_number}")
            return False

    @staticmethod
    def is_valid_imsi(imsi):
        """
        Validates the International Mobile Subscriber Identity (IMSI).
        Ensures it is exactly 15 digits long.
        
        Args:
            imsi (str): The IMSI string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if imsi is None or str(imsi).strip() == "":
            LoggerManager.get_logger().warning(f"[IMSI_ERROR] - Invalid IMSI is None or empty: {imsi}")
            return False
        
        # Regex pattern for exactly 15 numeric digits
        pattern = r'^\d{15}$'
        if re.match(pattern, imsi) is not None:
            return True
        else:
            LoggerManager.get_logger().warning(f"[IMSI_ERROR] - Invalid IMSI: {imsi}")
            return False
 
    @staticmethod
    def is_valid_imei(imei):
        """
        Validates the International Mobile Equipment Identity (IMEI).
        Ensures it is exactly 15 digits long.
        
        Args:
            imei (str): The IMEI string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if imei is None or str(imei).strip() == "":
            LoggerManager.get_logger().warning(f"[IMEI_ERROR] - Invalid IMEI is None or empty: {imei}")
            return False
        
        # Regex pattern for exactly 15 numeric digits
        pattern = r'^\d{15}$'
        if re.match(pattern, imei) is not None:
            return True
        else:
            LoggerManager.get_logger().warning(f"[IMEI_ERROR] - Invalid IMEI: {imei}")
            return False

    @staticmethod
    def is_valid_call_type(call_type):
        """
        Validates the Call Type.
        Ensures it belongs to a predefined set of valid types: Voice, Data, SMS.
        
        Args:
            call_type (str): The call type string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if call_type is None or str(call_type).strip() == "":
            LoggerManager.get_logger().warning(f"[CALL_TYPE_ERROR] - Invalid Call Type is None or empty: {call_type}")
            return False
        
        # Define the valid set of call types
        valid_call_types = {"Voice", "Data", "SMS", }
        
        # Clean the input by stripping whitespace and capitalizing the first letter
        cleaned_call_type= str(call_type).strip().capitalize()
        
        # Handle the specific case format for "SMS"
        if cleaned_call_type == "Sms":
            cleaned_call_type = "SMS"
            
        if cleaned_call_type in valid_call_types:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_TYPE_ERROR] - Invalid Call Type: {call_type}")
            return False


    @staticmethod
    def is_valid_call_duration(duration):
        """
        Validates the Call Duration.
        Ensures the duration is a numeric value and is greater than or equal to zero.
        
        Args:
            duration (str/int/float): The call duration to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if duration is None or str(duration).strip() == "":
            LoggerManager.get_logger().warning(f"[DURATION_ERROR] - Invalid Call Duration is None or empty: {duration}")
            return False
        
        try:
            # Attempt to convert the duration to a float
            duration_float = float(duration)
            if duration_float >= 0:
                return True 
            else:
                LoggerManager.get_logger().warning(f"[DURATION_ERROR] - Invalid Call Duration (negative): {duration}")
                return False
        except ValueError:
            # Catch cases where the duration contains non-numeric characters
            LoggerManager.get_logger().warning(f"[DURATION_ERROR] - Invalid Call Duration (not a number): {duration}")
            return False


    @staticmethod
    def is_valid_timestamp(timestamp):
        """
        Validates the Call Timestamp.
        Checks the input against multiple accepted date-time formats.
        
        Args:
            timestamp (str): The datetime string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if timestamp is None or str(timestamp).strip() == "":
            LoggerManager.get_logger().warning(f"[TIMESTAMP_ERROR] - Invalid Timestamp is None or empty: {timestamp}")
            return False
        
        # List of acceptable datetime formats
        valid_timestamp_formats = ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
        
        # Iterate through the formats and attempt to parse the timestamp
        for fmt in valid_timestamp_formats:
            try:
                datetime.datetime.strptime(timestamp, fmt)
                return True
            except ValueError:
                continue # Try the next format if the current one fails
                
        LoggerManager.get_logger().warning(f"[TIMESTAMP_ERROR] - Invalid Timestamp format: {timestamp}")
        return False


    @staticmethod
    def is_valid_called_number(called_number):
        """
        Validates the Called Number (destination number).
        Uses the same regex rules as MSISDN for Egyptian formatting.
        
        Args:
            called_number (str): The called mobile number to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if called_number is None or str(called_number).strip() == "":
            LoggerManager.get_logger().warning(f"[CALLED_NUMBER_ERROR] - Invalid CALLED NUMBER is None or empty: {called_number}")
            return False
        
        # Regex pattern for Egyptian numbers
        pattern = r'(002|\+2)?01[0125][0-9]{8}$'
        if re.match(pattern, called_number) is not None:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALLED_NUMBER_ERROR] - Invalid CALLED NUMBER: {called_number}")
            return False


    @staticmethod
    def is_valid_call_status(status):
        """
        Validates the Call Status.
        Ensures the status matches predefined states like ANSWERED, MISSED, etc.
        
        Args:
            status (str): The call status string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if status is None or str(status).strip() == "":
            LoggerManager.get_logger().warning(f"[CALL_STATUS_ERROR] - Invalid Call Type is None or empty: {status}")
            return False
        
        # Define the set of accepted operational statuses
        valid_call_status = {"ANSWERED", "MISSED", "BUSY", "DROPPED", "BLOCKED" }
        
        # Clean the input to uppercase and strip whitespace for accurate matching
        cleaned_status= str(status).strip().upper()
        
        if cleaned_status in valid_call_status:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_STATUS_ERROR] - Invalid Call Status: {status}")
            return False


    @staticmethod
    def is_valid_cell_id(cell_id):
        """
        Validates the Cell ID (Base Station Identifier).
        Ensures it is a numeric value containing between 5 and 7 digits.
        
        Args:
            cell_id (str): The Cell ID to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if cell_id is None or str(cell_id).strip() == "":
            LoggerManager.get_logger().warning(f"[CELL_ID_ERROR] - Invalid Cell ID is None or empty: {cell_id}")
            return False
        
        # Regex pattern for exactly 5 to 7 numeric digits
        pattern = r'^\d{5,7}$'
        if re.match(pattern, cell_id) is not None:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CELL_ID_ERROR] - Invalid Cell ID: {cell_id}")
            return False


    @staticmethod
    def is_valid_call_direction(direction):
        """
        Validates the Call Direction.
        Ensures the direction is one of the valid routing states: INCOMING, OUTGOING, FORWARDED.
        
        Args:
            direction (str): The call direction string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if direction is None or str(direction).strip() == "":
            LoggerManager.get_logger().warning(f"[CALL_DIRECTION_ERROR] - Invalid Call Direction is None or empty: {direction}")
            return False
        
        # Define the valid set of call directions
        valid_call_directions = {"INCOMING", "OUTGOING", "FORWARDED"}
        
        # Clean the input to uppercase and strip whitespace
        cleaned_direction= str(direction).strip().upper()
        
        if cleaned_direction in valid_call_directions:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_DIRECTION_ERROR] - Invalid Call Direction: {direction}")
            return False
