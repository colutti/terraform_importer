# -*- coding: utf-8 -*-
"""
    Author: Rafael Colucci
    Contact: rafacolucci@gmail.com

    This is a small utility that make it easier to import existing Azure Resources in Terraform
    It only works for a few resources, but it should be easy to extend it

    Before using this script you need to execute:

        - terraform plan -out <plan_name>.tfplan
        - terraform show -json <plan_name>.tfplan > <plan_name>.json

    After convering the plan to json, just call this script as follow:

        - python3 import.py --plan <plan_name>.json --subscription <your_subscription_id>

            Note: if you wish to execute the import automatically, you can use the parameter apply:

                - python3 import.py --plan <plan_name>.json --subscription <your_subscription_id> --apply
"""
import json
import subprocess
import argparse
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import AzureCliCredential


def __virtual_machine(vm):
    """
        Given a vm change in terraform, it returns a command to import the VM
    """
    address = vm["address"]
    name = vm["change"]["after"]["name"]
    resource_group = vm["change"]["after"]["resource_group_name"]
    vm_id = __get_vm_id(name, resource_group)
    import_command = "terraform import {} {}".format(address, vm_id)
    return import_command


def __managed_disk(managed_disk):
    """
        Given a managed disk change in terraform, it returns a command to import the VM
    """
    address = managed_disk["address"]
    name = managed_disk["change"]["after"]["name"]
    resource_group = managed_disk["change"]["after"]["resource_group_name"]
    managed_disk_id = __get_disk_id(name, resource_group)
    import_command = "terraform import {} {}".format(address, managed_disk_id)
    return import_command


def import_resources(plan):
    """
        Main function. Given a terraform json plan, it tries to import existing resources
    """
    for i in plan["resource_changes"]:
        import_command = None
        if i["change"]["actions"][0] == "create":

            if i["type"] == "azurerm_virtual_machine":
                import_command = __virtual_machine(i)

            if i["type"] == "azurerm_managed_disk":
                import_command = __managed_disk(i)

        if import_command:
            print(import_command)
            if args.apply:
                subprocess.run(f"{import_command}", shell=True)


def __get_vm_id(vm_name, resource_group):
    """
        Given a resource group and a vm name, it returns the Azure ID of the VM
    """
    compute_client = __get_azure_credentials()
    vm_azure = compute_client.virtual_machines.get(resource_group, vm_name)
    return vm_azure.id


def __get_azure_credentials():
    """
        Authenticates in Azure and returns a ComputeManagementClient
    """
    Subscription_Id = args.subscription
    credential = AzureCliCredential()
    compute_client = ComputeManagementClient(credential, Subscription_Id)
    return compute_client


def __get_disk_id(disk_name, resource_group):
    """
        Given a resource group and a vm disk name, it returns the Azure ID of the disk
    """
    compute_client = __get_azure_credentials()
    managed_disk = compute_client.disks.get(resource_group, disk_name)
    return managed_disk.id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Terraform import - Azure')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--apply', default=False, action="store_true")
    args = parser.parse_args()

    with open(args.plan) as f:
        plan = json.loads(f.read())

    import_resources(plan)
