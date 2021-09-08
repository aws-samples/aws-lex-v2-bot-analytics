# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# pylint: disable=global-statement
"""Boto3 Client"""
from os import getenv
import json
import boto3
from botocore.config import Config
from .logger import get_logger


LOGGER = get_logger(__name__)

CLIENT_CONFIG = Config(
    retries={"mode": "adaptive", "max_attempts": 10},
    **json.loads(getenv("AWS_SDK_USER_AGENT", "{}")),
)

_HELPERS_SERVICE_CLIENTS = dict()


def get_client(service_name, config=CLIENT_CONFIG):
    """Get Boto3 Client"""
    global _HELPERS_SERVICE_CLIENTS
    if service_name not in _HELPERS_SERVICE_CLIENTS:
        LOGGER.debug("Initializing global boto3 client for %s", service_name)
        _HELPERS_SERVICE_CLIENTS[service_name] = boto3.client(service_name, config=config)
    return _HELPERS_SERVICE_CLIENTS[service_name]


def reset_client():
    """Reset Boto3 Client"""
    global _HELPERS_SERVICE_CLIENTS
    _HELPERS_SERVICE_CLIENTS = dict()
