var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['./base'], function(base) {
  var QueryCollection, QueryModel, _ref, _ref1;
  QueryModel = (function(_super) {
    __extends(QueryModel, _super);

    function QueryModel() {
      _ref = QueryModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    QueryModel.prototype.parse = function(attrs) {
      QueryModel.__super__.parse.apply(this, arguments);
      if ((attrs != null) && (attrs.shared_users == null)) {
        attrs.shared_users = [];
      }
      return attrs;
    };

    return QueryModel;

  })(base.Model);
  QueryCollection = (function(_super) {
    __extends(QueryCollection, _super);

    function QueryCollection() {
      _ref1 = QueryCollection.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    QueryCollection.prototype.model = QueryModel;

    return QueryCollection;

  })(base.Collection);
  return {
    QueryModel: QueryModel,
    QueryCollection: QueryCollection
  };
});
