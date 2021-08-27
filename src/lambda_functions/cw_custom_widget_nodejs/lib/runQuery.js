// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const { StartQueryCommand, GetQueryResultsCommand } = require('@aws-sdk/client-cloudwatch-logs'); // eslint-disable-line import/no-unresolved

const CHECK_QUERY_STATUS_DELAY_MS = 250;

const sleep = async (delay) => new Promise((resolve) => setTimeout(resolve, delay));

const runQuery = async (logsClient, logGroups, queryString, startTime, endTime) => {
  const startQueryCommand = new StartQueryCommand({
    logGroupNames: logGroups.replace(/\s/g, '').split(','),
    queryString,
    startTime,
    endTime,
  });

  // TODO add cache
  const startQuery = await logsClient.send(startQueryCommand);
  const { queryId } = startQuery;

  // eslint-disable-next-line no-constant-condition
  while (true) {
    /* eslint-disable no-await-in-loop */
    const getQueryResultsCommand = new GetQueryResultsCommand({ queryId });
    const queryResults = await logsClient.send(getQueryResultsCommand);
    if (queryResults.status !== 'Complete') {
      await sleep(CHECK_QUERY_STATUS_DELAY_MS); // Sleep before calling again
    } else {
      return queryResults.results;
    }
  }
};

module.exports = {
  runQuery,
};
