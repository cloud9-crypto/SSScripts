---
Title: "SSM-CrowdStrike-Installation-Status"
path: Fetching SSM-CrowdStrike Status on EC2 instances
---


# Setup AWS CLI

## What You'll Need

Before using the installation, you must already have:
* Access to an AWS Accounts.

### Configure Your CLI Environment
If you are new to MassMutual and need to Setup AWS CLI please refer to [AWSCLI](https://github.com/massmutual/sre-aws-helpers) and follow the README file to Setup.
Now from your terminal need to run `getAWSTempCredentials` to authenticate your token to specific AWS Account.

# How to Fetch Status of SSM and CrowdStrike Packages across all AWS account EC2 instances
Now you need to run the script. Please don't change/rename any folders just you need to clone repo and add your EC2 pem files in PEM folder, then direct to correct patch  at [here](https://github.com/massmutual/SRE-Security-Automation-Scripts/blob/main/Scan-Instances/instacescanner.py#L93). Please don't change and push any code to this repository.

```
git@github.com:massmutual/SRE-Security-Automation-Scripts.git
Cloning into 'SRE-Security-Automation-Scripts'...
```
After cloning this repository, change directory to `cd SRESECOPS/SRE-Security-Automation-Scripts/Scan-Instances` then run `python3 instacescanner.py` and make sure you need to setup python3 in your local.
**Note:** This script will take time to get generated .csv report and with standard csv name "Package_Detected_Scanned_Hosts_List.csv" saved in `Scan-Instances`
