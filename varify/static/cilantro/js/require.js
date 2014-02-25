var requirejs,require,define;!function(global){function isFunction(t){return"[object Function]"===ostring.call(t)}function isArray(t){return"[object Array]"===ostring.call(t)}function each(t,e){if(t){var n;for(n=0;n<t.length&&(!t[n]||!e(t[n],n,t));n+=1);}}function eachReverse(t,e){if(t){var n;for(n=t.length-1;n>-1&&(!t[n]||!e(t[n],n,t));n-=1);}}function hasProp(t,e){return hasOwn.call(t,e)}function getOwn(t,e){return hasProp(t,e)&&t[e]}function eachProp(t,e){var n;for(n in t)if(hasProp(t,n)&&e(t[n],n))break}function mixin(t,e,n,i){return e&&eachProp(e,function(e,r){(n||!hasProp(t,r))&&(i&&"string"!=typeof e?(t[r]||(t[r]={}),mixin(t[r],e,n,i)):t[r]=e)}),t}function bind(t,e){return function(){return e.apply(t,arguments)}}function scripts(){return document.getElementsByTagName("script")}function defaultOnError(t){throw t}function getGlobal(t){if(!t)return t;var e=global;return each(t.split("."),function(t){e=e[t]}),e}function makeError(t,e,n,i){var r=new Error(e+"\nhttp://requirejs.org/docs/errors.html#"+t);return r.requireType=t,r.requireModules=i,n&&(r.originalError=n),r}function newContext(t){function e(t){var e,n;for(e=0;t[e];e+=1)if(n=t[e],"."===n)t.splice(e,1),e-=1;else if(".."===n){if(1===e&&(".."===t[2]||".."===t[0]))break;e>0&&(t.splice(e-1,2),e-=2)}}function n(t,n,i){var r,o,s,a,l,c,u,h,p,d,f,g=n&&n.split("/"),m=g,y=C.map,v=y&&y["*"];if(t&&"."===t.charAt(0)&&(n?(m=getOwn(C.pkgs,n)?g=[n]:g.slice(0,g.length-1),t=m.concat(t.split("/")),e(t),o=getOwn(C.pkgs,r=t[0]),t=t.join("/"),o&&t===r+"/"+o.main&&(t=r)):0===t.indexOf("./")&&(t=t.substring(2))),i&&y&&(g||v)){for(a=t.split("/"),l=a.length;l>0;l-=1){if(u=a.slice(0,l).join("/"),g)for(c=g.length;c>0;c-=1)if(s=getOwn(y,g.slice(0,c).join("/")),s&&(s=getOwn(s,u))){h=s,p=l;break}if(h)break;!d&&v&&getOwn(v,u)&&(d=getOwn(v,u),f=l)}!h&&d&&(h=d,p=f),h&&(a.splice(0,p,h),t=a.join("/"))}return t}function i(t){isBrowser&&each(scripts(),function(e){return e.getAttribute("data-requiremodule")===t&&e.getAttribute("data-requirecontext")===b.contextName?(e.parentNode.removeChild(e),!0):void 0})}function r(t){var e=getOwn(C.paths,t);return e&&isArray(e)&&e.length>1?(e.shift(),b.require.undef(t),b.require([t]),!0):void 0}function o(t){var e,n=t?t.indexOf("!"):-1;return n>-1&&(e=t.substring(0,n),t=t.substring(n+1,t.length)),[e,t]}function s(t,e,i,r){var s,a,l,c,u=null,h=e?e.name:null,p=t,d=!0,f="";return t||(d=!1,t="_@r"+(A+=1)),c=o(t),u=c[0],t=c[1],u&&(u=n(u,h,r),a=getOwn(E,u)),t&&(u?f=a&&a.normalize?a.normalize(t,function(t){return n(t,h,r)}):n(t,h,r):(f=n(t,h,r),c=o(f),u=c[0],f=c[1],i=!0,s=b.nameToUrl(f))),l=!u||a||i?"":"_unnormalized"+(M+=1),{prefix:u,name:f,parentMap:e,unnormalized:!!l,url:s,originalName:p,isDefine:d,id:(u?u+"!"+f:f)+l}}function a(t){var e=t.id,n=getOwn(k,e);return n||(n=k[e]=new b.Module(t)),n}function l(t,e,n){var i=t.id,r=getOwn(k,i);!hasProp(E,i)||r&&!r.defineEmitComplete?(r=a(t),r.error&&"error"===e?n(r.error):r.on(e,n)):"defined"===e&&n(E[i])}function c(t,e){var n=t.requireModules,i=!1;e?e(t):(each(n,function(e){var n=getOwn(k,e);n&&(n.error=t,n.events.error&&(i=!0,n.emit("error",t)))}),i||req.onError(t))}function u(){globalDefQueue.length&&(apsp.apply(P,[P.length-1,0].concat(globalDefQueue)),globalDefQueue=[])}function h(t){delete k[t],delete T[t]}function p(t,e,n){var i=t.map.id;t.error?t.emit("error",t.error):(e[i]=!0,each(t.depMaps,function(i,r){var o=i.id,s=getOwn(k,o);!s||t.depMatched[r]||n[o]||(getOwn(e,o)?(t.defineDep(r,E[o]),t.check()):p(s,e,n))}),n[i]=!0)}function d(){var t,e,n,o,s=1e3*C.waitSeconds,a=s&&b.startTime+s<(new Date).getTime(),l=[],u=[],h=!1,f=!0;if(!v){if(v=!0,eachProp(T,function(n){if(t=n.map,e=t.id,n.enabled&&(t.isDefine||u.push(n),!n.error))if(!n.inited&&a)r(e)?(o=!0,h=!0):(l.push(e),i(e));else if(!n.inited&&n.fetched&&t.isDefine&&(h=!0,!t.prefix))return f=!1}),a&&l.length)return n=makeError("timeout","Load timeout for modules: "+l,null,l),n.contextName=b.contextName,c(n);f&&each(u,function(t){p(t,{},{})}),a&&!o||!h||!isBrowser&&!isWebWorker||w||(w=setTimeout(function(){w=0,d()},50)),v=!1}}function f(t){hasProp(E,t[0])||a(s(t[0],null,!0)).init(t[1],t[2])}function g(t,e,n,i){t.detachEvent&&!isOpera?i&&t.detachEvent(i,e):t.removeEventListener(n,e,!1)}function m(t){var e=t.currentTarget||t.srcElement;return g(e,b.onScriptLoad,"load","onreadystatechange"),g(e,b.onScriptError,"error"),{node:e,id:e&&e.getAttribute("data-requiremodule")}}function y(){var t;for(u();P.length;){if(t=P.shift(),null===t[0])return c(makeError("mismatch","Mismatched anonymous define() module: "+t[t.length-1]));f(t)}}var v,_,b,x,w,C={waitSeconds:7,baseUrl:"./",paths:{},pkgs:{},shim:{},config:{}},k={},T={},S={},P=[],E={},N={},A=1,M=1;return x={require:function(t){return t.require?t.require:t.require=b.makeRequire(t.map)},exports:function(t){return t.usingExports=!0,t.map.isDefine?t.exports?t.exports:t.exports=E[t.map.id]={}:void 0},module:function(t){return t.module?t.module:t.module={id:t.map.id,uri:t.map.url,config:function(){var e,n=getOwn(C.pkgs,t.map.id);return e=n?getOwn(C.config,t.map.id+"/"+n.main):getOwn(C.config,t.map.id),e||{}},exports:E[t.map.id]}}},_=function(t){this.events=getOwn(S,t.id)||{},this.map=t,this.shim=getOwn(C.shim,t.id),this.depExports=[],this.depMaps=[],this.depMatched=[],this.pluginMaps={},this.depCount=0},_.prototype={init:function(t,e,n,i){i=i||{},this.inited||(this.factory=e,n?this.on("error",n):this.events.error&&(n=bind(this,function(t){this.emit("error",t)})),this.depMaps=t&&t.slice(0),this.errback=n,this.inited=!0,this.ignore=i.ignore,i.enabled||this.enabled?this.enable():this.check())},defineDep:function(t,e){this.depMatched[t]||(this.depMatched[t]=!0,this.depCount-=1,this.depExports[t]=e)},fetch:function(){if(!this.fetched){this.fetched=!0,b.startTime=(new Date).getTime();var t=this.map;return this.shim?(b.makeRequire(this.map,{enableBuildCallback:!0})(this.shim.deps||[],bind(this,function(){return t.prefix?this.callPlugin():this.load()})),void 0):t.prefix?this.callPlugin():this.load()}},load:function(){var t=this.map.url;N[t]||(N[t]=!0,b.load(this.map.id,t))},check:function(){if(this.enabled&&!this.enabling){var t,e,n=this.map.id,i=this.depExports,r=this.exports,o=this.factory;if(this.inited){if(this.error)this.emit("error",this.error);else if(!this.defining){if(this.defining=!0,this.depCount<1&&!this.defined){if(isFunction(o)){if(this.events.error&&this.map.isDefine||req.onError!==defaultOnError)try{r=b.execCb(n,o,i,r)}catch(s){t=s}else r=b.execCb(n,o,i,r);if(this.map.isDefine&&(e=this.module,e&&void 0!==e.exports&&e.exports!==this.exports?r=e.exports:void 0===r&&this.usingExports&&(r=this.exports)),t)return t.requireMap=this.map,t.requireModules=this.map.isDefine?[this.map.id]:null,t.requireType=this.map.isDefine?"define":"require",c(this.error=t)}else r=o;this.exports=r,this.map.isDefine&&!this.ignore&&(E[n]=r,req.onResourceLoad&&req.onResourceLoad(b,this.map,this.depMaps)),h(n),this.defined=!0}this.defining=!1,this.defined&&!this.defineEmitted&&(this.defineEmitted=!0,this.emit("defined",this.exports),this.defineEmitComplete=!0)}}else this.fetch()}},callPlugin:function(){var t=this.map,e=t.id,i=s(t.prefix);this.depMaps.push(i),l(i,"defined",bind(this,function(i){var r,o,u,p=this.map.name,d=this.map.parentMap?this.map.parentMap.name:null,f=b.makeRequire(t.parentMap,{enableBuildCallback:!0});return this.map.unnormalized?(i.normalize&&(p=i.normalize(p,function(t){return n(t,d,!0)})||""),o=s(t.prefix+"!"+p,this.map.parentMap),l(o,"defined",bind(this,function(t){this.init([],function(){return t},null,{enabled:!0,ignore:!0})})),u=getOwn(k,o.id),u&&(this.depMaps.push(o),this.events.error&&u.on("error",bind(this,function(t){this.emit("error",t)})),u.enable()),void 0):(r=bind(this,function(t){this.init([],function(){return t},null,{enabled:!0})}),r.error=bind(this,function(t){this.inited=!0,this.error=t,t.requireModules=[e],eachProp(k,function(t){0===t.map.id.indexOf(e+"_unnormalized")&&h(t.map.id)}),c(t)}),r.fromText=bind(this,function(n,i){var o=t.name,l=s(o),u=useInteractive;i&&(n=i),u&&(useInteractive=!1),a(l),hasProp(C.config,e)&&(C.config[o]=C.config[e]);try{req.exec(n)}catch(h){return c(makeError("fromtexteval","fromText eval for "+e+" failed: "+h,h,[e]))}u&&(useInteractive=!0),this.depMaps.push(l),b.completeLoad(o),f([o],r)}),i.load(t.name,f,r,C),void 0)})),b.enable(i,this),this.pluginMaps[i.id]=i},enable:function(){T[this.map.id]=this,this.enabled=!0,this.enabling=!0,each(this.depMaps,bind(this,function(t,e){var n,i,r;if("string"==typeof t){if(t=s(t,this.map.isDefine?this.map:this.map.parentMap,!1,!this.skipMap),this.depMaps[e]=t,r=getOwn(x,t.id))return this.depExports[e]=r(this),void 0;this.depCount+=1,l(t,"defined",bind(this,function(t){this.defineDep(e,t),this.check()})),this.errback&&l(t,"error",bind(this,this.errback))}n=t.id,i=k[n],hasProp(x,n)||!i||i.enabled||b.enable(t,this)})),eachProp(this.pluginMaps,bind(this,function(t){var e=getOwn(k,t.id);e&&!e.enabled&&b.enable(t,this)})),this.enabling=!1,this.check()},on:function(t,e){var n=this.events[t];n||(n=this.events[t]=[]),n.push(e)},emit:function(t,e){each(this.events[t],function(t){t(e)}),"error"===t&&delete this.events[t]}},b={config:C,contextName:t,registry:k,defined:E,urlFetched:N,defQueue:P,Module:_,makeModuleMap:s,nextTick:req.nextTick,onError:c,configure:function(t){t.baseUrl&&"/"!==t.baseUrl.charAt(t.baseUrl.length-1)&&(t.baseUrl+="/");var e=C.pkgs,n=C.shim,i={paths:!0,config:!0,map:!0};eachProp(t,function(t,e){i[e]?"map"===e?(C.map||(C.map={}),mixin(C[e],t,!0,!0)):mixin(C[e],t,!0):C[e]=t}),t.shim&&(eachProp(t.shim,function(t,e){isArray(t)&&(t={deps:t}),!t.exports&&!t.init||t.exportsFn||(t.exportsFn=b.makeShimExports(t)),n[e]=t}),C.shim=n),t.packages&&(each(t.packages,function(t){var n;t="string"==typeof t?{name:t}:t,n=t.location,e[t.name]={name:t.name,location:n||t.name,main:(t.main||"main").replace(currDirRegExp,"").replace(jsSuffixRegExp,"")}}),C.pkgs=e),eachProp(k,function(t,e){t.inited||t.map.unnormalized||(t.map=s(e))}),(t.deps||t.callback)&&b.require(t.deps||[],t.callback)},makeShimExports:function(t){function e(){var e;return t.init&&(e=t.init.apply(global,arguments)),e||t.exports&&getGlobal(t.exports)}return e},makeRequire:function(e,r){function o(n,i,l){var u,h,p;return r.enableBuildCallback&&i&&isFunction(i)&&(i.__requireJsBuild=!0),"string"==typeof n?isFunction(i)?c(makeError("requireargs","Invalid require call"),l):e&&hasProp(x,n)?x[n](k[e.id]):req.get?req.get(b,n,e,o):(h=s(n,e,!1,!0),u=h.id,hasProp(E,u)?E[u]:c(makeError("notloaded",'Module name "'+u+'" has not been loaded yet for context: '+t+(e?"":". Use require([])")))):(y(),b.nextTick(function(){y(),p=a(s(null,e)),p.skipMap=r.skipMap,p.init(n,i,l,{enabled:!0}),d()}),o)}return r=r||{},mixin(o,{isBrowser:isBrowser,toUrl:function(t){var i,r=t.lastIndexOf("."),o=t.split("/")[0],s="."===o||".."===o;return-1!==r&&(!s||r>1)&&(i=t.substring(r,t.length),t=t.substring(0,r)),b.nameToUrl(n(t,e&&e.id,!0),i,!0)},defined:function(t){return hasProp(E,s(t,e,!1,!0).id)},specified:function(t){return t=s(t,e,!1,!0).id,hasProp(E,t)||hasProp(k,t)}}),e||(o.undef=function(t){u();var n=s(t,e,!0),r=getOwn(k,t);i(t),delete E[t],delete N[n.url],delete S[t],r&&(r.events.defined&&(S[t]=r.events),h(t))}),o},enable:function(t){var e=getOwn(k,t.id);e&&a(t).enable()},completeLoad:function(t){var e,n,i,o=getOwn(C.shim,t)||{},s=o.exports;for(u();P.length;){if(n=P.shift(),null===n[0]){if(n[0]=t,e)break;e=!0}else n[0]===t&&(e=!0);f(n)}if(i=getOwn(k,t),!e&&!hasProp(E,t)&&i&&!i.inited){if(!(!C.enforceDefine||s&&getGlobal(s)))return r(t)?void 0:c(makeError("nodefine","No define call for "+t,null,[t]));f([t,o.deps||[],o.exportsFn])}d()},nameToUrl:function(t,e,n){var i,r,o,s,a,l,c,u,h;if(req.jsExtRegExp.test(t))u=t+(e||"");else{for(i=C.paths,r=C.pkgs,a=t.split("/"),l=a.length;l>0;l-=1){if(c=a.slice(0,l).join("/"),o=getOwn(r,c),h=getOwn(i,c)){isArray(h)&&(h=h[0]),a.splice(0,l,h);break}if(o){s=t===o.name?o.location+"/"+o.main:o.location,a.splice(0,l,s);break}}u=a.join("/"),u+=e||(/^data\:|\?/.test(u)||n?"":".js"),u=("/"===u.charAt(0)||u.match(/^[\w\+\.\-]+:/)?"":C.baseUrl)+u}return C.urlArgs?u+((-1===u.indexOf("?")?"?":"&")+C.urlArgs):u},load:function(t,e){req.load(b,t,e)},execCb:function(t,e,n,i){return e.apply(i,n)},onScriptLoad:function(t){if("load"===t.type||readyRegExp.test((t.currentTarget||t.srcElement).readyState)){interactiveScript=null;var e=m(t);b.completeLoad(e.id)}},onScriptError:function(t){var e=m(t);return r(e.id)?void 0:c(makeError("scripterror","Script error for: "+e.id,t,[e.id]))}},b.require=b.makeRequire(),b}function getInteractiveScript(){return interactiveScript&&"interactive"===interactiveScript.readyState?interactiveScript:(eachReverse(scripts(),function(t){return"interactive"===t.readyState?interactiveScript=t:void 0}),interactiveScript)}var req,s,head,baseElement,dataMain,src,interactiveScript,currentlyAddingScript,mainScript,subPath,version="2.1.9",commentRegExp=/(\/\*([\s\S]*?)\*\/|([^:]|^)\/\/(.*)$)/gm,cjsRequireRegExp=/[^.]\s*require\s*\(\s*["']([^'"\s]+)["']\s*\)/g,jsSuffixRegExp=/\.js$/,currDirRegExp=/^\.\//,op=Object.prototype,ostring=op.toString,hasOwn=op.hasOwnProperty,ap=Array.prototype,apsp=ap.splice,isBrowser=!("undefined"==typeof window||"undefined"==typeof navigator||!window.document),isWebWorker=!isBrowser&&"undefined"!=typeof importScripts,readyRegExp=isBrowser&&"PLAYSTATION 3"===navigator.platform?/^complete$/:/^(complete|loaded)$/,defContextName="_",isOpera="undefined"!=typeof opera&&"[object Opera]"===opera.toString(),contexts={},cfg={},globalDefQueue=[],useInteractive=!1;if("undefined"==typeof define){if("undefined"!=typeof requirejs){if(isFunction(requirejs))return;cfg=requirejs,requirejs=void 0}"undefined"==typeof require||isFunction(require)||(cfg=require,require=void 0),req=requirejs=function(t,e,n,i){var r,o,s=defContextName;return isArray(t)||"string"==typeof t||(o=t,isArray(e)?(t=e,e=n,n=i):t=[]),o&&o.context&&(s=o.context),r=getOwn(contexts,s),r||(r=contexts[s]=req.s.newContext(s)),o&&r.configure(o),r.require(t,e,n)},req.config=function(t){return req(t)},req.nextTick="undefined"!=typeof setTimeout?function(t){setTimeout(t,4)}:function(t){t()},require||(require=req),req.version=version,req.jsExtRegExp=/^\/|:|\?|\.js$/,req.isBrowser=isBrowser,s=req.s={contexts:contexts,newContext:newContext},req({}),each(["toUrl","undef","defined","specified"],function(t){req[t]=function(){var e=contexts[defContextName];return e.require[t].apply(e,arguments)}}),isBrowser&&(head=s.head=document.getElementsByTagName("head")[0],baseElement=document.getElementsByTagName("base")[0],baseElement&&(head=s.head=baseElement.parentNode)),req.onError=defaultOnError,req.createNode=function(t){var e=t.xhtml?document.createElementNS("http://www.w3.org/1999/xhtml","html:script"):document.createElement("script");return e.type=t.scriptType||"text/javascript",e.charset="utf-8",e.async=!0,e},req.load=function(t,e,n){var i,r=t&&t.config||{};if(isBrowser)return i=req.createNode(r,e,n),i.setAttribute("data-requirecontext",t.contextName),i.setAttribute("data-requiremodule",e),!i.attachEvent||i.attachEvent.toString&&i.attachEvent.toString().indexOf("[native code")<0||isOpera?(i.addEventListener("load",t.onScriptLoad,!1),i.addEventListener("error",t.onScriptError,!1)):(useInteractive=!0,i.attachEvent("onreadystatechange",t.onScriptLoad)),i.src=n,currentlyAddingScript=i,baseElement?head.insertBefore(i,baseElement):head.appendChild(i),currentlyAddingScript=null,i;if(isWebWorker)try{importScripts(n),t.completeLoad(e)}catch(o){t.onError(makeError("importscripts","importScripts failed for "+e+" at "+n,o,[e]))}},isBrowser&&!cfg.skipDataMain&&eachReverse(scripts(),function(t){return head||(head=t.parentNode),dataMain=t.getAttribute("data-main"),dataMain?(mainScript=dataMain,cfg.baseUrl||(src=mainScript.split("/"),mainScript=src.pop(),subPath=src.length?src.join("/")+"/":"./",cfg.baseUrl=subPath),mainScript=mainScript.replace(jsSuffixRegExp,""),req.jsExtRegExp.test(mainScript)&&(mainScript=dataMain),cfg.deps=cfg.deps?cfg.deps.concat(mainScript):[mainScript],!0):void 0}),define=function(t,e,n){var i,r;"string"!=typeof t&&(n=e,e=t,t=null),isArray(e)||(n=e,e=null),!e&&isFunction(n)&&(e=[],n.length&&(n.toString().replace(commentRegExp,"").replace(cjsRequireRegExp,function(t,n){e.push(n)}),e=(1===n.length?["require"]:["require","exports","module"]).concat(e))),useInteractive&&(i=currentlyAddingScript||getInteractiveScript(),i&&(t||(t=i.getAttribute("data-requiremodule")),r=contexts[i.getAttribute("data-requirecontext")])),(r?r.defQueue:globalDefQueue).push([t,e,n])},define.amd={jQuery:!0},req.exec=function(text){return eval(text)},req(cfg)}}(this);