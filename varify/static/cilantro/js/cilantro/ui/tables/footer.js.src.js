var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['marionette', './row'], function(Marionette, row) {
  var Footer;
  Footer = (function(_super) {
    __extends(Footer, _super);

    function Footer() {
      return Footer.__super__.constructor.apply(this, arguments);
    }

    Footer.prototype.tagName = 'tfoot';

    Footer.prototype.template = function() {};

    return Footer;

  })(Marionette.ItemView);
  return {
    Footer: Footer
  };
});
