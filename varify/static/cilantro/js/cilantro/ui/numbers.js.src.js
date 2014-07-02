define(['./core'], function(c) {
  return {
    renderCount: function($el, count, fallback) {
      if (fallback == null) {
        fallback = '<em>n/a</em>';
      }
      if (count == null) {
        return $el.html(fallback);
      } else {
        return $el.html(c.utils.prettyNumber(count, c.config.get('threshold'))).attr('title', c.utils.toDelimitedNumber(count));
      }
    }
  };
});
