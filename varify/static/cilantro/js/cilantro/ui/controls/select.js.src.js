var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(['underscore', 'backbone', 'marionette', '../../core', './base'], function(_, Backbone, Marionette, c, base) {
  var MultiSelectionList, SelectionListItem, SingleSelectionList;
  SelectionListItem = (function(_super) {
    __extends(SelectionListItem, _super);

    function SelectionListItem() {
      return SelectionListItem.__super__.constructor.apply(this, arguments);
    }

    SelectionListItem.prototype.template = function() {};

    SelectionListItem.prototype.tagName = 'option';

    SelectionListItem.prototype.modelEvents = function() {
      return {
        'change:selected': 'render'
      };
    };

    SelectionListItem.prototype.onRender = function() {
      var label;
      label = this.model.get('label');
      if (label === '') {
        this.$el.text('(empty)');
      } else if (label === 'null') {
        this.$el.text('(null)');
      } else {
        this.$el.text(label);
      }
      this.$el.attr('value', this.model.get('value'));
      return this.$el.attr('selected', this.model.get('selected'));
    };

    return SelectionListItem;

  })(Marionette.ItemView);
  SingleSelectionList = (function(_super) {
    __extends(SingleSelectionList, _super);

    function SingleSelectionList() {
      return SingleSelectionList.__super__.constructor.apply(this, arguments);
    }

    SingleSelectionList.prototype.className = 'selection-list';

    SingleSelectionList.prototype.itemView = SelectionListItem;

    SingleSelectionList.prototype.itemViewOptions = function(model, index) {
      return {
        model: model
      };
    };

    SingleSelectionList.prototype.itemViewContainer = '.items';

    SingleSelectionList.prototype.template = 'controls/select/list';

    SingleSelectionList.prototype.ui = {
      items: '.items'
    };

    SingleSelectionList.prototype.events = {
      'change .items': 'onSelectionChange'
    };

    SingleSelectionList.prototype.collectionEvents = {
      'reset': 'onCollectionSync'
    };

    SingleSelectionList.prototype.initialize = function(options) {
      var limit;
      this.wait();
      if (!this.collection) {
        this.collection = new Backbone.Collection;
        if (c.isSupported('2.3.1')) {
          limit = 0;
        } else {
          limit = 1000;
        }
        this.model.values({
          limit: limit
        }).done((function(_this) {
          return function(resp) {
            _this.collection.reset(resp.values);
            return _this.ready();
          };
        })(this));
      }
      return this.on('ready', function() {
        return this.change();
      });
    };

    SingleSelectionList.prototype.onCollectionSync = function() {
      return this.render();
    };

    SingleSelectionList.prototype.onSelectionChange = function() {
      return this.change();
    };

    SingleSelectionList.prototype.getField = function() {
      return this.model.id;
    };

    SingleSelectionList.prototype.getOperator = function() {
      return "exact";
    };

    SingleSelectionList.prototype.getValue = function() {
      return this.ui.items.val();
    };

    SingleSelectionList.prototype.setValue = function(value) {
      return this.ui.items.val(value);
    };

    SingleSelectionList.prototype.validate = function(attrs) {
      if (_.isNull(attrs.value) || _.isUndefined(attrs.value)) {
        return 'An option must be selected';
      }
    };

    return SingleSelectionList;

  })(base.ControlCompositeView);
  MultiSelectionList = (function(_super) {
    __extends(MultiSelectionList, _super);

    function MultiSelectionList() {
      return MultiSelectionList.__super__.constructor.apply(this, arguments);
    }

    MultiSelectionList.prototype.onCollectionSync = function() {
      return this.render();
    };

    MultiSelectionList.prototype.onSelectionChange = function(event) {
      this.ui.items.children().each((function(_this) {
        return function(i, el) {
          return _this.collection.models[i].set('selected', el.selected);
        };
      })(this));
      return this.change();
    };

    MultiSelectionList.prototype.onRender = function() {
      return this.ui.items.attr('multiple', true);
    };

    MultiSelectionList.prototype.getOperator = function() {
      return "in";
    };

    MultiSelectionList.prototype.getValue = function() {
      return _.map(this.collection.where({
        selected: true
      }), function(model) {
        return model.get('value');
      });
    };

    MultiSelectionList.prototype.setValue = function(values) {
      if (values == null) {
        values = [];
      }
      return this.collection.each(function(model) {
        var _ref;
        return model.set('selected', (_ref = model.get('value'), __indexOf.call(values, _ref) >= 0));
      });
    };

    MultiSelectionList.prototype.validate = function(attrs) {
      if (!attrs.value || !attrs.value.length) {
        return 'At least one option must be selected';
      }
    };

    return MultiSelectionList;

  })(SingleSelectionList);
  return {
    SingleSelectionList: SingleSelectionList,
    MultiSelectionList: MultiSelectionList
  };
});
