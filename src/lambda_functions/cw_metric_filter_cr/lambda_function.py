#!/usr/bin/env python3.8
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""CloudWatch Metrics Filter Dimension CloudFormation Custom Resource

CloudFormation does not currently (as of 07/2021) support configuring
dimensions on Metrics Filters. This custom resource adds dimensions to an
existing Metrics Filter.
"""

import logging
from os import getenv

import boto3
from botocore.config import Config as BotoCoreConfig
from crhelper import CfnResource


LOGGER = logging.getLogger(__name__)
LOG_LEVEL = getenv("LOG_LEVEL", "DEBUG")
HELPER = CfnResource(
    json_logging=True,
    log_level=LOG_LEVEL,
)

# global init code goes here so that it can pass failure in case
# of an exception
try:
    # boto3 client
    CLIENT_CONFIG = BotoCoreConfig(
        retries={"mode": "adaptive", "max_attempts": 5},
    )
    CLIENT = boto3.client("logs", config=CLIENT_CONFIG)
except Exception as init_exception:  # pylint: disable=broad-except
    HELPER.init_failure(init_exception)


def get_metric_filter(
    log_group_name,
    filter_name_prefix,
    metric_name,
    metric_namespace,
):
    """Gets a metric filter matching the parameters"""
    paginator = CLIENT.get_paginator("describe_metric_filters")
    response_iterator = paginator.paginate(
        logGroupName=log_group_name,
        filterNamePrefix=filter_name_prefix,
    )
    metric_filters_response = [
        metric_filter
        for response in response_iterator
        for metric_filter in response.get("metricFilters", [])
    ]
    LOGGER.debug("metric filters response: %s", metric_filters_response)
    if not metric_filters_response:
        raise ValueError(
            "failed to find existing metric filter with "
            f"logGroupName: [{log_group_name}], "
            f"filterNamePrefix: [{filter_name_prefix}]"
        )
    # Get the fist metric filter with a matching transformation with the same
    # metricNameSpace and metricName
    # NOTE: There is a chance that there are multiple metric filters since the
    # describe_metric_filters uses a name prefix
    for m_f in metric_filters_response:
        metric_filters = [
            m_f
            for m_t in m_f["metricTransformations"]
            if m_t["metricName"] == metric_name and m_t["metricNamespace"] == metric_namespace
        ]
        if metric_filters:
            break

    if not metric_filters:
        raise ValueError(
            "failed to find existing metric filter with "
            f"logGroupName: [{log_group_name}], "
            f"filterNamePrefix: [{filter_name_prefix}], "
            f"metricName: [{metric_name}], "
            f"metricNamespace: [{metric_namespace}]"
        )

    metric_filter_properties = [
        "filterName",
        "filterPattern",
        "logGroupName",
        "metricTransformations",
    ]
    # only return the properties that are needed for the put_metric_filter call
    return {k: v for k, v in metric_filters[0].items() if k in metric_filter_properties}


def put_metric_filter_dimension(
    filter_name,
    log_group_name,
    metric_transformation,
    request_type,
):
    """Put Metric Filter Dimension"""
    metric_namespace = metric_transformation["MetricNamespace"]
    metric_name = metric_transformation["MetricName"]
    is_create_update = request_type.lower() in ["create", "update"]
    dimensions = metric_transformation["Dimensions"] if is_create_update else {}

    metric_filter_match = get_metric_filter(
        filter_name_prefix=filter_name,
        log_group_name=log_group_name,
        metric_namespace=metric_namespace,
        metric_name=metric_name,
    )

    metric_transformations = []
    for m_t in metric_filter_match["metricTransformations"]:
        is_target_metric_transformation = (
            m_t["metricName"] == metric_name and m_t["metricNamespace"] == metric_namespace
        )

        # add dimension to the target metric transformation
        transformation = (
            {**m_t, **{"dimensions": dimensions}} if is_target_metric_transformation else m_t
        )

        # Remove dimensions from metric transformation when deleting the resource.
        # Setting to an empty dict seems to have a different effect
        if not is_create_update and is_target_metric_transformation:
            del transformation["dimensions"]

        metric_transformations.append(transformation)

    metrics_filter_args = {
        **metric_filter_match,
        **{"metricTransformations": metric_transformations},
    }

    CLIENT.put_metric_filter(**metrics_filter_args)


@HELPER.create
@HELPER.update
def create_or_update_metric_filter_dimension(event, _):
    """Create or Update Resource"""
    resource_type = event["ResourceType"]
    resource_properties = event["ResourceProperties"]

    if resource_type == "Custom::MetricFilterDimension":
        filter_name = resource_properties["FilterName"]
        log_group_name = resource_properties["LogGroupName"]

        metric_transformations = resource_properties["MetricTransformations"]
        for metric_transformation in metric_transformations:
            put_metric_filter_dimension(
                filter_name=filter_name,
                log_group_name=log_group_name,
                metric_transformation=metric_transformation,
                request_type=event["RequestType"],
            )

        return

    raise ValueError(f"invalid resource type: {resource_type}")


@HELPER.delete
def delete_metric_filter_dimension(event, _):
    """Delete Resource"""
    # ignore all exceptions when deleting. TODO: target specific scenarios
    # when an exeption is generated when the resource does not exists or has
    # been deleted
    try:
        create_or_update_metric_filter_dimension(event, _)
    except Exception as exception:  # pylint: disable=broad-except
        LOGGER.error("failed to delete exception: %s", exception)


def handler(event, context):
    """Lambda Handler"""
    HELPER(event, context)
