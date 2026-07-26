"""
Silver Layer ETL Pipeline - Telecom Data Warehouse.

This script extracts raw CDR (Call Detail Record) data from the Bronze layer,
performs data cleaning, transformation, and business logic application,
and loads the structured data into the Silver layer (CDR_Cleaned).
"""

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import urllib
from load_bronze_layer import LoggerManager

# Set up logging configuration for the Silver layer
current_directory = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_directory, "silver_ETL.log")

logger = LoggerManager.get_logger(log_path=log_path)


def run_silver_layer():
    """
    Executes the end-to-end ETL process for the Silver layer.
    
    Steps:
    1. Extract: Reads raw data from 'BRONZE.CDR_Raw' via SQL Server.
    2. Transform: 
        - Removes duplicates to ensure data quality.
        - Maps column names to match the target database schema.
        - Parses date/time and extracts dimensions (year, month, day, hour).
        - Applies business rules to isolate Voice duration, Data volume, and SMS count.
    3. Load: Truncates the existing target table and appends the cleaned data
       to 'Silver.CDR_Cleaned' for idempotency.
       
    Raises:
        Exception: Propagates any SQL or pandas exceptions after logging them.
    """
    logger.info("Starting Silver layer ETL Process....")

    # =========================================================================
    # DATABASE CONNECTION
    # =========================================================================
    server_name = r"DESKTOP-93EA6VA\SQLEXPRESS"
    database_name = "Telecom_DW"

    logger.info("Connecting to SQL Server....")
    
    # Construct the ODBC connection string
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_name};"
        f"DATABASE={database_name};"
        f"Trusted_Connection=yes;"
    )
            
    # Safely parse connection string and create SQLAlchemy engine
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # =========================================================================
    # 1. EXTRACTION PHASE
    # =========================================================================
    logger.info("Starting data Extraction from Bronze layer....")
    try:
        # Retrieve all records from the raw bronze table
        query = f"SELECT * FROM BRONZE.CDR_Raw"
        df = pd.read_sql(query, engine)
        logger.info(f"Successfully extracted {len(df)} rows from BRONZE.CDR_Raw.")

    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise

    # =========================================================================
    # 2. TRANSFORMATION PHASE
    # =========================================================================
    logger.info(f"Starting data tansformation and cleaning....")

    try:
        # Remove duplicate records
        df.drop_duplicates(inplace=True)

        # Map DataFrame columns to exactly match the SQL Server Silver table schema
        df.rename(columns={
            "msisdn": "caller_number",
            "imsi": "sim_id",
            "imei": "device_id",
            "cell_id": "cell_tower_id",
            "duration": "call_duration",
            "time_stamp": "call_start_time"
            }, inplace=True)

        # Standardize the timestamp column and drop records with invalid dates
        df["call_start_time"] = pd.to_datetime(df["call_start_time"], errors="coerce")
        df.dropna(subset=["call_start_time"], inplace=True)

        # Extract time-based dimensions for easier aggregation in the Gold layer
        df["call_year"] = df["call_start_time"].dt.year.astype(int)
        df["call_month"] = df["call_start_time"].dt.month.astype(int)
        df["call_day"] = df["call_start_time"].dt.day.astype(int)
        df["call_hour"] = df["call_start_time"].dt.hour.astype(int)    

        # Initialize base columns for separated metrics
        df["data_volume_mb"] = 0
        df["sms_count"] = 0

        # Business Rule 1: Handle "Data" events
        # If call_type is 'data', the original duration represents data volume
        df["data_volume_mb"] = np.where(
            df["call_type"].str.lower() == "data",
            df["call_duration"],
            df["data_volume_mb"]
        )
        # Data sessions don't have a receiving party, so mask the called_number
        df.loc[df["call_type"].str.lower() == "data", "called_number"] = "Unavailable"
        
        # Ensure duration is treated as a numeric value for subsequent calculations
        df["call_duration"] = pd.to_numeric(df["call_duration"], errors="coerce")

        # Business Rule 2: Handle "SMS" events
        # Assume 1 standard SMS is 160 characters. Default to 1 if duration is less than 160.
        calculated_sms = (df["call_duration"] // 160).astype(int)
        df["sms_count"] = np.where(
            df["call_type"].str.lower() == "sms",
            np.where(calculated_sms > 0, calculated_sms, 1), 
            df["sms_count"]
        )

        # Business Rule 3: Handle "Voice" events
        # Isolate call duration to only apply to voice calls; zero out for Data/SMS
        df["call_duration"] = np.where(df["call_type"].str.lower() != "voice", 0, df["call_duration"])

        # Fill any remaining NULLs resulting from conversions and cast metrics to integer
        columns_to_fill = ["call_duration", "data_volume_mb", "sms_count"]
        df[columns_to_fill] = df[columns_to_fill].fillna(0)

        for col in columns_to_fill:
            df[col] = df[col].astype(int)

    except Exception as e:
        logger.error(f"Error during data tansformation and cleaning: {e}")
        raise

    # =========================================================================
    # 3. LOADING PHASE
    # =========================================================================
    logger.info(f"Loading cleaned data into Silver.CDR_Cleaned....")
    try:
        # Use TRUNCATE before appending to ensure an idempotent load operation
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE Silver.CDR_Cleaned"))
            logger.info(f"Existing data in Silver.CDR_Cleaned has been truncated.")

        # Load the cleaned dataset into the SQL Server database
        df.to_sql(
                name="CDR_Cleaned",
                schema="Silver",
                con=engine,
                if_exists="append", 
                index=False         
            )

        logger.info(f"Data Successfully loaded into Silver layer without duplicates.")
        
    except Exception as e:
        logger.error(f"Error loading data to database: {e}")
        raise

    print("Success => Data is now in the Silver Layer.")


# Standard boilerplate to protect execution during module import (e.g., via Airflow)
if __name__ == "__main__":
    run_silver_layer()
