# -*- coding: utf-8 -*-

"""
    Author: Rafael Colucci
    Contact: rafacolucci@gmail.com

    This is a small utility that make it easier to import existing
    Azure Resources in Terraform
    It only works for a few resources, but it should be easy to extend it

    Before using this script you need to execute:

        - terraform plan -out <plan_name>.tfplan
        - terraform show -json <plan_name>.tfplan > <plan_name>.json

    After convering the plan to json, just call this script as follow:

        - python3 import.py
                    --plan <plan_name>.json
                    --subscription <your_subscription_id>

"""
import argparse
import json
import chardet

import terraform
import azure_resources


def import_resources(plan_json, subscription, module):
    """
    Main function. Given a terraform json plan,
    it tries to import existing resources
    """
    terraform_plan = terraform.parse_plan(plan_json, module)
    if terraform_plan:
        for item in terraform_plan:
            terraform_command = None
            if "delete" in item["actions"]:
                terraform_command = f"\nterraform state rm {item['address']}"
            if "create" in item["actions"]:
                resource_id = azure_resources.get_resource_id(
                    item['name'], subscription, item['type'], item['resource_group'])
                terraform_command = f"\nterraform import {item['address']} {resource_id}" if resource_id else f"\nResource {item['name']} of type {item['type']} not found"
            if terraform_command:
                print(terraform_command)


def __get_file_encoding(file_name):
    """
    Given a file path, returns the encoding of the file (utf, ascii, etc)
    """
    rawdata = open(file_name, "rb").read()
    result = chardet.detect(rawdata)
    return result["encoding"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terraform import - Azure")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--subscription", required=True)
    parser.add_argument("--module", required=False)
    args = parser.parse_args()
    plan_file = args.plan
    charenc = __get_file_encoding(plan_file)
    with open(plan_file, encoding=charenc) as f:
        plan = json.loads(f.read())
    import_resources(plan, args.subscription, args.module)
