#!/usr/bin/env python3.9
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Lex Slots CloudWatch Custom Widgets"""

import json

import pandas as pd

_SLOT_NAME_SUFFIX = ".value.originalValue"


def render_slots_top_n_widget(event, input_df):
    """Render Slots Custom Widget"""
    # pylint: disable=too-many-locals
    slots_to_exclude = event.get("slotsToExclude", [])
    intents_to_exclude = event.get("intentToExclude", [])
    top_n = event.get("topN", 10)

    # deserialize json from message fields
    message_series = input_df["@message"].apply(json.loads)
    # flatten dictionaries up to one level and create a dataframe from it
    # only one level to selectively flatten other fields
    normalized_message_df = pd.DataFrame.from_records(
        pd.json_normalize(message_series, max_level=1)
    )
    # extract sessionState.intent dictionaries and turn then into a dataframe
    intent_df = pd.DataFrame.from_records(normalized_message_df["sessionState.intent"])
    # extract slots and normalize
    slots_df = pd.json_normalize(intent_df["slots"]).dropna(how="all")
    # join slots with intent to get a flattened dataframe with slots and intents
    slots_intent_df = slots_df.join(intent_df)

    # get intent names in data without exclusion
    slots_intent_columns = slots_intent_df.columns
    intent_names = [i for i in slots_intent_df["name"].unique() if i not in intents_to_exclude]

    # get slot names in data without exclusion
    slots_to_exclude_column_names = [f"{s}{_SLOT_NAME_SUFFIX}" for s in slots_to_exclude]
    slot_names = [
        c[: -len(_SLOT_NAME_SUFFIX)]
        for c in slots_intent_columns
        if c.endswith(_SLOT_NAME_SUFFIX) and c not in slots_to_exclude_column_names
    ]

    intent_slot_topn_values = []
    for intent_name in intent_names:
        for slot_name in slot_names:
            slot_column_name = f"{slot_name}{_SLOT_NAME_SUFFIX}"

            intent_slot_values_df = slots_intent_df[
                (slots_intent_df["name"] == intent_name)
                & slots_intent_df["state"].isin(["Fulfilled", "ReadyForFullfilment"])
            ][[slot_column_name]].rename({slot_column_name: "value"}, axis="columns")

            intent_slot_topn_values_df = (
                intent_slot_values_df.value_counts()
                .head(top_n)
                .to_frame()
                .rename({0: "count"}, axis="columns")
                .reset_index()
            )

            intent_slot_topn_values.append(
                {
                    "intent_name": intent_name,
                    "slot_name": slot_name,
                    "topn_df": intent_slot_topn_values_df,
                }
            )

    output = f"<h2>Top {top_n} Slot Values in Fulfilled Intents</h2>"
    for entry in intent_slot_topn_values:
        if not entry["topn_df"].empty:
            output = (
                output
                + f"<br><h3>Intent: {entry['intent_name']}"
                + f" Slot: {entry['slot_name']}</h3><br>"
            )
            output = output + entry["topn_df"].to_html(index=False)

    return output
