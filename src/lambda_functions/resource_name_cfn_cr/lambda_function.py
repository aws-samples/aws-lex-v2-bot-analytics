#!/usr/bin/env python3.9
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Resource Name CloudFormation Custom Resource

This is used generate a resource name prefix based on the parameters
of the stack.

It takes the following resource attributes:
- BotId
- BotLocaleId
- StackName

It retrieves the Bot Name using the DescribeBot API and returns a string like:
<BotName>-<BotId>-<BotLocaleId>-<StackName>

This is used to be able to generate resource names related to the bot but
still keep them human readable. It also works around the `serverlessrepo`
prefix that is added by the Serverless Application Repository (SAR)
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

SAR_STACK_PREFIX = "serverlessrepo-"

# global init code goes here so that it can pass failure in case
# of an exception
try:
    # boto3 client
    CLIENT_CONFIG = BotoCoreConfig(
        retries={"mode": "adaptive", "max_attempts": 5},
    )
    CLIENT = boto3.client("lexv2-models", config=CLIENT_CONFIG)
except Exception as init_exception:  # pylint: disable=broad-except
    HELPER.init_failure(init_exception)


@HELPER.create
@HELPER.update
def create_or_update_resource_name(event, _):
    """Create or Update Resource"""
    resource_type = event["ResourceType"]
    resource_properties = event["ResourceProperties"]

    if resource_type == "Custom::ResourceName":
        bot_id = resource_properties["BotId"]
        bot_locale_id = resource_properties["BotLocaleId"]
        stack_name = resource_properties["StackName"].removeprefix(SAR_STACK_PREFIX)

        try:
            response = CLIENT.describe_bot(
                botId=bot_id,
            )
            bot_name = response["botName"]
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.error("failed to call describe_bot - exception: %s", exception)
            raise

        return f"{bot_name}-{bot_id}-{bot_locale_id}-{stack_name}"

    raise ValueError(f"invalid resource type: {resource_type}")


@HELPER.delete
def delete_no_op(event, _):
    """Delete Resource"""
    LOGGER.info("delete event ignored: %s", event)


def handler(event, context):
    """Lambda Handler"""
    HELPER(event, context)
