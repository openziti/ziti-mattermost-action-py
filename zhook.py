#!/usr/bin/env python3

import argparse
import base64
import json
import os
import sys

import openziti
import requests


class MattermostWebhookBody:
  actionRepoIcon = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true"
  prThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Chef-Closeup.png?raw=true"
  prApprovedThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Dabbing.png?raw=true"
  issueThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-has-an-Idea-Closeup.png?raw=true"
  # releaseThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Cash-Money-Closeup.png?raw=true"
  releaseThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Parties-Closeup.png?raw=true"
  fipsReleaseThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-The-Cop-Closeup.png?raw=true"
  watchThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-is-Star-Struck.png?raw=true"
  failureThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Angry-Closeup.png?raw=true"

  prColor = "#32CD32"
  pushColor = "#708090"
  issueColor = "#FFA500"
  releaseColor = "#DB7093"
  todoColor = "#FFFFFF"
  watchColor = "#FFD700"
  failureColor = "#FF0000"

  def __init__(self, username, icon, eventName, eventJson, actionRepo):
    self.username = username
    self.icon = icon
    self.eventName = eventName.lower()
    self.eventJson = eventJson
    self.actionRepo = actionRepo
    self.event = json.loads(eventJson)
    self.repo = self.event["repository"]
    self.sender = self.event["sender"]

    self.body = {
      "username": self.sender['login'],
      "icon_url": self.sender['avatar_url'],
      "props": {"card": f"```json\n{self.eventJson}\n```"},
    }

    # self.attachment = {
    #   "author_name": self.senderJson['login'],
    #   "author_icon": self.senderJson['avatar_url'],
    #   "author_link": self.senderJson['html_url'],
    #   "footer": self.actionRepo,
    #   "footer_icon": self.actionRepoIcon,
    # }
    self.attachment = {
    }

    if eventName == "push":
      self.addPushDetails()
    elif eventName == "pull_request":
      self.addPullRequestDetails()
    elif eventName == "pull_request_review_comment":
      self.addPullRequestReviewCommentDetails()
    elif eventName == "pull_request_review":
      self.addPullRequestReviewDetails()
    elif eventName == "delete":
      self.addDeleteDetails()
    elif eventName == "create":
      self.addCreateDetails()
    elif eventName == "issues":
      self.addIssuesDetails()
    elif eventName == "issue_comment":
      self.addIssueCommentDetails()
    elif eventName == "fork":
      self.addForkDetails()
    elif eventName == "release":
      self.addReleaseDetails()
    elif eventName == "repository_dispatch":
      event_type = self.event.get("action", None)
      if event_type == "ziti_release":
        self.addFipsReleaseDetails()
      elif event_type == "ziti_promote_stable":
        self.addFipsPromoteStableDetails()
      else:
        self.addDispatchFallbackDetails()
    elif eventName == "watch":
      self.addWatchDetails()
    elif eventName == "workflow_dispatch":
      workflow = self.event.get("workflow", "")
      if "release" in workflow:
        self.addFipsReleaseDetails()
      elif "promote" in workflow:
        self.addFipsPromoteStableDetails()
      else:
        self.addDispatchFallbackDetails()
    elif eventName == "workflow_failure":
      self.addWorkflowFailureDetails()
    else:
      self.addDefaultDetails()

    self.body["attachments"] = [self.attachment]

  def createTitle(self):
    login = self.sender["login"]
    loginUrl = self.sender["html_url"]
    repoName = self.repo["full_name"]
    repoUrl = self.repo["html_url"]
    # starCount = self.repoJson["stargazers_count"]
    # starUrl = f"{repoUrl}/stargazers"

    title = f"{self.eventName.capitalize().replace('_', ' ')}"

    try:
      action = self.event["action"]
      title += f" {action}"
    except Exception:
      pass

    # return f"{title} by [{login}]({loginUrl}) in [{repoName}]({repoUrl}) ([{starCount} :star:]({starUrl}))"
    return f"{title} by [{login}]({loginUrl}) in [{repoName}]({repoUrl})"

  def addPushDetails(self):
    self.body["text"] = self.createTitle()
    forced = self.event["forced"]
    commits = self.event["commits"]

    if forced:
      pushBody = "Force-pushed "
    else:
      pushBody = "Pushed "

    pushBody += f"[{len(commits)} commit(s)]({self.event['compare']}) to {self.event['ref']}"
    for c in commits:
      pushBody += f"\n[`{c['id'][:6]}`]({c['url']}) {c['message']}"
    self.attachment["color"] = self.pushColor
    self.attachment["text"] = pushBody

  def addPullRequestDetails(self):
    self.body["text"] = self.createTitle()
    prJson = self.event["pull_request"]
    headJson = prJson["head"]
    baseJson = prJson["base"]
    self.attachment["color"] = self.prColor
    bodyTxt = f"Pull request [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']})\n"
    bodyTxt += f"{headJson['label']} -> {baseJson['label']}\n"

    try:
      reviewers = prJson["requested_reviewers"]
      bodyTxt += "Reviewer(s):"
      for r in reviewers:
        bodyTxt += f" [{r['login']}]({r['html_url']}),"
    except Exception:
      pass

    try:
      reviewers = prJson["requested_teams"]
      for r in reviewers:
        bodyTxt += f" [{r['name']}]({r['html_url']}),"
    except Exception:
      pass

    bodyTxt = bodyTxt.rstrip(',')
    bodyTxt += "\n"

    try:
      bodyContent = prJson['body']
      if bodyContent is not None:
        bodyTxt += f"{bodyContent}"
    except Exception:
      pass

    bodyTxt += "\n#new-pull-request"

    self.attachment["color"] = self.prColor
    self.attachment["text"] = bodyTxt
    self.attachment["thumb_url"] = self.prThumbnail

  def addPullRequestReviewCommentDetails(self):
    self.body["text"] = self.createTitle()
    commentJson = self.event["comment"]
    prJson = self.event['pull_request']
    bodyTxt = f"[Comment]({commentJson['html_url']}) in [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']}):\n"

    try:
      bodyTxt += f"{commentJson['body']}"
    except Exception:
      pass

    self.attachment["color"] = self.prColor
    self.attachment["text"] = bodyTxt

  def addPullRequestReviewDetails(self):
    self.body["text"] = self.createTitle()
    reviewJson = self.event["review"]
    reviewState = reviewJson['state']
    prJson = self.event['pull_request']
    bodyTxt = f"[Review]({reviewJson['html_url']}) of [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']})\n"
    bodyTxt += f"Review State: {reviewState.capitalize()}\n"
    bodyTxt += f"{reviewJson['body']}"
    self.attachment["text"] = bodyTxt

    self.attachment["color"] = self.prColor
    if reviewState == "approved":
      self.attachment["thumb_url"] = self.prApprovedThumbnail

  def addDeleteDetails(self):
    self.body["text"] = self.createTitle()
    self.attachment["text"] = f"Deleted {self.event['ref_type']} \"{self.event['ref']}\""

  def addCreateDetails(self):
    self.body["text"] = self.createTitle()
    self.attachment["text"] = f"Created {self.event['ref_type']} \"{self.event['ref']}\""

  def addIssuesDetails(self):
    self.body["text"] = self.createTitle()
    action = self.event["action"]
    issueJson = self.event["issue"]
    issueTitle = issueJson["title"]
    issueUrl = issueJson["html_url"]
    issueBody = issueJson["body"]

    self.attachment["color"] = self.issueColor
    if action == "created" or action == "opened":
      self.attachment["thumb_url"] = self.issueThumbnail

    bodyText = f"Issue [{issueTitle}]({issueUrl})\n"
    try:
      assignees = issueJson["assignees"]
      bodyText += "Assignee(s):"
      for a in assignees:
        bodyText += f" [{a['login']}]({a['html_url']}),"
      bodyText = bodyText.rstrip(',')
      bodyText += "\n"
    except Exception:
      pass

    bodyText += f"{issueBody}"
    self.attachment["text"] = bodyText

  def addIssueCommentDetails(self):
    self.body["text"] = self.createTitle()
    commentJson = self.event["comment"]
    commentBody = commentJson["body"]
    commentUrl = commentJson["html_url"]
    issueJson = self.event["issue"]
    issueTitle = issueJson["title"]
    issueNumber = issueJson["number"]

    prJson = issueJson.get("pull_request")
    if prJson is not None:
      bodyTxt = f"[Comment]({commentUrl}) on [PR#{issueNumber}: {issueTitle}]({commentUrl})\n"
      self.attachment["color"] = self.prColor
    else:
      bodyTxt = f"[Comment]({commentUrl}) on [Issue#{issueNumber}: {issueTitle}]({commentUrl})\n"
      self.attachment["color"] = self.issueColor

    bodyTxt += commentBody
    self.attachment["text"] = bodyTxt

  def addForkDetails(self):
    self.body["text"] = self.createTitle()
    forkeeJson = self.event["forkee"]
    bodyText = f"Forkee [{forkeeJson['full_name']}]({forkeeJson['html_url']})"
    self.attachment["text"] = bodyText

  def addReleaseDetails(self):
    self.body["text"] = self.createTitle()
    action = self.event["action"]
    releaseJson = self.event["release"]
    isDraft = releaseJson["draft"]
    isPrerelease = releaseJson["prerelease"]

    self.attachment["color"] = self.releaseColor
    if action == "released":
      self.attachment["thumb_url"] = self.releaseThumbnail

    if isDraft:
      bodyText = "Draft release"
    elif isPrerelease:
      bodyText = "Prerelease "
    else:
      bodyText = "Release"

    releaseTitle = releaseJson.get("name")
    tagName = releaseJson["tag_name"]

    if releaseTitle is None:
      releaseTitle = f" {tagName}"
    else:
      releaseTitle += f" ({tagName})"

    bodyText += f" [{releaseTitle}]({releaseJson['html_url']})"

    releaseBody = releaseJson.get("body")
    if releaseBody is not None:
      bodyText += f"\n{releaseBody}"

    self.attachment["text"] = bodyText

  def addFipsReleaseDetails(self):
    # Pre-release announcement (ziti_release or workflow_dispatch with release workflow)
    # Check both client_payload (repository_dispatch) and inputs (workflow_dispatch)
    payload = self.event.get("client_payload", {})
    inputs = self.event.get("inputs", {})
    version = payload.get("version") or inputs.get("version")
    if not version:
        self.attachment["text"] = "[ziti-fips] Pre-release published, but version not found in event."
        return
    if not version.startswith("v"):
        version = f"v{version}"
    repo = self.repo["full_name"]
    release_url = f"https://github.com/{repo}/releases/tag/{version}"
    self.body["text"] = f"FIPS Pre-release published by [{repo}](https://github.com/{repo})"
    self.attachment["color"] = self.releaseColor
    self.attachment["thumb_url"] = self.fipsReleaseThumbnail
    self.attachment["text"] = f"FIPS Pre-release [{version}]({release_url}) is now available."

  def addFipsPromoteStableDetails(self):
    # Promotion to stable announcement (ziti_promote_stable or workflow_dispatch with promote workflow)
    # Check both client_payload (repository_dispatch) and inputs (workflow_dispatch)
    payload = self.event.get("client_payload", {})
    inputs = self.event.get("inputs", {})
    version = payload.get("version") or inputs.get("version")
    if not version:
        self.attachment["text"] = "[ziti-fips] Stable promotion, but version not found in event."
        return
    if not version.startswith("v"):
        version = f"v{version}"
    repo = self.repo["full_name"]
    release_url = f"https://github.com/{repo}/releases/tag/{version}"
    self.body["text"] = f"FIPS Release promoted to stable in [{repo}](https://github.com/{repo})"
    self.attachment["color"] = self.releaseColor
    self.attachment["thumb_url"] = self.fipsReleaseThumbnail
    self.attachment["text"] = f"FIPS Release [{version}]({release_url}) has been promoted to stable."

  def addDispatchFallbackDetails(self):
    # Generic fallback for repository_dispatch or workflow_dispatch that don't match FIPS handlers
    event_type = self.event.get("action", None)
    workflow = self.event.get("workflow", "")
    payload = self.event.get("client_payload", {})
    inputs = self.event.get("inputs", {})
    repo = self.repo["full_name"]

    self.body["text"] = f"Dispatch event received by [{repo}](https://github.com/{repo})"
    self.attachment["color"] = self.releaseColor

    details = []
    if event_type:
      details.append(f"Event type: `{event_type}`")
    if workflow:
      details.append(f"Workflow: `{workflow}`")
    if payload:
      details.append(f"Payload: ```json\n{json.dumps(payload, indent=2)}\n```")
    if inputs:
      details.append(f"Inputs: ```json\n{json.dumps(inputs, indent=2)}\n```")

    self.attachment["text"] = "\n".join(details) if details else "No additional details"

  def addWatchDetails(self):
    self.body["text"] = f"{self.createTitle()} #stargazer"
    login = self.sender["login"]
    loginUrl = self.sender["html_url"]
    userUrl = self.sender["url"]
    starCount = self.repo["stargazers_count"]

    bodyText = f"[{login}]({loginUrl}) is stargazer number {starCount}\n\n"

    try:
      r = requests.get(userUrl)
      print(f"Get User Info Response Status: {r.status_code}")
      # print(r.headers)
      # print(r.content)

      userDetailsJson = json.loads(r.content)

      name = userDetailsJson['name']
      company = userDetailsJson['company']
      location = userDetailsJson['location']
      email = userDetailsJson['email']
      twitter = userDetailsJson['twitter_username']
      blog = userDetailsJson['blog']
      bio = userDetailsJson['bio']

      if name is not None and name:
        bodyText += f"\nName: {name}  "

      if company is not None and company:
        bodyText += f"\nCompany: {company}  "

      if location is not None and location:
        bodyText += f"\nLocation: {location}  "

      if email is not None and email:
        bodyText += f"\nEmail: {email}  "

      if twitter is not None and twitter:
        bodyText += f"\nTwitter: {twitter}  "

      if blog is not None and blog:
        bodyText += f"\nBlog: {blog}  "

      if bio is not None and bio:
        bodyText += f"\nBio: {bio}  "

    except Exception as e:
      print(f"Exception retrieving user info: {e}")

    try:
      # HTML not supported in Mattermost markdown...
      # bodyText += "\n\n<details><summary>GitHub Stats</summary>"
      bodyText += f"\n\n![Github Stats](https://github-readme-stats.vercel.app/api?username={login}&hide=stars&hide_rank=true)"
      # bodyText += "\n</details>"

      # These stats only cover the repos in the user's home (not all languages used in commits in any repo...)
      # bodyText += "\n\n<details><summary>Top Langs</summary>"
      # bodyText += f"\n\n![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={login}&layout=compact)"
      # bodyText += "\n</details>"
    except Exception as e:
      print(f"Exception retrieving stats image: {e}")

    self.attachment["thumb_url"] = self.watchThumbnail
    self.attachment["color"] = self.watchColor
    self.attachment["text"] = bodyText

  def addWorkflowFailureDetails(self):
    self.body["text"] = f"Workflow failure by [{self.sender['login']}]({self.sender['html_url']}) in [{self.repo['full_name']}]({self.repo['html_url']})"
    self.attachment["color"] = self.failureColor
    self.attachment["thumb_url"] = self.failureThumbnail
    self.attachment["text"] = self.event["action"]

  def addDefaultDetails(self):
    self.attachment["color"] = self.todoColor
    self.attachment["text"] = self.createTitle()
    self.attachment["fallback"] = f"{self.eventName.capitalize().replace('_', ' ')} by {self.sender['login']} in {self.repo['full_name']}"

  def dumpJson(self):
    return json.dumps(self.body)


