var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(['underscore', 'backbone', 'marionette', '../../core', './base'], function(_, Backbone, Marionette, c, base) {
  var MultiSelectionList, SelectionListItem, SingleSelectionList, _ref, _ref1, _ref2;
  SelectionListItem = (function(_super) {
    __extends(SelectionListItem, _super);

    function SelectionListItem() {
      _ref = SelectionListItem.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    SelectionListItem.prototype.template = function() {};

    SelectionListItem.prototype.tagName = 'option';

    SelectionListItem.prototype.modelEvents = function() {
      return {
        'change:selected': 'render'
      };
    };

    SelectionListItem.prototype.onRender = function() {
      this.$el.text(this.model.get('label'));
      this.$el.attr('value', this.model.get('value'));
      return this.$el.attr('selected', this.model.get('selected'));
    };

    return SelectionListItem;

  })(Marionette.ItemView);
  SingleSelectionList = (function(_super) {
    __extends(SingleSelectionList, _super);

    function SingleSelectionList() {
      _ref1 = SingleSelectionList.__super__.constructor.apply(this, arguments);
      return _ref1;
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
      var limit,
        _this = this;
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
        }).done(function(resp) {
          _this.collection.reset(resp.values);
          return _this.ready();
        });
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

    return SingleSelectionList;

  })(base.ControlCompositeView);
  MultiSelectionList = (function(_super) {
    __extends(MultiSelectionList, _super);

    function MultiSelectionList() {
      _ref2 = MultiSelectionList.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    MultiSelectionList.prototype.onCollectionSync = function() {
      return this.render();
    };

    MultiSelectionList.prototype.onSelectionChange = function(event) {
      var _this = this;
      this.ui.items.children().each(function(i, el) {
        return _this.collection.models[i].set('selected', el.selected);
      });
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
        var _ref3;
        return model.set('selected', (_ref3 = model.get('value'), __indexOf.call(values, _ref3) >= 0));
      });
    };

    return MultiSelectionList;

  })(SingleSelectionList);
  return {
    SingleSelectionList: SingleSelectionList,
    MultiSelectionList: MultiSelectionList
  };
});
