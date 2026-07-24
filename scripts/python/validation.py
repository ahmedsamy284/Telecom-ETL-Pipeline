"""
CDR (Call Detail Record) Data Validation Utility Module.
This module provides centralized logging and data validation functions
to ensure the integrity of telecom data fields before ingestion.
It validates the raw data and routes it to either a valid or invalid dataset.
"""

import re
import logging
import os
import datetime
import csv
# Import output configurations from the data generator to maintain a Single Source of Truth
from data_generator import OUTPUT_DIR, OUTPUT_FILE

# ---------------------------------------------------------
# Global Configuration & Path Setup
# ---------------------------------------------------------
# Set up the current directory and the absolute path for the error log file.
current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, "Pipeline_Errors.log")


class LoggerManager:
    """
    A utility class to manage and configure the application's logging mechanism.
    Centralizes logging to ensure all pipeline errors are tracked uniformly.
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
            filename=log_file_path,
            filemode="a", # Append mode to keep previous execution logs intact
            encoding="utf-8",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S"
        )
        return logging.getLogger()


class DataValidator:
    """
    A collection of static methods to validate various fields of a Call Detail Record (CDR).
    Each method checks specific business rules (e.g., regex, data types, sets).
    Invalid fields are automatically logged using the LoggerManager for auditability.
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
        # Check for None or empty string to prevent TypeErrors in regex
        if phone_number is None or str(phone_number).strip() == "":
            LoggerManager.get_logger().warning(f"[MSISDN_ERROR] - Invalid MSISDN is None or empty: {phone_number}")
            return False
        
        # Regex pattern for Egyptian numbers: optional +2 or 002, followed by 010/011/012/015 and exactly 8 digits
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
        
        # Regex pattern enforcing exactly 15 numeric digits (no letters or special chars)
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
        
        # Regex pattern enforcing exactly 15 numeric digits
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
        Ensures it belongs to a predefined categorical set: Voice, Data, SMS.
        
        Args:
            call_type (str): The call type string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if call_type is None or str(call_type).strip() == "":
            LoggerManager.get_logger().warning(f"[CALL_TYPE_ERROR] - Invalid Call Type is None or empty: {call_type}")
            return False
        
        # Define the allowed set of call types based on business logic
        valid_call_types = {"Voice", "Data", "SMS"}
        
        # Clean the input by stripping surrounding whitespace and capitalizing the first letter
        cleaned_call_type = str(call_type).strip().capitalize()
        
        # Handle the specific edge case for "SMS" (since capitalize() makes it "Sms")
        if cleaned_call_type == "Sms":
            cleaned_call_type = "SMS"
            
        # O(1) membership check using a Python Set
        if cleaned_call_type in valid_call_types:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_TYPE_ERROR] - Invalid Call Type: {call_type}")
            return False

    @staticmethod
    def is_valid_call_duration(duration):
        """
        Validates the Call Duration.
        Ensures the duration is a numeric value and is logically greater than or equal to zero.
        
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
            # Attempt to type-cast the duration to a float
            duration_float = float(duration)
            # Duration cannot be negative in a telecommunications context
            if duration_float >= 0:
                return True 
            else:
                LoggerManager.get_logger().warning(f"[DURATION_ERROR] - Invalid Call Duration (negative): {duration}")
                return False
        except ValueError:
            # Catch cases where the duration contains non-numeric characters (e.g., "five mins")
            LoggerManager.get_logger().warning(f"[DURATION_ERROR] - Invalid Call Duration (not a number): {duration}")
            return False

    @staticmethod
    def is_valid_timestamp(timestamp):
        """
        Validates the Call Timestamp.
        Checks the input string against multiple acceptable date-time formats.
        
        Args:
            timestamp (str): The datetime string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Check for None or empty string
        if timestamp is None or str(timestamp).strip() == "":
            LoggerManager.get_logger().warning(f"[TIMESTAMP_ERROR] - Invalid Timestamp is None or empty: {timestamp}")
            return False
        
        # List of acceptable datetime formats encountered in raw systems
        valid_timestamp_formats = ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
        
        # Iterate through the formats and attempt to parse the timestamp
        for fmt in valid_timestamp_formats:
            try:
                datetime.datetime.strptime(timestamp, fmt)
                return True # Successfully parsed, format is valid
            except ValueError:
                continue # Try the next format in the list if the current one fails
                
        # If the loop finishes without returning True, no formats matched
        LoggerManager.get_logger().warning(f"[TIMESTAMP_ERROR] - Invalid Timestamp format: {timestamp}")
        return False

    @staticmethod
    def is_valid_called_number(called_number):
        """
        Validates the Called Number (destination number).
        Uses the same regex rules as MSISDN to ensure correct routing format.
        
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
        Ensures the status matches predefined operational states (e.g., ANSWERED, MISSED).
        
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
        valid_call_status = {"ANSWERED", "MISSED", "BUSY", "DROPPED", "BLOCKED"}
        
        # Clean the input to uppercase and strip whitespace for accurate case-insensitive matching
        cleaned_status = str(status).strip().upper()
        
        if cleaned_status in valid_call_status:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_STATUS_ERROR] - Invalid Call Status: {status}")
            return False

    @staticmethod
    def is_valid_cell_id(cell_id):
        """
        Validates the Cell ID (Base Station Identifier).
        Ensures it is a numeric value containing between 5 and 7 digits based on network specs.
        
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
        cleaned_direction = str(direction).strip().upper()
        
        if cleaned_direction in valid_call_directions:
            return True
        else:
            LoggerManager.get_logger().warning(f"[CALL_DIRECTION_ERROR] - Invalid Call Direction: {direction}")
            return False