def _try_parse_json(s: str):
  """Try to parse a string as JSON and return True if successful."""
  try:
    json.loads(s)
    return True
  except Exception:
    return False


def _try_decode_b64_to_json_str(s: str):
  """Try to decode a base64 string to a JSON string with various fallback strategies."""
  if s is None:
    return None
  try:
    # strict validation first
    decoded = base64.b64decode(s, validate=True)
    decoded_str = decoded.decode('utf-8')
    if _try_parse_json(decoded_str):
      return decoded_str
  except Exception:
    # Try non-strict decode
    try:
      decoded = base64.b64decode(s)
      decoded_str = decoded.decode('utf-8')
      if _try_parse_json(decoded_str):
        return decoded_str
    except Exception:
      pass
    # As a last resort, try appending one to four '=' padding chars
    for i in range(1, 5):
      try:
        s_padded = s + ("=" * i)
        decoded = base64.b64decode(s_padded)
        decoded_str = decoded.decode('utf-8')
        if _try_parse_json(decoded_str):
          return decoded_str
      except Exception:
        continue
  return None


def _safe_hint(s):
  """Create a safe string hint for debugging purposes."""
  if s is None:
    return "<none>"
  hint_len = len(s)
  head = s[:8].replace('\n', ' ')
  return f"len={hint_len}, startswith='{head}...'"


