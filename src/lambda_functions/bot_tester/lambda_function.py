#!/usr/bin/env python3.8
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Lex Bot Runner Lambda Function"""
import json
import logging
import random
from os import environ, getenv

from bot_conversations import get_bot_conversation  # pylint: disable=import-error
from run_conversation_test import run_conversation_test  # pylint: disable=import-error


LOGGER = logging.getLogger(__name__)
LOG_LEVEL = getenv("LOG_LEVEL", "DEBUG")
LOGGER.setLevel(LOG_LEVEL)

BOTS_CONFIG_JSON = environ["BOTS_CONFIG_JSON"]
BOTS_CONFIG = json.loads(BOTS_CONFIG_JSON)
BOT_NAMES = list(BOTS_CONFIG.keys())


def handler(event, context):
    """Lambda Handler"""
    # pylint: disable=unused-argument
    LOGGER.info("bots config: %s", BOTS_CONFIG)
    bot_logical_name = random.choice(BOT_NAMES)  # nosec
    locale_ids = BOTS_CONFIG[bot_logical_name]["localeIds"].split(",")
    locale_id = random.choice(locale_ids)  # nosec
    bot_args = {
        "botId": BOTS_CONFIG[bot_logical_name]["botId"],
        "botAliasId": BOTS_CONFIG[bot_logical_name]["botAliasId"],
        "localeId": locale_id,
    }
    LOGGER.info("bot: %s", bot_args)
    session_id = context.aws_request_id

    conversation = get_bot_conversation(bot_logical_name=bot_logical_name, locale=locale_id)
    LOGGER.debug("conversation: %s", conversation)
    responses = run_conversation_test(
        bot_args=bot_args,
        conversation=conversation,
        session_id=session_id,
    )
    LOGGER.debug("responses: %s", responses)
