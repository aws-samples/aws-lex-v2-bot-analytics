#!/usr/bin/env python3.8
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Bot Conversation Definitions"""
import random
from faker import Faker  # pylint: disable=import-error


class BankerBot:
    """Banker Bot Conversation"""

    # pylint: disable=too-few-public-methods
    DEFINITIONS = {
        "en_US": {
            "account_types": {"savings", "checking", "credit card", "visa", "mastercard", "amex"},
            "check_balance_utterances": {
                "check balance",
                "what's the balance in my account",
                "I want to know my balance",
            },
            "welcome_utterances": {"hi", "hello", "help", "I need help", "can you please help"},
            "fallback_utterances": {"what is this", "exit", "i am lost"},
        }
    }

    def __init__(self, locale="en_US"):
        self._locale = locale
        self._faker = Faker(locale=locale)

    def get_bot_conversations(self):
        """Get a Banker Bot Conversation"""
        return [
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["welcome_utterances"]
                        ),
                    },
                }
            ],
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["fallback_utterances"]
                        ),
                    },
                }
            ],
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["check_balance_utterances"]
                        ),
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["account_types"]
                        ),
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {"text": self._faker.date_of_birth().isoformat()},
                },
            ],
        ]


def get_bot_conversation(bot_logical_name="BankerBot", locale="en_US"):
    """Get Bot Conversation Definition"""
    bot = None
    if bot_logical_name == "BankerBot":
        bot = BankerBot(locale=locale)

    if not bot:
        raise ValueError(f"unknown bot logical name: {bot_logical_name}")

    conversations = bot.get_bot_conversations()
    conversation = random.choice(conversations)  # nosec

    return conversation
