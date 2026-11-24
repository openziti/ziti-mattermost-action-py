// Mattermost renders message attachments with its mm-blocks components, and its stylesheet caps them with
// `.mm-blocks{max-width:700px}`. This plugin adds a stylesheet that removes the cap and lets attachment text wrap
// under the thumbnail. It changes styles only, so disabling the plugin restores the stock layout.
(function () {
  var PLUGIN_ID = 'com.openziti.wide-attachments';
  var STYLE_ID = 'wide-attachments-style';

  // Mattermost renders an attachment with a thumb_url as a column set two containers below .mm-blocks: a stretch
  // column with the attachment's blocks, then an auto column with the thumbnail. Field rows are column sets too, but
  // deeper and without an auto column. Plain child and sibling selectors only: the stylesheet once used :has(), and
  // Chromium then restyled much of the page on each keystroke in the message box.
  var SET = '.mm-blocks > .mm-blocks-container > .mm-blocks-container > .mm-blocks-column-set';
  var THUMB = SET + ' > .mm-blocks-column--stretch + .mm-blocks-column--auto';
  var STACK = SET + ' > .mm-blocks-column--stretch:not(:last-child) > .mm-blocks-container';
  var BLOCK = STACK + ' > :is(' + ['text', 'container', 'column-set', 'image', 'button', 'divider', 'collapsible',
    'select'].map(function (b) { return '.mm-blocks-' + b; }).join(', ') + ')';

  var css = [
    '.mm-blocks { max-width: none !important; }',

    // A float must come before the text to wrap it, but the thumbnail column comes after the text column. So pin
    // the thumbnail top-right and float an empty spacer of the same size at the start of the stack. The spacer is
    // the 120px thumbnail plus the 12px column gap, which fits square thumbnails such as the Ziggy images.
    SET + ' { position: relative; }',
    THUMB + ' { position: absolute; top: 0; right: 0; }',
    STACK + '::before { content: ""; float: right; width: 132px; height: 124px; }',
    // Text wraps under the spacer. Fields, buttons, and images sit beside it, as they sit beside the thumbnail in
    // the stock layout. flow-root keeps the card at least as tall as the spacer. The stack is a flex column in the
    // stock stylesheet, and floats do not cross flex items, so it becomes a block with margins for the stock 12px
    // gap. Blocks drop their full width to fit beside the spacer.
    STACK + ' { display: flow-root !important; }',
    BLOCK + ' { width: auto !important; }',
    BLOCK + ':not(:first-child) { margin-top: 12px; }',
  ].join('\n');

  window.registerPlugin(PLUGIN_ID, {
    initialize: function () {
      var style = document.createElement('style');
      style.id = STYLE_ID;
      style.textContent = css;
      document.head.appendChild(style);
    },
    uninitialize: function () {
      var style = document.getElementById(STYLE_ID);
      if (style) {
        style.remove();
      }
    },
  });
})();
