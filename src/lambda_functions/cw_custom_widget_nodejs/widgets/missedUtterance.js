// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const {
  DescribeIntentCommand,
  ListIntentsCommand,
  UpdateIntentCommand,
} = require('@aws-sdk/client-lex-models-v2'); // eslint-disable-line import/no-unresolved

const CSS = '<style>td { white-space: nowrap; }</style>';
const RESULTS_MISSED_UTTERANCE_KEY = '@missed_utterance';
const RESULTS_COUNT_KEY = '@count';
const DRAFT_VERSION = 'DRAFT';
const FALLBACK_INTENT_ID = 'FALLBCKINT';

const displayListMissedUtterance = async ({
  lexModelsClient,
  widgetContext,
  queryResults,
  context,
}) => {
  const {
    params: { botId, botLocaleId },
  } = widgetContext;
  // flatten CloudWatch Insights results into objects
  const results = queryResults.map((x) => x.reduce((a, c) => ({ [c.field]: c.value, ...a }), {}));

  // TODO use paginator
  const listIntentsCommand = new ListIntentsCommand({
    botId,
    localeId: botLocaleId,
    botVersion: DRAFT_VERSION,
  });
  const listIntentsResponse = await lexModelsClient.send(listIntentsCommand);
  const intentSummaries = listIntentsResponse.intentSummaries || [];

  const sampleUtteranceResponsePromises = intentSummaries.map(async (x) => {
    const describeIntentCommand = new DescribeIntentCommand({
      botId,
      localeId: botLocaleId,
      botVersion: DRAFT_VERSION,
      intentId: x.intentId,
    });
    const describeIntentResponse = await lexModelsClient.send(describeIntentCommand);
    const { sampleUtterances: responseUtterances = [] } = describeIntentResponse;
    return responseUtterances;
  });

  const sampleUtteranceResponses = await Promise.all(sampleUtteranceResponsePromises);
  const sampleUtterances = sampleUtteranceResponses
    .map((x) => x.map((y) => y.utterance))
    .reduce((a, x) => [...a, ...x], []);

  const missedUtterances = results.filter(
    // eslint-disable-next-line comma-dangle
    (x) => !sampleUtterances.includes(x[RESULTS_MISSED_UTTERANCE_KEY])
  );

  let html = `<p>
    <p>Quickly add a missed utterance to your bot</p>
    <p>Select an intent next to a missed utterance and click on the 'Add' button next to it
    to add the utterance to the ${DRAFT_VERSION} version of botId: ${botId} and
    locale: ${botLocaleId}</p>
    <p><strong>NOTE:</strong> Only missed utterances that are not already in an existing intent in
    the ${DRAFT_VERSION} version are listed</p>
    <p>This is meant for testing of your bot using the ${DRAFT_VERSION} version. You are going to
    need to build your bot after adding the utterance before testing</p>
    `;

  if (missedUtterances && missedUtterances.length > 0) {
    html += `
    <table><thead><tr>
      <th width="40%">Missed Utterance</th>
      <th width="10%">Count</th>
      <th width="35%">Intent</th>
      <th width="15%">Add</th>
    </tr></thead></table>`;

    const intentOptions = intentSummaries
      .filter((i) => i.intentId !== FALLBACK_INTENT_ID)
      .sort((i, j) => i.intentName.localeCompare(j.intentName))
      .map((i) => `<option value="${i.intentId}">${i.intentName}</option>`)
      .join('\n');

    missedUtterances.forEach((missedUtterance, index) => {
      const intentDropDown = `
      <select name="intentId-${index}">${intentOptions}</select>
      `;

      html += `
        <form>
        <table>
        <tr>
          <td width="40%">${missedUtterance[RESULTS_MISSED_UTTERANCE_KEY]}</td>
          <td width="10%">${missedUtterance[RESULTS_COUNT_KEY]}</td>
          <td width="35%">${intentDropDown}</td>
          <td width="15%">
            <a class="btn btn-primary">Add</a>
            <cwdb-action action="call" endpoint="${context.invokedFunctionArn}">
            {
              "shouldRunQuery": false,
              "action": {
                "operation": "addUtterance",
                "arguments": {
                  "utterance": "${missedUtterance[RESULTS_MISSED_UTTERANCE_KEY]}",
                  "formIndex": ${index}
                }
              }
            }
            </cwdb-action>
          </td>
        </tr>
        </table></form>
      `;
    });
  } else {
    html += `<p><strong>WARNING:</strong> Could not find missed utterances that are not already in
      an existing intent. See the values below:</p>`;
    html += `<p>Missed Utterance Query Result:</p><pre>${JSON.stringify(results, null, 2)}</pre>`;
    html += `<p>Configured utterances in bot:</p>
      <pre>${JSON.stringify(sampleUtterances, null, 2)}</pre>`;
  }

  return CSS + html;
};

const displayAddMissedUtterance = async ({
  lexModelsClient,
  widgetContext,
  context,
  action,
  form,
}) => {
  const {
    params: { botId, botLocaleId },
  } = widgetContext;

  const { utterance, formIndex } = action.arguments;
  const intentId = form[`intentId-${formIndex}`];

  try {
    const describeIntentCommand = new DescribeIntentCommand({
      botId,
      localeId: botLocaleId,
      botVersion: DRAFT_VERSION,
      intentId,
    });
    const describeIntentResponse = await lexModelsClient.send(describeIntentCommand);
    const { sampleUtterances: responseUtterances, intentName } = describeIntentResponse;

    const sampleUtterances = [...responseUtterances, { utterance }];

    const updateIntentCommand = new UpdateIntentCommand({
      ...describeIntentResponse,
      sampleUtterances,
    });
    await lexModelsClient.send(updateIntentCommand);

    return `
      <p></p>
      <p>Successfully added utterance: <em>"${utterance}"</em> to intent:
      <strong>${intentName}</strong> of botID: <strong>${botId}</strong>
      in locale: <strong>${botLocaleId}</strong>. These changes were done to the
      <strong>${DRAFT_VERSION}</strong> version of the bot.</p>

      <p><strong>NOTE:</strong> You should build your bot before your test</p>

      <p>Go back to the list of missed utterances:</p>
      <a class="btn btn-primary">List Missed Utterances</a>
      <cwdb-action action="call" endpoint="${context.invokedFunctionArn}">
    `;
  } catch (e) {
    console.error('Exception adding utterance to intent: ', e); // eslint-disable-line no-console
    return `<pre class="error">There was an error adding the utterance to the intent.
      Please see the Lambda logs</pre>`;
  }
};

const displayMissedUtterance = async ({
  lexModelsClient,
  widgetContext,
  queryResults,
  context,
  event,
}) => {
  const form = widgetContext.forms.all;
  const action = form.action || event.action || widgetContext.params.action
    || { operation: 'listMissedUtterance' }; // prettier-ignore
  const { operation } = action;
  switch (operation) {
    case 'addUtterance':
      return displayAddMissedUtterance({
        lexModelsClient,
        widgetContext,
        context,
        action,
        form,
      });
    case 'listMissedUtterance':
    default:
      return displayListMissedUtterance({
        lexModelsClient,
        widgetContext,
        queryResults,
        context,
      });
  }
};

module.exports = {
  displayMissedUtterance,
};
