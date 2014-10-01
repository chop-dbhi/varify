(function(e,t){typeof define=="function"&&define.amd?define(["module"],t):typeof exports=="object"?module.exports=t():e.returnExports=t()})(this,function(e){var t="0.0.1",n={},r={debug:function(e){i&&window.console.debug("[SolveBio] "+e)},error:function(e){window.console.error("[SolveBio] "+e)},warn:function(e){window.console.warn("[SolveBio] "+e)}};e&&typeof e.config=="function"&&(n=e.config());var i=n.debug||!1,s=n.appId,o=n.accessToken,u=n.apiHost?n.apiHost.replace(/\/?$/,""):"https://api.solvebio.com",a=[],f=function(e){var t=[];for(var n in e){var r=n,i=e[n];t.push(typeof i=="object"?f(i,r):encodeURIComponent(r)+"="+encodeURIComponent(i))}return t.join("&")},l=function(e,t){return e+(e.indexOf("?")>0?"&":"?")+f(t)},c={},h=!1,p=function(){if(h)return;h=!0,window.addEventListener("message",function(e){e=e.originalEvent||e;if(a.indexOf(e.origin)<0){r.debug("Invalid message origin ("+e.origin+"), "+'expected: "'+a+'"');return}var t;try{t=e.data&&e.data.length>0?JSON.parse(e.data):!1}catch(n){return}if(!t)return;if(t.name in c){var i=c[t.name];if(!i._loaded){r.debug('Dashboard "'+t.name+'" loaded!'),i._loaded=!0,i.postMessage({settings:i._settings});for(var s=0;s<i._onLoad.length;++s)i._onLoad[s](i)}t.height&&(r.debug("Dashboard updating height to: "+t.height+"px"),i._iframe.style.height=t.height+"px")}},!1)},d={version:function(){return t},setDebug:function(e){i=!!e},apiHost:function(){return u},setApiHost:function(e){r.debug("Setting API host to "+e),u=e.replace(/\/?$/,"")},setAppId:function(e){s=e},getAppId:function(){return s},setAccessToken:function(e){o=e},getAccessToken:function(){return o},rest:function(e,t,n,i,s){e=e.toUpperCase();var a=""+u+"/"+t.replace(/^\/?/,"");n=n||{},i=i||function(){},s=s||function(){},!o||(n.access_token=o),e==="GET"||e==="HEAD"?(a=l(a,n),n=null):n=JSON.stringify(n,null,4);var f=new XMLHttpRequest;return f.onreadystatechange=function(){if(f.readyState===4&&f.status!==200)try{s(JSON.parse(f.responseText))}catch(e){s(f.responseText)}if(f.readyState===4&&f.status===200)try{i(JSON.parse(f.responseText))}catch(e){s(f.responseText)}},r.debug("Sending "+e+" request to "+a),f.open(e,a,!0),f.setRequestHeader("Content-type","application/json"),f.send(n),f},Dashboards:{all:function(){return c},create:function(e,t,n,s){var f,h,d;if(e in c)return c[e];f=document.getElementById(n.replace("#",""));if(!f)return r.error('Dashboards.create() could not find target by ID "'+n+'"'),!1;p(),s=s?s:{},s.name=e,s.debug=i,u&&(s.apiHost=u),o&&(s.accessToken=o);var v=document.createElement("a");v.href=t;var m=v.protocol+"//"+v.host;return a.push(m),h=document.createElement("iframe"),h.setAttribute("src",l(t,{name:e,debug:i,origin:window.location.origin})),h.setAttribute("id",e+"-iframe"),h.setAttribute("name",e),h.setAttribute("width","100%"),h.setAttribute("height","100%"),h.setAttribute("scrolling","no"),h.setAttribute("frameborder","0"),h.style.border="none",h.style.width="100%",h.style.minHeight="800px",f.insertBefore(h,f.firstChild),d={_name:e,_id:e+"-iframe",_iframe:h,_loaded:!1,_origin:m,_settings:s,_onLoad:[],postMessage:function(e){d._iframe&&d._iframe.contentWindow?d._iframe.contentWindow.postMessage(JSON.stringify(e),d._origin):r.error("Could not postMessage to dashboard: "+d._name)},ready:function(e){this._loaded?e(this):this._onLoad.push(e)}},c[e]=d,d},get:function(e){return c[e]},"delete":function(e){if(e in c){var t=c[e]._iframe;delete c[e];try{t.parentNode.removeChild(t)}catch(n){}}else r.error('Could not delete dashboard "'+e+'": not found.')}}},v=function(e){d[e.toLowerCase()]=function(){return this.rest.apply(this,[e].concat([].slice.call(arguments)))}},m=["GET","PUT","POST","DELETE"];for(var g=0;g<m.length;g++)v(m[g]);return d})