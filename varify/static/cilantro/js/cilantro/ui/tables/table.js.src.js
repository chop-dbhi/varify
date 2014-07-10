var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', './body', './header', './footer'], function(_, Marionette, body, header, footer) {
  var Table;
  Table = (function(_super) {
    __extends(Table, _super);

    function Table() {
      return Table.__super__.constructor.apply(this, arguments);
    }

    Table.prototype.tagName = 'table';

    Table.prototype.className = 'table table-striped';

    Table.prototype.itemView = body.Body;

    Table.prototype.itemViewOptions = function(item, index) {
      return _.defaults({
        collection: item.series
      }, this.options);
    };

    Table.prototype.collectionEvents = {
      'change:currentpage': 'showCurrentPage'
    };

    Table.prototype.initialize = function() {
      this.header = new header.Header(_.defaults({
        collection: this.collection.indexes
      }, this.options));
      this.footer = new footer.Footer(_.defaults({
        collection: this.collection.indexes
      }, this.options));
      this.header.render();
      this.footer.render();
      this.$el.append(this.header.el, this.footer.el);
      return this.collection.on('reset', (function(_this) {
        return function() {
          if (_this.collection.objectCount === 0) {
            return _this.$el.hide();
          } else {
            return _this.$el.show();
          }
        };
      })(this));
    };

    Table.prototype.showCurrentPage = function(model, num, options) {
      return this.children.each(function(view) {
        return view.$el.toggle(view.model.id === num);
      });
    };

    return Table;

  })(Marionette.CollectionView);
  return {
    Table: Table
  };
});
