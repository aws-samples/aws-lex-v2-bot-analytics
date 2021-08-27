// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const { CloudWatchLogsClient } = require('@aws-sdk/client-cloudwatch-logs'); // eslint-disable-line import/no-unresolved
const { LexModelsV2Client } = require('@aws-sdk/client-lex-models-v2'); // eslint-disable-line import/no-unresolved
const { runQuery } = require('./lib');
const {
  displayConversationPath,
  displayHeatmapSessionHourOfDay,
  displayHeatmapIntentPerHour,
  displayMissedUtterance,
} = require('./widgets');

const DOCS = `
## Lex Analytics Widgets
Renders Lex Analytics Custom Widgets

### Widget parameters
Param | Description
---|---
**widgetType** | heatmapSessionHourOfDay\\|heatmapIntentPerHour\\|conversationPath
**logGroups** | The log groups (comma-separated) to run query against
**query** | The query used to get the data to generate the widget content

### Example parameters
\`\`\` yaml
widgetType: heatmapIntentPerHour
logGroups: ${process.env.AWS_LAMBDA_LOG_GROUP_NAME}
query: 'fields @timestamp, @message | sort @timestamp desc | limit 20'
\`\`\`
`;

const AWS_SDK_MAX_RETRIES = Number(process.env.AWS_SDK_MAX_RETRIES) || 16;
const LOGS_CLIENT = new CloudWatchLogsClient({
  region: process.env.AWS_REGION,
  maxAttempts: AWS_SDK_MAX_RETRIES,
});
const LEX_MODELS_CLIENT = new LexModelsV2Client({
  region: process.env.AWS_REGION,
  maxAttempts: AWS_SDK_MAX_RETRIES,
});

exports.handler = async (event, context) => {
  if (event.describe) {
    return DOCS;
  }
  console.debug(JSON.stringify(event)); // eslint-disable-line no-console

  const { widgetContext } = event;
  const form = widgetContext.forms.all;
  const logGroups = form.logGroups || event.logGroups || widgetContext.params.logGroups || '';
  const query = form.query || event.query || widgetContext.params.query || '';
  const widgetType = form.widgetType || event.widgetType || widgetContext.params.widgetType || '';
  const timeRange = widgetContext.timeRange.zoom || widgetContext.timeRange;
  const shouldRunQuery = event.shouldRunQuery ?? true;

  let queryResults;
  if (shouldRunQuery) {
    if (!query || query.trim() === '') {
      return '<pre class="error">Required parameter "query" is empty or undefined</pre>';
    }
    try {
      queryResults = await runQuery(LOGS_CLIENT, logGroups, query, timeRange.start, timeRange.end);
    } catch (e) {
      console.error('exception: ', e); // eslint-disable-line no-console
      return '<pre class="error">Exception running query. Please see Lambda logs.</pre>';
    }
  }

  if (!widgetType) {
    return '<pre class="error">Required parameter "widgetType" is not defined</pre>';
  }

  switch (widgetType) {
    case 'missedUtterance':
      return displayMissedUtterance({
        lexModelsClient: LEX_MODELS_CLIENT,
        widgetContext,
        context,
        queryResults,
        event,
      });
    case 'heatmapSessionHourOfDay':
      return displayHeatmapSessionHourOfDay({ widgetContext, queryResults });
    case 'heatmapIntentPerHour':
      return displayHeatmapIntentPerHour({ widgetContext, queryResults });
    case 'conversationPath':
      return displayConversationPath({ widgetContext, queryResults });
    default:
      return `<pre class="error">unknown widgetType: ${widgetType}</pre>`;
  }
};
