#!/usr/bin/env python3.8
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Lex Bot Conversation Runner"""
import boto3
from botocore.config import Config as BotoCoreConfig

CLIENT_CONFIG = BotoCoreConfig(
    retries={"mode": "adaptive", "max_attempts": 5},
)
CLIENT = boto3.client("lexv2-runtime", config=CLIENT_CONFIG)


def run_conversation_test(bot_args, conversation, session_id="test"):
    """Runs Lex Conversation Test"""
    responses = []
    for interaction in conversation:
        api_function = getattr(CLIENT, interaction["operation"])
        response = api_function(**bot_args, sessionId=session_id, **interaction["args"])
        responses.append(response)

    return responses
