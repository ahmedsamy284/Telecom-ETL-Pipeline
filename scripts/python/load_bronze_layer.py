"""
==========================================
Telecom ETL Pipeline - Bronze Layer Loader
==========================================

This script is responsible for loading validated Call Detail Record (CDR) 
data from a local CSV file into the Bronze layer of the Telecom Data Warehouse 
(SQL Server). It utilizes pandas for data manipulation, SQLAlchemy for 
database connectivity, and a custom LoggerManager for execution tracking.
"""

import os
import pandas as pd
from sqlalchemy import create_engine
import urllib
import logging 

# Define dynamic paths for the current directory and the log file
current_directory = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_directory, "load_to_bronze.log")


class LoggerManager:
    """
    A utility class to manage and configure centralized logging for the ETL process.
    """

    @staticmethod
    def get_logger(log_path=log_path):
        """
        Configures and returns a custom logger instance.

        Args:
            log_path (str): The absolute path where the log file will be saved.
                            Defaults to 'load_to_bronze.log' in the current directory.

        Returns:
            logging.Logger: Configured logger object ready to record events.
        """
        logging.basicConfig(
            filename=log_path,
            filemode="a", # Append mode to keep previous execution logs intact
            encoding="utf-8",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S"
        )
        return logging.getLogger()


def load_data_to_bronze(csv_file_path, server_name, database_name):
    """
    Reads validated CSV data, handles schema mapping, and loads it 
    into the Bronze.CDR_Raw table in SQL Server.

    Args:
        csv_file_path (str): The absolute path to the validated CSV data file.
        server_name (str): The SQL Server instance name.
        database_name (str): The target database name (e.g., Telecom_DW).
    """
    # Initialize the logger
    logger = LoggerManager.get_logger()
    
    try:
        logger.info("Starting the load process to Bronze Layer....")

        # 1. Data Extraction
        logger.info(f"Reading data from: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        # Convert all columns to string to match the SQL Server VARCHAR data types
        df = df.astype(str)

        # 2. Schema Mapping (Transformation)
        # Rename 'timestamp' to 'time_stamp' to resolve SQL Server schema mismatch
        df.rename(columns={"timestamp": "time_stamp"}, inplace=True)

        # 3. Database Connection
        logger.info("Connecting to SQL Server....")
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server_name};"
            f"DATABASE={database_name};"
            f"Trusted_Connection=yes;"
        )

        # Parse the connection string for SQLAlchemy
        params = urllib.parse.quote_plus(connection_string)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

        # 4. Data Loading
        logger.info("Loading data into Bronze.CDR_Raw table....")
        # Truncate the table to remove old data before appending the new batch.
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE Bronze.CDR_Raw"))
            
        df.to_sql(
            name="CDR_Raw",
            schema="Bronze",
            con=engine,
            if_exists="append", # Append to existing table without dropping it
            index=False         # Exclude pandas dataframe index from being inserted
        )

        logger.info("Data loaded successfully to Bronze Layer.")
        print("Success => Data is now in the Bronze Layer.")

    except Exception as e:
        # Catch and log any errors that occur during the ETL process
        logger.error(f"Error during loading data: {e}")
        print("An error occurred! \nPlease check the load_to_bronze.log file.")


if __name__ =="__main__":
    
    # Define configuration parameters for the execution block
    VALID_DATA_FILE = r"D:\datasets\valid_cdr_data.csv"
    SQL_SERVER_NAME = r"DESKTOP-93EA6VA\SQLEXPRESS"
    DB_NAME = "Telecom_DW"

    # Trigger the load process
    load_data_to_bronze(VALID_DATA_FILE, SQL_SERVER_NAME, DB_NAME)

