# Fund Raising Management System

A secure, transparent, and comprehensive desktop application for managing fundraising campaigns, built with Python and PyQt6. The system addresses the lack of accountability in traditional fundraising by providing a robust digital platform that securely connects Funders, Admins, Survey Takers, and Data Analysts.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data-yellow.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Analytics-orange.svg)

## 🌟 Key Features
- **Role-Based Workflows**: Specialized interactive modules for Admins, Funders, Data Analysts, and Survey Takers.
- **Campaign Management**: Instantly convert approved area-need surveys into active, transparent fundraising campaigns.
- **Secure Donations**: A 6-step verified flow for donations, including 13-digit CNIC verification, dynamic payment method selection, and automated invoice/challan generation.
- **Data Analytics**: Integrated Matplotlib dashboards for real-time visualization of financial stats, regional funds distribution, and top funder leaderboards.
- **Premium UI/UX**: A state-of-the-art dark-themed design with custom animated components, glowing buttons, hover effects, and toast notifications.

## 🛠️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Muhammad-Wasif/Fund-Raising-Management-System.git
   cd Fund-Raising-Management-System
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate testing data:**
   *(Optional but recommended to populate the dashboards with sample campaigns, funders, and donations)*
   ```bash
   python generate_test_data.py
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 🔑 Default Testing Credentials
If you are testing the application locally, use the following credentials to access the different modules:
- **Admin**: Username: `admin` | Password: `admin123`
- **Funder**: Username: `funder` | Password: `funder123`
- **Data Analyst**: Username: `analyst` | Password: `analyst123`
- **Survey Taker**: Username: `survey` | Password: `survey123`

---
*Developed by Muhammad Wasif - 2025*
