# Billing Automation Script

## Problem Statement
There was a requirement to extract daily live billing data (Bills, Collections, Refunds, and Cancelled Bills) for analysis in Power BI.

**The challenge:** The hospital software did not provide any API or database for connectivity.

**The only option available:** Download data manually from the HealthPlix portal every day.

This manual process was time-consuming, error-prone, and repetitive.
---
## Solution

- To overcome this limitation, I built a Python automation script using Selenium.
- The script logs in automatically to the portal.
- Navigates to the required sections (Bills, Collections, Refunds, Cancelled Bills).
- Downloads the data into Excel files.
- Stores the files in a local folder for further use in analytics (Power BI).
- This automation saved hours of manual work and ensured consistency in data refresh.

## Features

- Automated Login: Secure login into the portal.

- Multi-Module Extraction: Downloads data for:
**Bills** 
**Collections**
**Refunds**
**Cancelled Bills**

- Excel Export: Saves data in Excel format.

- Time-Saving: Reduces daily manual effort.

# How to Run
1. Requirements
Python 3.9+

Install dependencies:
pip install -r requirements.txt

2. Run the Script

3. Configuration
- Update your login credentials (if required) inside the script (demo placeholders provided).
- Ensure Chrome browser & ChromeDriver are installed and match versions.

## Disclaimer

This script is a demonstration of the type of automation I implemented in my workplace.
Sensitive data, credentials, and proprietary logic are excluded.
Script logic is recreated only for demonstration purposes.