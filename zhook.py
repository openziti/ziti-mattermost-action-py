import requests
import openziti
import json
import os

zitiId = os.getenv("INPUT_ZITIID")
url = os.getenv("INPUT_WEBHOOKURL")
eventJsonStr = os.getenv("INPUT_EVENTJSON")

username = os.getenv("INPUT_SENDERUSERNAME", "GitHubZ")
icon = os.getenv("INPUT_SENDERICONULR", "https://github.com/fluidicon.png")
channel = os.getenv("INPUT_DESTCHANNEL", "dev-notifications")

actionRepo = os.getenv("GITHUB_ACTION_REPOSITORY", "ziti-mattermost-action")
eventName = os.getenv("GITHUB_EVENT_NAME", "unspecified")

def createTitle(eventJson):
  repoJson = eventJson["repository"]
  senderJson = eventJson["sender"]

  title = f"{eventName.capitalize().replace('_',' ')}"

  try:
    action = eventJson["action"]
    title += f" {action}"
  except:
    pass

  return f"{title} by [{senderJson['login']}]({senderJson['html_url']}) in [{repoJson['full_name']}]({repoJson['html_url']})"  

def createEventBody(eventName, eventJsonStr):
  eventJson = json.loads(eventJsonStr)
  repoJson = eventJson["repository"]
  senderJson = eventJson["sender"]

  body = {
    "username": username, 
    "icon_url": icon,
    "channel": channel,
    "props": { "card": f"```json\n{eventJsonStr}\n```" },
  }

  attachment = {
    "author_name": senderJson['login'],
    "author_icon": senderJson['avatar_url'],
    "author_link": senderJson['html_url'],
    "footer": actionRepo,
    "footer_icon": "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true",
  }

  if eventName == "push":
    body["text"] = createTitle(eventJson)
    commits = eventJson["commits"]
    pushBody = f"Pushed [{len(commits)} commit(s)]({eventJson['compare']}) to {eventJson['ref']}"
    for c in commits:
      pushBody += f"\n[`{c['id'][:6]}`]({c['url']}) {c['message']}"
    attachment["color"] = "#000000"
    attachment["text"] = pushBody

  elif eventName == "pull_request":
    body["text"] = createTitle(eventJson)
    prJson = eventJson["pull_request"]
    attachment["color"] = "#00FF00"
    attachment["title"] = prJson["title"]
    attachment["title_link"] = prJson["html_url"]

    bodyTxt = prJson['body']
    if bodyTxt is not None:
      bodyTxt += "\n"
    bodyTxt += "#new-pull-request"
    attachment["text"] = bodyTxt

    attachment["thumb_url"] = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true"
  
  elif eventName == "pull_request_review_comment":
    body["text"] = createTitle(eventJson)
    commentJson = eventJson["comment"]
    prJson = eventJson['pull_request']
    bodyTxt = f"[Comment]({commentJson['html_url']}) in [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']}):\n"
    bodyTxt += f"{commentJson['body']}"
    attachment["text"] = bodyTxt
  
  elif eventName == "pull_request_review":
    body["text"] = createTitle(eventJson)
    reviewJson = eventJson["review"]
    reviewState = reviewJson['state']
    prJson = eventJson['pull_request']
    bodyTxt = f"[Review]({reviewJson['html_url']}) of [PR#{prJson['number']}: {prJson['title']}]({prJson['html_url']}):\n"
    bodyTxt += f"Review State: {reviewState.capitalize()}\n"
    bodyTxt += f"{reviewJson['body']}"
    attachment["text"] = bodyTxt

    if reviewState == "approved":
      attachment["color"] = "#00FF00"
      attachment["thumb_url"] = "https://raw.githubusercontent.com/openziti/branding/main/images/ziggy/closeups/Ziggy-Dabbing.png"
  
  else:
    attachment["color"] = "#FFFFFF"
    attachment["text"] = createTitle(eventJson)
    attachment["fallback"] = f"{eventName.capitalize().replace('_',' ')} by {senderJson['login']} in {repoJson['full_name']}"

  body["attachments"] = [attachment]

  return body

if __name__ == '__main__':
  # Setup Ziti identity
  idFilename = "id.json"
  os.environ["ZITI_IDENTITIES"] = idFilename
  with open(idFilename, 'w') as f:
    f.write(zitiId)

  # Setup webhook JSON
  eventName = eventName.lower()
  body = createEventBody(eventName, eventJsonStr)

  # Post the webhook over Ziti
  headers = {'Content-Type': 'application/json',}
  jsonData = json.dumps(body)
  print(f"{jsonData}")

  with openziti.monkeypatch():
    try:
      r = requests.post(url, headers=headers, data=jsonData)
      print(f"Response Status: {r.status_code}")
      print(r.headers)
      print(r.content)
    except Exception as e:
      print(f"Error posting webhook: {e}")

