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


def __get_file_encoding(file_name):
    """
    Given a file path, returns the encoding of the file (utf, ascii, etc)
    """
    rawdata = open(file_name, "rb").read()
    result = chardet.detect(rawdata)
    return result["encoding"]


def __parse_arguments():
    parser = argparse.ArgumentParser(description="Terraform import - Azure")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--subscription", required=True)
    parser.add_argument("--module", required=False)
    parser.add_argument("--deleteaction", default="removefromstate",
                        choices=["removefromstate", "removeresource"])
    arguments = parser.parse_args()
    return arguments


def __delete_resource(resource, deleteaction, terraform_command_list):
    if deleteaction == "removefromstate":
        terraform_command_list.append({"type": "rm", "name": resource['name'], "command":
                                       f"terraform state rm {resource['address']}"})
    else:
        terraform_command_list.append({"type": "apply", "name": resource['name'], "command":
                                       f"terraform apply --target=\"{resource['address']}\""})


def __apply_resource_changes(resource, terraform_command_list, subscription):
    resource_id = azure_resources.get_resource_id(
        resource['name'], subscription, resource['type'], resource['resource_group'])
    if resource_id:
        terraform_command_list.append({"type": "import", "name": resource['name'], "command":
                                       f"terraform import {resource['address']} {resource_id}"})
    else:
        terraform_command_list.append({"type": "apply", "name": resource['name'], "command":
                                       f"terraform apply --target=\"{resource['address']}\""})


def __parse_plan(plan_file, module):
    charenc = __get_file_encoding(plan_file)
    with open(plan_file, encoding=charenc) as f:
        plan = json.loads(f.read())
    terraform_plan = terraform.parse_plan(plan, module)
    return terraform_plan


def __import_resources(plan_file, subscription, module, deleteaction):
    """
    Main function. Given a terraform json plan,
    it tries to import existing resources
    """
    terraform_plan = __parse_plan(plan_file, module)
    if not terraform_plan:
        return None
    terraform_command_list = []
    for item in terraform_plan:
        if "delete" in item["actions"]:
            __delete_resource(item, deleteaction, terraform_command_list)
        if "create" in item["actions"]:
            __apply_resource_changes(
                item, terraform_command_list, subscription)
    terraform_command_list.sort(key=lambda x: x['command'], reverse=True)
    return terraform_command_list


def __get_unique_resource_names_list(terraform_command_list):
    unique_resources = []
    for command in terraform_command_list:
        found = False
        for name in unique_resources:
            if command["name"] == name:
                found = True
                break
        if not found:
            unique_resources.append(command["name"])
    unique_resources.sort(key=lambda x: x, reverse=False)
    return unique_resources


def __print_results(terraform_command_list, unique_resources):
    for resource in unique_resources:
        print(f"\n# {resource}")
        for command in terraform_command_list:
            if resource == command["name"]:
                print(f"\t{command['command']}")


if __name__ == "__main__":
    args = __parse_arguments()
    terraform_commands = __import_resources(
        args.plan, args.subscription, args.module, args.deleteaction)
    resources = __get_unique_resource_names_list(terraform_commands)
    __print_results(terraform_commands, resources)
