/*
======================================================================================
Project Name : Telecom Data Warehouse Pipeline
Architecture : 3-Tier Medallion Architecture (Bronze -> Silver -> Gold)
Environment  : SQL Server (T-SQL)
Description  : Physical database schema setup and dimensional modeling for Telecom CDR 
               (Call Detail Record) analytics.
               - BRONZE : Raw, untyped data directly from source systems.
               - SILVER : Cleansed, strongly-typed data with enforced business rules.
               - GOLD   : Star schema optimized for BI reporting and aggregations.
======================================================================================
*/

USE master;
GO

-- ===================================================================================
-- 1. DATABASE SETUP
-- Description: Drop existing database to ensure a clean state, then recreate it.
-- ===================================================================================

IF EXISTS (SELECT 1 FROM sys.databases WHERE name ='Telecom_DW')
BEGIN
    -- Force disconnect all active connections before dropping to prevent locks
	ALTER DATABASE Telecom_DW SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
	DROP DATABASE Telecom_DW;
END;
GO

CREATE DATABASE Telecom_DW;
GO

USE Telecom_DW;
GO


-- ===================================================================================
-- 2. SCHEMA CREATION
-- Description: Organizing tables logically into Medallion architectural layers.
-- ===================================================================================

CREATE SCHEMA Bronze;
GO

CREATE SCHEMA Silver;
GO

CREATE SCHEMA Gold;
GO


-- ===================================================================================
-- 3. BRONZE LAYER: Raw Data Ingestion
-- Description: Stores data exactly as received from the source file. All columns are 
--              set to VARCHAR to prevent ingestion failures due to type mismatches.
-- ===================================================================================

IF OBJECT_ID ('Bronze.CDR_Raw','U') IS NOT NULL
	DROP TABLE Bronze.CDR_Raw;
GO

CREATE TABLE Bronze.CDR_Raw (
	msisdn            VARCHAR(50),  -- Source caller number
	imsi              VARCHAR(50),  -- Source SIM card ID 
	imei              VARCHAR(50),  -- Source Device ID 
	call_type         VARCHAR(50),  -- Event type (Voice, SMS, Data)
	duration          VARCHAR(50),  -- Raw duration value
	time_stamp        VARCHAR(50),  -- Raw timestamp string
    called_number     VARCHAR(50),  -- Source receiver number 
    call_status       VARCHAR(50),  -- Event status (Success, Failed, etc.)
    cell_id           VARCHAR(50),  -- Raw Cell tower ID 
    call_direction    VARCHAR(50)   -- Event direction (Inbound, Outbound)
);
GO


-- ===================================================================================
-- 4. SILVER LAYER: Cleansed and Standardized Data
-- Description: Data is cast to target data types, source columns are mapped to 
--              standardized business terms, and metrics (SMS/Data) are separated.
-- ===================================================================================

IF OBJECT_ID('Silver.CDR_Cleaned','U') IS NOT NULL
    DROP TABLE Silver.CDR_Cleaned;
GO

CREATE TABLE Silver.CDR_Cleaned (
	caller_number      VARCHAR(50), -- Mapped from: msisdn
	sim_id             VARCHAR(50), -- Mapped from: imsi
	device_id          VARCHAR(50), -- Mapped from: imei
	call_type          VARCHAR(50), 
    call_status        VARCHAR(50), 
    call_direction     VARCHAR(50), 
    called_number      VARCHAR(50), 
    cell_tower_id      VARCHAR(50), -- Mapped from: cell_id
    call_start_time    DATETIME,    -- Mapped from: time_stamp & casted
    call_year          INT,         -- Time Dimension: Year
    call_month         INT,         -- Time Dimension: Month
    call_day           INT,         -- Time Dimension: Day
    call_hour          INT,         -- Time Dimension: Hour
    call_duration      INT,         -- Metric: Voice duration (Seconds)
    data_volume_mb     INT,         -- Metric: Data usage (MB)
    sms_count          INT          -- Metric: SMS count (Based on 160-char rule)
);
GO


-- ===================================================================================
-- 5. GOLD LAYER: Dimensional Modeling (Star Schema)
-- Description: Optimized for fast analytical queries. Contains Dimension tables 
--              (descriptive attributes) and a Fact table (measurable metrics).
-- ===================================================================================

/*
--------------------------------------------------------------------------------------
Table: Gold.Dim_Subscriber
Type : Dimension
Grain: One row per unique caller (Subscriber).
--------------------------------------------------------------------------------------
*/
IF OBJECT_ID('Gold.Dim_Subscriber','U') IS NOT NULL
    DROP TABLE Gold.Dim_Subscriber;
GO

CREATE TABLE Gold.Dim_Subscriber (
    subscriber_id      INT IDENTITY(1,1) PRIMARY KEY, -- Surrogate Key
    caller_number      VARCHAR(50),                   -- Natural/Business Key
	sim_id             VARCHAR(50)                    -- Subscriber SIM detail
);
GO


/*
--------------------------------------------------------------------------------------
Table: Gold.Dim_Service
Type : Dimension
Grain: One row per unique combination of Call Type, Status, and Direction.
--------------------------------------------------------------------------------------
*/
IF OBJECT_ID('Gold.Dim_Service','U') IS NOT NULL
    DROP TABLE Gold.Dim_Service;
GO

CREATE TABLE Gold.Dim_Service (
    service_id         INT IDENTITY(1,1) PRIMARY KEY, -- Surrogate Key
    call_type          VARCHAR(50),                   -- e.g., Voice, Data, SMS
    call_status        VARCHAR(50),                   -- e.g., Success, Failed
    call_direction     VARCHAR(50)                    -- e.g., Inbound, Outbound
);
GO


/*
--------------------------------------------------------------------------------------
Table: Gold.Fact_CDR
Type : Transactional Fact Table
Grain: One row per individual network event/transaction (Call/SMS/Data session).
--------------------------------------------------------------------------------------
*/
IF OBJECT_ID('Gold.Fact_CDR','U') IS NOT NULL
    DROP TABLE Gold.Fact_CDR;
GO

CREATE TABLE Gold.Fact_CDR (
    -- ==========================================
    -- Foreign Keys (Dimension Links)
    -- ==========================================
    subscriber_id            INT FOREIGN KEY REFERENCES Gold.Dim_Subscriber(subscriber_id),
    service_id               INT FOREIGN KEY REFERENCES Gold.Dim_Service(service_id),
    
    -- ==========================================
    -- Degenerate Dimensions (Attributes without a standalone Dim table)
    -- ==========================================
    device_id                VARCHAR(50), 
    called_number            VARCHAR(50), 
    cell_tower_id            VARCHAR(50), 
    exact_call_start_time    DATETIME, 
    
    -- ==========================================
    -- Time Dimensions (Derived for partitioning and BI filters)
    -- ==========================================
    call_year                INT,
    call_month               INT,
    call_day                 INT,
    call_hour                INT,
    
    -- ==========================================
    -- Measures / Facts (Aggregatable Metrics)
    -- ==========================================
    call_duration            INT,
    data_volume_mb           INT,
    sms_count                INT
);
GO