def generate_json_schema(obj, max_depth=10, current_depth=0):
  """Generate a schema representation of a JSON object by inferring types from values."""
  if current_depth >= max_depth:
    return "<max_depth_reached>"

  if obj is None:
    return "null"
  elif isinstance(obj, bool):
    return "boolean"
  elif isinstance(obj, int):
    return "integer"
  elif isinstance(obj, float):
    return "number"
  elif isinstance(obj, str):
    return "string"
  elif isinstance(obj, list):
    if len(obj) == 0:
      return "array[]"
    # Get schema of first element as representative
    element_schema = generate_json_schema(obj[0], max_depth, current_depth + 1)
    return f"array[{element_schema}]"
  elif isinstance(obj, dict):
    schema = {}
    for key, value in obj.items():
      schema[key] = generate_json_schema(value, max_depth, current_depth + 1)
    return schema
  else:
    return "unknown"


def generate_test_event(event_type):
  """Generate a test GitHub event JSON for the specified event type."""
  base_repo = {
    "full_name": "testuser/testrepo",
    "html_url": "https://github.com/testuser/testrepo",
    "stargazers_count": 42
  }

  base_sender = {
    "login": "testuser",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345",
    "html_url": "https://github.com/testuser",
    "url": "https://api.github.com/users/testuser"
  }

  events = {
    "push": {
      "repository": base_repo,
      "sender": base_sender,
      "forced": False,
      "commits": [
        {
          "id": "abc123def456",
          "url": "https://github.com/testuser/testrepo/commit/abc123",
          "message": "Test commit message"
        }
      ],
      "compare": "https://github.com/testuser/testrepo/compare/abc123..def456",
      "ref": "refs/heads/main"
    },
    "pull_request": {
      "action": "opened",
      "repository": base_repo,
      "sender": base_sender,
      "pull_request": {
        "number": 123,
        "title": "Test Pull Request",
        "html_url": "https://github.com/testuser/testrepo/pull/123",
        "body": "This is a test PR description",
        "head": {"label": "testuser:feature-branch"},
        "base": {"label": "testuser:main"},
        "requested_reviewers": []
      }
    },
    "issues": {
      "action": "opened",
      "repository": base_repo,
      "sender": base_sender,
      "issue": {
        "number": 456,
        "title": "Test Issue",
        "html_url": "https://github.com/testuser/testrepo/issues/456",
        "body": "This is a test issue description",
        "assignees": []
      }
    },
    "release": {
      "action": "released",
      "repository": base_repo,
      "sender": base_sender,
      "release": {
        "name": "v1.0.0",
        "tag_name": "v1.0.0",
        "html_url": "https://github.com/testuser/testrepo/releases/tag/v1.0.0",
        "body": "## What's Changed\n- Feature A\n- Bug fix B",
        "draft": False,
        "prerelease": False
      }
    },
    "watch": {
      "action": "started",
      "repository": base_repo,
      "sender": base_sender
    },
    "fork": {
      "repository": base_repo,
      "sender": base_sender,
      "forkee": {
        "full_name": "anotheruser/testrepo",
        "html_url": "https://github.com/anotheruser/testrepo"
      }
    }
  }

  if event_type not in events:
    available = ", ".join(sorted(events.keys()))
    raise ValueError(f"Unknown event type: {event_type}. Available: {available}")

  return json.dumps(events[event_type])


