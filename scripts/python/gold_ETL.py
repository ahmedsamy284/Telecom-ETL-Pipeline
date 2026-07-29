"""
Gold Layer ETL Module for Telecom Data Warehouse.

This script is responsible for the final stage of the Medallion architecture (Gold Layer).
It extracts cleaned data from the Silver layer, processes it into a Star Schema format
by generating dimension tables (Dim_Subscriber, Dim_Service) and a fact table (Fact_CDR),
and loads the final modeled data into the SQL Server database.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
from load_bronze_layer import LoggerManager

# Setup dynamic paths for the script execution and logging
current_directory = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_directory, "gold_ETL.log")

# Initialize the custom logger for tracking the Gold layer events
logger = LoggerManager.get_logger(log_path=log_path)

def run_gold_layer():
    """
    Executes the ETL process to populate the Gold Layer (Star Schema).

    Steps performed:
    1. Establishes a connection to the SQL Server database.
    2. Clears existing data in the Gold layer to ensure idempotency (Full Load approach).
    3. Extracts the cleaned Call Detail Records (CDR) from the Silver layer.
    4. Isolates, deduplicates, and loads data into Dimension tables to generate Surrogate Keys.
    5. Retrieves the newly generated Surrogate Keys from the database.
    6. Merges the Surrogate Keys back into the main dataset.
    7. Filters and loads the final aggregatable metrics and foreign keys into the Fact table.

    Raises:
        Exception: If any database connection, transformation, or loading error occurs, 
                   the execution is halted and the error is logged.
    """
    logger.info(f"Starting Gold layer ETL Process....")

    # Database configuration parameters
    server_name = r"DESKTOP-93EA6VA\SQLEXPRESS"
    database_name = "Telecom_DW"

    logger.info("Connecting to SQL Server....")
    
    # Define the ODBC connection string
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_name};"
        f"DATABASE={database_name};"
        f"Trusted_Connection=yes;"
    )
            
    # Safely parse connection string and create SQLAlchemy engine
    # urllib.parse.quote_plus is used to escape special characters in the connection string
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
    try:
        # Note: Keeping the original log message string as requested, 
        # though this step is preparing extraction from the Silver layer.
        logger.info(f"Starting data Extraction from Bronze layer....")    

        # ---------------------------------------------------------
        # STEP 1: Ensure Idempotency (Clear existing Gold data)
        # ---------------------------------------------------------
        # Deleting from the Fact table first to respect Foreign Key constraints,
        # then deleting from the Dimension tables.
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM Gold.Fact_CDR"))
            conn.execute(text("DELETE FROM Gold.Dim_Subscriber"))
            conn.execute(text("DELETE FROM Gold.Dim_Service"))

            # Reset the Identity seed for dimension tables to 0.
            # This ensures that Surrogate Keys (IDs) start fresh from 1 upon reloading, 
            # preventing large ID gaps caused by the DELETE operations.
            conn.execute(text("DBCC CHECKIDENT ('Gold.Dim_Subscriber', RESEED, 0)"))
            conn.execute(text("DBCC CHECKIDENT ('Gold.Dim_Service', RESEED, 0)"))
            

        # ---------------------------------------------------------
        # STEP 2: Extract Data from Silver Layer
        # ---------------------------------------------------------
        logger.info(f"Extracting Cleaned data from Silver.CDR_Cleaned.....")

        # Pull the entirely cleaned dataset into a Pandas DataFrame
        silver_query = "SELECT * FROM Silver.CDR_Cleaned"
        silver_df = pd.read_sql(silver_query, engine)

        logger.info(f"Successfully extracted {len(silver_df)} rows from Silver layer.")

        # ---------------------------------------------------------
        # STEP 3: Process and Load Dim_Subscriber
        # ---------------------------------------------------------
        logger.info(f"Processing and Loading Gold.Dim_Subscriber.....")

        # Extract unique subscribers and load them to the DB to generate IDENTITY IDs
        dim_sub_raw = silver_df[["caller_number", "sim_id"]].drop_duplicates()
        dim_sub_raw.to_sql(
            "Dim_Subscriber", 
            schema="Gold", 
            con=engine, 
            if_exists="append", 
            index=False
        )
        
        # Read back from the DB to retrieve the auto-generated 'subscriber_id' (Surrogate Key)
        dim_sub_db = pd.read_sql("SELECT subscriber_id, caller_number, sim_id FROM Gold.Dim_Subscriber", engine)

        # ---------------------------------------------------------
        # STEP 4: Process and Load Dim_Service
        # ---------------------------------------------------------
        logger.info(f"Processing and Loading Gold.Dim_Service.....")        
        
        # Extract unique service combinations and load them to generate IDENTITY IDs
        dim_srv_raw = silver_df[["call_type", "call_status", "call_direction"]].drop_duplicates()
        dim_srv_raw.to_sql(
            "Dim_Service", 
            schema="Gold", 
            con=engine, 
            if_exists="append", 
            index=False
        )
        
        # Read back from the DB to retrieve the auto-generated 'service_id' (Surrogate Key)
        dim_srv_db = pd.read_sql("SELECT service_id, call_type, call_status, call_direction FROM Gold.Dim_Service", engine)

        # ---------------------------------------------------------
        # STEP 5: Merge Surrogate Keys to create Fact Table data
        # ---------------------------------------------------------
        logger.info(f"Merging Dimensions with Silver Data to create Fact_CDR.....")  

        # Perform a left join to map the new 'subscriber_id' to the main dataset
        fact_df = pd.merge(
            silver_df, dim_sub_db, 
            on=["caller_number", "sim_id"], 
            how="left"
        )
        
        # Perform a left join to map the new 'service_id' to the main dataset
        fact_df = pd.merge(
            fact_df, dim_srv_db, 
            on=["call_type", "call_status", "call_direction"], 
            how="left"
        ) 
        
        # ---------------------------------------------------------
        # STEP 6: Load Data into Fact_CDR
        # ---------------------------------------------------------
        logger.info(f"Loading Data into Gold.Fact_CDR.....")
        
        # Select strictly the columns defined in the Star Schema DDL
        fact_columns = [
            "subscriber_id", "service_id", "device_id", "called_number",
            "cell_tower_id", "call_start_time", "call_year", "call_month",
            "call_day", "call_hour", "call_duration", "data_volume_mb", "sms_count"
        ] 

        final_fact_df = fact_df[fact_columns]
        
        # Append the finalized fact data to SQL Server
        final_fact_df.to_sql(
            "Fact_CDR", 
            schema="Gold",
            con=engine,
            if_exists="append",
            index=False
        )

        logger.info(f"Successfully loaded {len(final_fact_df)} rows into Gold.Fact_CDR.")

    except Exception as e:
        # Catch, log, and re-raise any critical failure during the ETL pipeline
        logger.error(f"Error during Gold Layer ETL: {e}")
        raise

    print(f"Success => Data is now structured in the Gold Layer (Star Schema).")


if __name__ == "__main__":
    run_gold_layer()
