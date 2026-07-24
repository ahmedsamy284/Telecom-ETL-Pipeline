/*
======================================================================================
Project: Telecom Data Warehouse (Medallion Architecture)
Description: This script sets up the physical database schema for a Telecom ETL pipeline.
             It implements a 3-tier Medallion architecture:
             - Bronze: Raw data ingestion.
             - Silver: Cleansed, standardized, and enriched data.
             - Gold: Star schema for analytical queries.
======================================================================================
*/

USE master;
GO

-- ===================================================================================
-- 1. Database Setup: Drop existing database to ensure a clean slate, then recreate it
-- ===================================================================================

-- Drop and Recreate the 'Telecom_DW' Database (if it exists)
IF EXISTS (SELECT 1 FROM sys.databases WHERE name ='Telecom_DW')
BEGIN
    -- Force disconnect all active connections before dropping
	ALTER DATABASE Telecom_DW SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
	DROP DATABASE Telecom_DW;
END;
GO

-- Create the new 'Telecom_DW' database
 CREATE DATABASE Telecom_DW;
 GO

 USE Telecom_DW;
 GO


-- ===================================================================================
-- 2. Schema Creation: Organizing tables into Medallion layers
-- ===================================================================================

 Create Schema Bronze;
 GO

 Create Schema Silver;
 GO

 Create Schema Gold;
 GO


-- ===================================================================================
-- 3. BRONZE LAYER: Raw Data Ingestion
-- Description: Stores data exactly as received from the source CSV.
-- All columns are string types to prevent ingestion failures due to type mismatch.
-- ===================================================================================

 IF OBJECT_ID ('Bronze.CDR_Raw','U') IS NOT NULL
	DROP TABLE Bronze.CDR_Raw;
GO

CREATE TABLE Bronze.CDR_Raw (
	msisdn            VARCHAR(50),  -- Caller number (Raw)
	imsi              VARCHAR(50),  -- SIM card ID (Raw)
	imei              VARCHAR(50),  -- Device ID (Raw)
	call_type         VARCHAR(50),  -- Type of call (e.g., Voice, SMS, Data)
	duration     VARCHAR(50),  -- Duration of call (Raw string)
	time_stamp        VARCHAR(50), -- Call start time (Raw string)
    called_number     VARCHAR(50),  -- Receiver number (Raw)
    call_status       VARCHAR(50),  -- Status (e.g., Success, Failed)
    cell_id           VARCHAR(50),  -- Cell tower ID (Raw)
    call_direction    VARCHAR(50)   -- Direction (e.g., Inbound, Outbound)
);
GO


-- ===================================================================================
-- 4. SILVER LAYER: Cleansed and Standardized Data
-- Description: Data is cast to appropriate data types, column names are standardized 
-- to business terms, and the timestamp is derived into separate date/time parts.
-- ===================================================================================

IF OBJECT_ID('Silver.CDR_Cleaned','U') IS NOT NULL
    DROP TABLE Silver.CDR_Cleaned;
GO

CREATE TABLE Silver.CDR_Cleaned (
	caller_number      VARCHAR(50), -- Standardized from msisdn
	sim_id             VARCHAR(50), -- Standardized from imsi
	device_id          VARCHAR(50), -- Standardized from imei
	call_type          VARCHAR(50),
    call_status        VARCHAR(50),
    call_direction     VARCHAR(50),
    called_number      VARCHAR(50), 
    cell_tower_id      VARCHAR(50), -- Standardized from cell_id (Kept as VARCHAR to preserve integrity)
    call_start_time    DATETIME,    -- Standardized from time_stamp and cast to DATETIME
    call_year          INT,         -- Extracted from call_start_time
    call_month         INT,         -- Extracted from call_start_time
    call_day           INT,         -- Extracted from call_start_time
    call_hour          INT,         -- Extracted from call_start_time
    call_duration      INT          -- Cast to INT for aggregation
);
GO


-- ===================================================================================
-- 5. GOLD LAYER: Dimensional Modeling (Star Schema)
-- Description: Optimized for fast analytical queries. Contains Dimension tables 
-- (descriptive attributes) and a Fact table (measurable metrics).
-- ===================================================================================

-- 5.1 Dimension Table: Subscriber
-- Stores information related to the user making the call
IF OBJECT_ID('Gold.Dim_Subscriber','U') IS NOT NULL
    DROP TABLE Gold.Dim_Subscriber;
GO

CREATE TABLE Gold.Dim_Subscriber (
    subscriber_id      INT IDENTITY(1,1) PRIMARY KEY, -- Surrogate Key
    caller_number      VARCHAR(50),                   -- Natural Key
	sim_id             VARCHAR(50)
);
GO


-- 5.2 Dimension Table: Service
-- Stores information related to the service configuration of the call
IF OBJECT_ID('Gold.Dim_Service','U') IS NOT NULL
    DROP TABLE Gold.Dim_Service;
GO

CREATE TABLE Gold.Dim_Service (
    service_id         INT IDENTITY(1,1) PRIMARY KEY, -- Surrogate Key
    call_type          VARCHAR(50),
    call_status        VARCHAR(50),
    call_direction     VARCHAR(50)
);
GO


-- 5.3 Fact Table: Call Detail Records (CDR)
-- Stores the quantitative data and foreign keys connecting to dimensions
IF OBJECT_ID('Gold.Fact_CDR','U') IS NOT NULL
    DROP TABLE Gold.Fact_CDR;
GO

CREATE TABLE Gold.Fact_CDR (
    -- Foreign Keys representing relationships to Dimension tables
    subscriber_id            INT FOREIGN KEY REFERENCES Gold.Dim_Subscriber(subscriber_id),
    service_id               INT FOREIGN KEY REFERENCES Gold.Dim_Service(service_id),
    
    -- Degenerate Dimensions (attributes left in the fact table without a separate dim table)
    device_id                VARCHAR(50), 
    called_number            VARCHAR(50), 
    cell_tower_id            VARCHAR(50), 
    exact_call_start_time    DATETIME, 
    
    -- Derived Date/Time parts for fast querying
    call_year                INT,
    call_month               INT,
    call_day                 INT,
    call_hour                INT,
    
    -- Measure / Metric
    call_duration            INT
);
GO
