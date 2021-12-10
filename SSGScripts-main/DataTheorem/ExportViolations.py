from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import xlwt

from dt_api_security_results.client import ApiSecurityResultsClient
from dt_api_security_results.models.policy_violations import RelevanceEnum

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import dtKey


@dataclass
class ExportedViolationRow:
    violation_uuid: UUID
    title: str
    relevance: RelevanceEnum
    affected_asset_name: str
    affected_asset_type: str
    affected_asset_cloud_console_url: Optional[str]
    description: str
    recommendation: str
    date_discovered: datetime

    @property
    def violation_portal_url(self) -> str:
        return f"https://www.securetheorem.com/api/inspect/policy-violations/{self.violation_uuid}"


def retrieve_urgent_violations(api_key: str) -> List[ExportedViolationRow]:  # noqa: C901 (complexity)
    policy_rules_per_ids = {}
    policy_rule_types_per_ids = {}
    network_services_per_ids = {}
    cloud_resources_per_ids = {}
    restful_apis_per_ids = {}
    web_apps_per_ids = {}
    api_operations_per_ids = {}

    # Retrieve all of the open violations that are URGENT
    client = ApiSecurityResultsClient(api_key=api_key)
    print("Fetching all URGENT violations")
    cursor = None

    # We have to go through all the pages
    all_urgent_violations = []
    while True:
        response = client.policy_violations_list(cursor=cursor, filter_by_relevance=RelevanceEnum("URGENT"))
        print(f"Fetched {len(response.policy_violations)} violations")

        # Make the data easy to query
        all_urgent_violations.extend(response.policy_violations)
        policy_rules_per_ids.update({rule.id: rule for rule in response.policy_rules})
        policy_rule_types_per_ids.update({rule_type.id: rule_type for rule_type in response.policy_rule_types})
        network_services_per_ids.update({service.id: service for service in response.network_services})
        cloud_resources_per_ids.update({resource.id: resource for resource in response.cloud_resources})
        web_apps_per_ids.update({web_app.id: web_app for web_app in response.web_applications})
        restful_apis_per_ids.update({restful_api.id: restful_api for restful_api in response.restful_apis})
        api_operations_per_ids.update(
            {
                api_operation.id: (api_operation, restful_apis_per_ids[api_operation.restful_api_id])
                for api_operation in response.api_operations
            }
        )

        cursor = response.pagination_information.next_cursor
        if not cursor:
            # We went through all the pages; all done here
            break

    # Start processing each violation
    exported_violations = []
    for violation in all_urgent_violations:
        # Skip violations with an exception (ie. manually closed by a user in the portal)
        if violation.exception_type:
            continue

        if violation.affected_network_service_id:
            # The violation/issue affects a network service
            service = network_services_per_ids[violation.affected_network_service_id]
            asset_name = service.url
            asset_type = "Server"
            cloud_console_url = None

        elif violation.affected_cloud_resource_id:
            # The violation/issue affects a network service
            resource = cloud_resources_per_ids[violation.affected_cloud_resource_id]
            asset_name = resource.name
            asset_type = resource.asset_type_name
            cloud_console_url = resource.cloud_console_url

        elif violation.affected_api_operation_id:
            # The violation/issue affects an API operation
            asset_type = "API Operation"
            cloud_console_url = None
            api_operation, api = api_operations_per_ids[violation.affected_api_operation_id]
            asset_name = f"{api_operation.http_method} at {api.base_url}{api_operation.path}"

        elif violation.affected_web_application_id:
            # The violation/issue affects a Single Page Application
            web_app = web_apps_per_ids[violation.affected_web_application_id]
            asset_name = f"{web_app.base_url}{web_app.base_path}"
            asset_type = "Single Page Web Application"
            cloud_console_url = None
        else:
            raise ValueError()

        # Lookup meta-data about the policy violation
        policy_rule = policy_rules_per_ids[violation.violated_policy_rule_id]
        policy_rule_type = policy_rule_types_per_ids[policy_rule.policy_rule_type_id]

        exported_violations.append(
            ExportedViolationRow(
                violation_uuid=violation.id,
                title=policy_rule_type.title,
                relevance=policy_rule.relevance,
                affected_asset_name=asset_name,
                affected_asset_type=asset_type,
                affected_asset_cloud_console_url=cloud_console_url,
                description=policy_rule_type.description,
                recommendation=policy_rule_type.recommendation,
                date_discovered=violation.date_created,
            )
        )
    return exported_violations


def make_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("api_key")
    return parser


def main() -> None:
    args = make_argument_parser().parse_args()
    xls_file = "urgent_violations.xls"

    exported_violations = retrieve_urgent_violations(args.api_key)

    print(f"Dumping {len(exported_violations)} violations from to {xls_file}...")
    book = xlwt.Workbook()
    sheet = book.add_sheet("Policy Violations")

    sheet.write(0, 0, "Unique ID")
    sheet.write(0, 1, "Title")
    sheet.write(0, 2, "Relevance")
    sheet.write(0, 3, "Asset Name")
    sheet.write(0, 4, "Asset Type")
    sheet.write(0, 5, "Asset Cloud Console URL")
    sheet.write(0, 6, "Description")
    sheet.write(0, 7, "Recommendation")
    sheet.write(0, 8, "Date Discovered")
    sheet.write(0, 9, "Data Theorem Portal URL")

    for index, violation_row in enumerate(exported_violations, start=1):
        sheet.write(index, 0, str(violation_row.violation_uuid))
        sheet.write(index, 1, violation_row.title)
        sheet.write(index, 2, violation_row.relevance)
        sheet.write(index, 3, violation_row.affected_asset_name)
        sheet.write(index, 4, violation_row.affected_asset_type)
        sheet.write(index, 5, violation_row.affected_asset_cloud_console_url)
        sheet.write(index, 6, violation_row.description)
        sheet.write(index, 7, violation_row.recommendation)
        sheet.write(index, 8, violation_row.date_discovered.date().isoformat())
        sheet.write(index, 9, violation_row.violation_portal_url)

    book.save(xls_file)
    print("All done!")


if __name__ == "__main__":
    main()
