var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', './row'], function(_, Marionette, row) {
  var Header, HeaderCell, HeaderRow, _ref, _ref1;
  HeaderCell = (function(_super) {
    __extends(HeaderCell, _super);

    HeaderCell.prototype.tagName = 'th';

    function HeaderCell(options) {
      if (options.view == null) {
        throw new Error('ViewModel instance required');
      }
      this.view = options.view;
      delete options.view;
      HeaderCell.__super__.constructor.call(this, options);
    }

    HeaderCell.prototype.onClick = function() {
      _.each(this.view.facets.models, function(f) {
        var direction;
        if (f.get('concept') === this.model.id) {
          direction = f.get('sort');
          if (direction != null) {
            if (direction.toLowerCase() === "asc") {
              f.set('sort', "desc");
              return f.set('sort_index', 0);
            } else {
              f.unset('sort');
              return f.unset('sort_index');
            }
          } else {
            f.set('sort', "asc");
            return f.set('sort_index', 0);
          }
        } else {
          f.unset('sort');
          return f.unset('sort_index');
        }
      }, this);
      return this.view.save();
    };

    HeaderCell.prototype.initialize = function() {
      return this.listenTo(this.model, 'change:visible', this.toggleVisible);
    };

    HeaderCell.prototype.events = {
      "click": "onClick"
    };

    HeaderCell.prototype.getSortIconClass = function() {
      var direction, model,
        _this = this;
      model = _.find(this.view.facets.models, function(m) {
        return _this.model.id === m.get('concept');
      });
      if (model == null) {
        return;
      }
      direction = (model.get('sort') || '').toLowerCase();
      switch (direction) {
        case 'asc':
          return 'icon-sort-up';
        case 'desc':
          return 'icon-sort-down';
        default:
          return 'icon-sort';
      }
    };

    HeaderCell.prototype.render = function() {
      var iconClass;
      this.toggleVisible();
      iconClass = this.getSortIconClass();
      this.$el.html("<span>" + (this.model.get('name')) + " <i class=" + iconClass + "></i></span>");
      this.$el.attr('title', this.model.get('name'));
      return this;
    };

    HeaderCell.prototype.toggleVisible = function() {
      return this.$el.toggle(this.model.get('visible'));
    };

    return HeaderCell;

  })(Marionette.ItemView);
  HeaderRow = (function(_super) {
    __extends(HeaderRow, _super);

    function HeaderRow() {
      _ref = HeaderRow.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    HeaderRow.prototype.itemView = HeaderCell;

    return HeaderRow;

  })(row.Row);
  Header = (function(_super) {
    __extends(Header, _super);

    function Header() {
      _ref1 = Header.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    Header.prototype.tagName = 'thead';

    Header.prototype.render = function() {
      row = new HeaderRow(_.extend({}, this.options, {
        collection: this.collection
      }));
      this.$el.html(row.el);
      row.render();
      return this;
    };

    return Header;

  })(Marionette.ItemView);
  return {
    Header: Header
  };
});
