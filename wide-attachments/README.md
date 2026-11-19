# Wide Attachments Mattermost plugin

Mattermost renders message attachments, the cards this action posts, with its `mm-blocks` components. Its stylesheet
caps them at 700px wide with `.mm-blocks{max-width:700px}`, so a long card fills only part of a wide channel, and the
thumbnail keeps its own column down the right side of the card.

This plugin adds one stylesheet to the Mattermost web and desktop apps that:

- removes the 700px cap, so a card spans the full post width.
- wraps the card text under the thumbnail, instead of leaving a column of empty space below it.

It is a webapp-only plugin. It has no server code, and it changes styles only, so disabling it restores the stock
layout. Mobile apps do not run webapp plugins and keep their own layout.

| File | What it is |
| --- | --- |
| [plugin.json](plugin.json) | The plugin manifest. |
| [webapp/main.js](webapp/main.js) | The whole plugin: a stylesheet and the code that adds and removes it. |
| [com.openziti.wide-attachments-0.1.0.tar.gz](com.openziti.wide-attachments-0.1.0.tar.gz) | The bundle an admin uploads, built from the files above. |
| [build.sh](build.sh) | Packages `plugin.json` and `webapp/main.js` into the bundle. |
| [release.sh](release.sh) | Builds the bundle and publishes it as a GitHub release. |

## Build the bundle

The repo holds a built bundle, so an admin can download
[com.openziti.wide-attachments-0.1.0.tar.gz](com.openziti.wide-attachments-0.1.0.tar.gz) and skip this step. After
you change `plugin.json` or `webapp/main.js`, rebuild the bundle and commit it with the change:

```bash
./wide-attachments/build.sh
cp wide-attachments/build/com.openziti.wide-attachments-*.tar.gz wide-attachments/
```

The script writes `wide-attachments/build/com.openziti.wide-attachments-<version>.tar.gz` and prints its path. It
needs bash and `tar`. On Windows, run it from Git Bash or WSL. When you raise `version` in `plugin.json`, delete the
old bundle and update the links in this README.

## Release the bundle

[release.sh](release.sh) publishes the bundle as a GitHub release. Run it with an authenticated `gh` CLI, after you
tag the commit and push the tag:

```bash
git tag wide-attachments-v0.1.0
git push origin wide-attachments-v0.1.0
./wide-attachments/release.sh wide-attachments-v0.1.0
```

The script fails if the tag version does not match `plugin.json`. The release is not marked latest, so the action's
own `vX.Y.Z` release stays the repo's latest release, and the `vN` branches that action users pin to do not move.

## Preview it without installing

An admin can see the result in their own browser tab before installing anything. The preview lasts until the tab
reloads and changes nothing for other users.

1. Open a channel that has a long card with a thumbnail, such as a pull request card from this action.
2. Open the browser developer tools (F12) and select the **Console** tab.
3. Paste the following and press Enter:

   ```js
   const L = '.mm-blocks-column--stretch > .mm-blocks-container > .mm-blocks-text:first-child';
   const T = `.mm-blocks-column-set:has(> .mm-blocks-column--auto .mm-blocks-image):has(> ${L})`;
   const S = `${T} > .mm-blocks-column--stretch > .mm-blocks-container`;
   document.head.insertAdjacentHTML('beforeend', `<style>
     .mm-blocks { max-width: none !important; }
     ${T} { position: relative; }
     ${T} > .mm-blocks-column--auto { position: absolute; top: 0; right: 0; }
     ${T} > ${L}::before { content: ""; float: right; width: 132px; height: 124px; }
     ${S} { display: flow-root !important; }
     ${S} > * + * { margin-top: 12px; }
     ${S} > :not(:first-child) { width: auto !important; }
   </style>`);
   ```

4. Check that the cards span the channel width and that the text wraps under the thumbnail.

## Install

Installing needs a system admin. It applies to every user of the web and desktop apps on that server.

1. In **System Console > Plugins > Plugin Management**, set **Enable Plugins** and **Enable Plugin Uploads** to
   true, then save. On a self-hosted server, `PluginSettings.EnableUploads` in `config.json` controls the upload
   setting.
2. Under **Upload Plugin**, select **Choose File**, pick the `.tar.gz` bundle, and select **Upload**.
3. Under **Installed Plugins**, find **Wide Attachments** and select **Enable**.

With `mmctl`, steps 2 and 3 are:

```bash
mmctl plugin add com.openziti.wide-attachments-0.1.0.tar.gz
mmctl plugin enable com.openziti.wide-attachments
```

## Test it

1. Reload Mattermost in the browser, or select **View > Reload** in the desktop app.
2. Open a channel that has a long card with a thumbnail. Check that the card spans the channel width and that the
   text below the thumbnail runs the full width of the card.
3. Open a card with short text and a thumbnail, such as a "Created branch" card. Check that the card is at least as
   tall as the thumbnail and that the thumbnail stays inside the card.
4. Open a card without a thumbnail, such as a push card. Check that it spans the channel width and is otherwise
   unchanged.

## Remove it

Under **Installed Plugins**, select **Disable** next to **Wide Attachments**, then reload. Cards return to the stock
700px layout. Select **Remove** to delete the plugin from the server.

## Limits

- The selectors depend on the `mm-blocks` class names in the Mattermost 12 webapp. If a later Mattermost release
  renames them, the plugin stops doing anything, and cards fall back to the stock layout.
- The spacer that makes room for the thumbnail is 132x124px, sized for the 120px square Ziggy thumbnails this action
  sends. A thumbnail that is wider than it is tall overlaps the first lines of text.

## Effects on other attachments

The plugin applies to every attachment on the server, not only to cards from this action.

- Every attachment from every integration spans the full post width.
- Only an attachment whose text comes first and that has a thumbnail gets the wrapped layout. Fields, buttons, and
  images after short text sit beside the thumbnail, as in the stock layout. Other attachments keep the stock
  thumbnail column.
- Plain posts, without attachments, do not change.
- On a narrow screen, such as the web app on a phone browser, the text also wraps under the thumbnail, so a card
  takes less height than in the stock layout.
- The Mattermost mobile apps do not run webapp plugins, so cards there keep the stock layout.
- The selectors use the CSS `:has()` selector, which current Chrome, Edge, Firefox, Safari, and the desktop app
  support. An older browser ignores the rules and shows the stock layout.
