# Testing zhook.py

## Quick Start

Run tests with dummy event data using the `--test` flag:

```bash
# Basic test with push event
INPUT_ZITIID="$(< ziti-id.json)" \
INPUT_WEBHOOKURL="http://webhook.mattermost.ziti.internal/hooks/<incoming webhook secret>" \
python3 zhook.py --test

# Test different event types
python3 zhook.py --test --event-type pull_request
python3 zhook.py --test --event-type issues

# Preview payload without sending
python3 zhook.py --test --dry-run
```

## Required Inputs

**Ziti Identity** (one of):
- `INPUT_ZITIID` - Identity JSON, e.g., `"$(< file.json)"` or unescaped string
- `INPUT_ZITIID` - Base64-encoded identity JSON
- `INPUT_ZITIJWT` - Enrollment JWT token

**Webhook URL**:
- `INPUT_WEBHOOKURL` - Mattermost webhook URLs accessible via Ziti, one per line
- Optional in test mode (defaults to `http://127.0.0.1:2171/post` for httpbin testing)

## Test Modes

**`--test`** - Generate dummy GitHub event data automatically

**`--event-type TYPE`** - Choose event: `push`, `pull_request`, `issues`, `release`, `watch`, `fork` (default: push)

**`--dry-run`** - Print payload without sending (no Ziti connection needed)

## Help

Run `python3 zhook.py --help` to see all environment variables and their GitHub Actions sources.
