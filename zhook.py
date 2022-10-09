import requests
import openziti
import json
import sys
import os


class MattermostWebhookBody:
  actionRepoIcon = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true"
  prThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Chef-Closeup.png?raw=true"
  prApprovedThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Dabbing.png?raw=true"
  issueThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-has-an-Idea-Closeup.png?raw=true"
  # releaseThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Cash-Money-Closeup.png?raw=true"
  releaseThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-Parties-Closeup.png?raw=true"
  watchThumbnail = "https://github.com/openziti/branding/blob/main/images/ziggy/closeups/Ziggy-is-Star-Struck.png?raw=true"

  prColor = "#32CD32"
  pushColor = "#708090"
  issueColor = "#FFA500"
  releaseColor = "#DB7093"
  todoColor = "#FFFFFF"
  watchColor = "#FFD700"

  def __init__(self, username, icon, channel, eventName, eventJsonStr, actionRepo):
    self.username = username
    self.icon = icon
    self.channel = channel
    self.eventName = eventName.lower()
    self.eventJsonStr = eventJsonStr
    self.actionRepo = actionRepo
    self.eventJson = json.loads(eventJsonStr)
    self.repoJson = self.eventJson["repository"]
    self.senderJson = self.eventJson["sender"]

    self.body = {
      # "username": self.username,
      # "icon_url": self.icon,
      "username": self.senderJson['login'],
      "icon_url": self.senderJson['avatar_url'],
      "channel": self.channel,
      "props": {"card": f"```json\n{self.eventJsonStr}\n```"},
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
    elif eventName == "watch":
      self.addWatchDetails()
    else:
      self.addDefaultDetails()

    self.body["attachments"] = [self.attachment]

  def createTitle(self):
    login = self.senderJson["login"]
    loginUrl = self.senderJson["html_url"]
    repoName = self.repoJson["full_name"]
    repoUrl = self.repoJson["html_url"]
    # starCount = self.repoJson["stargazers_count"]
    # starUrl = f"{repoUrl}/stargazers"

    title = f"{self.eventName.capitalize().replace('_',' ')}"

    try:
      action = self.eventJson["action"]
      title += f" {action}"
    except Exception:
      pass

    # return f"{title} by [{login}]({loginUrl}) in [{repoName}]({repoUrl}) ([{starCount} :star:]({starUrl}))"
    return f"{title} by [{login}]({loginUrl}) in [{repoName}]({repoUrl})"

  def addPushDetails(self):
    self.body["text"] = self.createTitle()
    forced = self.eventJson["forced"]
    commits = self.eventJson["commits"]

    if forced:
      pushBody = "Force-pushed "
    else:
      pushBody = "Pushed "

    pushBody += f"[{len(commits)} commit(s)]({self.eventJson['compare']}) to {self.eventJson['ref']}"
    for c in commits:
      pushBody += f"\n[`{c['id'][:6]}`]({c['url']}) {c['message']}"
    self.attachment["color"] = self.pushColor
    self.attachment["text"] = pushBody

  def addPullRequestDetails(self):
    self.body["text"] = self.createTitle()
    prJson = self.eventJson["pull_request"]
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
    commentJson = self.eventJson["comment"]
    prJson = self.eventJson['pull_request']
    bodyTxt = f"[Comment]({commentJson['html_url']}) in [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']}):\n"

    try:
      bodyTxt += f"{commentJson['body']}"
    except Exception:
      pass

    self.attachment["color"] = self.prColor
    self.attachment["text"] = bodyTxt

  def addPullRequestReviewDetails(self):
    self.body["text"] = self.createTitle()
    reviewJson = self.eventJson["review"]
    reviewState = reviewJson['state']
    prJson = self.eventJson['pull_request']
    bodyTxt = f"[Review]({reviewJson['html_url']}) of [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']})\n"
    bodyTxt += f"Review State: {reviewState.capitalize()}\n"
    bodyTxt += f"{reviewJson['body']}"
    self.attachment["text"] = bodyTxt

    self.attachment["color"] = self.prColor
    if reviewState == "approved":
      self.attachment["thumb_url"] = self.prApprovedThumbnail

  def addDeleteDetails(self):
    self.body["text"] = self.createTitle()
    self.attachment["text"] = f"Deleted {self.eventJson['ref_type']} \"{self.eventJson['ref']}\""

  def addCreateDetails(self):
    self.body["text"] = self.createTitle()
    self.attachment["text"] = f"Created {self.eventJson['ref_type']} \"{self.eventJson['ref']}\""

  def addIssuesDetails(self):
    self.body["text"] = self.createTitle()
    action = self.eventJson["action"]
    issueJson = self.eventJson["issue"]
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
    commentJson = self.eventJson["comment"]
    commentBody = commentJson["body"]
    commentUrl = commentJson["html_url"]
    issueJson = self.eventJson["issue"]
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
    forkeeJson = self.eventJson["forkee"]
    bodyText = f"Forkee [{forkeeJson['full_name']}]({forkeeJson['html_url']})"
    self.attachment["text"] = bodyText

  def addReleaseDetails(self):
    self.body["text"] = self.createTitle()
    action = self.eventJson["action"]
    releaseJson = self.eventJson["release"]
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

  def addWatchDetails(self):
    self.body["text"] = f"{self.createTitle()} #stargazer"
    login = self.senderJson["login"]
    loginUrl = self.senderJson["html_url"]
    userUrl = self.senderJson["url"]
    starCount = self.repoJson["stargazers_count"]

    bodyText = f"[{login}]({loginUrl}) is stargazer number {starCount}\n"

    try:
      userUrl = "https://api.github.com/users/vs4vijay"

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

      if name is not None:
        bodyText += f"\nName: {name}  "

      if company is not None:
        bodyText += f"\nCompany: {company}  "

      if location is not None:
        bodyText += f"\nLocation: {location}  "

      if email is not None:
        bodyText += f"\nEmail: {email}  "

      if twitter is not None:
        bodyText += f"\nTwitter: {twitter}  "

      if blog is not None:
        bodyText += f"\nBlog: {blog}  "

      if bio is not None:
        bodyText += f"\nBio: {bio}  "

    except Exception:
      print(f"Exception retrieving user info: {e}")

    ##bodyText += f"\n<details><summary>Github Stats</summary>"
    #bodyText += f"![Github Stats](https://github-readme-stats.vercel.app/api?username={login})"
    ##bodyText += f"</details>"

    ##bodyText += f"\n<details><summary>Languages</summary>"
    #bodyText += f"![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={login}&layout=compact)"
    ##bodyText += f"</details>"

    self.attachment["thumb_url"] = self.watchThumbnail
    self.attachment["color"] = self.watchColor
    self.attachment["text"] = bodyText

  def addDefaultDetails(self):
    self.attachment["color"] = self.todoColor
    self.attachment["text"] = self.createTitle()
    self.attachment["fallback"] = f"{eventName.capitalize().replace('_',' ')} by {self.senderJson['login']} in {self.repoJson['full_name']}"

  def dumpJson(self):
    return json.dumps(self.body)


if __name__ == '__main__':
  zitiId = os.getenv("INPUT_ZITIID")
  url = os.getenv("INPUT_WEBHOOKURL")
  eventJsonStr = os.getenv("INPUT_EVENTJSON")
  username = os.getenv("INPUT_SENDERUSERNAME")
  icon = os.getenv("INPUT_SENDERICONURL")
  channel = os.getenv("INPUT_DESTCHANNEL")
  actionRepo = os.getenv("GITHUB_ACTION_REPOSITORY")
  eventName = os.getenv("GITHUB_EVENT_NAME")

  # Setup Ziti identity
  idFilename = "id.json"
  os.environ["ZITI_IDENTITIES"] = idFilename
  with open(idFilename, 'w') as f:
    f.write(zitiId)

  # Create webhook body
  try:
    mwb = MattermostWebhookBody(username, icon, channel, eventName, eventJsonStr, actionRepo)
  except Exception as e:
    print(f"Exception creating webhook body: {e}")
    sys.exit(-1)

  # Post the webhook over Ziti
  headers = {'Content-Type': 'application/json'}
  data = mwb.dumpJson()
  print(f"{data}")

  with openziti.monkeypatch():
    try:
      r = requests.post(url, headers=headers, data=data)
      print(f"Response Status: {r.status_code}")
      print(r.headers)
      print(r.content)
    except Exception as e:
      print(f"Exception posting webhook: {e}")
      sys.exit(-1)
