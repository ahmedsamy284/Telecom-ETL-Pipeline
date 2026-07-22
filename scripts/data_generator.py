import csv
import random
import os
from datetime import datetime, timedelta

# ---------------------------------------------------------
# Path Configuration (Using Absolute Paths)
# ---------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'datasets')

os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'cdr_data_1M.csv')

# ---------------------------------------------------------
# File configurations
# ---------------------------------------------------------
NUM_ROWS = 1_000_000
ERROR_RATE = 0.01  # 1% error rate per column

# Constants matching the validation pipeline exact rules
CALL_TYPES = ['Voice', 'SMS', 'Data']
CALL_STATUSES = ['ANSWERED', 'MISSED', 'FAILED', 'DROPPED']
CALL_DIRECTIONS = ['INCOMING', 'OUTGOING', 'FORWARDED'] 
PREFIXES = ['010', '011', '012', '015']

def generate_phone_number(is_valid=True):
    """Generates an 11-digit MSISDN/Phone Number."""
    if is_valid:
        return random.choice(PREFIXES) + ''.join([str(random.randint(0, 9)) for _ in range(8)])
    else:
        # Invalid numbers for regex testing (letters, too long, or wrong prefix)
        return random.choice(['01912345678', '01012345A98', '12345'])

def generate_imsi(is_valid=True):
    """Generates a 15-digit IMSI number."""
    if is_valid:
        # Starting with 602 for Egypt for realism
        return '602' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
    else:
        return '602' + ''.join([str(random.randint(0, 9)) for _ in range(5)]) # Invalid length

def generate_imei(is_valid=True):
    """Generates a 15-digit IMEI number."""
    if is_valid:
        return ''.join([str(random.randint(0, 9)) for _ in range(15)])
    else:
        return ''.join([str(random.randint(0, 9)) for _ in range(10)]) + 'ABCDE' # Invalid alphanumeric

def generate_timestamp(is_valid=True):
    """Generates a combined Date and Time string."""
    start = datetime(2026, 1, 1)
    random_days = random.randint(0, 180)
    random_seconds = random.randint(0, 86400)
    dt = start + timedelta(days=random_days, seconds=random_seconds)
    
    if is_valid:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Invalid format to trigger validation failure
        return dt.strftime('%Y/%m/%d') 

def generate_cell_id(is_valid=True):
    """Generates a Cell ID (5 to 7 digits for valid records)."""
    if is_valid:
        return str(random.randint(10000, 9999999))
    else:
        # Invalid: Too short, too long, or contains characters
        return random.choice([
            str(random.randint(10, 999)),             # 2-3 digits
            str(random.randint(10000000, 999999999)), # 8-9 digits
            "CELL_ERR"                                # Letters
        ])

def generate_cdr_data():
    """
    Main function to generate mock CDR data with an independent 1% error rate per column.
    """
    print(f"Starting data generation for {NUM_ROWS} rows...")
    print(f"Output file will be saved at: {OUTPUT_FILE}")
    
    # Enforcing UTF-8 encoding
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write exact 10-column CSV header
        writer.writerow([
            'msisdn', 'imsi', 'imei', 'call_type', 'duration', 
            'timestamp', 'called_number', 'call_status', 'cell_id', 'call_direction'
        ])

        for i in range(1, NUM_ROWS + 1):
            
            # Applying 1% error rate independently to each column
            msisdn = generate_phone_number(random.random() > ERROR_RATE)
            imsi = generate_imsi(random.random() > ERROR_RATE)
            imei = generate_imei(random.random() > ERROR_RATE)
            
            # 1% chance for invalid categorical values
            call_type = random.choice(CALL_TYPES) if random.random() > ERROR_RATE else "INVALID_TYPE"
            call_status = random.choice(CALL_STATUSES) if random.random() > ERROR_RATE else "UNKNOWN_STAT"
            call_direction = random.choice(CALL_DIRECTIONS) if random.random() > ERROR_RATE else "WRONG_DIR"
            
            # 1% chance for invalid duration (Negative duration)
            if random.random() > ERROR_RATE:
                duration = random.randint(10, 3600)
            else:
                duration = random.randint(-100, -1) 
                
            timestamp = generate_timestamp(random.random() > ERROR_RATE)
            called_number = generate_phone_number(random.random() > ERROR_RATE)
            cell_id = generate_cell_id(random.random() > ERROR_RATE)

            # Write row to CSV
            writer.writerow([
                msisdn, imsi, imei, call_type, duration,
                timestamp, called_number, call_status, cell_id, call_direction
            ])
            
            # Print progress every 100,000 rows
            if i % 100_000 == 0:
                print(f"{i} rows generated...")

    print("Data generation completed successfully!")

if __name__ == '__main__':
    generate_cdr_data()