class DataProcessor:
    """
    Core data processing engine for the ETL pipeline.
    Responsible for ingesting the raw CSV file, applying the validation rules to each row,
    and routing the data into 'valid' or 'invalid' datasets based on the results.
    """

    @staticmethod
    def process_cdr_file(input_file_path, valid_file_path, invalid_file_path):
        """
        Processes the CDR dataset in a streaming fashion to optimize memory usage.
        
        Args:
            input_file_path (str): The path to the raw dataset to be validated.
            valid_file_path (str): The destination path for records that pass all checks.
            invalid_file_path (str): The destination path for records that fail one or more checks.
        """
        # Define the expected schema (column names) for the CDR dataset
        fieldnames = [
            'msisdn', 'imsi', 'imei', 'call_type', 'duration', 'timestamp',
            'called_number', 'call_status', 'cell_id', 'call_direction'
        ]

        try:
            # Use Context Managers (with open) to safely handle file I/O operations.
            # 'newline=""' is used with CSV modules to prevent extra blank lines in Windows environments.
            with open(input_file_path, mode='r', encoding='utf-8') as infile,\
                 open(valid_file_path, mode='w', encoding='utf-8', newline='') as valid_file,\
                 open(invalid_file_path, mode='w', encoding='utf-8', newline='') as invalid_file:

                # Initialize dictionary-based CSV reader and writers for easier column referencing
                reader = csv.DictReader(infile)
                valid_writer = csv.DictWriter(valid_file, fieldnames=fieldnames)
                invalid_writer = csv.DictWriter(invalid_file, fieldnames=fieldnames)            

                # Write the column headers to both output files before processing rows
                valid_writer.writeheader()
                invalid_writer.writeheader()

                # Initialize metrics counters for the execution report
                processed_count = 0
                valid_count = 0
                invalid_count = 0

                # Iterate through the file row-by-row (streaming) instead of loading all into RAM
                for row in reader:
                    processed_count += 1

                    # Apply specific validation rules to each field extracted via dict get()
                    v_msisdn = DataValidator.is_valid_msisdn(row.get('msisdn'))
                    v_imsi = DataValidator.is_valid_imsi(row.get('imsi'))
                    v_imei = DataValidator.is_valid_imei(row.get('imei'))
                    v_type = DataValidator.is_valid_call_type(row.get('call_type'))
                    v_duration = DataValidator.is_valid_call_duration(row.get('duration'))
                    v_time = DataValidator.is_valid_timestamp(row.get('timestamp'))
                    v_called = DataValidator.is_valid_called_number(row.get('called_number'))
                    v_status = DataValidator.is_valid_call_status(row.get('call_status'))
                    v_cell = DataValidator.is_valid_cell_id(row.get('cell_id'))
                    v_dir = DataValidator.is_valid_call_direction(row.get('call_direction'))

                    # Aggregating validation results: The row is valid ONLY if all field checks return True
                    is_row_valid = all([
                        v_msisdn, v_imsi, v_imei, v_type, v_duration, 
                        v_time, v_called, v_status, v_cell, v_dir 
                    ])

                    # Route the row to the corresponding file based on the aggregation result
                    if is_row_valid:
                        valid_writer.writerow(row)
                        valid_count += 1
                    else:
                        invalid_writer.writerow(row)
                        invalid_count += 1

                # Print pipeline execution metrics to the console upon successful completion
                print(f"--- Data Processing Complete ---")
                print(f"Total Rows Processed: {processed_count}")
                print(f"Valid Records: {valid_count}")
                print(f"Invalid Records: {invalid_count}")

        # Gracefully handle the case where the Data Generator hasn't created the raw file yet
        except FileNotFoundError:
            error_msg = f"Error: The input file was not found at {input_file_path}"
            print(error_msg)
            LoggerManager.get_logger().error(error_msg)

        # Catch-all exception block to prevent hard crashes and ensure the error is logged
        except Exception as e:
            error_msg = f"An unexpected error occurred during processing: {e}"
            print(error_msg)
            LoggerManager.get_logger().error(error_msg)            

# ---------------------------------------------------------
# Main Execution Block
# ---------------------------------------------------------
if __name__ == "__main__":
    
    # Resolve file paths centrally utilizing variables from the Data Generator script
    INPUT_FILE = OUTPUT_FILE
    
    # Construct absolute paths for the output files to reside in the same datasets directory
    VALID_FILE = os.path.join(OUTPUT_DIR, "valid_cdr_data.csv")
    INVALID_FILE = os.path.join(OUTPUT_DIR, "invalid_cdr_data.csv")

    print("Starting data validation process. This might take a moment...")

    # Trigger the core processing pipeline
    DataProcessor.process_cdr_file(INPUT_FILE, VALID_FILE, INVALID_FILE)

    print("Validation process completed. Check your output files and the logs.")
