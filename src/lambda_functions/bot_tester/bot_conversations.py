#!/usr/bin/env python3.8
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Bot Conversation Definitions"""
import random
from faker import Faker  # pylint: disable=import-error

with open("audio/hello.pcm", "rb") as f:
    HELLO_AUDIO = f.read()

AUDIO_REQUEST_CONTENT_TYPE = (
    "audio/lpcm; sample-rate=8000; sample-size-bits=16; channel-count=1; is-big-endian=false"
)


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
            "confirmations": {"yes", "no"},
            "invalid_account_types": {"I don't know", "tax", "my account"},
            "transfer_funds_utterances": {
                "i want to make a transfer",
                "transfer",
                "transfer funds",
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
        user_name = self._faker.user_name()
        return [
            # welcome
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["welcome_utterances"]
                        ),
                        "requestAttributes": {"state": "init"},
                        "sessionState": {"sessionAttributes": {"username": user_name}},
                    },
                }
            ],
            # hello speech
            [
                {
                    "operation": "recognize_utterance",
                    "args": {
                        "inputStream": HELLO_AUDIO,
                        "requestContentType": AUDIO_REQUEST_CONTENT_TYPE,
                        "responseContentType": "text/plain;charset=utf-8",
                    },
                }
            ],
            # fallback utterance
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["fallback_utterances"]
                        ),
                        "sessionState": {"sessionAttributes": {"username": user_name}},
                    },
                }
            ],
            # check balance
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["check_balance_utterances"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {"appState": "CheckBalance", "username": user_name}
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["account_types"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "CheckBalance:Account",
                                "username": user_name,
                            }
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.date_of_birth().isoformat(),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "CheckBalance:Account:DoB",
                                "username": user_name,
                            }
                        },
                    },
                },
            ],
            # check balance invalid account slot value
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["check_balance_utterances"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {"appState": "CheckBalance", "username": user_name}
                        },
                    },
                },
                *[
                    {
                        "operation": "recognize_text",
                        "args": {
                            "text": t,
                            "sessionState": {
                                "sessionAttributes": {
                                    "appState": "CheckBalance:Account",
                                    "username": user_name,
                                }
                            },
                        },
                    }
                    for t in self.DEFINITIONS[self._locale]["invalid_account_types"]
                ],
            ],
            # transfer funds
            [
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["transfer_funds_utterances"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "TransferFunds",
                                "username": user_name,
                            }
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["account_types"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "TransferFunds:SrcAccount",
                                "username": user_name,
                            }
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["account_types"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "TransferFunds:DstAccount",
                                "username": user_name,
                            }
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.pricetag(),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "Transfer:Amount",
                                "username": user_name,
                            }
                        },
                    },
                },
                {
                    "operation": "recognize_text",
                    "args": {
                        "text": self._faker.random_element(
                            elements=self.DEFINITIONS[self._locale]["confirmations"]
                        ),
                        "sessionState": {
                            "sessionAttributes": {
                                "appState": "TransferFunds:DstAccount",
                                "username": user_name,
                            }
                        },
                    },
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
