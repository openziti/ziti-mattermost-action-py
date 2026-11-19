// Mattermost renders message attachments with its mm-blocks components, and its stylesheet caps them with
// `.mm-blocks{max-width:700px}`. This plugin adds a stylesheet that removes the cap and lets attachment text wrap
// under the thumbnail. It changes styles only, so disabling the plugin restores the stock layout.
(function () {
  var PLUGIN_ID = 'com.openziti.wide-attachments';
  var STYLE_ID = 'wide-attachments-style';

  // The text block that carries the spacer, and a column set that has it next to an image column, as Mattermost
  // renders an attachment with text and a thumb_url. Child combinators only: a looser match also reaches the labels
  // of attachment fields, which sit deeper in the stretch column. Other column sets keep the stock thumbnail column.
  var LEAD_TEXT = '.mm-blocks-column--stretch > .mm-blocks-container > .mm-blocks-text:first-child';
  var THUMB_SET = '.mm-blocks-column-set:has(> .mm-blocks-column--auto .mm-blocks-image):has(> ' + LEAD_TEXT + ')';
  var STACK = THUMB_SET + ' > .mm-blocks-column--stretch > .mm-blocks-container';

  var css = [
    '.mm-blocks { max-width: none !important; }',

    // A float must come before the text to wrap it, but the thumbnail column comes after the text column. So pin
    // the thumbnail top-right and float an empty spacer of the same size at the start of the text. The spacer is
    // the 120px thumbnail plus the 12px column gap, which fits square thumbnails such as the Ziggy images.
    THUMB_SET + ' { position: relative; }',
    THUMB_SET + ' > .mm-blocks-column--auto { position: absolute; top: 0; right: 0; }',
    THUMB_SET + ' > ' + LEAD_TEXT + '::before {' +
      ' content: ""; float: right; width: 132px; height: 124px; }',
    // The spacer floats in the whole stack, not only in the text, so fields and images after short text sit beside
    // the thumbnail as they do in the stock layout. flow-root keeps the card at least as tall as the spacer. The
    // stack is a flex column in the stock stylesheet, and floats do not cross flex items, so it becomes a block with
    // margins for the stock 12px gap. Later blocks drop their full width to fit beside the spacer.
    STACK + ' { display: flow-root !important; }',
    STACK + ' > * + * { margin-top: 12px; }',
    STACK + ' > :not(:first-child) { width: auto !important; }',
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
