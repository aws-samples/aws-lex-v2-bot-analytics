#!/usr/bin/env python3.9
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Lex Session Attributes CloudWatch Custom Widgets"""

import json

import pandas as pd


def render_session_attributes_top_n_widget(event, input_df):
    """Render Session Attributes Custom Widget"""
    # pylint: disable=too-many-locals
    session_attributes_to_exclude = event.get("sessionAttributesToExclude", [])
    top_n = event.get("topN", 10)

    # deserialize json from message fields
    message_series = input_df["@message"].apply(json.loads)
    # flatten dictionaries
    normalized_message_df = pd.DataFrame.from_records(
        pd.json_normalize(message_series, max_level=1)
    )
    session_attributes_series = normalized_message_df["sessionState.sessionAttributes"].dropna(
        how="all"
    )
    if session_attributes_series.emtpy:
        return "<pre>No session attributes found</pre>"

    # extract sessionState.sessionAttributes dictionaries and turn then into a dataframe
    session_attributes_df = pd.DataFrame.from_records(session_attributes_series).drop(
        session_attributes_to_exclude,
        axis="columns",
        errors="ignore",
    )

    session_attributes_columns = session_attributes_df.columns
    session_attributes_topn_values = []
    for column in session_attributes_columns:
        topn_df = (
            session_attributes_df[column]
            .value_counts()
            .to_frame()
            .head(top_n)
            .reset_index()
            .rename({column: "count", "index": "value"}, axis="columns")
        )
        session_attributes_topn_values.append(
            {
                "name": column,
                "topn_df": topn_df,
            }
        )

    output = f"<h2>Top {top_n} Session Attribute Values</h2>"
    for entry in session_attributes_topn_values:
        if not entry["topn_df"].empty:
            output = output + f"<br><h3>Session Attribute Key: {entry['name']}</h3><br>"
            output = output + entry["topn_df"].to_html(index=False)

    return output
