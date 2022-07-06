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

def addFooter(attachment) :
  attachment["footer"] = actionRepo
  attachment["footer_icon"] = "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true"

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
  eventJson = json.loads(eventJsonStr)
  repoJson = eventJson["repository"]
  senderJson = eventJson["sender"]

  body = {
    "username": username, 
    "icon_url": icon,
    "channel": channel,
  }
  body["text"] = f"{eventName} by [{senderJson['login']}]({senderJson['html_url']}) in [{repoJson['name']}]({repoJson['html_url']})"

  attachment = {
    "color": "#00FF00",
    "author_name": "smilindave26",
    "author_icon": "https://avatars.githubusercontent.com/u/19175177?v=4",
    "author_link": "https://github.com/smilindave26",
    "title": "Update to TSDK v0.18.10 #137",
    "title_link": "https://github.com/openziti/ziti-sdk-swift/pull/137",
    "text": "No description provided.\n#new-pull-request",
    "thumb_url": "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true",
  }
  addFooter(attachment)

  body["attachments"] = [attachment]

  card = f"```json\n{eventJsonStr}\n```"
  body["props"] = {
    "card": card
  }

  eventName = eventName.lower()
  if eventName == "push":
    print("Gotcha PUSH")
  elif eventName == "pull-request":
    print("Gottha pull-request")
  else:
    print(f"Gotcha some other event {eventName}")

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

