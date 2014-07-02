/* global define */

define([
    'jquery',
    'underscore',
    'marionette'
], function($, _, Marionette) {

    var Header = Marionette.ItemView.extend({
        tagName: 'thead',

        template: 'varify/tables/header',

        events: {
            'click th': 'onClick'
        },

        initialize: function() {
            this.data = {};

            if (!(this.data.view = this.options.view)) {
                throw new Error('view model required');
            }
        },

        _getConcept: function(element) {
            var concept = parseInt(element.getAttribute('data-concept-id'), 10);

            if ((concept !== null) && !isNaN(concept)) {
                return concept;
            }

            // It is possible we registered a click event on a child of the
            // th element. If that is the case, try to read the concept from
            // parent of the event target.
            return parseInt(element.parentElement.getAttribute('data-concept-id'), 10);
        },

        onClick: function(event) {
            var concept, model;

            concept = this._getConcept(event.target);

            if ((concept === null) || isNaN(concept)) {
                throw new Error('Unrecognized concept ID on column');
            }

            model = _.find(this.data.view.facets.models, function(f) {
                return f.get('concept') === concept;
            });

            // If this column is not in the view already, add it in before
            // updating the view sort properties.
            if (!model) {
                this.data.view.facets.add({
                    concept: concept
                });
            }

            _.each(this.data.view.facets.models, function(f) {
                var direction;

                if (f.get('concept') === concept) {
                    direction = f.get('sort');

                    if (direction) {
                        if (direction.toLowerCase() === "asc") {
                            f.set('sort', "desc");
                            f.set('sort_index', 0);
                        }
                        else {
                            f.unset('sort');
                            f.unset('sort_index');
                        }
                    }
                    else {
                        f.set('sort', "asc");
                        f.set('sort_index', 0);
                    }
                }
                else {
                    f.unset('sort');
                    f.unset('sort_index');
                }
            });

            this.data.view.save();
        },

        onRender: function() {
            _.each(this.data.view.facets.models, function(f) {
                var $sortIcon, direction, sortClass;

                $sortIcon = $('th[data-concept-id=' + (f.get('concept')) + '] i');

                if ($sortIcon !== null) {
                    $sortIcon.removeClass('icon-sort icon-sort-up icon-sort-down');

                    direction = (f.get('sort') || '').toLowerCase();

                    switch (direction) {
                        case 'asc':
                            sortClass = 'icon-sort-up';
                            break;
                        case 'desc':
                            sortClass = 'icon-sort-down';
                            break;
                        default:
                            sortClass = 'icon-sort';
                    }

                    $sortIcon.addClass(sortClass);
                }
            });
        }
    });

    return {
        Header: Header
    };

});
