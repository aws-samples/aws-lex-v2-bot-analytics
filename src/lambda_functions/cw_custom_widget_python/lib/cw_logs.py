# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""CloudWatch Log Insights Query"""

from time import sleep
import pandas as pd


_QUERY_WAIT_STATUS = ["Scheduled", "Running"]
_QUERY_TARGET_STATUS = ["Complete"]
_QUERY_MAX_TRIES = 60
_DEFAULT_POLL_SLEEP_TIME_IN_SECS = 0.5


def get_query_results_as_df(
    query,
    log_group_names,
    start_time,
    end_time,
    logger,
    logs_client,
    poll_sleep_time_in_secs=_DEFAULT_POLL_SLEEP_TIME_IN_SECS,
    max_tries=_QUERY_MAX_TRIES,
):
    """Get CloudWatch Log Insights Query Results as a Pandas Dataframe"""
    # pylint: disable=too-many-arguments
    args = {
        "logGroupNames": log_group_names,
        "startTime": start_time,
        "endTime": end_time,
        "queryString": query,
    }
    response = logs_client.start_query(**args)
    logger.debug(response)
    query_id = response["queryId"]

    tries = 0
    while True:
        response = logs_client.get_query_results(queryId=query_id)
        logger.debug(response)
        status = response["status"]
        if status not in _QUERY_WAIT_STATUS or tries >= max_tries:
            break
        sleep(poll_sleep_time_in_secs)
        tries = tries + 1
    if status not in _QUERY_TARGET_STATUS:
        logger.error("failed waiting for query - response: %s, tries: %s", response, tries)
        raise RuntimeError("Failed waiting for query")

    return pd.DataFrame(({i["field"]: i["value"] for i in r} for r in response["results"]))
