var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __slice = [].slice;

define(['underscore', 'marionette', './base'], function(_, Marionette, base) {
  var EmptyPage, ListingPage, LoadingPage, Page, PageRoll, Paginator, _ref, _ref1, _ref2, _ref3, _ref4, _ref5;
  EmptyPage = (function(_super) {
    __extends(EmptyPage, _super);

    function EmptyPage() {
      _ref = EmptyPage.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    EmptyPage.prototype.message = 'No page results';

    return EmptyPage;

  })(base.EmptyView);
  LoadingPage = (function(_super) {
    __extends(LoadingPage, _super);

    function LoadingPage() {
      _ref1 = LoadingPage.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    LoadingPage.prototype.message = 'Loading page...';

    return LoadingPage;

  })(base.LoadView);
  Paginator = (function(_super) {
    __extends(Paginator, _super);

    function Paginator() {
      _ref2 = Paginator.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    Paginator.prototype.template = 'paginator';

    Paginator.prototype.requestDelay = 250;

    Paginator.prototype.className = 'paginator';

    Paginator.prototype.ui = {
      first: '[data-page=first]',
      prev: '[data-page=prev]',
      next: '[data-page=next]',
      last: '[data-page=last]',
      pageCount: '.page-count',
      currentPage: '.current-page',
      buttons: '[data-toggle=tooltip]'
    };

    Paginator.prototype.modelEvents = {
      'change:pagecount': 'renderPageCount',
      'change:currentpage': 'renderCurrentPage'
    };

    Paginator.prototype.events = {
      'click [data-page=first]': 'requestChangePage',
      'click [data-page=prev]': 'requestChangePage',
      'click [data-page=next]': 'requestChangePage',
      'click [data-page=last]': 'requestChangePage'
    };

    Paginator.prototype.initialize = function() {
      return this._changePage = _.debounce(this.changePage, this.requestDelay);
    };

    Paginator.prototype.onRender = function() {
      this.ui.buttons.tooltip({
        animation: false,
        placement: 'bottom'
      });
      if (!this.model.pageIsLoading()) {
        this.renderPageCount(this.model, this.model.getPageCount());
        return this.renderCurrentPage.apply(this, [this.model].concat(__slice.call(this.model.getCurrentPageStats())));
      }
    };

    Paginator.prototype.renderPageCount = function(model, value, options) {
      return this.ui.pageCount.text(value);
    };

    Paginator.prototype.renderCurrentPage = function(model, value, options) {
      this.ui.currentPage.text(value);
      this.ui.first.prop('disabled', !!options.first);
      this.ui.prev.prop('disabled', !!options.first);
      this.ui.next.prop('disabled', !!options.last);
      this.ui.last.prop('disabled', !!options.last);
      if (!!options.first) {
        this.ui.first.tooltip('hide');
        this.ui.prev.tooltip('hide');
      }
      if (!!options.last) {
        this.ui.next.tooltip('hide');
        return this.ui.last.tooltip('hide');
      }
    };

    Paginator.prototype.changePage = function(newPage) {
      switch (newPage) {
        case "first":
          return this.model.getFirstPage();
        case "prev":
          return this.model.getPreviousPage();
        case "next":
          return this.model.getNextPage();
        case "last":
          return this.model.getLastPage();
        default:
          throw new Error("Unknown paginator direction: " + newPage);
      }
    };

    Paginator.prototype.requestChangePage = function(event) {
      return this._changePage($(event.currentTarget).data('page'));
    };

    return Paginator;

  })(Marionette.ItemView);
  Page = (function(_super) {
    __extends(Page, _super);

    function Page() {
      _ref3 = Page.__super__.constructor.apply(this, arguments);
      return _ref3;
    }

    return Page;

  })(Marionette.ItemView);
  ListingPage = (function(_super) {
    __extends(ListingPage, _super);

    function ListingPage() {
      _ref4 = ListingPage.__super__.constructor.apply(this, arguments);
      return _ref4;
    }

    ListingPage.prototype.itemView = Page;

    ListingPage.prototype.emptyPage = EmptyPage;

    ListingPage.prototype.itemViewOptions = function(item, index) {
      return _.defaults({
        model: item,
        index: index
      }, this.options);
    };

    return ListingPage;

  })(Marionette.CollectionView);
  PageRoll = (function(_super) {
    __extends(PageRoll, _super);

    function PageRoll() {
      _ref5 = PageRoll.__super__.constructor.apply(this, arguments);
      return _ref5;
    }

    PageRoll.prototype.options = {
      list: true
    };

    PageRoll.prototype.itemView = Page;

    PageRoll.prototype.listView = ListingPage;

    PageRoll.prototype.emptyView = LoadingPage;

    PageRoll.prototype.getItemView = function() {
      if (this.options.list) {
        return this.listView;
      } else {
        return this.itemView;
      }
    };

    PageRoll.prototype.listViewOptions = function(item, index) {
      return {
        collection: item.items
      };
    };

    PageRoll.prototype.itemViewOptions = function(item, index) {
      var options;
      options = {
        model: item,
        index: index
      };
      if (this.options.list) {
        _.extend(options, this.listViewOptions(item, index));
      }
      return _.defaults(options, this.options);
    };

    PageRoll.prototype.collectionEvents = {
      'change:currentpage': 'showCurentPage'
    };

    PageRoll.prototype.showCurentPage = function(model, num, options) {
      return this.children.each(function(view) {
        return view.$el.toggle(view.model.id === num);
      });
    };

    return PageRoll;

  })(Marionette.CollectionView);
  return {
    Paginator: Paginator,
    Page: Page,
    ListingPage: ListingPage,
    PageRoll: PageRoll
  };
});
