# -*- coding: utf-8 -*-

"""Terraform handler.

This module handles terraform plan in json output format.

Check https://www.terraform.io/docs/internals/json-format.html
for more info

"""


def get_resource_changes(data):
    """
    Filters Resource Changes from Plan.
    Retrieves the resource_changes portion from terraform plan.
    Args:
        data (dict): dict from json.load('<terraform plan in json format>')
    Returns:
        List of resource_changes
    """
    if "resource_changes" in data.keys():
        return data["resource_changes"]
    return []


def filter_noop(resources):
    """
    Filters no-op actions.
    Parses all the resource_changes and cleans out the ones with no-op actions
    Args:
        data(list): list of resource_changes (output from get_resource_changes)
    Returns:
        List of resources that are going to be changed
    """
    changes = []
    for res in resources:
        if res["change"]["actions"] != ["no-op"]:
            changes.append(res)
    return changes


def filter_resource_type(resources, resource_type):
    """
    Filters by a specific resource type
    Parses all the resource_changes and cleans out the ones that are not of an specific type
    Args:
        data(list): list of resource_changes (output from get_resource_changes)
    Returns:
        List of resources that are going to be changed
    """
    changes = []
    for res in resources:
        if resource_type in res["type"]:
            changes.append(res)
    return changes


def calculate_name(resource):
    """
    Tries to calculate the name of the resource.
    Args:
        resource(dict): Resource object
    Returns:
        String name
    """
    name = ""
    before_name = ""
    after_name = ""
    if resource["change"]["before"] is not None:
        if "name" in resource["change"]["before"]:
            before_name = resource["change"]["before"]["name"].lower()
    if resource["change"]["after"] is not None:
        if "name" in resource["change"]["after"]:
            after_name = resource["change"]["after"]["name"].lower()

    if after_name and before_name and (after_name != before_name):
        name = before_name + " --> " + after_name
    elif after_name and before_name:
        name = before_name
    elif before_name and (after_name is not None):
        name = before_name
    elif after_name and (before_name is not None):
        name = after_name
    else:
        name = "<known after apply>"
    return name


def calculate_resource_group(resource):
    """
    Tries to calculate the RG of the resource.
    Args:
        resource(dict): Resource object
    Returns:
        String name
    """
    name = ""
    before_rg = ""
    after_rg = ""
    if resource["change"]["before"] is not None:
        if "resource_group_name" in resource["change"]["before"]:
            before_rg = resource["change"]["before"]["resource_group_name"].lower(
            )
    if resource["change"]["after"] is not None:
        if "resource_group_name" in resource["change"]["after"]:
            after_rg = resource["change"]["after"]["resource_group_name"].lower(
            )

    if after_rg and before_rg and (after_rg != before_rg):
        name = before_rg + " --> " + before_rg
    elif after_rg and before_rg:
        name = before_rg
    elif before_rg and (after_rg is not None):
        name = before_rg
    elif after_rg and (before_rg is not None):
        name = after_rg
    else:
        name = "<known after apply>"
    return name


def parse_resource(resource):
    """
    Parse Resource to retrieve metadata.
    Args:
        resource(dict): Resource object
    Returns:
        Dict with resources attributes
    """
    item = {
        "actions": resource["change"]["actions"],
        "name": calculate_name(resource),
        "address": resource["address"],
        "type": resource["type"],
        "resource_group": calculate_resource_group(resource) if resource["provider_name"] == "registry.terraform.io/hashicorp/azurerm" else ""
    }
    return item


def get_attributes(data):
    """
    Get attributes from resource.
    Args:
        data(list): list of resources
    Returns:
        List of resources dict with attributes
    """
    resources = []
    for res in data:
        resources.append(parse_resource(res))
    return resources


def parse_plan(tfplan, filter_by_resource_type: str = None):
    """
    Parse Terraform plan in JSON.
    Args:
        tfplan(dict): dict from json.load('<terraform plan in json format>')
    Returns:
        List of resources dict with attributes
    """
    all_resources = get_resource_changes(tfplan)
    resource_changing = filter_noop(all_resources)
    resources = get_attributes(resource_changing)
    if filter_by_resource_type:
        resources = filter_resource_type(resources, filter_by_resource_type)
    resources.sort(key=lambda x: x["name"], reverse=True)
    return resources
