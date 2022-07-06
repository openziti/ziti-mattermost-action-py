import requests
import openziti
import json
import os

zitiId = os.getenv("INPUT_ZITIID")
url = os.getenv("INPUT_WEBHOOKURL")
eventJson = os.getenv("INPUT_EVENTJSON")

username = os.getenv("INPUT_SENDERUSERNAME", "GitHubZ")
icon = os.getenv("INPUT_SENDERICONULR", "https://github.com/fluidicon.png")
channel = os.getenv("INPUT_DESTCHANNEL", "dev-notifications")

actionRepo = os.getenv("GITHUB_ACTION_REPOSITORY", "ziti-mattermost-action")
eventName = os.getenv("GITHUB_EVENT_NAME", "unspecified")

# Mattermost addressing
body = {
  "username": username, 
  "icon_url": icon,
  "channel": channel,
}

card = f"```json\n{eventJson}\n```"
body["props"] = {
  "card": card
}

attachment = {
  "color": "#00FF00",
  "pretext": "Pull request opened by [smilindave26](https://avatars.githubusercontent.com/u/19175177?v=4) in [openziti/ziti-sdk-swift](https://github.com/openziti/ziti-sdk-swift)",
  "fallback": "Pull request opend by smilindave26 in openziti/ziti-sdk-swift",
  "author_name": "smilindave26",
  "author_icon": "https://avatars.githubusercontent.com/u/19175177?v=4",
  "author_link": "https://github.com/smilindave26",
  "title": "Update to TSDK v0.18.10 #137",
  "title_link": "https://github.com/openziti/ziti-sdk-swift/pull/137",
  "text": "No description provided.\n#new-pull-request",
  "footer": actionRepo,
  "footer_icon": "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true",
  "thumb_url": "https://github.com/openziti/branding/blob/main/images/ziggy/png/Ziggy-Gits-It.png?raw=true",
}
body["attachments"] = [attachment]

if __name__ == '__main__':
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
  match eventName.lower():
    case "push":
      print("Gotcha PUSH")
    case _:
      print(f"Gotcha some other event {eventName}")

  #
  # Post the webhook over Ziti
  #
  headers = {'Content-Type': 'application/json',}
  jsonData = json.dumps(body)
  print(f"{jsonData}")

  with openziti.monkeypatch():
    r = requests.post(url, headers=headers, data=jsonData)
    print(f"Response Status: {r.status_code}")
    print(r.headers)
    print(r.content)
