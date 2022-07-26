# ziti-mattermost-action-py
GitHub Action that posts to a Mattermost webhook endpoint over OpenZiti

This GitHub workflow action uses [Ziti Python SDK](https://github.com/openziti/ziti-sdk-py) to post an event's payload information to a [Mattermost](https://mattermost.com/) instance over a `Ziti` connection. This allows the Mattermost server to remain private, i.e. not directly exposed to the internet.

## Usage

See [action.yml](action.yml) for descriptions of all available inputs.

```yml
name: ziti-mattermost-action-py
on:
  create:
  delete:
  issues:
  issue_comment:
  pull_request_review:
  pull_request_review_comment:
  pull_request:
  push:
  fork:
  release:
    types: [released]

jobs:
  ziti-webhook:
    runs-on: ubuntu-latest
    name: Ziti Mattermost Action - Py
    steps:
    - uses: openziti/ziti-mattermost-action-py@v1
      with:
        # Identity JSON containing key to access a Ziti network
        zitiId: ${{ secrets.ZITI_MATTERMOST_IDENTITY }}

        # URL to post the payload. Note that the `zitiId` must provide access to a service 
        # intercepting `my-mattermost-ziti-server`
        webhookUrl: 'https://{my-mattermost-ziti-server}/hook/{my-mattermost-webhook-id}}'

        eventJson: ${{ toJson(github.event) }}
        senderUsername: "GitHubZ"
        destChannel: "github-notifications"
```

### Inputs

#### `zitiId`

The `zitiId` input is the JSON formatted string of an identity enrolled  in an OpenZiti Network.

The identity can be created by enrolling via the `ziti edge enroll path/to/jwt [flags]` command.  The `ziti` CLI executable can be obtained [here](https://github.com/openziti/ziti/releases/latest).

#### `webhookUrl`

This input value is a Mattermost "Incoming Webhook" URL available over an OpenZiti Network to the identity specified by `zitiId`. This URL should be configured in Mattermost to allow posting to any valid channel with any sender username. The default username will be the `sender.login` from the GitHub Action event.
