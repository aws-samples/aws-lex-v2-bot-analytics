#!/usr/bin/env python3.9
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""
Lex Analytics CloudWatch Dashboard Custom Widget Lambda Handler
"""

# pylint: disable=import-error
from lib.client import get_client
from lib.logger import get_logger
from lib.cw_logs import get_query_results_as_df
from widgets.slots import render_slots_top_n_widget

# pylint: enable=import-error

LOGGER = get_logger(__name__)
CLIENT = get_client("logs")


def handler(event, _):
    """Lambda Handler"""
    LOGGER.debug(event)
    widget_context = event.get("widgetContext")

    time_range = widget_context.get("timeRange", {}).get("zoom") or widget_context.get("timeRange")
    start_time = time_range.get("start") // 1000
    end_time = time_range.get("end") // 1000

    log_group = event["logGroups"]
    query = event["query"]
    widget_type = event["widgetType"]

    try:
        input_df = get_query_results_as_df(
            log_group_names=[log_group],
            query=query,
            start_time=start_time,
            end_time=end_time,
            logs_client=CLIENT,
            logger=LOGGER,
        )
    except Exception as exception:  # pylint disable=broad-except
        LOGGER.error("exception running query: %s", exception)
        raise

    if input_df.empty:
        return "<pre>No data found</pre>"

    if widget_type == "slotsTopN":
        return render_slots_top_n_widget(event=event, input_df=input_df)

    raise RuntimeError(f"unknown widget type: {widget_type}")
