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

  title = f"{eventName.capitalize()}"

  if eventName == "pull_request":
    title = f"Pull request {eventJson['action']}"

  return f"{title} by [{senderJson['login']}]({senderJson['html_url']}) in [{repoJson['name']}]({repoJson['html_url']})"

def createAttachment(eventJson):
  senderJson = eventJson["sender"]

  attachment = {
    "author_name": senderJson['login'],
    "author_icon": senderJson['avatar_url'],
    "author_link": senderJson['html_url'],
    "footer": actionRepo,
    "footer_icon": "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true",
  }

  if eventName == "push":
    commits = eventJson["commits"]
    pushBody = f"[{len(commits)} commits]({eventJson['compare']}"
    for c in commits:
      pushBody = f"\n[`{c['id']}`](c['url']) {c['message']}"

    attachment["text"] = pushBody
  elif eventName == "pull_request":
    prJson = eventJson["pull_request"]
    attachment["color"] = "#00FF00"
    attachment["title"] = prJson["title"]
    attachment["title_link"] = prJson["html_url"]
    attachment["text"] = f"{prJson['body'] or ''}\n#new-pull-request"
    attachment["thumb_url"] = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true"
  else:
    print(f"Gotcha some other event {eventName}")

  return attachment

if __name__ == '__main__':
  # Temporaily print out the env... (TODO: remove this)
  for k, v in os.environ.items():
    print(f'{k}={v}')

  #
  # Setup Ziti identity
  #  
  idFilename = "id.json"
  os.environ["ZITI_IDENTITIES"] = idFilename
  with open(idFilename, 'w') as f:
    f.write(zitiId)

  #
  # Setup webhook JSON
  #
  eventName = eventName.lower()
  eventJson = json.loads(eventJsonStr)

  body = {
    "username": username, 
    "icon_url": icon,
    "channel": channel,
    "props": { "card": f"```json\n{eventJsonStr}\n```" },
  }
  body["text"] = createTitle(eventJson)
  body["attachments"] = [createAttachment(eventJson)]

  #
  # Post the webhook over Ziti
  #
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

