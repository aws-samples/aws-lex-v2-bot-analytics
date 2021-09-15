# Amazon Lex V2 Analytics

> An Amazon Lex V2 Analytics Dashboard Solution

## Solution Description

The Amazon Lex V2 Analytics Dashboard Solution helps you to monitor and
visualize the performance and operational metrics of your
[Lex V2 chatbot](https://docs.aws.amazon.com/lexv2/latest/dg/what-is.html).
It provides a dashboard that you can use to continuously analyze and improve the
experience of end-users interacting with your chatbot.

This solution implements metrics and visualizations that help you identify
chatbot performance, trends and engagement insights. This is done by extracting
operational data from your Lex V2 chatbot
[conversation logs](https://docs.aws.amazon.com/lexv2/latest/dg/monitoring-logs.html).
The solution presents a unified view of how users are interacting with your
chatbot in an
[Amazon CloudWatch dashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html).

Features include:

- A common view of valuable chatbot insights such as:
  - User and session activity (e.g. sentiment analysis, top-n sessions,
    text/speech modality)
  - Conversation statistics and aggregations (e.g. average of session duration,
    messages per session, session heatmaps)
  - Conversation flow, trends and history (e.g. intent path chart, intent per
    hour heatmaps)
  - Utterance history and performance (e.g. missed utterances, top-n utterances)
- Rich visualizations and widgets such as metrics charts, top-n lists, heatmaps,
  form-based utterance management
- Serverless architecture using pay-per-use managed services that scale
  transparently
- Metrics that can be used outside of the dashboard for alarming and monitoring

### Architecture

The solution architecture leverages the following AWS Services and features:

- **CloudWatch Logs** to store your chatbot conversation logs
- **CloudWatch Metric Filters** to create custom metrics from conversation logs
- **CloudWatch Log Insights** to query the conversation logs and to create powerful
  aggregations from the log data
- **CloudWatch Contributor Insights** to identify top contributors and
  outliers in higly variable data such as sessions and utterances
- **CloudWatch Dashboard** to put together a set of charts and visualizations
  representing the metrics and data insights from your chatbot conversations
- **CloudWatch Custom Widgets** to create custom visualizations like heatmaps
  and conversation flows using Lambda functions

## Quick Start

This solution can be easily installed in your AWS accounts by launching it from
the [AWS Serverless Repository](https://aws.amazon.com/serverless/serverlessrepo/).

### Deploy Using SAR

Click the following AWS Console link to create a dashboard for your Lex V2:

[https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:777566285978:applications/lexv2-analytics](https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:777566285978:applications/lexv2-analytics)

Once you click on the link, it will take you to the *create application page* in
the AWS Lambda console (this is a Serverless solution!). In this page, scroll
down to the **Application Settings** section to enter the parameters for your
dashboard. See the following sections for an overview on how to set the
parameters.

### Parameters

#### Existing Lex Bot

If you have an existing Lex V2 bot that already has
[conversation logs](https://docs.aws.amazon.com/lexv2/latest/dg/monitoring-logs.html)
enabled, you would need to configure the following parameters of the
under the **Application Settings** section:

- **BotId**: The ID of an existing Lex V2 Bot that is going to
  be used with this dashboard
- **BotLocaleId**: The Bot locale ID associated to the Bot Id with this
  dashboard. Defaults to `en_US`. Each dashboard creates metrics for a specific
  locale ID of a Lex bot.
- **LexConversationLogGroupName**: Name of an existing CloudWatch Log Group
  containing the Lex Conversation Logs. The Bot ID and Locale in the parameters
  above must be configured to use this Log Group for its conversation logs

**NOTE:** The *Application name* parameter (CloudFormation stack name) must
be unique per AWS account and region.

#### Sample Bot

Alternatively, if you just want to test drive the dashboard, this solution can
deploy a fully functional sample bot. The sample bot comes with a Lambda
function that is invoked every two minutes to generate conversation traffic.
This allows you to have data to see in the dashboard. If you want to deploy the
dashboard with the sample bot instead of using an existing bot, set the
**ShouldDeploySampleBots** parameter to `true`. This is a quick an easy way
to kick the tires!

#### Other Parameters

Set the **ShouldAddWriteWidgets** to `true` (defaults to `false`) if you want
your dashboard to have more than read-only visualizations. Setting this
parameter to `true` adds a widget that allows to add missed utterances to an
intent in your bot.

**NOTE:** Setting the **ShouldAddWriteWidgets** parameter to `true` will enable
users that are allowed to access your dashboard to also make changes to your
chatbot. Only set this parameter to true if you intend to provide the dashboard
users with more than just read-only access. This is useful when you restrict
access to the dashboard to only allow users who are also permitted to add
utterances to the intents configured in your bot.

The **LogLevel** parameter can be used to set the logging level of the Lambda
functions. The **LogRetentionInDays** controls the CloudWatch Logs retention
(in days) for the Bot Conversation Logs. This is only used when the stack
creates a Log Group for you if the *LexConversationLogGroupName* parameter is
left empty.

### Deploy

Once you have set the desired values in the **Application parameters** section,
scroll down to the bottom of the page and select the checkbox to acknowledge
that the application creates custom IAM roles and nested applications. Click on
the **Deploy** button to create the dashboard.

After you click the **Deploy** button, it will take you to the application
overview page. From there, you can click on the **Deployments** tab to watch
the deployment status. Click on the **View stack events** button to go
to the AWS CloudFormation console to see the deployment details. The stack may
take around 5 minutes to create. Wait until the stack status is
**CREATE_COMPLETE**.

### Go to the Dashboard

Once the stack creation has successfully completed, you can look for a direct
link to your dashboard under the **Outputs** tab of the stack in the AWS
CloudFormation console (**DashboardConsoleLink** output variable).

Alternatively, you can browse to the
[Dashboard section of the CloudWatch Console](https://console.aws.amazon.com/cloudwatch/home?#dashboards)
to find your newly created dashboard. The dashboard name contains the
stack name and bot information (name, ID, locale).

**NOTE:** You may need to wait a few minutes for data to be reflected in the
dashboard.

## Update Using SAR

After you've deployed the dashboard from SAR, you may need to update it.
For example, you may need to change an application setting, or you may want
to update the application to the latest version that was published.

You can use the same
[link](https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:777566285978:applications/lexv2-analytics)
used to deploy the stack to perform updates. Use the same procedure as
deploying the application, and provide the same **Application name** that you
originally used to deploy it.

*NOTE:* SAR prepends `serverlessrepro-` to your stack name. However, to deploy a
new version of your application, you should provide the original application
name without the `serverlessrepo-` prefix.

See the [SAR Updating Applications](https://docs.aws.amazon.com/serverlessrepo/latest/devguide/serverlessrepo-how-to-consume-new-version.html)
documentation for details.

## Deploy Using SAM

In addition to deploying the project using SAR as shown in the
[Quick Start](#quick-start) section, you can use the
[SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
to build and deploy the solution. This is a more advanced option that allows
you to deploy from source code. With this approach, you can make modifications
to the code and deploy the solution to your account by running a couple of SAM
CLI commands.

The SAM CLI is an extension of the AWS CLI that adds functionality for building
and testing Lambda applications. It uses Docker to run your functions in an
Amazon Linux environment that matches Lambda.

### Requirements

To use the SAM CLI, you need the following tools:

- SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3 installed](https://www.python.org/downloads/)
- Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy this project for the first time, run the following two
commands in your shell from the base directory of the code repository:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of this project. The second command
will package and deploy your application to your AWS account, with a series of
prompts.

These prompts allow you to customize your stack name and set up the AWS region.
It also allows you to input the CloudFormation parameters including parameters
to to deploy a sample bot or link the dashboard to one of your existing
chatbots.

Here is an example of the parameter prompts:

```shell
    Stack Name [lex-analytics]:
    AWS Region [us-east-1]:
    Parameter ShouldDeploySampleBots [False]:
    Parameter LogLevel [DEBUG]:
    Parameter LogRetentionInDays [90]:
    Parameter BotId []:
    Parameter BotLocaleId [en_US]:
    Parameter LexConversationLogGroupName []:
    Parameter ShouldAddWriteWidgets [False]
    #Shows you resources changes to be deployed and require a 'Y' to initiate deploy
    Confirm changes before deploy [Y/n]: n
    #SAM needs permission to be able to create roles to connect to the resources in your template
    Allow SAM CLI IAM role creation [Y/n]: n
    Capabilities [['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']]:
    Save arguments to configuration file [Y/n]:
```

You can see the description of the parameters in the **Parameters** section
in the [template.yaml](template.yaml) file and an overview in the
[parameters](#parameters) section.

Here are more details about the general SAM parameters:

- **Stack Name**: The name of the stack to deploy to CloudFormation. This
  should be unique to your account and region, and a good starting point would be
  something matching your project name.
- **AWS Region**: The AWS region you want to deploy your app to.
- **Confirm changes before deploy**: If set to yes, any change sets will be
  shown to you before execution for manual review. If set to no, the AWS SAM
  CLI will automatically deploy application changes.
- **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this
  example, create AWS IAM roles required for the AWS Lambda function(s)
  included to access AWS services. By default, these are scoped down to minimum
  required permissions. To deploy an AWS CloudFormation stack which creates or
  modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be
  provided. If permission isn't provided through this prompt, to deploy this
  example you must explicitly pass `--capabilities CAPABILITY_IAM` to the
  `sam deploy` command.
- **Save arguments to samconfig.toml**: If set to yes, your choices will be
  saved to a configuration file inside the project, so that in the future you
  can just re-run `sam deploy` without parameters to deploy changes to your
  application.

## Caveats / Known Issues

- Pie and bar charts in the dashboard may show not show accurate data for the
  selected time range. We are currently investigating this issue
- Metrics using CloudWatch Contributor Insights are limited to a 24 hour window
  within the selected time range. The CloudWatch Contributor Insights feature
  allows a maximum time range for the report is 24 hours, but you can choose a
  24-hour window that occurred up to 15 days ago.
- The Sentiment Analysis metrics will be empty if your bot does not have
  Sentiment Analysis enabled. For details, see the Lex V2
  [Sentiment Analysis](https://docs.aws.amazon.com/lex/latest/dg/sentiment-analysis.html)
  documentation.

## Development

This project uses the SAM CLI to build and deploy the solution. See the
[Deploy Using SAM](#deploy-using-sam) for an overview of using the SAM CLI.

### Development Environment Setup

This project is developed and tested on
[Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/)
using [AWS Cloud9](https://aws.amazon.com/cloud9/) and the following tools:

- Bash 4.2
- Python 3.8
- Python build and development requirements are listed in the
  [requirements/requirements-build.txt](requirements/requirements-build.txt) and
  [requirements/requirements-dev.txt](requirements/requirements-dev.txt) files
- AWS SAM CLI ~= 1.29.0
- Docker >= 20
- GNU make >= 3.82
- Node.js >= 14.17.3
- Node.js development dependencies are in the [package.json](package.json) file

The [samconfig.toml](samconfig.toml) file can be used to configure the SAM
environment. For more details see the
[SAM cli config documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-config.html)

### Makefile

This project contains a [Makefile](Makefile) that can be optionally used to
run tasks such as building and deploying the project. The `Makefile` is used
by the `make` command. It defines the dependencies between tasks such as
automatically only building the project based on changes before you deploy.

You can set the `CONFIG_ENV` environmental file to have the `Makefile`
use build and deployment configurations from the `samconfig.toml` file.

Here are some examples of tasks handled using the `make` command:

1. Install the required build tools and creates a python virtual environment:

    ```bash
    make install
    ```

2. Build the project:

    ```bash
    make build
    ```

3. Deploy the stack:

   Before deploying for the first time, you may need to configure your deployment
   settings using:

   ```bash
   sam deploy --guided
   ```

   Alternatively, you can edit the [samconfig.toml](samconfig.toml) file to
   configure your deployment values.

   After that initial setup, you can deploy using:

    ```bash
    make deploy
    ```

    You can also have multiple configurations in your `samconfig.toml` file and
    have the `Makefile` use a specific config by setting the `CONFIG_ENV`
    environmental variable:

    ```bash
    # uses the `[myconfig.deploy.parameters]` config entry in samconfig.toml
    CONFIG_ENV=myconfig make deploy
    ```

4. Run linters on the source code:

    ```bash
    make lint
    ```

5. Publish to SAR:

    ```bash
    make publish
    ```

6. Publish a release of built artifacts to an S3 bucket:

    ```bash
    RELEASE_S3_BUCKET=my-release-s3-bucket make release
    ```

7. Delete the stack:

    ```bash
    make delete-stack
    ```

#### Makefile SAM Local Invoke

To invoke local functions with an event file:

```bash
EVENT_FILE=tests/events/cw_metric_filter_cr/create.json make local-invoke-cw_metric_filter_cr
```

#### Makefile SAM Local Invoke Debug Lambda Functions

 To interactively debug Python Lambda functions inside the SAM container put
 `debugpy` as a dependency in the `requirements.txt` file under the function
 directory.

 To debug using Visual Studio Code, create a launch task to attach to the
 debugger (example found in the [launch.json](.vscode/launch.json) file under the
 .vscode directory):

 ```json
    {
        "name": "Debug SAM Lambda debugpy attach",
        "type": "python",
        "request": "attach",
        "port": 5678,
        "host": "localhost",
        "pathMappings": [
            {
                "localRoot": "${workspaceFolder}/${relativeFileDirname}",
                "remoteRoot": "/var/task"
            }
        ],
    },
    {
        "type": "node",
        "request": "attach",
        "name": "Debug SAM Node Lambda attach",
        "address": "localhost",
        "port": 5858,
        "pathMappings": [
            {
                "localRoot": "${workspaceFolder}/${relativeFileDirname}",
                "remoteRoot": "/var/task"
            }
        ],
        "protocol": "inspector",
        "stopOnEntry": false
    },
  ```

 Set the `DEBUGGER_PY` environmental variable to debug Python Lambda functions.
 Similarly, set the `DEBUGGER_JS` environmental variable to debug Node.js Lambda
 functions. For example, to debug the `cw_metric_filter_cr` function, run the
 following command (requires debugpy in the function requirements.txt folder):

```shell
DEBUGGER_PY=true EVENT_FILE=tests/events/cw_metric_filter_cr/create.json make local-invoke-cw_metric_filter_cr
```

### Resources

See the
[AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
for an introduction to SAM specification, the SAM CLI, and serverless
application concepts.

## Cleanup

To delete this application, you can use the SAM CLI:

  ```bash
  sam delete
  ```

 Or [delete the stack using the AWS CloudFormation Console](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
