
import sys
import os
import requests
import csv


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import dtKey

def getapiviolations():

    results = []
    policy_rules_per_ids = {}
    policy_rule_types_per_ids = {}
    network_services_per_ids = {}
    cloud_resources_per_ids = {}
    restful_apis_per_ids = {}
    web_apps_per_ids = {}
    api_operations_per_ids = {}
    cursor = "First"
    all_violations = []
    
    while True:
        if not cursor:
            break
        elif cursor == "First":
            url = "https://api.securetheorem.com/apis/api_security/results/v1beta1/policy_violations"
        else:
            url = "https://api.securetheorem.com/apis/api_security/results/v1beta1/policy_violations?cursor={0}".format(cursor)
        headers = {'Authorization':'APIKey '+ dtKey,'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        try:
            response = response.json()
        except JSONDecodeError:
            break     
        all_violations.extend(response['policy_violations'])
        policy_rules_per_ids.update({rule['id']: rule for rule in response['policy_rules']})
        policy_rule_types_per_ids.update({rule_type['id']: rule_type for rule_type in response['policy_rule_types']})
        network_services_per_ids.update({service['id']: service for service in response['network_services']})
        cloud_resources_per_ids.update({resource['id']: resource for resource in response['cloud_resources']})
        web_apps_per_ids.update({web_app['id']: web_app for web_app in response['web_applications']})
        restful_apis_per_ids.update({restful_api['id']: restful_api for restful_api in response['restful_apis']})
        api_operations_per_ids.update(
            {
                api_operation['id']: (api_operation, restful_apis_per_ids[api_operation['restful_api_id']])
                for api_operation in response['api_operations']
            }
        )
        cursor = response["pagination_information"]["next_cursor"]
        print(f"Fetched {len(response['policy_violations'])} violations")
    exported_violations = []
    for violation in all_violations:
        # Skip violations with an exception (ie. manually closed by a user in the portal)
        if violation['exception_type']:
            continue

        if violation['affected_network_service_id']:
            # The violation/issue affects a network service
            service = network_services_per_ids[violation['affected_network_service_id']]
            asset_name = service['url']
            asset_type = "Server"
            cloud_console_url = None

        elif violation['affected_cloud_resource_id']:
            # The violation/issue affects a network service
            resource = cloud_resources_per_ids[violation['affected_cloud_resource_id']]
            asset_name = resource['name']
            asset_type = resource['asset_type_name']
            cloud_console_url = resource['cloud_console_url']

        elif violation['affected_api_operation_id']:
            # The violation/issue affects an API operation
            asset_type = "API Operation"
            cloud_console_url = None
            api_operation, api = api_operations_per_ids[violation['affected_api_operation_id']]
            asset_name = f"{api_operation['http_method']} at {api['base_url']}{api_operation['path']}"

        elif violation['affected_web_application_id']:
            # The violation/issue affects a Single Page Application
            web_app = web_apps_per_ids[violation['affected_web_application_id']]
            asset_name = f"{web_app['base_url']}{web_app['base_path']}"
            asset_type = "Single Page Web Application"
            cloud_console_url = None
        else:
            raise ValueError()

        # Lookup meta-data about the policy violation
        policy_rule = policy_rules_per_ids[violation['violated_policy_rule_id']]
        policy_rule_type = policy_rule_types_per_ids[policy_rule['policy_rule_type_id']]

        viol = {}
        viol['violation_uuid']=violation['id']
        viol['title']=policy_rule_type['title']
        viol['relevance']=policy_rule['relevance']
        viol['affected_asset_name']=asset_name
        viol['affected_asset_type']=asset_type
        viol['affected_asset_cloud_console_url']=cloud_console_url
        viol['description']=policy_rule_type['description']
        viol['recommendation']=policy_rule_type['recommendation']
        viol['date_discovered']=violation['date_created']

        exported_violations.append(viol)
    results = exported_violations

    return results

def export(report):
    csv_columns = list(report[0].keys())
    loc = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/DataTheorem/apiviolationexport.csv"
    try:
        with open(loc, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in report:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def main():
    report = getapiviolations()
    #GET API NAME/ENDPOINT!
    export(report)

main()
