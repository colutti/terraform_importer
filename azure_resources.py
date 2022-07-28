# -*- coding: utf-8 -*-

from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient


def get_vm_id(vm_name, resource_group, subscription_id):
    """
    Given a resource group and a vm name, it returns the Azure ID of the VM
    """
    credential = AzureCliCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    vm_azure = compute_client.virtual_machines.get(resource_group, vm_name)
    return vm_azure.id


def get_resource_group_id(resource_group, _resource_group, subscription_id):
    """
    Given a resource group and a vm name, it returns the Azure ID of the VM
    """
    credential = AzureCliCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    rg_azure = resource_client.resource_groups.get(resource_group)
    return rg_azure.id


def get_app_service_plan_id(app_service_plan_name, resource_group, subscription_id):
    """
    Given a resource group and an app service plan, it returns the Azure ID of the plan
    """
    credential = AzureCliCredential()
    website_management_client = WebSiteManagementClient(
        credential, subscription_id)
    app_service_plan = website_management_client.app_service_plans.get(
        resource_group, app_service_plan_name)
    return app_service_plan.id


def get_disk_id(disk_name, resource_group, subscription_id):
    """
    Given a resource group and a vm disk name,
    it returns the Azure ID of the disk
    """
    credential = AzureCliCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    managed_disk = compute_client.disks.get(resource_group, disk_name)
    return managed_disk.id


resource_id_methods = {
    "azurerm_virtual_machine": get_vm_id,
    "azurerm_resource_group": get_resource_group_id,
    "azurerm_service_plan": get_app_service_plan_id,
    "azurerm_managed_disk": get_disk_id
}


def get_resource_id(resource_name, subscription_id, resource_type, resource_group=None):
    resource_id_method = resource_id_methods[resource_type] if any(
        resource_type in d for d in resource_id_methods) else None
    return resource_id_method(resource_name, resource_group, subscription_id) if resource_id_method else None
