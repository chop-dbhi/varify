// solvebio.js -- Javascript bindings for the SolveBio API
//
// 
// Copyright (c) 2014 Solve, Inc. (https://www.solvebio.com)
//
// The MIT License (MIT)
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
/* jshint camelcase: false */
(function(root, factory) {
    if (typeof define === 'function' && define.amd) { // jshint ignore:line
        // AMD. Register as an anonymous module.
        define(['module'], factory);  // jshint ignore:line
    } else if (typeof exports === 'object') {
        // Node. Does not work with strict CommonJS, but
        // only CommonJS-like environments that support module.exports,
        // like Node.
        module.exports = factory(); // jshint ignore:line
    } else {
        // Browser globals (root is window)
        root.returnExports = factory();
    }
}(this, function(module) {
    var version = "0.0.1";
    var config = {};

    var log = {
        debug: function(msg) {
            if (debug) {
                window.console.debug("[SolveBio] " + msg);
            }
        },
        error: function(msg) {
            window.console.error("[SolveBio] " + msg);
        },
        warn: function(msg) {
            window.console.warn("[SolveBio] " + msg);
        }
    };

    // Load config from requirejs
    if (module && typeof module.config === 'function') {
        config = module.config();
    }

    var debug = config.debug || false;
    var appId = config.appId;
    var accessToken = config.accessToken;
    var apiHost = config.apiHost ? config.apiHost.replace(/\/?$/, '') :
                 'https://api.solvebio.com';
    // The URL where the dashboard iframes are loaded from
    // Protocol, port and hostname of the target window must match.
    // Origins are set automatically when Dashboards are created.
    var dashboardOrigins = [];

    // Serializes data to a query string
    var serialize = function(obj) {
        var str = [];
        for (var p in obj) {
            var k = p,
                v = obj[p];
            str.push(typeof v === "object" ?
                serialize(v, k) : encodeURIComponent(k) + "=" + encodeURIComponent(v));
        }
        return str.join("&");
    };

    var buildURL = function(url, params) {
        return url + (url.indexOf("?") > 0 ? "&" : "?") + serialize(params);
    };

    // Contains named references to iframed dashboards
    var dashboards = {};
    var eventListenerCreated = false;

    var createEventListener = function() {
        if (eventListenerCreated) return;
        eventListenerCreated = true;

        window.addEventListener("message", function(ev) {
            ev = ev.originalEvent || ev;

            if (dashboardOrigins.indexOf(ev.origin) < 0) {
                log.debug('Invalid message origin ('+ev.origin+'), ' +
                          'expected: "'+dashboardOrigins+'"');
                return;
            }

            var data;

            try {
                data = (ev.data && (ev.data.length > 0)) ? JSON.parse(ev.data) : false;
            } catch (_error) {
                return;
            }

            if (!data) return;

            if (data.name in dashboards) {
                var dash = dashboards[data.name];

                if (!dash._loaded) {
                    log.debug('Dashboard "' + data.name + '" loaded!');
                    dash._loaded = true;
                    // Send the dashboard's settings
                    dash.postMessage({settings: dash._settings});
                    // Run the onLoad functions
                    for (var i = 0; i < dash._onLoad.length; ++i) {
                        dash._onLoad[i](dash);
                    }
                }

                // Height should always be provided in all messages.
                if (data.height) {
                    log.debug("Dashboard updating height to: " + data.height + "px");
                    dash._iframe.style.height = data.height + "px";
                }
            }
        }, false);
    };

    var SolveBio = {
        version: function() {
            return version;
        },

        setDebug: function(d) {
            debug = !!d;
        },

        apiHost: function() {
            return apiHost;
        },

        setApiHost: function(h) {
            log.debug('Setting API host to ' + h);
            apiHost = h.replace(/\/?$/, '');
        },

        setAppId: function(value) {
            appId = value;
        },

        getAppId: function() {
            return appId;
        },

        setAccessToken: function(t) {
            accessToken = t;
        },

        getAccessToken: function() {
            return accessToken;
        },

        rest: function(method, path, data, success, error) {
            method = method.toUpperCase();
            var url = "" + apiHost + "/" + path.replace(/^\/?/, "");
            data = data || {};
            success = success || function() {};
            error = error || function() {};

            if (!!accessToken) {
                data.access_token = accessToken;
            }

            if (method === "GET" || method === "HEAD") {
                // serialize the data into the query parameters
                url = buildURL(url, data);
                data = null;
            } else {
                // JSONify the data into the request body
                data = JSON.stringify(data, null, 4);
            }

            // IE6 and below are not supported
            var xhr = new XMLHttpRequest();

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status !== 200) {
                    try {
                        error(JSON.parse(xhr.responseText));
                    } catch (_error) {
                        error(xhr.responseText);
                    }
                }
                if (xhr.readyState === 4 && xhr.status === 200) {
                    try {
                        success(JSON.parse(xhr.responseText));
                    } catch (_error) {
                        error(xhr.responseText);
                    }
                }
            };

            log.debug('Sending ' + method + ' request to ' + url);
            xhr.open(method, url, true);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.send(data);

            return xhr;
        },

        // -------------------------------------------------------------------
        // Dashboards
        // -------------------------------------------------------------------

        Dashboards: {
            all: function() {
                return dashboards;
            },

            create: function(name, url, targetId, settings) {
                var target, iframe, dashboard;

                if (name in dashboards) {
                    return dashboards[name];
                }

                target = document.getElementById(targetId.replace("#", ""));

                if (!target) {
                    log.error('Dashboards.create() could not find target by ID "' +
                              targetId + '"');
                    return false;
                }

                createEventListener();

                settings = settings ? settings : {};
                settings.name = name;
                settings.debug = debug;

                if (apiHost) {
                  settings.apiHost = apiHost;
                }

                if (accessToken) {
                  settings.accessToken = accessToken;
                }

                // // setup the expected dashboard origin
                // if (!settings.origin) {
                //     // if no origin is set explicitly, use window.location
                //     settings.origin = window.location.origin;
                // }

                // parse the dashboard's origin from url
                var urlParser = document.createElement('a');
                urlParser.href = url;
                var origin = urlParser.protocol + '//' + urlParser.host;
                dashboardOrigins.push(origin);

                iframe = document.createElement('iframe');
                // build a URL with safe settings name and debug
                // other settings will be sent in a message on load
                iframe.setAttribute("src", buildURL(url, {
                    name: name,
                    debug: debug,
                    origin: window.location.origin
                }));
                iframe.setAttribute("id", name + "-iframe");
                iframe.setAttribute("name", name);
                iframe.setAttribute("width", "100%");
                iframe.setAttribute("height", "100%");
                iframe.setAttribute("scrolling", "no");
                iframe.setAttribute("frameborder", "0");
                iframe.style.border = "none";
                iframe.style.width = "100%";
                iframe.style.minHeight = "800px";
                target.insertBefore(iframe, target.firstChild);

                dashboard = {
                    _name: name,
                    _id: name + "-iframe",
                    _iframe: iframe,
                    _loaded: false,
                    _origin: origin,
                    _settings: settings,
                    _onLoad: [],

                    postMessage: function(data) {
                        if (dashboard._iframe && dashboard._iframe.contentWindow) {
                            dashboard._iframe.contentWindow.postMessage(
                                JSON.stringify(data), dashboard._origin);
                        }
                        else {
                            log.error('Could not postMessage to dashboard: ' +
                                      dashboard._name);
                        }
                    },

                    // Execute func when the dashboard is ready
                    ready: function(func) {
                        this._loaded ? func(this) : this._onLoad.push(func); // jshint ignore:line
                    }
                };

                dashboards[name] = dashboard;
                return dashboard;
            },

            get: function(name) {
                return dashboards[name];
            },

            delete: function(name) {
                if (name in dashboards) {
                    var f = dashboards[name]._iframe;
                    delete dashboards[name];
                    try {
                        f.parentNode.removeChild(f);
                    } catch (err) {}
                } else {
                    log.error('Could not delete dashboard "' + name + '": not found.');
                }
            }
        } // Dashboards
    }; // SolveBio

    // --------------------------------------------------------------------
    // REST shortcut methods
    // --------------------------------------------------------------------

    var restShortcut = function(method) {
        SolveBio[method.toLowerCase()] = function() {
            return this.rest.apply(this, [method].concat([].slice.call(arguments)));
        };
    };

    var methods = ["GET", "PUT", "POST", "DELETE"];
    for (var i = 0; i < methods.length; i++) {
        restShortcut(methods[i]);
    }

    return SolveBio;
}));
