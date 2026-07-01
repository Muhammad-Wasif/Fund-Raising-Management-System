import os
import pandas as pd
from datetime import datetime

data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)

# Campaigns
campaigns = pd.DataFrame([
    {'id': 'CMP10001', 'state': 'Sindh', 'region': 'Sindh', 'type': 'Education', 'target': 5000.0, 'raised': 1500.0, 'description': 'Build a new school', 'project_name': 'Sindh Education Initiative', 'admin': 'admin123', 'created': '2025-01-01 10:00:00', 'status': 'Active'},
    {'id': 'CMP10002', 'state': 'Punjab', 'region': 'Punjab', 'type': 'Health', 'target': 10000.0, 'raised': 10000.0, 'description': 'Medical supplies for local hospital', 'project_name': 'Lahore Health Drive', 'admin': 'admin123', 'created': '2025-02-01 11:30:00', 'status': 'Completed'},
    {'id': 'CMP10003', 'state': 'KPK', 'region': 'KPK', 'type': 'Infrastructure', 'target': 25000.0, 'raised': 500.0, 'description': 'Clean water wells', 'project_name': 'Peshawar Clean Water', 'admin': 'admin123', 'created': '2025-03-15 09:15:00', 'status': 'Active'}
])
campaigns.to_csv(os.path.join(data_dir, 'campaigns.csv'), index=False)

# Funders
funders = pd.DataFrame([
    {'cnic': '1234567890123', 'username': 'funder123'},
    {'cnic': '9876543210987', 'username': 'funder456'}
])
funders.to_csv(os.path.join(data_dir, 'funders.csv'), index=False)

# Donations
donations = pd.DataFrame([
    {'donation_id': 'DON20001', 'invoice_id': 'INV30001', 'challan_id': 'CH40001', 'campaign_id': 'CMP10001', 'funder_cnic': '1234567890123', 'funder_user': 'funder123', 'amount': 1000.0, 'date': '2025-04-10 14:00:00', 'payment_method': 'Bank Transfer - HBL-1234'},
    {'donation_id': 'DON20002', 'invoice_id': 'INV30002', 'challan_id': 'CH40002', 'campaign_id': 'CMP10002', 'funder_cnic': '9876543210987', 'funder_user': 'funder456', 'amount': 10000.0, 'date': '2025-04-12 16:30:00', 'payment_method': 'Cheque Payment - Meezan-56789'},
    {'donation_id': 'DON20003', 'invoice_id': 'INV30003', 'challan_id': 'CH40003', 'campaign_id': 'CMP10001', 'funder_cnic': '1234567890123', 'funder_user': 'funder123', 'amount': 500.0, 'date': '2025-04-15 09:00:00', 'payment_method': 'Mobile Payment - 03001234567'}
])
donations.to_csv(os.path.join(data_dir, 'donations.csv'), index=False)

# Surveys
surveys = pd.DataFrame([
    {'id': 'SUR50001', 'region': 'Balochistan', 'type': 'Education', 'amount': 8000.0, 'description': 'Books and uniforms for village children', 'taker': 'surveyuser', 'submitted': '2025-05-01 10:00:00', 'status': 'Pending'},
    {'id': 'SUR50002', 'region': 'Sindh', 'type': 'Food', 'amount': 2000.0, 'description': 'Monthly ration for 50 families', 'taker': 'surveyuser', 'submitted': '2025-05-02 11:00:00', 'status': 'Approved'}
])
surveys.to_csv(os.path.join(data_dir, 'surveys.csv'), index=False)

print("Test data generated successfully!")