@openziti.zitify()
def doPost(url, payload):
  """Post webhook payload to the specified URL over Ziti."""
  # Single request doesn't need session management
  response = requests.post(url, json=payload)
  print(f"Response Status: {response.status_code}")
  print(response.headers)
  print(response.content)
  return response


if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(
    description='Post GitHub events to Mattermost over Ziti',
    epilog='''
Environment Variables (set by GitHub Actions or manually for testing):

Required:
  INPUT_ZITIID              Ziti identity JSON (from: secrets.ZITI_IDENTITY)
                            Alternative: INPUT_ZITIJWT for enrollment JWT
  INPUT_WEBHOOKURL          Mattermost webhook URL (from: secrets.WEBHOOK_URL)
  INPUT_EVENTJSON           GitHub event JSON (from: toJson(github.event))
  GITHUB_EVENT_NAME         Event type (from: github.event_name)
                            Examples: push, pull_request, issues, release

Optional:
  INPUT_SENDERUSERNAME      Mattermost username (default: sender.login from event)
  INPUT_SENDERICONURL       Icon URL (default: sender.avatar_url from event)
  GITHUB_ACTION_REPOSITORY  Action repo (from: github.action_repository)
  INPUT_ZITILOGLEVEL        Ziti log level 0-6 (default: 3)

Test Mode Examples:
  # Quick test with push event
  INPUT_ZITIID="$(< ziti-id.json)" INPUT_WEBHOOKURL="http://webhook.ziti/hooks/ID" \\
    python3 zhook.py --test

  # Test pull request with dry-run
  INPUT_ZITIID="$(< ziti-id.json)" python3 zhook.py --test --event-type pull_request --dry-run

  # List available event types
  python3 zhook.py --help
''',
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument(
    '--test',
    action='store_true',
    help='Run in test mode with generated event data'
  )
  parser.add_argument(
    '--event-type',
    default='push',
    choices=['push', 'pull_request', 'issues', 'release', 'watch', 'fork'],
    help='Event type for test mode (default: push)'
  )
  parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Print the webhook payload without sending it'
  )

  args = parser.parse_args()

  # Test mode: generate dummy data
  if args.test:
    print(f"=== TEST MODE: Generating {args.event_type} event ===")
    if not os.getenv("INPUT_WEBHOOKURL"):
      os.environ["INPUT_WEBHOOKURL"] = "http://127.0.0.1:2171/post"
      print(f"Using default webhook URL: {os.environ['INPUT_WEBHOOKURL']}")
    if not os.getenv("INPUT_ZITIID") and not os.getenv("INPUT_ZITIJWT"):
      print("ERROR: Test mode requires INPUT_ZITIID or INPUT_ZITIJWT environment variable")
      print("Set one of these to your Ziti identity JSON or enrollment JWT")
      sys.exit(1)

    os.environ["INPUT_EVENTJSON"] = generate_test_event(args.event_type)
    os.environ["GITHUB_EVENT_NAME"] = args.event_type
    os.environ["INPUT_SENDERUSERNAME"] = os.getenv("INPUT_SENDERUSERNAME", "TestUser")
    os.environ["INPUT_SENDERICONURL"] = os.getenv("INPUT_SENDERICONURL", "https://github.com/fluidicon.png")
    os.environ["GITHUB_ACTION_REPOSITORY"] = os.getenv("GITHUB_ACTION_REPOSITORY", "testuser/testrepo")
    print("")

  url = os.getenv("INPUT_WEBHOOKURL")

  # Handle event JSON provided inline; auto-detect if it's JSON or base64-encoded JSON

  eventInput = os.getenv("INPUT_EVENTJSON")
  eventJson = ""

  if eventInput and _try_parse_json(eventInput):
    eventJson = eventInput
    print("Detected valid JSON in INPUT_EVENTJSON")
  else:
    decoded = _try_decode_b64_to_json_str(eventInput)
    if decoded is not None:
      eventJson = decoded
      print("Detected base64-encoded JSON in INPUT_EVENTJSON and decoded it")

  if not eventJson:
    print("ERROR: No valid event JSON provided in INPUT_EVENTJSON")
    exit(1)
  username = os.getenv("INPUT_SENDERUSERNAME")
  icon = os.getenv("INPUT_SENDERICONURL")
  actionRepo = os.getenv("GITHUB_ACTION_REPOSITORY")
  eventName = os.getenv("INPUT_EVENTNAME") or os.getenv("GITHUB_EVENT_NAME")
  zitiLogLevel = os.getenv("INPUT_ZITILOGLEVEL")
  if zitiLogLevel is not None:
    os.environ["ZITI_LOG"] = zitiLogLevel
    os.environ["TLSUV_DEBUG"] = zitiLogLevel

  # Set up Ziti identity
  zitiJwtInput = os.getenv("INPUT_ZITIJWT")
  zitiIdJson = None            # validated JSON string form
  if zitiJwtInput is not None:
    # Expect enroll to return the identity JSON content
    try:
      enrolled = openziti.enroll(zitiJwtInput)
      # Validate that the returned content is JSON
      json.loads(enrolled)
      zitiIdJson = enrolled
      print("Obtained valid identity JSON from INPUT_ZITIJWT enrollment")
    except Exception as e:
      print(f"ERROR: Failed to enroll or parse identity from INPUT_ZITIJWT: {e}")
      exit(1)
  else:
    # Support inline JSON or base64-encoded identity JSON from a single variable
    zitiIdInput = os.getenv("INPUT_ZITIID")

    # Prefer valid inline JSON if present
    if zitiIdInput and _try_parse_json(zitiIdInput):
      zitiIdJson = zitiIdInput
      print("Detected valid inline JSON in INPUT_ZITIID")
    else:
      # Try decoding inline as base64 if provided and not valid JSON
      decodedInline = _try_decode_b64_to_json_str(zitiIdInput) if zitiIdInput else None
      if decodedInline is not None:
        zitiIdJson = decodedInline
        print("Detected base64-encoded identity in INPUT_ZITIID and decoded it")

    if zitiIdJson is None:
      print("ERROR: no Ziti identity provided, set INPUT_ZITIID (inline JSON or base64-encoded), or INPUT_ZITIJWT")
      exit(1)

  idFilename = "id.json"
  with open(idFilename, 'w') as f:
    f.write(zitiIdJson)

  # Defer openziti.load() until inside the monkeypatch context to keep
  # initialization/teardown paired and avoid double-free on shutdown.

  # Create webhook body
  try:
    mwb = MattermostWebhookBody(username, icon, eventName, eventJson, actionRepo)
  except Exception as e:
    print(f"Exception creating webhook body: {e}")
    raise e

  # Post the webhook over Ziti
  # Build dict payload; requests will set Content-Type when using json=
  payload = mwb.body

  # Dry-run mode: print payload and exit
  if args.dry_run:
    print("=== DRY RUN MODE: Webhook payload ===")
    print(f"URL: {url}")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("=== Dry run complete (not sent) ===")
    sys.exit(0)

  # Load the identity for Ziti operations
  try:
    openziti.load(idFilename)
  except Exception as e:
    print(f"ERROR: Failed to load Ziti identity: {e}")
    print(f"DEBUG: INPUT_ZITIID hint: {_safe_hint(os.getenv('INPUT_ZITIID'))}")
    print(f"DEBUG: zitiIdJson len={len(zitiIdJson) if zitiIdJson else 0}")
    raise e

  # Post the webhook over Ziti
  try:
    print(f"Posting webhook to {url} with JSON payload keys {list(payload.keys())}")
    response = doPost(url, payload)
  except Exception as e:
    print(f"Exception posting webhook: {e}")
    raise e
  finally:
    openziti.shutdown()
