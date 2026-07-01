import os
import random
import pandas as pd
from datetime import datetime

# CSV File names
CAMPAIGNS_FILE = 'campaigns.csv'
FUNDERS_FILE = 'funders.csv'
SURVEYS_FILE = 'surveys.csv'
DONATIONS_FILE = 'donations.csv'


class DataManager:
    """Handles all data operations: CSV persistence, authentication, CRUD for all entities."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.campaigns_df = pd.DataFrame()
        self.funders_df = pd.DataFrame()
        self.donations_df = pd.DataFrame()
        self.surveys_df = pd.DataFrame()

        self.load_dataframes()

    def _path(self, filename):
        return os.path.join(self.data_dir, filename)

    # ────────────────────── ID Generation ──────────────────────
    def generate_id(self, prefix):
        """Generates an ID like CMP84721, DON32198, etc."""
        return prefix + str(random.randint(10000, 99999))

    # ────────────────────── Persistence ──────────────────────
    def save_data(self):
        """Save all non-empty DataFrames to their CSV files."""
        try:
            if not self.campaigns_df.empty:
                self.campaigns_df.to_csv(self._path(CAMPAIGNS_FILE), index=False)
            if not self.funders_df.empty:
                self.funders_df.to_csv(self._path(FUNDERS_FILE), index=False)
            if not self.surveys_df.empty:
                self.surveys_df.to_csv(self._path(SURVEYS_FILE), index=False)
            if not self.donations_df.empty:
                self.donations_df.to_csv(self._path(DONATIONS_FILE), index=False)
            return True
        except Exception:
            return False

    def load_dataframes(self):
        """Load all DataFrames from CSV files, or init empty with schema."""
        try:
            p = self._path(CAMPAIGNS_FILE)
            if os.path.exists(p):
                self.campaigns_df = pd.read_csv(p)
            else:
                self.campaigns_df = pd.DataFrame(columns=[
                    'id', 'state', 'region', 'type', 'target', 'raised',
                    'description', 'project_name', 'admin', 'created', 'status'
                ])

            p = self._path(FUNDERS_FILE)
            if os.path.exists(p):
                self.funders_df = pd.read_csv(p)
            else:
                self.funders_df = pd.DataFrame(columns=['cnic', 'username'])

            p = self._path(DONATIONS_FILE)
            if os.path.exists(p):
                self.donations_df = pd.read_csv(p)
            else:
                self.donations_df = pd.DataFrame(columns=[
                    'donation_id', 'invoice_id', 'challan_id', 'campaign_id',
                    'funder_cnic', 'funder_user', 'amount', 'date', 'payment_method'
                ])

            p = self._path(SURVEYS_FILE)
            if os.path.exists(p):
                self.surveys_df = pd.read_csv(p)
            else:
                self.surveys_df = pd.DataFrame(columns=[
                    'id', 'region', 'type', 'amount', 'description',
                    'taker', 'submitted', 'status'
                ])
        except Exception:
            pass

    # ────────────────────── Authentication ──────────────────────
    def authenticate(self, role, username, password):
        """Validate credentials. Returns True/False."""
        passwords = {
            'admin': 'admin123',
            'funder': 'funder123',
            'analyst': 'analyst123',
            'survey': 'survey123',
        }
        return role in passwords and password.lower() == passwords[role]

    # ────────────────────── Survey Operations ──────────────────────
    def get_pending_surveys(self):
        if self.surveys_df.empty:
            return pd.DataFrame()
        return self.surveys_df[self.surveys_df['status'] != 'Approved'].reset_index(drop=False)

    def get_all_surveys(self):
        return self.surveys_df.copy()

    def submit_survey(self, region, fund_type, amount, description, taker):
        """Submit a new survey. Returns the generated survey ID."""
        survey_id = self.generate_id("SUR")
        new_survey = pd.DataFrame([{
            'id': survey_id,
            'region': region,
            'type': fund_type,
            'amount': float(amount),
            'description': description,
            'taker': taker,
            'submitted': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Pending'
        }])
        self.surveys_df = pd.concat([self.surveys_df, new_survey], ignore_index=True)
        self.save_data()
        return survey_id

    # ────────────────────── Campaign Operations ──────────────────────
    def create_campaign_from_survey(self, survey_original_idx, project_name, admin_user):
        """Create a campaign from a pending survey. Returns campaign ID."""
        survey = self.surveys_df.loc[survey_original_idx]
        campaign_id = self.generate_id("CMP")

        new_campaign = pd.DataFrame([{
            'id': campaign_id,
            'state': survey['region'],
            'region': survey['region'],
            'type': survey['type'],
            'target': float(survey['amount']),
            'raised': 0.0,
            'description': survey['description'],
            'project_name': project_name,
            'admin': admin_user,
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Active'
        }])

        self.campaigns_df = pd.concat([self.campaigns_df, new_campaign], ignore_index=True)
        self.surveys_df.at[survey_original_idx, 'status'] = 'Approved'
        self.save_data()
        return campaign_id

    def get_all_campaigns(self):
        return self.campaigns_df.copy()

    def get_active_campaigns(self):
        if self.campaigns_df.empty:
            return pd.DataFrame()
        return self.campaigns_df[self.campaigns_df['status'] == 'Active'].copy()

    # ────────────────────── Donation Operations ──────────────────────
    def get_all_donations(self):
        return self.donations_df.copy()

    def get_user_donations(self, funder_user):
        if self.donations_df.empty:
            return pd.DataFrame()
        return self.donations_df[self.donations_df['funder_user'] == funder_user].copy()

    def validate_cnic(self, cnic, username):
        """Returns (is_valid: bool, message: str)."""
        if not cnic.isdigit() or len(cnic) != 13:
            return False, "CNIC must be exactly 13 digits"
        if not self.funders_df.empty:
            funder_row = self.funders_df[self.funders_df['cnic'] == cnic]
            if not funder_row.empty:
                if funder_row.iloc[0]['username'] != username:
                    return False, "CNIC already linked to a different username"
        return True, "Valid"

    def make_donation(self, campaign_id, funder_cnic, funder_user, amount, payment_method):
        """
        Process a donation. Returns (success, info_dict, excess_amount).
        actual_amount = min(amount, remaining). excess = amount - actual.
        """
        camp_mask = self.campaigns_df['id'] == campaign_id
        if not camp_mask.any():
            return False, {}, 0

        camp_idx = self.campaigns_df[camp_mask].index[0]
        campaign = self.campaigns_df.loc[camp_idx]
        remaining = campaign['target'] - campaign['raised']

        actual_amount = min(amount, max(remaining, 0))
        excess = round(amount - actual_amount, 2)

        donation_id = self.generate_id("DON")
        invoice_id = self.generate_id("INV")
        challan_id = self.generate_id("CH")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_donation = pd.DataFrame([{
            'donation_id': donation_id,
            'invoice_id': invoice_id,
            'challan_id': challan_id,
            'campaign_id': campaign_id,
            'funder_cnic': funder_cnic,
            'funder_user': funder_user,
            'amount': actual_amount,
            'date': now_str,
            'payment_method': payment_method,
        }])
        self.donations_df = pd.concat([self.donations_df, new_donation], ignore_index=True)

        # Register funder if new
        if self.funders_df.empty or not (self.funders_df['cnic'] == funder_cnic).any():
            new_funder = pd.DataFrame([{'cnic': funder_cnic, 'username': funder_user}])
            self.funders_df = pd.concat([self.funders_df, new_funder], ignore_index=True)

        # Update campaign raised amount
        self.campaigns_df.at[camp_idx, 'raised'] = self.campaigns_df.at[camp_idx, 'raised'] + actual_amount
        fully_funded = self.campaigns_df.at[camp_idx, 'raised'] >= self.campaigns_df.at[camp_idx, 'target']
        if fully_funded:
            self.campaigns_df.at[camp_idx, 'status'] = 'Completed'

        self.save_data()

        info = {
            'donation_id': donation_id,
            'invoice_id': invoice_id,
            'challan_id': challan_id,
            'campaign_name': campaign['project_name'],
            'campaign_id': campaign_id,
            'amount': actual_amount,
            'payment_method': payment_method,
            'date': now_str,
            'fully_funded': fully_funded,
        }
        return True, info, excess

    def get_campaign_name(self, campaign_id):
        """Lookup project_name for a campaign_id."""
        if self.campaigns_df.empty:
            return "Unknown"
        row = self.campaigns_df[self.campaigns_df['id'] == campaign_id]
        return row.iloc[0]['project_name'] if not row.empty else "Unknown"

    # ────────────────────── Analytics ──────────────────────
    def get_top_funders(self, top_n=10):
        if self.donations_df.empty:
            return pd.DataFrame()
        totals = self.donations_df.groupby('funder_cnic')['amount'].agg(['sum', 'count']).reset_index()
        totals.columns = ['cnic', 'total_donated', 'num_donations']
        totals = totals.sort_values('total_donated', ascending=False)
        if not self.funders_df.empty:
            totals = totals.merge(self.funders_df, on='cnic', how='left')
        return totals.head(top_n).reset_index(drop=True)

    def get_financial_stats(self):
        stats = {}
        if not self.campaigns_df.empty:
            stats['total_campaigns'] = len(self.campaigns_df)
            stats['successful'] = int((self.campaigns_df['raised'] >= self.campaigns_df['target']).sum())
            stats['total_raised'] = float(self.campaigns_df['raised'].sum())
            stats['total_target'] = float(self.campaigns_df['target'].sum())
        else:
            stats['total_campaigns'] = 0
            stats['successful'] = 0
            stats['total_raised'] = 0.0
            stats['total_target'] = 0.0

        if not self.donations_df.empty:
            stats['total_donations'] = len(self.donations_df)
            stats['avg_donation'] = float(self.donations_df['amount'].mean())
        else:
            stats['total_donations'] = 0
            stats['avg_donation'] = 0.0

        return stats

    def get_regional_data(self):
        if self.campaigns_df.empty:
            return pd.DataFrame()
        regional = self.campaigns_df.groupby('region').agg({
            'id': 'count', 'raised': 'sum', 'target': 'sum'
        }).reset_index()
        regional.columns = ['Region', 'Campaigns', 'Total Raised', 'Total Target']
        return regional.sort_values('Total Raised', ascending=False).reset_index(drop=True)

    def get_payment_method_distribution(self):
        if self.donations_df.empty:
            return pd.Series(dtype=float)
        return self.donations_df['payment_method'].str.split(' - ').str[0].value_counts()
