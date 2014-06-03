var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', 'marionette'], function(_, Backbone, Marionette) {
  var ButtonSelect, ButtonSelectEmptyOption, ButtonSelectOption, _ref, _ref1;
  ButtonSelectEmptyOption = (function(_super) {
    __extends(ButtonSelectEmptyOption, _super);

    function ButtonSelectEmptyOption() {
      _ref = ButtonSelectEmptyOption.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    ButtonSelectEmptyOption.prototype.className = 'disabled';

    ButtonSelectEmptyOption.prototype.tagName = 'li';

    ButtonSelectEmptyOption.prototype.template = 'button/select-option';

    ButtonSelectEmptyOption.prototype.events = {
      'click': 'prevent'
    };

    ButtonSelectEmptyOption.prototype.prevent = function(event) {
      return event != null ? event.preventDefault() : void 0;
    };

    ButtonSelectEmptyOption.prototype.serializeData = function() {
      return {
        label: 'No options are available'
      };
    };

    return ButtonSelectEmptyOption;

  })(Marionette.ItemView);
  ButtonSelectOption = (function(_super) {
    __extends(ButtonSelectOption, _super);

    function ButtonSelectOption() {
      _ref1 = ButtonSelectOption.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    ButtonSelectOption.prototype.tagName = 'li';

    ButtonSelectOption.prototype.template = 'button/select-option';

    ButtonSelectOption.prototype.events = {
      'click': 'select'
    };

    ButtonSelectOption.prototype.serializeData = function() {
      return {
        label: this.model.get('label') || this.model.get('value')
      };
    };

    ButtonSelectOption.prototype.select = function(event) {
      if (event != null) {
        event.preventDefault();
      }
      return this.model.set('selected', true);
    };

    return ButtonSelectOption;

  })(Marionette.ItemView);
  ButtonSelect = (function(_super) {
    __extends(ButtonSelect, _super);

    ButtonSelect.prototype.className = 'btn-group btn-select';

    ButtonSelect.prototype.template = 'button/select';

    ButtonSelect.prototype.itemView = ButtonSelectOption;

    ButtonSelect.prototype.itemViewContainer = '.dropdown-menu';

    ButtonSelect.prototype.emptyView = ButtonSelectEmptyOption;

    ButtonSelect.prototype.options = {
      placeholder: '----'
    };

    ButtonSelect.prototype.ui = {
      toggle: '.dropdown-toggle',
      menu: '.dropdown-menu',
      selection: '.dropdown-selection'
    };

    ButtonSelect.prototype.collectionEvents = {
      'change:selected': 'updateSelection'
    };

    function ButtonSelect(options) {
      var choices, value;
      if (options == null) {
        options = {};
      }
      if (!(options.collection instanceof Backbone.Collection)) {
        if (((choices = options.collection) != null) && typeof choices[0] !== 'object') {
          choices = (function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = choices.length; _i < _len; _i++) {
              value = choices[_i];
              _results.push({
                value: value,
                label: value
              });
            }
            return _results;
          })();
        }
        options.collection = new Backbone.Collection(choices);
      }
      ButtonSelect.__super__.constructor.call(this, options);
    }

    ButtonSelect.prototype.setSelection = function(value) {
      var model;
      if ((model = this.collection.findWhere({
        value: value
      }))) {
        return model.set('selected', true);
      }
    };

    ButtonSelect.prototype.getSelection = function(value) {
      var model;
      if ((model = this.collection.findWhere({
        selected: true
      }))) {
        return model.get('value');
      }
    };

    ButtonSelect.prototype.updateSelection = function(model, selected, options) {
      var value;
      if (!selected) {
        return;
      }
      value = model.get('value');
      this.collection.each(function(_model) {
        if (_model !== model) {
          return _model.set('selected', false, {
            silent: true
          });
        }
      });
      this.ui.selection.html(model.get('label') || value);
      this.$el.trigger('change', value);
      return this.trigger('change', model, value, options);
    };

    ButtonSelect.prototype.onRender = function() {
      var model;
      if (/^(small|large|mini)$/.test(this.options.size)) {
        this.ui.toggle.addClass("btn-" + this.options.size);
      }
      this.ui.toggle.dropdown();
      if ((model = this.collection.findWhere({
        selected: true
      }))) {
        return this.updateSelection(model, true);
      } else {
        return this.ui.selection.html(this.options.placeholder);
      }
    };

    return ButtonSelect;

  })(Marionette.CompositeView);
  return {
    ButtonSelect: ButtonSelect
  };
});
