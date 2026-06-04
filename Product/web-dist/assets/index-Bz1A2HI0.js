(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))s(o);new MutationObserver(o=>{for(const c of o)if(c.type==="childList")for(const u of c.addedNodes)u.tagName==="LINK"&&u.rel==="modulepreload"&&s(u)}).observe(document,{childList:!0,subtree:!0});function n(o){const c={};return o.integrity&&(c.integrity=o.integrity),o.referrerPolicy&&(c.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?c.credentials="include":o.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function s(o){if(o.ep)return;o.ep=!0;const c=n(o);fetch(o.href,c)}})();function w1(i){return i&&i.__esModule&&Object.prototype.hasOwnProperty.call(i,"default")?i.default:i}var Dh={exports:{}},Ml={};var _x;function D1(){if(_x)return Ml;_x=1;var i=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function n(s,o,c){var u=null;if(c!==void 0&&(u=""+c),o.key!==void 0&&(u=""+o.key),"key"in o){c={};for(var d in o)d!=="key"&&(c[d]=o[d])}else c=o;return o=c.ref,{$$typeof:i,type:s,key:u,ref:o!==void 0?o:null,props:c}}return Ml.Fragment=t,Ml.jsx=n,Ml.jsxs=n,Ml}var vx;function N1(){return vx||(vx=1,Dh.exports=D1()),Dh.exports}var D=N1(),Nh={exports:{}},re={};var xx;function L1(){if(xx)return re;xx=1;var i=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),n=Symbol.for("react.fragment"),s=Symbol.for("react.strict_mode"),o=Symbol.for("react.profiler"),c=Symbol.for("react.consumer"),u=Symbol.for("react.context"),d=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),h=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),_=Symbol.for("react.activity"),v=Symbol.iterator;function y(z){return z===null||typeof z!="object"?null:(z=v&&z[v]||z["@@iterator"],typeof z=="function"?z:null)}var b={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},R=Object.assign,S={};function x(z,Q,St){this.props=z,this.context=Q,this.refs=S,this.updater=St||b}x.prototype.isReactComponent={},x.prototype.setState=function(z,Q){if(typeof z!="object"&&typeof z!="function"&&z!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,z,Q,"setState")},x.prototype.forceUpdate=function(z){this.updater.enqueueForceUpdate(this,z,"forceUpdate")};function A(){}A.prototype=x.prototype;function N(z,Q,St){this.props=z,this.context=Q,this.refs=S,this.updater=St||b}var L=N.prototype=new A;L.constructor=N,R(L,x.prototype),L.isPureReactComponent=!0;var H=Array.isArray;function B(){}var O={H:null,A:null,T:null,S:null},E=Object.prototype.hasOwnProperty;function U(z,Q,St){var Rt=St.ref;return{$$typeof:i,type:z,key:Q,ref:Rt!==void 0?Rt:null,props:St}}function V(z,Q){return U(z.type,Q,z.props)}function F(z){return typeof z=="object"&&z!==null&&z.$$typeof===i}function j(z){var Q={"=":"=0",":":"=2"};return"$"+z.replace(/[=:]/g,function(St){return Q[St]})}var lt=/\/+/g;function ct(z,Q){return typeof z=="object"&&z!==null&&z.key!=null?j(""+z.key):Q.toString(36)}function q(z){switch(z.status){case"fulfilled":return z.value;case"rejected":throw z.reason;default:switch(typeof z.status=="string"?z.then(B,B):(z.status="pending",z.then(function(Q){z.status==="pending"&&(z.status="fulfilled",z.value=Q)},function(Q){z.status==="pending"&&(z.status="rejected",z.reason=Q)})),z.status){case"fulfilled":return z.value;case"rejected":throw z.reason}}throw z}function I(z,Q,St,Rt,Nt){var ot=typeof z;(ot==="undefined"||ot==="boolean")&&(z=null);var Mt=!1;if(z===null)Mt=!0;else switch(ot){case"bigint":case"string":case"number":Mt=!0;break;case"object":switch(z.$$typeof){case i:case t:Mt=!0;break;case g:return Mt=z._init,I(Mt(z._payload),Q,St,Rt,Nt)}}if(Mt)return Nt=Nt(z),Mt=Rt===""?"."+ct(z,0):Rt,H(Nt)?(St="",Mt!=null&&(St=Mt.replace(lt,"$&/")+"/"),I(Nt,Q,St,"",function(ee){return ee})):Nt!=null&&(F(Nt)&&(Nt=V(Nt,St+(Nt.key==null||z&&z.key===Nt.key?"":(""+Nt.key).replace(lt,"$&/")+"/")+Mt)),Q.push(Nt)),1;Mt=0;var Tt=Rt===""?".":Rt+":";if(H(z))for(var Ht=0;Ht<z.length;Ht++)Rt=z[Ht],ot=Tt+ct(Rt,Ht),Mt+=I(Rt,Q,St,ot,Nt);else if(Ht=y(z),typeof Ht=="function")for(z=Ht.call(z),Ht=0;!(Rt=z.next()).done;)Rt=Rt.value,ot=Tt+ct(Rt,Ht++),Mt+=I(Rt,Q,St,ot,Nt);else if(ot==="object"){if(typeof z.then=="function")return I(q(z),Q,St,Rt,Nt);throw Q=String(z),Error("Objects are not valid as a React child (found: "+(Q==="[object Object]"?"object with keys {"+Object.keys(z).join(", ")+"}":Q)+"). If you meant to render a collection of children, use an array instead.")}return Mt}function G(z,Q,St){if(z==null)return z;var Rt=[],Nt=0;return I(z,Rt,"","",function(ot){return Q.call(St,ot,Nt++)}),Rt}function $(z){if(z._status===-1){var Q=z._result;Q=Q(),Q.then(function(St){(z._status===0||z._status===-1)&&(z._status=1,z._result=St)},function(St){(z._status===0||z._status===-1)&&(z._status=2,z._result=St)}),z._status===-1&&(z._status=0,z._result=Q)}if(z._status===1)return z._result.default;throw z._result}var dt=typeof reportError=="function"?reportError:function(z){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var Q=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof z=="object"&&z!==null&&typeof z.message=="string"?String(z.message):String(z),error:z});if(!window.dispatchEvent(Q))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",z);return}console.error(z)},xt={map:G,forEach:function(z,Q,St){G(z,function(){Q.apply(this,arguments)},St)},count:function(z){var Q=0;return G(z,function(){Q++}),Q},toArray:function(z){return G(z,function(Q){return Q})||[]},only:function(z){if(!F(z))throw Error("React.Children.only expected to receive a single React element child.");return z}};return re.Activity=_,re.Children=xt,re.Component=x,re.Fragment=n,re.Profiler=o,re.PureComponent=N,re.StrictMode=s,re.Suspense=p,re.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=O,re.__COMPILER_RUNTIME={__proto__:null,c:function(z){return O.H.useMemoCache(z)}},re.cache=function(z){return function(){return z.apply(null,arguments)}},re.cacheSignal=function(){return null},re.cloneElement=function(z,Q,St){if(z==null)throw Error("The argument must be a React element, but you passed "+z+".");var Rt=R({},z.props),Nt=z.key;if(Q!=null)for(ot in Q.key!==void 0&&(Nt=""+Q.key),Q)!E.call(Q,ot)||ot==="key"||ot==="__self"||ot==="__source"||ot==="ref"&&Q.ref===void 0||(Rt[ot]=Q[ot]);var ot=arguments.length-2;if(ot===1)Rt.children=St;else if(1<ot){for(var Mt=Array(ot),Tt=0;Tt<ot;Tt++)Mt[Tt]=arguments[Tt+2];Rt.children=Mt}return U(z.type,Nt,Rt)},re.createContext=function(z){return z={$$typeof:u,_currentValue:z,_currentValue2:z,_threadCount:0,Provider:null,Consumer:null},z.Provider=z,z.Consumer={$$typeof:c,_context:z},z},re.createElement=function(z,Q,St){var Rt,Nt={},ot=null;if(Q!=null)for(Rt in Q.key!==void 0&&(ot=""+Q.key),Q)E.call(Q,Rt)&&Rt!=="key"&&Rt!=="__self"&&Rt!=="__source"&&(Nt[Rt]=Q[Rt]);var Mt=arguments.length-2;if(Mt===1)Nt.children=St;else if(1<Mt){for(var Tt=Array(Mt),Ht=0;Ht<Mt;Ht++)Tt[Ht]=arguments[Ht+2];Nt.children=Tt}if(z&&z.defaultProps)for(Rt in Mt=z.defaultProps,Mt)Nt[Rt]===void 0&&(Nt[Rt]=Mt[Rt]);return U(z,ot,Nt)},re.createRef=function(){return{current:null}},re.forwardRef=function(z){return{$$typeof:d,render:z}},re.isValidElement=F,re.lazy=function(z){return{$$typeof:g,_payload:{_status:-1,_result:z},_init:$}},re.memo=function(z,Q){return{$$typeof:h,type:z,compare:Q===void 0?null:Q}},re.startTransition=function(z){var Q=O.T,St={};O.T=St;try{var Rt=z(),Nt=O.S;Nt!==null&&Nt(St,Rt),typeof Rt=="object"&&Rt!==null&&typeof Rt.then=="function"&&Rt.then(B,dt)}catch(ot){dt(ot)}finally{Q!==null&&St.types!==null&&(Q.types=St.types),O.T=Q}},re.unstable_useCacheRefresh=function(){return O.H.useCacheRefresh()},re.use=function(z){return O.H.use(z)},re.useActionState=function(z,Q,St){return O.H.useActionState(z,Q,St)},re.useCallback=function(z,Q){return O.H.useCallback(z,Q)},re.useContext=function(z){return O.H.useContext(z)},re.useDebugValue=function(){},re.useDeferredValue=function(z,Q){return O.H.useDeferredValue(z,Q)},re.useEffect=function(z,Q){return O.H.useEffect(z,Q)},re.useEffectEvent=function(z){return O.H.useEffectEvent(z)},re.useId=function(){return O.H.useId()},re.useImperativeHandle=function(z,Q,St){return O.H.useImperativeHandle(z,Q,St)},re.useInsertionEffect=function(z,Q){return O.H.useInsertionEffect(z,Q)},re.useLayoutEffect=function(z,Q){return O.H.useLayoutEffect(z,Q)},re.useMemo=function(z,Q){return O.H.useMemo(z,Q)},re.useOptimistic=function(z,Q){return O.H.useOptimistic(z,Q)},re.useReducer=function(z,Q,St){return O.H.useReducer(z,Q,St)},re.useRef=function(z){return O.H.useRef(z)},re.useState=function(z){return O.H.useState(z)},re.useSyncExternalStore=function(z,Q,St){return O.H.useSyncExternalStore(z,Q,St)},re.useTransition=function(){return O.H.useTransition()},re.version="19.2.6",re}var yx;function Km(){return yx||(yx=1,Nh.exports=L1()),Nh.exports}var yt=Km();const U1=w1(yt);var Lh={exports:{}},bl={},Uh={exports:{}},Ph={};var Sx;function P1(){return Sx||(Sx=1,(function(i){function t(I,G){var $=I.length;I.push(G);t:for(;0<$;){var dt=$-1>>>1,xt=I[dt];if(0<o(xt,G))I[dt]=G,I[$]=xt,$=dt;else break t}}function n(I){return I.length===0?null:I[0]}function s(I){if(I.length===0)return null;var G=I[0],$=I.pop();if($!==G){I[0]=$;t:for(var dt=0,xt=I.length,z=xt>>>1;dt<z;){var Q=2*(dt+1)-1,St=I[Q],Rt=Q+1,Nt=I[Rt];if(0>o(St,$))Rt<xt&&0>o(Nt,St)?(I[dt]=Nt,I[Rt]=$,dt=Rt):(I[dt]=St,I[Q]=$,dt=Q);else if(Rt<xt&&0>o(Nt,$))I[dt]=Nt,I[Rt]=$,dt=Rt;else break t}}return G}function o(I,G){var $=I.sortIndex-G.sortIndex;return $!==0?$:I.id-G.id}if(i.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var c=performance;i.unstable_now=function(){return c.now()}}else{var u=Date,d=u.now();i.unstable_now=function(){return u.now()-d}}var p=[],h=[],g=1,_=null,v=3,y=!1,b=!1,R=!1,S=!1,x=typeof setTimeout=="function"?setTimeout:null,A=typeof clearTimeout=="function"?clearTimeout:null,N=typeof setImmediate<"u"?setImmediate:null;function L(I){for(var G=n(h);G!==null;){if(G.callback===null)s(h);else if(G.startTime<=I)s(h),G.sortIndex=G.expirationTime,t(p,G);else break;G=n(h)}}function H(I){if(R=!1,L(I),!b)if(n(p)!==null)b=!0,B||(B=!0,j());else{var G=n(h);G!==null&&q(H,G.startTime-I)}}var B=!1,O=-1,E=5,U=-1;function V(){return S?!0:!(i.unstable_now()-U<E)}function F(){if(S=!1,B){var I=i.unstable_now();U=I;var G=!0;try{t:{b=!1,R&&(R=!1,A(O),O=-1),y=!0;var $=v;try{e:{for(L(I),_=n(p);_!==null&&!(_.expirationTime>I&&V());){var dt=_.callback;if(typeof dt=="function"){_.callback=null,v=_.priorityLevel;var xt=dt(_.expirationTime<=I);if(I=i.unstable_now(),typeof xt=="function"){_.callback=xt,L(I),G=!0;break e}_===n(p)&&s(p),L(I)}else s(p);_=n(p)}if(_!==null)G=!0;else{var z=n(h);z!==null&&q(H,z.startTime-I),G=!1}}break t}finally{_=null,v=$,y=!1}G=void 0}}finally{G?j():B=!1}}}var j;if(typeof N=="function")j=function(){N(F)};else if(typeof MessageChannel<"u"){var lt=new MessageChannel,ct=lt.port2;lt.port1.onmessage=F,j=function(){ct.postMessage(null)}}else j=function(){x(F,0)};function q(I,G){O=x(function(){I(i.unstable_now())},G)}i.unstable_IdlePriority=5,i.unstable_ImmediatePriority=1,i.unstable_LowPriority=4,i.unstable_NormalPriority=3,i.unstable_Profiling=null,i.unstable_UserBlockingPriority=2,i.unstable_cancelCallback=function(I){I.callback=null},i.unstable_forceFrameRate=function(I){0>I||125<I?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):E=0<I?Math.floor(1e3/I):5},i.unstable_getCurrentPriorityLevel=function(){return v},i.unstable_next=function(I){switch(v){case 1:case 2:case 3:var G=3;break;default:G=v}var $=v;v=G;try{return I()}finally{v=$}},i.unstable_requestPaint=function(){S=!0},i.unstable_runWithPriority=function(I,G){switch(I){case 1:case 2:case 3:case 4:case 5:break;default:I=3}var $=v;v=I;try{return G()}finally{v=$}},i.unstable_scheduleCallback=function(I,G,$){var dt=i.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?dt+$:dt):$=dt,I){case 1:var xt=-1;break;case 2:xt=250;break;case 5:xt=1073741823;break;case 4:xt=1e4;break;default:xt=5e3}return xt=$+xt,I={id:g++,callback:G,priorityLevel:I,startTime:$,expirationTime:xt,sortIndex:-1},$>dt?(I.sortIndex=$,t(h,I),n(p)===null&&I===n(h)&&(R?(A(O),O=-1):R=!0,q(H,$-dt))):(I.sortIndex=xt,t(p,I),b||y||(b=!0,B||(B=!0,j()))),I},i.unstable_shouldYield=V,i.unstable_wrapCallback=function(I){var G=v;return function(){var $=v;v=G;try{return I.apply(this,arguments)}finally{v=$}}}})(Ph)),Ph}var Mx;function O1(){return Mx||(Mx=1,Uh.exports=P1()),Uh.exports}var Oh={exports:{}},Hn={};var bx;function F1(){if(bx)return Hn;bx=1;var i=Km();function t(p){var h="https://react.dev/errors/"+p;if(1<arguments.length){h+="?args[]="+encodeURIComponent(arguments[1]);for(var g=2;g<arguments.length;g++)h+="&args[]="+encodeURIComponent(arguments[g])}return"Minified React error #"+p+"; visit "+h+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function n(){}var s={d:{f:n,r:function(){throw Error(t(522))},D:n,C:n,L:n,m:n,X:n,S:n,M:n},p:0,findDOMNode:null},o=Symbol.for("react.portal");function c(p,h,g){var _=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:o,key:_==null?null:""+_,children:p,containerInfo:h,implementation:g}}var u=i.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function d(p,h){if(p==="font")return"";if(typeof h=="string")return h==="use-credentials"?h:""}return Hn.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=s,Hn.createPortal=function(p,h){var g=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!h||h.nodeType!==1&&h.nodeType!==9&&h.nodeType!==11)throw Error(t(299));return c(p,h,null,g)},Hn.flushSync=function(p){var h=u.T,g=s.p;try{if(u.T=null,s.p=2,p)return p()}finally{u.T=h,s.p=g,s.d.f()}},Hn.preconnect=function(p,h){typeof p=="string"&&(h?(h=h.crossOrigin,h=typeof h=="string"?h==="use-credentials"?h:"":void 0):h=null,s.d.C(p,h))},Hn.prefetchDNS=function(p){typeof p=="string"&&s.d.D(p)},Hn.preinit=function(p,h){if(typeof p=="string"&&h&&typeof h.as=="string"){var g=h.as,_=d(g,h.crossOrigin),v=typeof h.integrity=="string"?h.integrity:void 0,y=typeof h.fetchPriority=="string"?h.fetchPriority:void 0;g==="style"?s.d.S(p,typeof h.precedence=="string"?h.precedence:void 0,{crossOrigin:_,integrity:v,fetchPriority:y}):g==="script"&&s.d.X(p,{crossOrigin:_,integrity:v,fetchPriority:y,nonce:typeof h.nonce=="string"?h.nonce:void 0})}},Hn.preinitModule=function(p,h){if(typeof p=="string")if(typeof h=="object"&&h!==null){if(h.as==null||h.as==="script"){var g=d(h.as,h.crossOrigin);s.d.M(p,{crossOrigin:g,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0})}}else h==null&&s.d.M(p)},Hn.preload=function(p,h){if(typeof p=="string"&&typeof h=="object"&&h!==null&&typeof h.as=="string"){var g=h.as,_=d(g,h.crossOrigin);s.d.L(p,g,{crossOrigin:_,integrity:typeof h.integrity=="string"?h.integrity:void 0,nonce:typeof h.nonce=="string"?h.nonce:void 0,type:typeof h.type=="string"?h.type:void 0,fetchPriority:typeof h.fetchPriority=="string"?h.fetchPriority:void 0,referrerPolicy:typeof h.referrerPolicy=="string"?h.referrerPolicy:void 0,imageSrcSet:typeof h.imageSrcSet=="string"?h.imageSrcSet:void 0,imageSizes:typeof h.imageSizes=="string"?h.imageSizes:void 0,media:typeof h.media=="string"?h.media:void 0})}},Hn.preloadModule=function(p,h){if(typeof p=="string")if(h){var g=d(h.as,h.crossOrigin);s.d.m(p,{as:typeof h.as=="string"&&h.as!=="script"?h.as:void 0,crossOrigin:g,integrity:typeof h.integrity=="string"?h.integrity:void 0})}else s.d.m(p)},Hn.requestFormReset=function(p){s.d.r(p)},Hn.unstable_batchedUpdates=function(p,h){return p(h)},Hn.useFormState=function(p,h,g){return u.H.useFormState(p,h,g)},Hn.useFormStatus=function(){return u.H.useHostTransitionStatus()},Hn.version="19.2.6",Hn}var Ex;function B1(){if(Ex)return Oh.exports;Ex=1;function i(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(i)}catch(t){console.error(t)}}return i(),Oh.exports=F1(),Oh.exports}var Tx;function I1(){if(Tx)return bl;Tx=1;var i=O1(),t=Km(),n=B1();function s(e){var a="https://react.dev/errors/"+e;if(1<arguments.length){a+="?args[]="+encodeURIComponent(arguments[1]);for(var r=2;r<arguments.length;r++)a+="&args[]="+encodeURIComponent(arguments[r])}return"Minified React error #"+e+"; visit "+a+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function o(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function c(e){var a=e,r=e;if(e.alternate)for(;a.return;)a=a.return;else{e=a;do a=e,(a.flags&4098)!==0&&(r=a.return),e=a.return;while(e)}return a.tag===3?r:null}function u(e){if(e.tag===13){var a=e.memoizedState;if(a===null&&(e=e.alternate,e!==null&&(a=e.memoizedState)),a!==null)return a.dehydrated}return null}function d(e){if(e.tag===31){var a=e.memoizedState;if(a===null&&(e=e.alternate,e!==null&&(a=e.memoizedState)),a!==null)return a.dehydrated}return null}function p(e){if(c(e)!==e)throw Error(s(188))}function h(e){var a=e.alternate;if(!a){if(a=c(e),a===null)throw Error(s(188));return a!==e?null:e}for(var r=e,l=a;;){var f=r.return;if(f===null)break;var m=f.alternate;if(m===null){if(l=f.return,l!==null){r=l;continue}break}if(f.child===m.child){for(m=f.child;m;){if(m===r)return p(f),e;if(m===l)return p(f),a;m=m.sibling}throw Error(s(188))}if(r.return!==l.return)r=f,l=m;else{for(var M=!1,w=f.child;w;){if(w===r){M=!0,r=f,l=m;break}if(w===l){M=!0,l=f,r=m;break}w=w.sibling}if(!M){for(w=m.child;w;){if(w===r){M=!0,r=m,l=f;break}if(w===l){M=!0,l=m,r=f;break}w=w.sibling}if(!M)throw Error(s(189))}}if(r.alternate!==l)throw Error(s(190))}if(r.tag!==3)throw Error(s(188));return r.stateNode.current===r?e:a}function g(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e;for(e=e.child;e!==null;){if(a=g(e),a!==null)return a;e=e.sibling}return null}var _=Object.assign,v=Symbol.for("react.element"),y=Symbol.for("react.transitional.element"),b=Symbol.for("react.portal"),R=Symbol.for("react.fragment"),S=Symbol.for("react.strict_mode"),x=Symbol.for("react.profiler"),A=Symbol.for("react.consumer"),N=Symbol.for("react.context"),L=Symbol.for("react.forward_ref"),H=Symbol.for("react.suspense"),B=Symbol.for("react.suspense_list"),O=Symbol.for("react.memo"),E=Symbol.for("react.lazy"),U=Symbol.for("react.activity"),V=Symbol.for("react.memo_cache_sentinel"),F=Symbol.iterator;function j(e){return e===null||typeof e!="object"?null:(e=F&&e[F]||e["@@iterator"],typeof e=="function"?e:null)}var lt=Symbol.for("react.client.reference");function ct(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===lt?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case R:return"Fragment";case x:return"Profiler";case S:return"StrictMode";case H:return"Suspense";case B:return"SuspenseList";case U:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case b:return"Portal";case N:return e.displayName||"Context";case A:return(e._context.displayName||"Context")+".Consumer";case L:var a=e.render;return e=e.displayName,e||(e=a.displayName||a.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case O:return a=e.displayName||null,a!==null?a:ct(e.type)||"Memo";case E:a=e._payload,e=e._init;try{return ct(e(a))}catch{}}return null}var q=Array.isArray,I=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,G=n.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,$={pending:!1,data:null,method:null,action:null},dt=[],xt=-1;function z(e){return{current:e}}function Q(e){0>xt||(e.current=dt[xt],dt[xt]=null,xt--)}function St(e,a){xt++,dt[xt]=e.current,e.current=a}var Rt=z(null),Nt=z(null),ot=z(null),Mt=z(null);function Tt(e,a){switch(St(ot,a),St(Nt,e),St(Rt,null),a.nodeType){case 9:case 11:e=(e=a.documentElement)&&(e=e.namespaceURI)?Vv(e):0;break;default:if(e=a.tagName,a=a.namespaceURI)a=Vv(a),e=Hv(a,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}Q(Rt),St(Rt,e)}function Ht(){Q(Rt),Q(Nt),Q(ot)}function ee(e){e.memoizedState!==null&&St(Mt,e);var a=Rt.current,r=Hv(a,e.type);a!==r&&(St(Nt,e),St(Rt,r))}function $t(e){Nt.current===e&&(Q(Rt),Q(Nt)),Mt.current===e&&(Q(Mt),vl._currentValue=$)}var Xe,he;function xe(e){if(Xe===void 0)try{throw Error()}catch(r){var a=r.stack.trim().match(/\n( *(at )?)/);Xe=a&&a[1]||"",he=-1<r.stack.indexOf(`
    at`)?" (<anonymous>)":-1<r.stack.indexOf("@")?"@unknown:0:0":""}return`
`+Xe+e+he}var Ue=!1;function ue(e,a){if(!e||Ue)return"";Ue=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var l={DetermineComponentFrameRoot:function(){try{if(a){var vt=function(){throw Error()};if(Object.defineProperty(vt.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(vt,[])}catch(ut){var st=ut}Reflect.construct(e,[],vt)}else{try{vt.call()}catch(ut){st=ut}e.call(vt.prototype)}}else{try{throw Error()}catch(ut){st=ut}(vt=e())&&typeof vt.catch=="function"&&vt.catch(function(){})}}catch(ut){if(ut&&st&&typeof ut.stack=="string")return[ut.stack,st.stack]}return[null,null]}};l.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var f=Object.getOwnPropertyDescriptor(l.DetermineComponentFrameRoot,"name");f&&f.configurable&&Object.defineProperty(l.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var m=l.DetermineComponentFrameRoot(),M=m[0],w=m[1];if(M&&w){var k=M.split(`
`),et=w.split(`
`);for(f=l=0;l<k.length&&!k[l].includes("DetermineComponentFrameRoot");)l++;for(;f<et.length&&!et[f].includes("DetermineComponentFrameRoot");)f++;if(l===k.length||f===et.length)for(l=k.length-1,f=et.length-1;1<=l&&0<=f&&k[l]!==et[f];)f--;for(;1<=l&&0<=f;l--,f--)if(k[l]!==et[f]){if(l!==1||f!==1)do if(l--,f--,0>f||k[l]!==et[f]){var pt=`
`+k[l].replace(" at new "," at ");return e.displayName&&pt.includes("<anonymous>")&&(pt=pt.replace("<anonymous>",e.displayName)),pt}while(1<=l&&0<=f);break}}}finally{Ue=!1,Error.prepareStackTrace=r}return(r=e?e.displayName||e.name:"")?xe(r):""}function cn(e,a){switch(e.tag){case 26:case 27:case 5:return xe(e.type);case 16:return xe("Lazy");case 13:return e.child!==a&&a!==null?xe("Suspense Fallback"):xe("Suspense");case 19:return xe("SuspenseList");case 0:case 15:return ue(e.type,!1);case 11:return ue(e.type.render,!1);case 1:return ue(e.type,!0);case 31:return xe("Activity");default:return""}}function Ze(e){try{var a="",r=null;do a+=cn(e,r),r=e,e=e.return;while(e);return a}catch(l){return`
Error generating stack: `+l.message+`
`+l.stack}}var Dn=Object.prototype.hasOwnProperty,Y=i.unstable_scheduleCallback,an=i.unstable_cancelCallback,pe=i.unstable_shouldYield,Ve=i.unstable_requestPaint,Ct=i.unstable_now,$e=i.unstable_getCurrentPriorityLevel,P=i.unstable_ImmediatePriority,T=i.unstable_UserBlockingPriority,J=i.unstable_NormalPriority,_t=i.unstable_LowPriority,Et=i.unstable_IdlePriority,wt=i.log,Pt=i.unstable_setDisableYieldValue,ft=null,ht=null;function Ot(e){if(typeof wt=="function"&&Pt(e),ht&&typeof ht.setStrictMode=="function")try{ht.setStrictMode(ft,e)}catch{}}var Ft=Math.clz32?Math.clz32:ae,Lt=Math.log,Dt=Math.LN2;function ae(e){return e>>>=0,e===0?32:31-(Lt(e)/Dt|0)|0}var se=256,me=262144,X=4194304;function At(e){var a=e&42;if(a!==0)return a;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function mt(e,a,r){var l=e.pendingLanes;if(l===0)return 0;var f=0,m=e.suspendedLanes,M=e.pingedLanes;e=e.warmLanes;var w=l&134217727;return w!==0?(l=w&~m,l!==0?f=At(l):(M&=w,M!==0?f=At(M):r||(r=w&~e,r!==0&&(f=At(r))))):(w=l&~m,w!==0?f=At(w):M!==0?f=At(M):r||(r=l&~e,r!==0&&(f=At(r)))),f===0?0:a!==0&&a!==f&&(a&m)===0&&(m=f&-f,r=a&-a,m>=r||m===32&&(r&4194048)!==0)?a:f}function zt(e,a){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&a)===0}function Ut(e,a){switch(e){case 1:case 2:case 4:case 8:case 64:return a+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return a+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function bt(){var e=X;return X<<=1,(X&62914560)===0&&(X=4194304),e}function Yt(e){for(var a=[],r=0;31>r;r++)a.push(e);return a}function ne(e,a){e.pendingLanes|=a,a!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function sn(e,a,r,l,f,m){var M=e.pendingLanes;e.pendingLanes=r,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=r,e.entangledLanes&=r,e.errorRecoveryDisabledLanes&=r,e.shellSuspendCounter=0;var w=e.entanglements,k=e.expirationTimes,et=e.hiddenUpdates;for(r=M&~r;0<r;){var pt=31-Ft(r),vt=1<<pt;w[pt]=0,k[pt]=-1;var st=et[pt];if(st!==null)for(et[pt]=null,pt=0;pt<st.length;pt++){var ut=st[pt];ut!==null&&(ut.lane&=-536870913)}r&=~vt}l!==0&&we(e,l,0),m!==0&&f===0&&e.tag!==0&&(e.suspendedLanes|=m&~(M&~a))}function we(e,a,r){e.pendingLanes|=a,e.suspendedLanes&=~a;var l=31-Ft(a);e.entangledLanes|=a,e.entanglements[l]=e.entanglements[l]|1073741824|r&261930}function xi(e,a){var r=e.entangledLanes|=a;for(e=e.entanglements;r;){var l=31-Ft(r),f=1<<l;f&a|e[l]&a&&(e[l]|=a),r&=~f}}function si(e,a){var r=a&-a;return r=(r&42)!==0?1:Us(r),(r&(e.suspendedLanes|a))!==0?0:r}function Us(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function Do(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function No(){var e=G.p;return e!==0?e:(e=window.event,e===void 0?32:ux(e.type))}function Lo(e,a){var r=G.p;try{return G.p=e,a()}finally{G.p=r}}var zn=Math.random().toString(36).slice(2),un="__reactFiber$"+zn,Nn="__reactProps$"+zn,pa="__reactContainer$"+zn,Xa="__reactEvents$"+zn,tc="__reactListeners$"+zn,xr="__reactHandles$"+zn,Uo="__reactResources$"+zn,Wa="__reactMarker$"+zn;function Po(e){delete e[un],delete e[Nn],delete e[Xa],delete e[tc],delete e[xr]}function qa(e){var a=e[un];if(a)return a;for(var r=e.parentNode;r;){if(a=r[pa]||r[un]){if(r=a.alternate,a.child!==null||r!==null&&r.child!==null)for(e=Yv(e);e!==null;){if(r=e[un])return r;e=Yv(e)}return a}e=r,r=e.parentNode}return null}function Ya(e){if(e=e[un]||e[pa]){var a=e.tag;if(a===5||a===6||a===13||a===31||a===26||a===27||a===3)return e}return null}function Ps(e){var a=e.tag;if(a===5||a===26||a===27||a===6)return e.stateNode;throw Error(s(33))}function Ka(e){var a=e[Uo];return a||(a=e[Uo]={hoistableStyles:new Map,hoistableScripts:new Map}),a}function pn(e){e[Wa]=!0}var ec=new Set,C={};function K(e,a){at(e,a),at(e+"Capture",a)}function at(e,a){for(C[e]=a,e=0;e<a.length;e++)ec.add(a[e])}var nt=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),it={},It={};function kt(e){return Dn.call(It,e)?!0:Dn.call(it,e)?!1:nt.test(e)?It[e]=!0:(it[e]=!0,!1)}function Bt(e,a,r){if(kt(a))if(r===null)e.removeAttribute(a);else{switch(typeof r){case"undefined":case"function":case"symbol":e.removeAttribute(a);return;case"boolean":var l=a.toLowerCase().slice(0,5);if(l!=="data-"&&l!=="aria-"){e.removeAttribute(a);return}}e.setAttribute(a,""+r)}}function Xt(e,a,r){if(r===null)e.removeAttribute(a);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(a);return}e.setAttribute(a,""+r)}}function jt(e,a,r,l){if(l===null)e.removeAttribute(r);else{switch(typeof l){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(r);return}e.setAttributeNS(a,r,""+l)}}function Qt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function le(e){var a=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(a==="checkbox"||a==="radio")}function Zt(e,a,r){var l=Object.getOwnPropertyDescriptor(e.constructor.prototype,a);if(!e.hasOwnProperty(a)&&typeof l<"u"&&typeof l.get=="function"&&typeof l.set=="function"){var f=l.get,m=l.set;return Object.defineProperty(e,a,{configurable:!0,get:function(){return f.call(this)},set:function(M){r=""+M,m.call(this,M)}}),Object.defineProperty(e,a,{enumerable:l.enumerable}),{getValue:function(){return r},setValue:function(M){r=""+M},stopTracking:function(){e._valueTracker=null,delete e[a]}}}}function Ae(e){if(!e._valueTracker){var a=le(e)?"checked":"value";e._valueTracker=Zt(e,a,""+e[a])}}function tn(e){if(!e)return!1;var a=e._valueTracker;if(!a)return!0;var r=a.getValue(),l="";return e&&(l=le(e)?e.checked?"true":"false":e.value),e=l,e!==r?(a.setValue(e),!0):!1}function We(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Pe=/[\n"\\]/g;function Oe(e){return e.replace(Pe,function(a){return"\\"+a.charCodeAt(0).toString(16)+" "})}function Gt(e,a,r,l,f,m,M,w){e.name="",M!=null&&typeof M!="function"&&typeof M!="symbol"&&typeof M!="boolean"?e.type=M:e.removeAttribute("type"),a!=null?M==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+Qt(a)):e.value!==""+Qt(a)&&(e.value=""+Qt(a)):M!=="submit"&&M!=="reset"||e.removeAttribute("value"),a!=null?ge(e,M,Qt(a)):r!=null?ge(e,M,Qt(r)):l!=null&&e.removeAttribute("value"),f==null&&m!=null&&(e.defaultChecked=!!m),f!=null&&(e.checked=f&&typeof f!="function"&&typeof f!="symbol"),w!=null&&typeof w!="function"&&typeof w!="symbol"&&typeof w!="boolean"?e.name=""+Qt(w):e.removeAttribute("name")}function Vn(e,a,r,l,f,m,M,w){if(m!=null&&typeof m!="function"&&typeof m!="symbol"&&typeof m!="boolean"&&(e.type=m),a!=null||r!=null){if(!(m!=="submit"&&m!=="reset"||a!=null)){Ae(e);return}r=r!=null?""+Qt(r):"",a=a!=null?""+Qt(a):r,w||a===e.value||(e.value=a),e.defaultValue=a}l=l??f,l=typeof l!="function"&&typeof l!="symbol"&&!!l,e.checked=w?e.checked:!!l,e.defaultChecked=!!l,M!=null&&typeof M!="function"&&typeof M!="symbol"&&typeof M!="boolean"&&(e.name=M),Ae(e)}function ge(e,a,r){a==="number"&&We(e.ownerDocument)===e||e.defaultValue===""+r||(e.defaultValue=""+r)}function bn(e,a,r,l){if(e=e.options,a){a={};for(var f=0;f<r.length;f++)a["$"+r[f]]=!0;for(r=0;r<e.length;r++)f=a.hasOwnProperty("$"+e[r].value),e[r].selected!==f&&(e[r].selected=f),f&&l&&(e[r].defaultSelected=!0)}else{for(r=""+Qt(r),a=null,f=0;f<e.length;f++){if(e[f].value===r){e[f].selected=!0,l&&(e[f].defaultSelected=!0);return}a!==null||e[f].disabled||(a=e[f])}a!==null&&(a.selected=!0)}}function ri(e,a,r){if(a!=null&&(a=""+Qt(a),a!==e.value&&(e.value=a),r==null)){e.defaultValue!==a&&(e.defaultValue=a);return}e.defaultValue=r!=null?""+Qt(r):""}function Pi(e,a,r,l){if(a==null){if(l!=null){if(r!=null)throw Error(s(92));if(q(l)){if(1<l.length)throw Error(s(93));l=l[0]}r=l}r==null&&(r=""),a=r}r=Qt(a),e.defaultValue=r,l=e.textContent,l===r&&l!==""&&l!==null&&(e.value=l),Ae(e)}function oi(e,a){if(a){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=a;return}}e.textContent=a}var Fe=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function en(e,a,r){var l=a.indexOf("--")===0;r==null||typeof r=="boolean"||r===""?l?e.setProperty(a,""):a==="float"?e.cssFloat="":e[a]="":l?e.setProperty(a,r):typeof r!="number"||r===0||Fe.has(a)?a==="float"?e.cssFloat=r:e[a]=(""+r).trim():e[a]=r+"px"}function Oi(e,a,r){if(a!=null&&typeof a!="object")throw Error(s(62));if(e=e.style,r!=null){for(var l in r)!r.hasOwnProperty(l)||a!=null&&a.hasOwnProperty(l)||(l.indexOf("--")===0?e.setProperty(l,""):l==="float"?e.cssFloat="":e[l]="");for(var f in a)l=a[f],a.hasOwnProperty(f)&&r[f]!==l&&en(e,f,l)}else for(var m in a)a.hasOwnProperty(m)&&en(e,m,a[m])}function Ne(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Ki=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),Za=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function Os(e){return Za.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function ma(){}var Rf=null;function Cf(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var yr=null,Sr=null;function zg(e){var a=Ya(e);if(a&&(e=a.stateNode)){var r=e[Nn]||null;t:switch(e=a.stateNode,a.type){case"input":if(Gt(e,r.value,r.defaultValue,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name),a=r.name,r.type==="radio"&&a!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll('input[name="'+Oe(""+a)+'"][type="radio"]'),a=0;a<r.length;a++){var l=r[a];if(l!==e&&l.form===e.form){var f=l[Nn]||null;if(!f)throw Error(s(90));Gt(l,f.value,f.defaultValue,f.defaultValue,f.checked,f.defaultChecked,f.type,f.name)}}for(a=0;a<r.length;a++)l=r[a],l.form===e.form&&tn(l)}break t;case"textarea":ri(e,r.value,r.defaultValue);break t;case"select":a=r.value,a!=null&&bn(e,!!r.multiple,a,!1)}}}var wf=!1;function Vg(e,a,r){if(wf)return e(a,r);wf=!0;try{var l=e(a);return l}finally{if(wf=!1,(yr!==null||Sr!==null)&&(Gc(),yr&&(a=yr,e=Sr,Sr=yr=null,zg(a),e)))for(a=0;a<e.length;a++)zg(e[a])}}function Oo(e,a){var r=e.stateNode;if(r===null)return null;var l=r[Nn]||null;if(l===null)return null;r=l[a];t:switch(a){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break t;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(s(231,a,typeof r));return r}var ga=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Df=!1;if(ga)try{var Fo={};Object.defineProperty(Fo,"passive",{get:function(){Df=!0}}),window.addEventListener("test",Fo,Fo),window.removeEventListener("test",Fo,Fo)}catch{Df=!1}var Qa=null,Nf=null,nc=null;function Hg(){if(nc)return nc;var e,a=Nf,r=a.length,l,f="value"in Qa?Qa.value:Qa.textContent,m=f.length;for(e=0;e<r&&a[e]===f[e];e++);var M=r-e;for(l=1;l<=M&&a[r-l]===f[m-l];l++);return nc=f.slice(e,1<l?1-l:void 0)}function ic(e){var a=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&a===13&&(e=13)):e=a,e===10&&(e=13),32<=e||e===13?e:0}function ac(){return!0}function Gg(){return!1}function Zn(e){function a(r,l,f,m,M){this._reactName=r,this._targetInst=f,this.type=l,this.nativeEvent=m,this.target=M,this.currentTarget=null;for(var w in e)e.hasOwnProperty(w)&&(r=e[w],this[w]=r?r(m):m[w]);return this.isDefaultPrevented=(m.defaultPrevented!=null?m.defaultPrevented:m.returnValue===!1)?ac:Gg,this.isPropagationStopped=Gg,this}return _(a.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=ac)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=ac)},persist:function(){},isPersistent:ac}),a}var Fs={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},sc=Zn(Fs),Bo=_({},Fs,{view:0,detail:0}),RE=Zn(Bo),Lf,Uf,Io,rc=_({},Bo,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Of,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Io&&(Io&&e.type==="mousemove"?(Lf=e.screenX-Io.screenX,Uf=e.screenY-Io.screenY):Uf=Lf=0,Io=e),Lf)},movementY:function(e){return"movementY"in e?e.movementY:Uf}}),kg=Zn(rc),CE=_({},rc,{dataTransfer:0}),wE=Zn(CE),DE=_({},Bo,{relatedTarget:0}),Pf=Zn(DE),NE=_({},Fs,{animationName:0,elapsedTime:0,pseudoElement:0}),LE=Zn(NE),UE=_({},Fs,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),PE=Zn(UE),OE=_({},Fs,{data:0}),jg=Zn(OE),FE={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},BE={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},IE={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function zE(e){var a=this.nativeEvent;return a.getModifierState?a.getModifierState(e):(e=IE[e])?!!a[e]:!1}function Of(){return zE}var VE=_({},Bo,{key:function(e){if(e.key){var a=FE[e.key]||e.key;if(a!=="Unidentified")return a}return e.type==="keypress"?(e=ic(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?BE[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Of,charCode:function(e){return e.type==="keypress"?ic(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?ic(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),HE=Zn(VE),GE=_({},rc,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Xg=Zn(GE),kE=_({},Bo,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Of}),jE=Zn(kE),XE=_({},Fs,{propertyName:0,elapsedTime:0,pseudoElement:0}),WE=Zn(XE),qE=_({},rc,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),YE=Zn(qE),KE=_({},Fs,{newState:0,oldState:0}),ZE=Zn(KE),QE=[9,13,27,32],Ff=ga&&"CompositionEvent"in window,zo=null;ga&&"documentMode"in document&&(zo=document.documentMode);var JE=ga&&"TextEvent"in window&&!zo,Wg=ga&&(!Ff||zo&&8<zo&&11>=zo),qg=" ",Yg=!1;function Kg(e,a){switch(e){case"keyup":return QE.indexOf(a.keyCode)!==-1;case"keydown":return a.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Zg(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Mr=!1;function $E(e,a){switch(e){case"compositionend":return Zg(a);case"keypress":return a.which!==32?null:(Yg=!0,qg);case"textInput":return e=a.data,e===qg&&Yg?null:e;default:return null}}function tT(e,a){if(Mr)return e==="compositionend"||!Ff&&Kg(e,a)?(e=Hg(),nc=Nf=Qa=null,Mr=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(a.ctrlKey||a.altKey||a.metaKey)||a.ctrlKey&&a.altKey){if(a.char&&1<a.char.length)return a.char;if(a.which)return String.fromCharCode(a.which)}return null;case"compositionend":return Wg&&a.locale!=="ko"?null:a.data;default:return null}}var eT={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Qg(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a==="input"?!!eT[e.type]:a==="textarea"}function Jg(e,a,r,l){yr?Sr?Sr.push(l):Sr=[l]:yr=l,a=Kc(a,"onChange"),0<a.length&&(r=new sc("onChange","change",null,r,l),e.push({event:r,listeners:a}))}var Vo=null,Ho=null;function nT(e){Pv(e,0)}function oc(e){var a=Ps(e);if(tn(a))return e}function $g(e,a){if(e==="change")return a}var t0=!1;if(ga){var Bf;if(ga){var If="oninput"in document;if(!If){var e0=document.createElement("div");e0.setAttribute("oninput","return;"),If=typeof e0.oninput=="function"}Bf=If}else Bf=!1;t0=Bf&&(!document.documentMode||9<document.documentMode)}function n0(){Vo&&(Vo.detachEvent("onpropertychange",i0),Ho=Vo=null)}function i0(e){if(e.propertyName==="value"&&oc(Ho)){var a=[];Jg(a,Ho,e,Cf(e)),Vg(nT,a)}}function iT(e,a,r){e==="focusin"?(n0(),Vo=a,Ho=r,Vo.attachEvent("onpropertychange",i0)):e==="focusout"&&n0()}function aT(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return oc(Ho)}function sT(e,a){if(e==="click")return oc(a)}function rT(e,a){if(e==="input"||e==="change")return oc(a)}function oT(e,a){return e===a&&(e!==0||1/e===1/a)||e!==e&&a!==a}var li=typeof Object.is=="function"?Object.is:oT;function Go(e,a){if(li(e,a))return!0;if(typeof e!="object"||e===null||typeof a!="object"||a===null)return!1;var r=Object.keys(e),l=Object.keys(a);if(r.length!==l.length)return!1;for(l=0;l<r.length;l++){var f=r[l];if(!Dn.call(a,f)||!li(e[f],a[f]))return!1}return!0}function a0(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function s0(e,a){var r=a0(e);e=0;for(var l;r;){if(r.nodeType===3){if(l=e+r.textContent.length,e<=a&&l>=a)return{node:r,offset:a-e};e=l}t:{for(;r;){if(r.nextSibling){r=r.nextSibling;break t}r=r.parentNode}r=void 0}r=a0(r)}}function r0(e,a){return e&&a?e===a?!0:e&&e.nodeType===3?!1:a&&a.nodeType===3?r0(e,a.parentNode):"contains"in e?e.contains(a):e.compareDocumentPosition?!!(e.compareDocumentPosition(a)&16):!1:!1}function o0(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var a=We(e.document);a instanceof e.HTMLIFrameElement;){try{var r=typeof a.contentWindow.location.href=="string"}catch{r=!1}if(r)e=a.contentWindow;else break;a=We(e.document)}return a}function zf(e){var a=e&&e.nodeName&&e.nodeName.toLowerCase();return a&&(a==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||a==="textarea"||e.contentEditable==="true")}var lT=ga&&"documentMode"in document&&11>=document.documentMode,br=null,Vf=null,ko=null,Hf=!1;function l0(e,a,r){var l=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;Hf||br==null||br!==We(l)||(l=br,"selectionStart"in l&&zf(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),ko&&Go(ko,l)||(ko=l,l=Kc(Vf,"onSelect"),0<l.length&&(a=new sc("onSelect","select",null,a,r),e.push({event:a,listeners:l}),a.target=br)))}function Bs(e,a){var r={};return r[e.toLowerCase()]=a.toLowerCase(),r["Webkit"+e]="webkit"+a,r["Moz"+e]="moz"+a,r}var Er={animationend:Bs("Animation","AnimationEnd"),animationiteration:Bs("Animation","AnimationIteration"),animationstart:Bs("Animation","AnimationStart"),transitionrun:Bs("Transition","TransitionRun"),transitionstart:Bs("Transition","TransitionStart"),transitioncancel:Bs("Transition","TransitionCancel"),transitionend:Bs("Transition","TransitionEnd")},Gf={},c0={};ga&&(c0=document.createElement("div").style,"AnimationEvent"in window||(delete Er.animationend.animation,delete Er.animationiteration.animation,delete Er.animationstart.animation),"TransitionEvent"in window||delete Er.transitionend.transition);function Is(e){if(Gf[e])return Gf[e];if(!Er[e])return e;var a=Er[e],r;for(r in a)if(a.hasOwnProperty(r)&&r in c0)return Gf[e]=a[r];return e}var u0=Is("animationend"),f0=Is("animationiteration"),d0=Is("animationstart"),cT=Is("transitionrun"),uT=Is("transitionstart"),fT=Is("transitioncancel"),h0=Is("transitionend"),p0=new Map,kf="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");kf.push("scrollEnd");function Fi(e,a){p0.set(e,a),K(a,[e])}var lc=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var a=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(a))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},yi=[],Tr=0,jf=0;function cc(){for(var e=Tr,a=jf=Tr=0;a<e;){var r=yi[a];yi[a++]=null;var l=yi[a];yi[a++]=null;var f=yi[a];yi[a++]=null;var m=yi[a];if(yi[a++]=null,l!==null&&f!==null){var M=l.pending;M===null?f.next=f:(f.next=M.next,M.next=f),l.pending=f}m!==0&&m0(r,f,m)}}function uc(e,a,r,l){yi[Tr++]=e,yi[Tr++]=a,yi[Tr++]=r,yi[Tr++]=l,jf|=l,e.lanes|=l,e=e.alternate,e!==null&&(e.lanes|=l)}function Xf(e,a,r,l){return uc(e,a,r,l),fc(e)}function zs(e,a){return uc(e,null,null,a),fc(e)}function m0(e,a,r){e.lanes|=r;var l=e.alternate;l!==null&&(l.lanes|=r);for(var f=!1,m=e.return;m!==null;)m.childLanes|=r,l=m.alternate,l!==null&&(l.childLanes|=r),m.tag===22&&(e=m.stateNode,e===null||e._visibility&1||(f=!0)),e=m,m=m.return;return e.tag===3?(m=e.stateNode,f&&a!==null&&(f=31-Ft(r),e=m.hiddenUpdates,l=e[f],l===null?e[f]=[a]:l.push(a),a.lane=r|536870912),m):null}function fc(e){if(50<fl)throw fl=0,th=null,Error(s(185));for(var a=e.return;a!==null;)e=a,a=e.return;return e.tag===3?e.stateNode:null}var Ar={};function dT(e,a,r,l){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=a,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ci(e,a,r,l){return new dT(e,a,r,l)}function Wf(e){return e=e.prototype,!(!e||!e.isReactComponent)}function _a(e,a){var r=e.alternate;return r===null?(r=ci(e.tag,a,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=a,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&65011712,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,a=e.dependencies,r.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r.refCleanup=e.refCleanup,r}function g0(e,a){e.flags&=65011714;var r=e.alternate;return r===null?(e.childLanes=0,e.lanes=a,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=r.childLanes,e.lanes=r.lanes,e.child=r.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=r.memoizedProps,e.memoizedState=r.memoizedState,e.updateQueue=r.updateQueue,e.type=r.type,a=r.dependencies,e.dependencies=a===null?null:{lanes:a.lanes,firstContext:a.firstContext}),e}function dc(e,a,r,l,f,m){var M=0;if(l=e,typeof e=="function")Wf(e)&&(M=1);else if(typeof e=="string")M=_1(e,r,Rt.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case U:return e=ci(31,r,a,f),e.elementType=U,e.lanes=m,e;case R:return Vs(r.children,f,m,a);case S:M=8,f|=24;break;case x:return e=ci(12,r,a,f|2),e.elementType=x,e.lanes=m,e;case H:return e=ci(13,r,a,f),e.elementType=H,e.lanes=m,e;case B:return e=ci(19,r,a,f),e.elementType=B,e.lanes=m,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case N:M=10;break t;case A:M=9;break t;case L:M=11;break t;case O:M=14;break t;case E:M=16,l=null;break t}M=29,r=Error(s(130,e===null?"null":typeof e,"")),l=null}return a=ci(M,r,a,f),a.elementType=e,a.type=l,a.lanes=m,a}function Vs(e,a,r,l){return e=ci(7,e,l,a),e.lanes=r,e}function qf(e,a,r){return e=ci(6,e,null,a),e.lanes=r,e}function _0(e){var a=ci(18,null,null,0);return a.stateNode=e,a}function Yf(e,a,r){return a=ci(4,e.children!==null?e.children:[],e.key,a),a.lanes=r,a.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},a}var v0=new WeakMap;function Si(e,a){if(typeof e=="object"&&e!==null){var r=v0.get(e);return r!==void 0?r:(a={value:e,source:a,stack:Ze(a)},v0.set(e,a),a)}return{value:e,source:a,stack:Ze(a)}}var Rr=[],Cr=0,hc=null,jo=0,Mi=[],bi=0,Ja=null,Zi=1,Qi="";function va(e,a){Rr[Cr++]=jo,Rr[Cr++]=hc,hc=e,jo=a}function x0(e,a,r){Mi[bi++]=Zi,Mi[bi++]=Qi,Mi[bi++]=Ja,Ja=e;var l=Zi;e=Qi;var f=32-Ft(l)-1;l&=~(1<<f),r+=1;var m=32-Ft(a)+f;if(30<m){var M=f-f%5;m=(l&(1<<M)-1).toString(32),l>>=M,f-=M,Zi=1<<32-Ft(a)+f|r<<f|l,Qi=m+e}else Zi=1<<m|r<<f|l,Qi=e}function Kf(e){e.return!==null&&(va(e,1),x0(e,1,0))}function Zf(e){for(;e===hc;)hc=Rr[--Cr],Rr[Cr]=null,jo=Rr[--Cr],Rr[Cr]=null;for(;e===Ja;)Ja=Mi[--bi],Mi[bi]=null,Qi=Mi[--bi],Mi[bi]=null,Zi=Mi[--bi],Mi[bi]=null}function y0(e,a){Mi[bi++]=Zi,Mi[bi++]=Qi,Mi[bi++]=Ja,Zi=a.id,Qi=a.overflow,Ja=e}var Ln=null,Qe=null,Me=!1,$a=null,Ei=!1,Qf=Error(s(519));function ts(e){var a=Error(s(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw Xo(Si(a,e)),Qf}function S0(e){var a=e.stateNode,r=e.type,l=e.memoizedProps;switch(a[un]=e,a[Nn]=l,r){case"dialog":ve("cancel",a),ve("close",a);break;case"iframe":case"object":case"embed":ve("load",a);break;case"video":case"audio":for(r=0;r<hl.length;r++)ve(hl[r],a);break;case"source":ve("error",a);break;case"img":case"image":case"link":ve("error",a),ve("load",a);break;case"details":ve("toggle",a);break;case"input":ve("invalid",a),Vn(a,l.value,l.defaultValue,l.checked,l.defaultChecked,l.type,l.name,!0);break;case"select":ve("invalid",a);break;case"textarea":ve("invalid",a),Pi(a,l.value,l.defaultValue,l.children)}r=l.children,typeof r!="string"&&typeof r!="number"&&typeof r!="bigint"||a.textContent===""+r||l.suppressHydrationWarning===!0||Iv(a.textContent,r)?(l.popover!=null&&(ve("beforetoggle",a),ve("toggle",a)),l.onScroll!=null&&ve("scroll",a),l.onScrollEnd!=null&&ve("scrollend",a),l.onClick!=null&&(a.onclick=ma),a=!0):a=!1,a||ts(e,!0)}function M0(e){for(Ln=e.return;Ln;)switch(Ln.tag){case 5:case 31:case 13:Ei=!1;return;case 27:case 3:Ei=!0;return;default:Ln=Ln.return}}function wr(e){if(e!==Ln)return!1;if(!Me)return M0(e),Me=!0,!1;var a=e.tag,r;if((r=a!==3&&a!==27)&&((r=a===5)&&(r=e.type,r=!(r!=="form"&&r!=="button")||mh(e.type,e.memoizedProps)),r=!r),r&&Qe&&ts(e),M0(e),a===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Qe=qv(e)}else if(a===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Qe=qv(e)}else a===27?(a=Qe,ps(e.type)?(e=yh,yh=null,Qe=e):Qe=a):Qe=Ln?Ai(e.stateNode.nextSibling):null;return!0}function Hs(){Qe=Ln=null,Me=!1}function Jf(){var e=$a;return e!==null&&(ti===null?ti=e:ti.push.apply(ti,e),$a=null),e}function Xo(e){$a===null?$a=[e]:$a.push(e)}var $f=z(null),Gs=null,xa=null;function es(e,a,r){St($f,a._currentValue),a._currentValue=r}function ya(e){e._currentValue=$f.current,Q($f)}function td(e,a,r){for(;e!==null;){var l=e.alternate;if((e.childLanes&a)!==a?(e.childLanes|=a,l!==null&&(l.childLanes|=a)):l!==null&&(l.childLanes&a)!==a&&(l.childLanes|=a),e===r)break;e=e.return}}function ed(e,a,r,l){var f=e.child;for(f!==null&&(f.return=e);f!==null;){var m=f.dependencies;if(m!==null){var M=f.child;m=m.firstContext;t:for(;m!==null;){var w=m;m=f;for(var k=0;k<a.length;k++)if(w.context===a[k]){m.lanes|=r,w=m.alternate,w!==null&&(w.lanes|=r),td(m.return,r,e),l||(M=null);break t}m=w.next}}else if(f.tag===18){if(M=f.return,M===null)throw Error(s(341));M.lanes|=r,m=M.alternate,m!==null&&(m.lanes|=r),td(M,r,e),M=null}else M=f.child;if(M!==null)M.return=f;else for(M=f;M!==null;){if(M===e){M=null;break}if(f=M.sibling,f!==null){f.return=M.return,M=f;break}M=M.return}f=M}}function Dr(e,a,r,l){e=null;for(var f=a,m=!1;f!==null;){if(!m){if((f.flags&524288)!==0)m=!0;else if((f.flags&262144)!==0)break}if(f.tag===10){var M=f.alternate;if(M===null)throw Error(s(387));if(M=M.memoizedProps,M!==null){var w=f.type;li(f.pendingProps.value,M.value)||(e!==null?e.push(w):e=[w])}}else if(f===Mt.current){if(M=f.alternate,M===null)throw Error(s(387));M.memoizedState.memoizedState!==f.memoizedState.memoizedState&&(e!==null?e.push(vl):e=[vl])}f=f.return}e!==null&&ed(a,e,r,l),a.flags|=262144}function pc(e){for(e=e.firstContext;e!==null;){if(!li(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function ks(e){Gs=e,xa=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Un(e){return b0(Gs,e)}function mc(e,a){return Gs===null&&ks(e),b0(e,a)}function b0(e,a){var r=a._currentValue;if(a={context:a,memoizedValue:r,next:null},xa===null){if(e===null)throw Error(s(308));xa=a,e.dependencies={lanes:0,firstContext:a},e.flags|=524288}else xa=xa.next=a;return r}var hT=typeof AbortController<"u"?AbortController:function(){var e=[],a=this.signal={aborted:!1,addEventListener:function(r,l){e.push(l)}};this.abort=function(){a.aborted=!0,e.forEach(function(r){return r()})}},pT=i.unstable_scheduleCallback,mT=i.unstable_NormalPriority,mn={$$typeof:N,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function nd(){return{controller:new hT,data:new Map,refCount:0}}function Wo(e){e.refCount--,e.refCount===0&&pT(mT,function(){e.controller.abort()})}var qo=null,id=0,Nr=0,Lr=null;function gT(e,a){if(qo===null){var r=qo=[];id=0,Nr=rh(),Lr={status:"pending",value:void 0,then:function(l){r.push(l)}}}return id++,a.then(E0,E0),a}function E0(){if(--id===0&&qo!==null){Lr!==null&&(Lr.status="fulfilled");var e=qo;qo=null,Nr=0,Lr=null;for(var a=0;a<e.length;a++)(0,e[a])()}}function _T(e,a){var r=[],l={status:"pending",value:null,reason:null,then:function(f){r.push(f)}};return e.then(function(){l.status="fulfilled",l.value=a;for(var f=0;f<r.length;f++)(0,r[f])(a)},function(f){for(l.status="rejected",l.reason=f,f=0;f<r.length;f++)(0,r[f])(void 0)}),l}var T0=I.S;I.S=function(e,a){lv=Ct(),typeof a=="object"&&a!==null&&typeof a.then=="function"&&gT(e,a),T0!==null&&T0(e,a)};var js=z(null);function ad(){var e=js.current;return e!==null?e:qe.pooledCache}function gc(e,a){a===null?St(js,js.current):St(js,a.pool)}function A0(){var e=ad();return e===null?null:{parent:mn._currentValue,pool:e}}var Ur=Error(s(460)),sd=Error(s(474)),_c=Error(s(542)),vc={then:function(){}};function R0(e){return e=e.status,e==="fulfilled"||e==="rejected"}function C0(e,a,r){switch(r=e[r],r===void 0?e.push(a):r!==a&&(a.then(ma,ma),a=r),a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,D0(e),e;default:if(typeof a.status=="string")a.then(ma,ma);else{if(e=qe,e!==null&&100<e.shellSuspendCounter)throw Error(s(482));e=a,e.status="pending",e.then(function(l){if(a.status==="pending"){var f=a;f.status="fulfilled",f.value=l}},function(l){if(a.status==="pending"){var f=a;f.status="rejected",f.reason=l}})}switch(a.status){case"fulfilled":return a.value;case"rejected":throw e=a.reason,D0(e),e}throw Ws=a,Ur}}function Xs(e){try{var a=e._init;return a(e._payload)}catch(r){throw r!==null&&typeof r=="object"&&typeof r.then=="function"?(Ws=r,Ur):r}}var Ws=null;function w0(){if(Ws===null)throw Error(s(459));var e=Ws;return Ws=null,e}function D0(e){if(e===Ur||e===_c)throw Error(s(483))}var Pr=null,Yo=0;function xc(e){var a=Yo;return Yo+=1,Pr===null&&(Pr=[]),C0(Pr,e,a)}function Ko(e,a){a=a.props.ref,e.ref=a!==void 0?a:null}function yc(e,a){throw a.$$typeof===v?Error(s(525)):(e=Object.prototype.toString.call(a),Error(s(31,e==="[object Object]"?"object with keys {"+Object.keys(a).join(", ")+"}":e)))}function N0(e){function a(Z,W){if(e){var tt=Z.deletions;tt===null?(Z.deletions=[W],Z.flags|=16):tt.push(W)}}function r(Z,W){if(!e)return null;for(;W!==null;)a(Z,W),W=W.sibling;return null}function l(Z){for(var W=new Map;Z!==null;)Z.key!==null?W.set(Z.key,Z):W.set(Z.index,Z),Z=Z.sibling;return W}function f(Z,W){return Z=_a(Z,W),Z.index=0,Z.sibling=null,Z}function m(Z,W,tt){return Z.index=tt,e?(tt=Z.alternate,tt!==null?(tt=tt.index,tt<W?(Z.flags|=67108866,W):tt):(Z.flags|=67108866,W)):(Z.flags|=1048576,W)}function M(Z){return e&&Z.alternate===null&&(Z.flags|=67108866),Z}function w(Z,W,tt,gt){return W===null||W.tag!==6?(W=qf(tt,Z.mode,gt),W.return=Z,W):(W=f(W,tt),W.return=Z,W)}function k(Z,W,tt,gt){var Jt=tt.type;return Jt===R?pt(Z,W,tt.props.children,gt,tt.key):W!==null&&(W.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===E&&Xs(Jt)===W.type)?(W=f(W,tt.props),Ko(W,tt),W.return=Z,W):(W=dc(tt.type,tt.key,tt.props,null,Z.mode,gt),Ko(W,tt),W.return=Z,W)}function et(Z,W,tt,gt){return W===null||W.tag!==4||W.stateNode.containerInfo!==tt.containerInfo||W.stateNode.implementation!==tt.implementation?(W=Yf(tt,Z.mode,gt),W.return=Z,W):(W=f(W,tt.children||[]),W.return=Z,W)}function pt(Z,W,tt,gt,Jt){return W===null||W.tag!==7?(W=Vs(tt,Z.mode,gt,Jt),W.return=Z,W):(W=f(W,tt),W.return=Z,W)}function vt(Z,W,tt){if(typeof W=="string"&&W!==""||typeof W=="number"||typeof W=="bigint")return W=qf(""+W,Z.mode,tt),W.return=Z,W;if(typeof W=="object"&&W!==null){switch(W.$$typeof){case y:return tt=dc(W.type,W.key,W.props,null,Z.mode,tt),Ko(tt,W),tt.return=Z,tt;case b:return W=Yf(W,Z.mode,tt),W.return=Z,W;case E:return W=Xs(W),vt(Z,W,tt)}if(q(W)||j(W))return W=Vs(W,Z.mode,tt,null),W.return=Z,W;if(typeof W.then=="function")return vt(Z,xc(W),tt);if(W.$$typeof===N)return vt(Z,mc(Z,W),tt);yc(Z,W)}return null}function st(Z,W,tt,gt){var Jt=W!==null?W.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return Jt!==null?null:w(Z,W,""+tt,gt);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case y:return tt.key===Jt?k(Z,W,tt,gt):null;case b:return tt.key===Jt?et(Z,W,tt,gt):null;case E:return tt=Xs(tt),st(Z,W,tt,gt)}if(q(tt)||j(tt))return Jt!==null?null:pt(Z,W,tt,gt,null);if(typeof tt.then=="function")return st(Z,W,xc(tt),gt);if(tt.$$typeof===N)return st(Z,W,mc(Z,tt),gt);yc(Z,tt)}return null}function ut(Z,W,tt,gt,Jt){if(typeof gt=="string"&&gt!==""||typeof gt=="number"||typeof gt=="bigint")return Z=Z.get(tt)||null,w(W,Z,""+gt,Jt);if(typeof gt=="object"&&gt!==null){switch(gt.$$typeof){case y:return Z=Z.get(gt.key===null?tt:gt.key)||null,k(W,Z,gt,Jt);case b:return Z=Z.get(gt.key===null?tt:gt.key)||null,et(W,Z,gt,Jt);case E:return gt=Xs(gt),ut(Z,W,tt,gt,Jt)}if(q(gt)||j(gt))return Z=Z.get(tt)||null,pt(W,Z,gt,Jt,null);if(typeof gt.then=="function")return ut(Z,W,tt,xc(gt),Jt);if(gt.$$typeof===N)return ut(Z,W,tt,mc(W,gt),Jt);yc(W,gt)}return null}function Wt(Z,W,tt,gt){for(var Jt=null,Re=null,Kt=W,fe=W=0,Se=null;Kt!==null&&fe<tt.length;fe++){Kt.index>fe?(Se=Kt,Kt=null):Se=Kt.sibling;var Ce=st(Z,Kt,tt[fe],gt);if(Ce===null){Kt===null&&(Kt=Se);break}e&&Kt&&Ce.alternate===null&&a(Z,Kt),W=m(Ce,W,fe),Re===null?Jt=Ce:Re.sibling=Ce,Re=Ce,Kt=Se}if(fe===tt.length)return r(Z,Kt),Me&&va(Z,fe),Jt;if(Kt===null){for(;fe<tt.length;fe++)Kt=vt(Z,tt[fe],gt),Kt!==null&&(W=m(Kt,W,fe),Re===null?Jt=Kt:Re.sibling=Kt,Re=Kt);return Me&&va(Z,fe),Jt}for(Kt=l(Kt);fe<tt.length;fe++)Se=ut(Kt,Z,fe,tt[fe],gt),Se!==null&&(e&&Se.alternate!==null&&Kt.delete(Se.key===null?fe:Se.key),W=m(Se,W,fe),Re===null?Jt=Se:Re.sibling=Se,Re=Se);return e&&Kt.forEach(function(xs){return a(Z,xs)}),Me&&va(Z,fe),Jt}function te(Z,W,tt,gt){if(tt==null)throw Error(s(151));for(var Jt=null,Re=null,Kt=W,fe=W=0,Se=null,Ce=tt.next();Kt!==null&&!Ce.done;fe++,Ce=tt.next()){Kt.index>fe?(Se=Kt,Kt=null):Se=Kt.sibling;var xs=st(Z,Kt,Ce.value,gt);if(xs===null){Kt===null&&(Kt=Se);break}e&&Kt&&xs.alternate===null&&a(Z,Kt),W=m(xs,W,fe),Re===null?Jt=xs:Re.sibling=xs,Re=xs,Kt=Se}if(Ce.done)return r(Z,Kt),Me&&va(Z,fe),Jt;if(Kt===null){for(;!Ce.done;fe++,Ce=tt.next())Ce=vt(Z,Ce.value,gt),Ce!==null&&(W=m(Ce,W,fe),Re===null?Jt=Ce:Re.sibling=Ce,Re=Ce);return Me&&va(Z,fe),Jt}for(Kt=l(Kt);!Ce.done;fe++,Ce=tt.next())Ce=ut(Kt,Z,fe,Ce.value,gt),Ce!==null&&(e&&Ce.alternate!==null&&Kt.delete(Ce.key===null?fe:Ce.key),W=m(Ce,W,fe),Re===null?Jt=Ce:Re.sibling=Ce,Re=Ce);return e&&Kt.forEach(function(C1){return a(Z,C1)}),Me&&va(Z,fe),Jt}function ke(Z,W,tt,gt){if(typeof tt=="object"&&tt!==null&&tt.type===R&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case y:t:{for(var Jt=tt.key;W!==null;){if(W.key===Jt){if(Jt=tt.type,Jt===R){if(W.tag===7){r(Z,W.sibling),gt=f(W,tt.props.children),gt.return=Z,Z=gt;break t}}else if(W.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===E&&Xs(Jt)===W.type){r(Z,W.sibling),gt=f(W,tt.props),Ko(gt,tt),gt.return=Z,Z=gt;break t}r(Z,W);break}else a(Z,W);W=W.sibling}tt.type===R?(gt=Vs(tt.props.children,Z.mode,gt,tt.key),gt.return=Z,Z=gt):(gt=dc(tt.type,tt.key,tt.props,null,Z.mode,gt),Ko(gt,tt),gt.return=Z,Z=gt)}return M(Z);case b:t:{for(Jt=tt.key;W!==null;){if(W.key===Jt)if(W.tag===4&&W.stateNode.containerInfo===tt.containerInfo&&W.stateNode.implementation===tt.implementation){r(Z,W.sibling),gt=f(W,tt.children||[]),gt.return=Z,Z=gt;break t}else{r(Z,W);break}else a(Z,W);W=W.sibling}gt=Yf(tt,Z.mode,gt),gt.return=Z,Z=gt}return M(Z);case E:return tt=Xs(tt),ke(Z,W,tt,gt)}if(q(tt))return Wt(Z,W,tt,gt);if(j(tt)){if(Jt=j(tt),typeof Jt!="function")throw Error(s(150));return tt=Jt.call(tt),te(Z,W,tt,gt)}if(typeof tt.then=="function")return ke(Z,W,xc(tt),gt);if(tt.$$typeof===N)return ke(Z,W,mc(Z,tt),gt);yc(Z,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,W!==null&&W.tag===6?(r(Z,W.sibling),gt=f(W,tt),gt.return=Z,Z=gt):(r(Z,W),gt=qf(tt,Z.mode,gt),gt.return=Z,Z=gt),M(Z)):r(Z,W)}return function(Z,W,tt,gt){try{Yo=0;var Jt=ke(Z,W,tt,gt);return Pr=null,Jt}catch(Kt){if(Kt===Ur||Kt===_c)throw Kt;var Re=ci(29,Kt,null,Z.mode);return Re.lanes=gt,Re.return=Z,Re}}}var qs=N0(!0),L0=N0(!1),ns=!1;function rd(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function od(e,a){e=e.updateQueue,a.updateQueue===e&&(a.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function is(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function as(e,a,r){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(De&2)!==0){var f=l.pending;return f===null?a.next=a:(a.next=f.next,f.next=a),l.pending=a,a=fc(e),m0(e,null,r),a}return uc(e,l,a,r),fc(e)}function Zo(e,a,r){if(a=a.updateQueue,a!==null&&(a=a.shared,(r&4194048)!==0)){var l=a.lanes;l&=e.pendingLanes,r|=l,a.lanes=r,xi(e,r)}}function ld(e,a){var r=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,r===l)){var f=null,m=null;if(r=r.firstBaseUpdate,r!==null){do{var M={lane:r.lane,tag:r.tag,payload:r.payload,callback:null,next:null};m===null?f=m=M:m=m.next=M,r=r.next}while(r!==null);m===null?f=m=a:m=m.next=a}else f=m=a;r={baseState:l.baseState,firstBaseUpdate:f,lastBaseUpdate:m,shared:l.shared,callbacks:l.callbacks},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=a:e.next=a,r.lastBaseUpdate=a}var cd=!1;function Qo(){if(cd){var e=Lr;if(e!==null)throw e}}function Jo(e,a,r,l){cd=!1;var f=e.updateQueue;ns=!1;var m=f.firstBaseUpdate,M=f.lastBaseUpdate,w=f.shared.pending;if(w!==null){f.shared.pending=null;var k=w,et=k.next;k.next=null,M===null?m=et:M.next=et,M=k;var pt=e.alternate;pt!==null&&(pt=pt.updateQueue,w=pt.lastBaseUpdate,w!==M&&(w===null?pt.firstBaseUpdate=et:w.next=et,pt.lastBaseUpdate=k))}if(m!==null){var vt=f.baseState;M=0,pt=et=k=null,w=m;do{var st=w.lane&-536870913,ut=st!==w.lane;if(ut?(ye&st)===st:(l&st)===st){st!==0&&st===Nr&&(cd=!0),pt!==null&&(pt=pt.next={lane:0,tag:w.tag,payload:w.payload,callback:null,next:null});t:{var Wt=e,te=w;st=a;var ke=r;switch(te.tag){case 1:if(Wt=te.payload,typeof Wt=="function"){vt=Wt.call(ke,vt,st);break t}vt=Wt;break t;case 3:Wt.flags=Wt.flags&-65537|128;case 0:if(Wt=te.payload,st=typeof Wt=="function"?Wt.call(ke,vt,st):Wt,st==null)break t;vt=_({},vt,st);break t;case 2:ns=!0}}st=w.callback,st!==null&&(e.flags|=64,ut&&(e.flags|=8192),ut=f.callbacks,ut===null?f.callbacks=[st]:ut.push(st))}else ut={lane:st,tag:w.tag,payload:w.payload,callback:w.callback,next:null},pt===null?(et=pt=ut,k=vt):pt=pt.next=ut,M|=st;if(w=w.next,w===null){if(w=f.shared.pending,w===null)break;ut=w,w=ut.next,ut.next=null,f.lastBaseUpdate=ut,f.shared.pending=null}}while(!0);pt===null&&(k=vt),f.baseState=k,f.firstBaseUpdate=et,f.lastBaseUpdate=pt,m===null&&(f.shared.lanes=0),cs|=M,e.lanes=M,e.memoizedState=vt}}function U0(e,a){if(typeof e!="function")throw Error(s(191,e));e.call(a)}function P0(e,a){var r=e.callbacks;if(r!==null)for(e.callbacks=null,e=0;e<r.length;e++)U0(r[e],a)}var Or=z(null),Sc=z(0);function O0(e,a){e=wa,St(Sc,e),St(Or,a),wa=e|a.baseLanes}function ud(){St(Sc,wa),St(Or,Or.current)}function fd(){wa=Sc.current,Q(Or),Q(Sc)}var ui=z(null),Ti=null;function ss(e){var a=e.alternate;St(fn,fn.current&1),St(ui,e),Ti===null&&(a===null||Or.current!==null||a.memoizedState!==null)&&(Ti=e)}function dd(e){St(fn,fn.current),St(ui,e),Ti===null&&(Ti=e)}function F0(e){e.tag===22?(St(fn,fn.current),St(ui,e),Ti===null&&(Ti=e)):rs()}function rs(){St(fn,fn.current),St(ui,ui.current)}function fi(e){Q(ui),Ti===e&&(Ti=null),Q(fn)}var fn=z(0);function Mc(e){for(var a=e;a!==null;){if(a.tag===13){var r=a.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||vh(r)||xh(r)))return a}else if(a.tag===19&&(a.memoizedProps.revealOrder==="forwards"||a.memoizedProps.revealOrder==="backwards"||a.memoizedProps.revealOrder==="unstable_legacy-backwards"||a.memoizedProps.revealOrder==="together")){if((a.flags&128)!==0)return a}else if(a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return null;a=a.return}a.sibling.return=a.return,a=a.sibling}return null}var Sa=0,ce=null,He=null,gn=null,bc=!1,Fr=!1,Ys=!1,Ec=0,$o=0,Br=null,vT=0;function rn(){throw Error(s(321))}function hd(e,a){if(a===null)return!1;for(var r=0;r<a.length&&r<e.length;r++)if(!li(e[r],a[r]))return!1;return!0}function pd(e,a,r,l,f,m){return Sa=m,ce=a,a.memoizedState=null,a.updateQueue=null,a.lanes=0,I.H=e===null||e.memoizedState===null?x_:wd,Ys=!1,m=r(l,f),Ys=!1,Fr&&(m=I0(a,r,l,f)),B0(e),m}function B0(e){I.H=nl;var a=He!==null&&He.next!==null;if(Sa=0,gn=He=ce=null,bc=!1,$o=0,Br=null,a)throw Error(s(300));e===null||_n||(e=e.dependencies,e!==null&&pc(e)&&(_n=!0))}function I0(e,a,r,l){ce=e;var f=0;do{if(Fr&&(Br=null),$o=0,Fr=!1,25<=f)throw Error(s(301));if(f+=1,gn=He=null,e.updateQueue!=null){var m=e.updateQueue;m.lastEffect=null,m.events=null,m.stores=null,m.memoCache!=null&&(m.memoCache.index=0)}I.H=y_,m=a(r,l)}while(Fr);return m}function xT(){var e=I.H,a=e.useState()[0];return a=typeof a.then=="function"?tl(a):a,e=e.useState()[0],(He!==null?He.memoizedState:null)!==e&&(ce.flags|=1024),a}function md(){var e=Ec!==0;return Ec=0,e}function gd(e,a,r){a.updateQueue=e.updateQueue,a.flags&=-2053,e.lanes&=~r}function _d(e){if(bc){for(e=e.memoizedState;e!==null;){var a=e.queue;a!==null&&(a.pending=null),e=e.next}bc=!1}Sa=0,gn=He=ce=null,Fr=!1,$o=Ec=0,Br=null}function Xn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return gn===null?ce.memoizedState=gn=e:gn=gn.next=e,gn}function dn(){if(He===null){var e=ce.alternate;e=e!==null?e.memoizedState:null}else e=He.next;var a=gn===null?ce.memoizedState:gn.next;if(a!==null)gn=a,He=e;else{if(e===null)throw ce.alternate===null?Error(s(467)):Error(s(310));He=e,e={memoizedState:He.memoizedState,baseState:He.baseState,baseQueue:He.baseQueue,queue:He.queue,next:null},gn===null?ce.memoizedState=gn=e:gn=gn.next=e}return gn}function Tc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function tl(e){var a=$o;return $o+=1,Br===null&&(Br=[]),e=C0(Br,e,a),a=ce,(gn===null?a.memoizedState:gn.next)===null&&(a=a.alternate,I.H=a===null||a.memoizedState===null?x_:wd),e}function Ac(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return tl(e);if(e.$$typeof===N)return Un(e)}throw Error(s(438,String(e)))}function vd(e){var a=null,r=ce.updateQueue;if(r!==null&&(a=r.memoCache),a==null){var l=ce.alternate;l!==null&&(l=l.updateQueue,l!==null&&(l=l.memoCache,l!=null&&(a={data:l.data.map(function(f){return f.slice()}),index:0})))}if(a==null&&(a={data:[],index:0}),r===null&&(r=Tc(),ce.updateQueue=r),r.memoCache=a,r=a.data[a.index],r===void 0)for(r=a.data[a.index]=Array(e),l=0;l<e;l++)r[l]=V;return a.index++,r}function Ma(e,a){return typeof a=="function"?a(e):a}function Rc(e){var a=dn();return xd(a,He,e)}function xd(e,a,r){var l=e.queue;if(l===null)throw Error(s(311));l.lastRenderedReducer=r;var f=e.baseQueue,m=l.pending;if(m!==null){if(f!==null){var M=f.next;f.next=m.next,m.next=M}a.baseQueue=f=m,l.pending=null}if(m=e.baseState,f===null)e.memoizedState=m;else{a=f.next;var w=M=null,k=null,et=a,pt=!1;do{var vt=et.lane&-536870913;if(vt!==et.lane?(ye&vt)===vt:(Sa&vt)===vt){var st=et.revertLane;if(st===0)k!==null&&(k=k.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),vt===Nr&&(pt=!0);else if((Sa&st)===st){et=et.next,st===Nr&&(pt=!0);continue}else vt={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},k===null?(w=k=vt,M=m):k=k.next=vt,ce.lanes|=st,cs|=st;vt=et.action,Ys&&r(m,vt),m=et.hasEagerState?et.eagerState:r(m,vt)}else st={lane:vt,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},k===null?(w=k=st,M=m):k=k.next=st,ce.lanes|=vt,cs|=vt;et=et.next}while(et!==null&&et!==a);if(k===null?M=m:k.next=w,!li(m,e.memoizedState)&&(_n=!0,pt&&(r=Lr,r!==null)))throw r;e.memoizedState=m,e.baseState=M,e.baseQueue=k,l.lastRenderedState=m}return f===null&&(l.lanes=0),[e.memoizedState,l.dispatch]}function yd(e){var a=dn(),r=a.queue;if(r===null)throw Error(s(311));r.lastRenderedReducer=e;var l=r.dispatch,f=r.pending,m=a.memoizedState;if(f!==null){r.pending=null;var M=f=f.next;do m=e(m,M.action),M=M.next;while(M!==f);li(m,a.memoizedState)||(_n=!0),a.memoizedState=m,a.baseQueue===null&&(a.baseState=m),r.lastRenderedState=m}return[m,l]}function z0(e,a,r){var l=ce,f=dn(),m=Me;if(m){if(r===void 0)throw Error(s(407));r=r()}else r=a();var M=!li((He||f).memoizedState,r);if(M&&(f.memoizedState=r,_n=!0),f=f.queue,bd(G0.bind(null,l,f,e),[e]),f.getSnapshot!==a||M||gn!==null&&gn.memoizedState.tag&1){if(l.flags|=2048,Ir(9,{destroy:void 0},H0.bind(null,l,f,r,a),null),qe===null)throw Error(s(349));m||(Sa&127)!==0||V0(l,a,r)}return r}function V0(e,a,r){e.flags|=16384,e={getSnapshot:a,value:r},a=ce.updateQueue,a===null?(a=Tc(),ce.updateQueue=a,a.stores=[e]):(r=a.stores,r===null?a.stores=[e]:r.push(e))}function H0(e,a,r,l){a.value=r,a.getSnapshot=l,k0(a)&&j0(e)}function G0(e,a,r){return r(function(){k0(a)&&j0(e)})}function k0(e){var a=e.getSnapshot;e=e.value;try{var r=a();return!li(e,r)}catch{return!0}}function j0(e){var a=zs(e,2);a!==null&&ei(a,e,2)}function Sd(e){var a=Xn();if(typeof e=="function"){var r=e;if(e=r(),Ys){Ot(!0);try{r()}finally{Ot(!1)}}}return a.memoizedState=a.baseState=e,a.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ma,lastRenderedState:e},a}function X0(e,a,r,l){return e.baseState=r,xd(e,He,typeof l=="function"?l:Ma)}function yT(e,a,r,l,f){if(Dc(e))throw Error(s(485));if(e=a.action,e!==null){var m={payload:f,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(M){m.listeners.push(M)}};I.T!==null?r(!0):m.isTransition=!1,l(m),r=a.pending,r===null?(m.next=a.pending=m,W0(a,m)):(m.next=r.next,a.pending=r.next=m)}}function W0(e,a){var r=a.action,l=a.payload,f=e.state;if(a.isTransition){var m=I.T,M={};I.T=M;try{var w=r(f,l),k=I.S;k!==null&&k(M,w),q0(e,a,w)}catch(et){Md(e,a,et)}finally{m!==null&&M.types!==null&&(m.types=M.types),I.T=m}}else try{m=r(f,l),q0(e,a,m)}catch(et){Md(e,a,et)}}function q0(e,a,r){r!==null&&typeof r=="object"&&typeof r.then=="function"?r.then(function(l){Y0(e,a,l)},function(l){return Md(e,a,l)}):Y0(e,a,r)}function Y0(e,a,r){a.status="fulfilled",a.value=r,K0(a),e.state=r,a=e.pending,a!==null&&(r=a.next,r===a?e.pending=null:(r=r.next,a.next=r,W0(e,r)))}function Md(e,a,r){var l=e.pending;if(e.pending=null,l!==null){l=l.next;do a.status="rejected",a.reason=r,K0(a),a=a.next;while(a!==l)}e.action=null}function K0(e){e=e.listeners;for(var a=0;a<e.length;a++)(0,e[a])()}function Z0(e,a){return a}function Q0(e,a){if(Me){var r=qe.formState;if(r!==null){t:{var l=ce;if(Me){if(Qe){e:{for(var f=Qe,m=Ei;f.nodeType!==8;){if(!m){f=null;break e}if(f=Ai(f.nextSibling),f===null){f=null;break e}}m=f.data,f=m==="F!"||m==="F"?f:null}if(f){Qe=Ai(f.nextSibling),l=f.data==="F!";break t}}ts(l)}l=!1}l&&(a=r[0])}}return r=Xn(),r.memoizedState=r.baseState=a,l={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Z0,lastRenderedState:a},r.queue=l,r=g_.bind(null,ce,l),l.dispatch=r,l=Sd(!1),m=Cd.bind(null,ce,!1,l.queue),l=Xn(),f={state:a,dispatch:null,action:e,pending:null},l.queue=f,r=yT.bind(null,ce,f,m,r),f.dispatch=r,l.memoizedState=e,[a,r,!1]}function J0(e){var a=dn();return $0(a,He,e)}function $0(e,a,r){if(a=xd(e,a,Z0)[0],e=Rc(Ma)[0],typeof a=="object"&&a!==null&&typeof a.then=="function")try{var l=tl(a)}catch(M){throw M===Ur?_c:M}else l=a;a=dn();var f=a.queue,m=f.dispatch;return r!==a.memoizedState&&(ce.flags|=2048,Ir(9,{destroy:void 0},ST.bind(null,f,r),null)),[l,m,e]}function ST(e,a){e.action=a}function t_(e){var a=dn(),r=He;if(r!==null)return $0(a,r,e);dn(),a=a.memoizedState,r=dn();var l=r.queue.dispatch;return r.memoizedState=e,[a,l,!1]}function Ir(e,a,r,l){return e={tag:e,create:r,deps:l,inst:a,next:null},a=ce.updateQueue,a===null&&(a=Tc(),ce.updateQueue=a),r=a.lastEffect,r===null?a.lastEffect=e.next=e:(l=r.next,r.next=e,e.next=l,a.lastEffect=e),e}function e_(){return dn().memoizedState}function Cc(e,a,r,l){var f=Xn();ce.flags|=e,f.memoizedState=Ir(1|a,{destroy:void 0},r,l===void 0?null:l)}function wc(e,a,r,l){var f=dn();l=l===void 0?null:l;var m=f.memoizedState.inst;He!==null&&l!==null&&hd(l,He.memoizedState.deps)?f.memoizedState=Ir(a,m,r,l):(ce.flags|=e,f.memoizedState=Ir(1|a,m,r,l))}function n_(e,a){Cc(8390656,8,e,a)}function bd(e,a){wc(2048,8,e,a)}function MT(e){ce.flags|=4;var a=ce.updateQueue;if(a===null)a=Tc(),ce.updateQueue=a,a.events=[e];else{var r=a.events;r===null?a.events=[e]:r.push(e)}}function i_(e){var a=dn().memoizedState;return MT({ref:a,nextImpl:e}),function(){if((De&2)!==0)throw Error(s(440));return a.impl.apply(void 0,arguments)}}function a_(e,a){return wc(4,2,e,a)}function s_(e,a){return wc(4,4,e,a)}function r_(e,a){if(typeof a=="function"){e=e();var r=a(e);return function(){typeof r=="function"?r():a(null)}}if(a!=null)return e=e(),a.current=e,function(){a.current=null}}function o_(e,a,r){r=r!=null?r.concat([e]):null,wc(4,4,r_.bind(null,a,e),r)}function Ed(){}function l_(e,a){var r=dn();a=a===void 0?null:a;var l=r.memoizedState;return a!==null&&hd(a,l[1])?l[0]:(r.memoizedState=[e,a],e)}function c_(e,a){var r=dn();a=a===void 0?null:a;var l=r.memoizedState;if(a!==null&&hd(a,l[1]))return l[0];if(l=e(),Ys){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[l,a],l}function Td(e,a,r){return r===void 0||(Sa&1073741824)!==0&&(ye&261930)===0?e.memoizedState=a:(e.memoizedState=r,e=uv(),ce.lanes|=e,cs|=e,r)}function u_(e,a,r,l){return li(r,a)?r:Or.current!==null?(e=Td(e,r,l),li(e,a)||(_n=!0),e):(Sa&42)===0||(Sa&1073741824)!==0&&(ye&261930)===0?(_n=!0,e.memoizedState=r):(e=uv(),ce.lanes|=e,cs|=e,a)}function f_(e,a,r,l,f){var m=G.p;G.p=m!==0&&8>m?m:8;var M=I.T,w={};I.T=w,Cd(e,!1,a,r);try{var k=f(),et=I.S;if(et!==null&&et(w,k),k!==null&&typeof k=="object"&&typeof k.then=="function"){var pt=_T(k,l);el(e,a,pt,pi(e))}else el(e,a,l,pi(e))}catch(vt){el(e,a,{then:function(){},status:"rejected",reason:vt},pi())}finally{G.p=m,M!==null&&w.types!==null&&(M.types=w.types),I.T=M}}function bT(){}function Ad(e,a,r,l){if(e.tag!==5)throw Error(s(476));var f=d_(e).queue;f_(e,f,a,$,r===null?bT:function(){return h_(e),r(l)})}function d_(e){var a=e.memoizedState;if(a!==null)return a;a={memoizedState:$,baseState:$,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ma,lastRenderedState:$},next:null};var r={};return a.next={memoizedState:r,baseState:r,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Ma,lastRenderedState:r},next:null},e.memoizedState=a,e=e.alternate,e!==null&&(e.memoizedState=a),a}function h_(e){var a=d_(e);a.next===null&&(a=e.alternate.memoizedState),el(e,a.next.queue,{},pi())}function Rd(){return Un(vl)}function p_(){return dn().memoizedState}function m_(){return dn().memoizedState}function ET(e){for(var a=e.return;a!==null;){switch(a.tag){case 24:case 3:var r=pi();e=is(r);var l=as(a,e,r);l!==null&&(ei(l,a,r),Zo(l,a,r)),a={cache:nd()},e.payload=a;return}a=a.return}}function TT(e,a,r){var l=pi();r={lane:l,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},Dc(e)?__(a,r):(r=Xf(e,a,r,l),r!==null&&(ei(r,e,l),v_(r,a,l)))}function g_(e,a,r){var l=pi();el(e,a,r,l)}function el(e,a,r,l){var f={lane:l,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null};if(Dc(e))__(a,f);else{var m=e.alternate;if(e.lanes===0&&(m===null||m.lanes===0)&&(m=a.lastRenderedReducer,m!==null))try{var M=a.lastRenderedState,w=m(M,r);if(f.hasEagerState=!0,f.eagerState=w,li(w,M))return uc(e,a,f,0),qe===null&&cc(),!1}catch{}if(r=Xf(e,a,f,l),r!==null)return ei(r,e,l),v_(r,a,l),!0}return!1}function Cd(e,a,r,l){if(l={lane:2,revertLane:rh(),gesture:null,action:l,hasEagerState:!1,eagerState:null,next:null},Dc(e)){if(a)throw Error(s(479))}else a=Xf(e,r,l,2),a!==null&&ei(a,e,2)}function Dc(e){var a=e.alternate;return e===ce||a!==null&&a===ce}function __(e,a){Fr=bc=!0;var r=e.pending;r===null?a.next=a:(a.next=r.next,r.next=a),e.pending=a}function v_(e,a,r){if((r&4194048)!==0){var l=a.lanes;l&=e.pendingLanes,r|=l,a.lanes=r,xi(e,r)}}var nl={readContext:Un,use:Ac,useCallback:rn,useContext:rn,useEffect:rn,useImperativeHandle:rn,useLayoutEffect:rn,useInsertionEffect:rn,useMemo:rn,useReducer:rn,useRef:rn,useState:rn,useDebugValue:rn,useDeferredValue:rn,useTransition:rn,useSyncExternalStore:rn,useId:rn,useHostTransitionStatus:rn,useFormState:rn,useActionState:rn,useOptimistic:rn,useMemoCache:rn,useCacheRefresh:rn};nl.useEffectEvent=rn;var x_={readContext:Un,use:Ac,useCallback:function(e,a){return Xn().memoizedState=[e,a===void 0?null:a],e},useContext:Un,useEffect:n_,useImperativeHandle:function(e,a,r){r=r!=null?r.concat([e]):null,Cc(4194308,4,r_.bind(null,a,e),r)},useLayoutEffect:function(e,a){return Cc(4194308,4,e,a)},useInsertionEffect:function(e,a){Cc(4,2,e,a)},useMemo:function(e,a){var r=Xn();a=a===void 0?null:a;var l=e();if(Ys){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[l,a],l},useReducer:function(e,a,r){var l=Xn();if(r!==void 0){var f=r(a);if(Ys){Ot(!0);try{r(a)}finally{Ot(!1)}}}else f=a;return l.memoizedState=l.baseState=f,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:f},l.queue=e,e=e.dispatch=TT.bind(null,ce,e),[l.memoizedState,e]},useRef:function(e){var a=Xn();return e={current:e},a.memoizedState=e},useState:function(e){e=Sd(e);var a=e.queue,r=g_.bind(null,ce,a);return a.dispatch=r,[e.memoizedState,r]},useDebugValue:Ed,useDeferredValue:function(e,a){var r=Xn();return Td(r,e,a)},useTransition:function(){var e=Sd(!1);return e=f_.bind(null,ce,e.queue,!0,!1),Xn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,a,r){var l=ce,f=Xn();if(Me){if(r===void 0)throw Error(s(407));r=r()}else{if(r=a(),qe===null)throw Error(s(349));(ye&127)!==0||V0(l,a,r)}f.memoizedState=r;var m={value:r,getSnapshot:a};return f.queue=m,n_(G0.bind(null,l,m,e),[e]),l.flags|=2048,Ir(9,{destroy:void 0},H0.bind(null,l,m,r,a),null),r},useId:function(){var e=Xn(),a=qe.identifierPrefix;if(Me){var r=Qi,l=Zi;r=(l&~(1<<32-Ft(l)-1)).toString(32)+r,a="_"+a+"R_"+r,r=Ec++,0<r&&(a+="H"+r.toString(32)),a+="_"}else r=vT++,a="_"+a+"r_"+r.toString(32)+"_";return e.memoizedState=a},useHostTransitionStatus:Rd,useFormState:Q0,useActionState:Q0,useOptimistic:function(e){var a=Xn();a.memoizedState=a.baseState=e;var r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return a.queue=r,a=Cd.bind(null,ce,!0,r),r.dispatch=a,[e,a]},useMemoCache:vd,useCacheRefresh:function(){return Xn().memoizedState=ET.bind(null,ce)},useEffectEvent:function(e){var a=Xn(),r={impl:e};return a.memoizedState=r,function(){if((De&2)!==0)throw Error(s(440));return r.impl.apply(void 0,arguments)}}},wd={readContext:Un,use:Ac,useCallback:l_,useContext:Un,useEffect:bd,useImperativeHandle:o_,useInsertionEffect:a_,useLayoutEffect:s_,useMemo:c_,useReducer:Rc,useRef:e_,useState:function(){return Rc(Ma)},useDebugValue:Ed,useDeferredValue:function(e,a){var r=dn();return u_(r,He.memoizedState,e,a)},useTransition:function(){var e=Rc(Ma)[0],a=dn().memoizedState;return[typeof e=="boolean"?e:tl(e),a]},useSyncExternalStore:z0,useId:p_,useHostTransitionStatus:Rd,useFormState:J0,useActionState:J0,useOptimistic:function(e,a){var r=dn();return X0(r,He,e,a)},useMemoCache:vd,useCacheRefresh:m_};wd.useEffectEvent=i_;var y_={readContext:Un,use:Ac,useCallback:l_,useContext:Un,useEffect:bd,useImperativeHandle:o_,useInsertionEffect:a_,useLayoutEffect:s_,useMemo:c_,useReducer:yd,useRef:e_,useState:function(){return yd(Ma)},useDebugValue:Ed,useDeferredValue:function(e,a){var r=dn();return He===null?Td(r,e,a):u_(r,He.memoizedState,e,a)},useTransition:function(){var e=yd(Ma)[0],a=dn().memoizedState;return[typeof e=="boolean"?e:tl(e),a]},useSyncExternalStore:z0,useId:p_,useHostTransitionStatus:Rd,useFormState:t_,useActionState:t_,useOptimistic:function(e,a){var r=dn();return He!==null?X0(r,He,e,a):(r.baseState=e,[e,r.queue.dispatch])},useMemoCache:vd,useCacheRefresh:m_};y_.useEffectEvent=i_;function Dd(e,a,r,l){a=e.memoizedState,r=r(l,a),r=r==null?a:_({},a,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var Nd={enqueueSetState:function(e,a,r){e=e._reactInternals;var l=pi(),f=is(l);f.payload=a,r!=null&&(f.callback=r),a=as(e,f,l),a!==null&&(ei(a,e,l),Zo(a,e,l))},enqueueReplaceState:function(e,a,r){e=e._reactInternals;var l=pi(),f=is(l);f.tag=1,f.payload=a,r!=null&&(f.callback=r),a=as(e,f,l),a!==null&&(ei(a,e,l),Zo(a,e,l))},enqueueForceUpdate:function(e,a){e=e._reactInternals;var r=pi(),l=is(r);l.tag=2,a!=null&&(l.callback=a),a=as(e,l,r),a!==null&&(ei(a,e,r),Zo(a,e,r))}};function S_(e,a,r,l,f,m,M){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,m,M):a.prototype&&a.prototype.isPureReactComponent?!Go(r,l)||!Go(f,m):!0}function M_(e,a,r,l){e=a.state,typeof a.componentWillReceiveProps=="function"&&a.componentWillReceiveProps(r,l),typeof a.UNSAFE_componentWillReceiveProps=="function"&&a.UNSAFE_componentWillReceiveProps(r,l),a.state!==e&&Nd.enqueueReplaceState(a,a.state,null)}function Ks(e,a){var r=a;if("ref"in a){r={};for(var l in a)l!=="ref"&&(r[l]=a[l])}if(e=e.defaultProps){r===a&&(r=_({},r));for(var f in e)r[f]===void 0&&(r[f]=e[f])}return r}function b_(e){lc(e)}function E_(e){console.error(e)}function T_(e){lc(e)}function Nc(e,a){try{var r=e.onUncaughtError;r(a.value,{componentStack:a.stack})}catch(l){setTimeout(function(){throw l})}}function A_(e,a,r){try{var l=e.onCaughtError;l(r.value,{componentStack:r.stack,errorBoundary:a.tag===1?a.stateNode:null})}catch(f){setTimeout(function(){throw f})}}function Ld(e,a,r){return r=is(r),r.tag=3,r.payload={element:null},r.callback=function(){Nc(e,a)},r}function R_(e){return e=is(e),e.tag=3,e}function C_(e,a,r,l){var f=r.type.getDerivedStateFromError;if(typeof f=="function"){var m=l.value;e.payload=function(){return f(m)},e.callback=function(){A_(a,r,l)}}var M=r.stateNode;M!==null&&typeof M.componentDidCatch=="function"&&(e.callback=function(){A_(a,r,l),typeof f!="function"&&(us===null?us=new Set([this]):us.add(this));var w=l.stack;this.componentDidCatch(l.value,{componentStack:w!==null?w:""})})}function AT(e,a,r,l,f){if(r.flags|=32768,l!==null&&typeof l=="object"&&typeof l.then=="function"){if(a=r.alternate,a!==null&&Dr(a,r,f,!0),r=ui.current,r!==null){switch(r.tag){case 31:case 13:return Ti===null?kc():r.alternate===null&&on===0&&(on=3),r.flags&=-257,r.flags|=65536,r.lanes=f,l===vc?r.flags|=16384:(a=r.updateQueue,a===null?r.updateQueue=new Set([l]):a.add(l),ih(e,l,f)),!1;case 22:return r.flags|=65536,l===vc?r.flags|=16384:(a=r.updateQueue,a===null?(a={transitions:null,markerInstances:null,retryQueue:new Set([l])},r.updateQueue=a):(r=a.retryQueue,r===null?a.retryQueue=new Set([l]):r.add(l)),ih(e,l,f)),!1}throw Error(s(435,r.tag))}return ih(e,l,f),kc(),!1}if(Me)return a=ui.current,a!==null?((a.flags&65536)===0&&(a.flags|=256),a.flags|=65536,a.lanes=f,l!==Qf&&(e=Error(s(422),{cause:l}),Xo(Si(e,r)))):(l!==Qf&&(a=Error(s(423),{cause:l}),Xo(Si(a,r))),e=e.current.alternate,e.flags|=65536,f&=-f,e.lanes|=f,l=Si(l,r),f=Ld(e.stateNode,l,f),ld(e,f),on!==4&&(on=2)),!1;var m=Error(s(520),{cause:l});if(m=Si(m,r),ul===null?ul=[m]:ul.push(m),on!==4&&(on=2),a===null)return!0;l=Si(l,r),r=a;do{switch(r.tag){case 3:return r.flags|=65536,e=f&-f,r.lanes|=e,e=Ld(r.stateNode,l,e),ld(r,e),!1;case 1:if(a=r.type,m=r.stateNode,(r.flags&128)===0&&(typeof a.getDerivedStateFromError=="function"||m!==null&&typeof m.componentDidCatch=="function"&&(us===null||!us.has(m))))return r.flags|=65536,f&=-f,r.lanes|=f,f=R_(f),C_(f,e,r,l),ld(r,f),!1}r=r.return}while(r!==null);return!1}var Ud=Error(s(461)),_n=!1;function Pn(e,a,r,l){a.child=e===null?L0(a,null,r,l):qs(a,e.child,r,l)}function w_(e,a,r,l,f){r=r.render;var m=a.ref;if("ref"in l){var M={};for(var w in l)w!=="ref"&&(M[w]=l[w])}else M=l;return ks(a),l=pd(e,a,r,M,m,f),w=md(),e!==null&&!_n?(gd(e,a,f),ba(e,a,f)):(Me&&w&&Kf(a),a.flags|=1,Pn(e,a,l,f),a.child)}function D_(e,a,r,l,f){if(e===null){var m=r.type;return typeof m=="function"&&!Wf(m)&&m.defaultProps===void 0&&r.compare===null?(a.tag=15,a.type=m,N_(e,a,m,l,f)):(e=dc(r.type,null,l,a,a.mode,f),e.ref=a.ref,e.return=a,a.child=e)}if(m=e.child,!Hd(e,f)){var M=m.memoizedProps;if(r=r.compare,r=r!==null?r:Go,r(M,l)&&e.ref===a.ref)return ba(e,a,f)}return a.flags|=1,e=_a(m,l),e.ref=a.ref,e.return=a,a.child=e}function N_(e,a,r,l,f){if(e!==null){var m=e.memoizedProps;if(Go(m,l)&&e.ref===a.ref)if(_n=!1,a.pendingProps=l=m,Hd(e,f))(e.flags&131072)!==0&&(_n=!0);else return a.lanes=e.lanes,ba(e,a,f)}return Pd(e,a,r,l,f)}function L_(e,a,r,l){var f=l.children,m=e!==null?e.memoizedState:null;if(e===null&&a.stateNode===null&&(a.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),l.mode==="hidden"){if((a.flags&128)!==0){if(m=m!==null?m.baseLanes|r:r,e!==null){for(l=a.child=e.child,f=0;l!==null;)f=f|l.lanes|l.childLanes,l=l.sibling;l=f&~m}else l=0,a.child=null;return U_(e,a,m,r,l)}if((r&536870912)!==0)a.memoizedState={baseLanes:0,cachePool:null},e!==null&&gc(a,m!==null?m.cachePool:null),m!==null?O0(a,m):ud(),F0(a);else return l=a.lanes=536870912,U_(e,a,m!==null?m.baseLanes|r:r,r,l)}else m!==null?(gc(a,m.cachePool),O0(a,m),rs(),a.memoizedState=null):(e!==null&&gc(a,null),ud(),rs());return Pn(e,a,f,r),a.child}function il(e,a){return e!==null&&e.tag===22||a.stateNode!==null||(a.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),a.sibling}function U_(e,a,r,l,f){var m=ad();return m=m===null?null:{parent:mn._currentValue,pool:m},a.memoizedState={baseLanes:r,cachePool:m},e!==null&&gc(a,null),ud(),F0(a),e!==null&&Dr(e,a,l,!0),a.childLanes=f,null}function Lc(e,a){return a=Pc({mode:a.mode,children:a.children},e.mode),a.ref=e.ref,e.child=a,a.return=e,a}function P_(e,a,r){return qs(a,e.child,null,r),e=Lc(a,a.pendingProps),e.flags|=2,fi(a),a.memoizedState=null,e}function RT(e,a,r){var l=a.pendingProps,f=(a.flags&128)!==0;if(a.flags&=-129,e===null){if(Me){if(l.mode==="hidden")return e=Lc(a,l),a.lanes=536870912,il(null,e);if(dd(a),(e=Qe)?(e=Wv(e,Ei),e=e!==null&&e.data==="&"?e:null,e!==null&&(a.memoizedState={dehydrated:e,treeContext:Ja!==null?{id:Zi,overflow:Qi}:null,retryLane:536870912,hydrationErrors:null},r=_0(e),r.return=a,a.child=r,Ln=a,Qe=null)):e=null,e===null)throw ts(a);return a.lanes=536870912,null}return Lc(a,l)}var m=e.memoizedState;if(m!==null){var M=m.dehydrated;if(dd(a),f)if(a.flags&256)a.flags&=-257,a=P_(e,a,r);else if(a.memoizedState!==null)a.child=e.child,a.flags|=128,a=null;else throw Error(s(558));else if(_n||Dr(e,a,r,!1),f=(r&e.childLanes)!==0,_n||f){if(l=qe,l!==null&&(M=si(l,r),M!==0&&M!==m.retryLane))throw m.retryLane=M,zs(e,M),ei(l,e,M),Ud;kc(),a=P_(e,a,r)}else e=m.treeContext,Qe=Ai(M.nextSibling),Ln=a,Me=!0,$a=null,Ei=!1,e!==null&&y0(a,e),a=Lc(a,l),a.flags|=4096;return a}return e=_a(e.child,{mode:l.mode,children:l.children}),e.ref=a.ref,a.child=e,e.return=a,e}function Uc(e,a){var r=a.ref;if(r===null)e!==null&&e.ref!==null&&(a.flags|=4194816);else{if(typeof r!="function"&&typeof r!="object")throw Error(s(284));(e===null||e.ref!==r)&&(a.flags|=4194816)}}function Pd(e,a,r,l,f){return ks(a),r=pd(e,a,r,l,void 0,f),l=md(),e!==null&&!_n?(gd(e,a,f),ba(e,a,f)):(Me&&l&&Kf(a),a.flags|=1,Pn(e,a,r,f),a.child)}function O_(e,a,r,l,f,m){return ks(a),a.updateQueue=null,r=I0(a,l,r,f),B0(e),l=md(),e!==null&&!_n?(gd(e,a,m),ba(e,a,m)):(Me&&l&&Kf(a),a.flags|=1,Pn(e,a,r,m),a.child)}function F_(e,a,r,l,f){if(ks(a),a.stateNode===null){var m=Ar,M=r.contextType;typeof M=="object"&&M!==null&&(m=Un(M)),m=new r(l,m),a.memoizedState=m.state!==null&&m.state!==void 0?m.state:null,m.updater=Nd,a.stateNode=m,m._reactInternals=a,m=a.stateNode,m.props=l,m.state=a.memoizedState,m.refs={},rd(a),M=r.contextType,m.context=typeof M=="object"&&M!==null?Un(M):Ar,m.state=a.memoizedState,M=r.getDerivedStateFromProps,typeof M=="function"&&(Dd(a,r,M,l),m.state=a.memoizedState),typeof r.getDerivedStateFromProps=="function"||typeof m.getSnapshotBeforeUpdate=="function"||typeof m.UNSAFE_componentWillMount!="function"&&typeof m.componentWillMount!="function"||(M=m.state,typeof m.componentWillMount=="function"&&m.componentWillMount(),typeof m.UNSAFE_componentWillMount=="function"&&m.UNSAFE_componentWillMount(),M!==m.state&&Nd.enqueueReplaceState(m,m.state,null),Jo(a,l,m,f),Qo(),m.state=a.memoizedState),typeof m.componentDidMount=="function"&&(a.flags|=4194308),l=!0}else if(e===null){m=a.stateNode;var w=a.memoizedProps,k=Ks(r,w);m.props=k;var et=m.context,pt=r.contextType;M=Ar,typeof pt=="object"&&pt!==null&&(M=Un(pt));var vt=r.getDerivedStateFromProps;pt=typeof vt=="function"||typeof m.getSnapshotBeforeUpdate=="function",w=a.pendingProps!==w,pt||typeof m.UNSAFE_componentWillReceiveProps!="function"&&typeof m.componentWillReceiveProps!="function"||(w||et!==M)&&M_(a,m,l,M),ns=!1;var st=a.memoizedState;m.state=st,Jo(a,l,m,f),Qo(),et=a.memoizedState,w||st!==et||ns?(typeof vt=="function"&&(Dd(a,r,vt,l),et=a.memoizedState),(k=ns||S_(a,r,k,l,st,et,M))?(pt||typeof m.UNSAFE_componentWillMount!="function"&&typeof m.componentWillMount!="function"||(typeof m.componentWillMount=="function"&&m.componentWillMount(),typeof m.UNSAFE_componentWillMount=="function"&&m.UNSAFE_componentWillMount()),typeof m.componentDidMount=="function"&&(a.flags|=4194308)):(typeof m.componentDidMount=="function"&&(a.flags|=4194308),a.memoizedProps=l,a.memoizedState=et),m.props=l,m.state=et,m.context=M,l=k):(typeof m.componentDidMount=="function"&&(a.flags|=4194308),l=!1)}else{m=a.stateNode,od(e,a),M=a.memoizedProps,pt=Ks(r,M),m.props=pt,vt=a.pendingProps,st=m.context,et=r.contextType,k=Ar,typeof et=="object"&&et!==null&&(k=Un(et)),w=r.getDerivedStateFromProps,(et=typeof w=="function"||typeof m.getSnapshotBeforeUpdate=="function")||typeof m.UNSAFE_componentWillReceiveProps!="function"&&typeof m.componentWillReceiveProps!="function"||(M!==vt||st!==k)&&M_(a,m,l,k),ns=!1,st=a.memoizedState,m.state=st,Jo(a,l,m,f),Qo();var ut=a.memoizedState;M!==vt||st!==ut||ns||e!==null&&e.dependencies!==null&&pc(e.dependencies)?(typeof w=="function"&&(Dd(a,r,w,l),ut=a.memoizedState),(pt=ns||S_(a,r,pt,l,st,ut,k)||e!==null&&e.dependencies!==null&&pc(e.dependencies))?(et||typeof m.UNSAFE_componentWillUpdate!="function"&&typeof m.componentWillUpdate!="function"||(typeof m.componentWillUpdate=="function"&&m.componentWillUpdate(l,ut,k),typeof m.UNSAFE_componentWillUpdate=="function"&&m.UNSAFE_componentWillUpdate(l,ut,k)),typeof m.componentDidUpdate=="function"&&(a.flags|=4),typeof m.getSnapshotBeforeUpdate=="function"&&(a.flags|=1024)):(typeof m.componentDidUpdate!="function"||M===e.memoizedProps&&st===e.memoizedState||(a.flags|=4),typeof m.getSnapshotBeforeUpdate!="function"||M===e.memoizedProps&&st===e.memoizedState||(a.flags|=1024),a.memoizedProps=l,a.memoizedState=ut),m.props=l,m.state=ut,m.context=k,l=pt):(typeof m.componentDidUpdate!="function"||M===e.memoizedProps&&st===e.memoizedState||(a.flags|=4),typeof m.getSnapshotBeforeUpdate!="function"||M===e.memoizedProps&&st===e.memoizedState||(a.flags|=1024),l=!1)}return m=l,Uc(e,a),l=(a.flags&128)!==0,m||l?(m=a.stateNode,r=l&&typeof r.getDerivedStateFromError!="function"?null:m.render(),a.flags|=1,e!==null&&l?(a.child=qs(a,e.child,null,f),a.child=qs(a,null,r,f)):Pn(e,a,r,f),a.memoizedState=m.state,e=a.child):e=ba(e,a,f),e}function B_(e,a,r,l){return Hs(),a.flags|=256,Pn(e,a,r,l),a.child}var Od={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function Fd(e){return{baseLanes:e,cachePool:A0()}}function Bd(e,a,r){return e=e!==null?e.childLanes&~r:0,a&&(e|=hi),e}function I_(e,a,r){var l=a.pendingProps,f=!1,m=(a.flags&128)!==0,M;if((M=m)||(M=e!==null&&e.memoizedState===null?!1:(fn.current&2)!==0),M&&(f=!0,a.flags&=-129),M=(a.flags&32)!==0,a.flags&=-33,e===null){if(Me){if(f?ss(a):rs(),(e=Qe)?(e=Wv(e,Ei),e=e!==null&&e.data!=="&"?e:null,e!==null&&(a.memoizedState={dehydrated:e,treeContext:Ja!==null?{id:Zi,overflow:Qi}:null,retryLane:536870912,hydrationErrors:null},r=_0(e),r.return=a,a.child=r,Ln=a,Qe=null)):e=null,e===null)throw ts(a);return xh(e)?a.lanes=32:a.lanes=536870912,null}var w=l.children;return l=l.fallback,f?(rs(),f=a.mode,w=Pc({mode:"hidden",children:w},f),l=Vs(l,f,r,null),w.return=a,l.return=a,w.sibling=l,a.child=w,l=a.child,l.memoizedState=Fd(r),l.childLanes=Bd(e,M,r),a.memoizedState=Od,il(null,l)):(ss(a),Id(a,w))}var k=e.memoizedState;if(k!==null&&(w=k.dehydrated,w!==null)){if(m)a.flags&256?(ss(a),a.flags&=-257,a=zd(e,a,r)):a.memoizedState!==null?(rs(),a.child=e.child,a.flags|=128,a=null):(rs(),w=l.fallback,f=a.mode,l=Pc({mode:"visible",children:l.children},f),w=Vs(w,f,r,null),w.flags|=2,l.return=a,w.return=a,l.sibling=w,a.child=l,qs(a,e.child,null,r),l=a.child,l.memoizedState=Fd(r),l.childLanes=Bd(e,M,r),a.memoizedState=Od,a=il(null,l));else if(ss(a),xh(w)){if(M=w.nextSibling&&w.nextSibling.dataset,M)var et=M.dgst;M=et,l=Error(s(419)),l.stack="",l.digest=M,Xo({value:l,source:null,stack:null}),a=zd(e,a,r)}else if(_n||Dr(e,a,r,!1),M=(r&e.childLanes)!==0,_n||M){if(M=qe,M!==null&&(l=si(M,r),l!==0&&l!==k.retryLane))throw k.retryLane=l,zs(e,l),ei(M,e,l),Ud;vh(w)||kc(),a=zd(e,a,r)}else vh(w)?(a.flags|=192,a.child=e.child,a=null):(e=k.treeContext,Qe=Ai(w.nextSibling),Ln=a,Me=!0,$a=null,Ei=!1,e!==null&&y0(a,e),a=Id(a,l.children),a.flags|=4096);return a}return f?(rs(),w=l.fallback,f=a.mode,k=e.child,et=k.sibling,l=_a(k,{mode:"hidden",children:l.children}),l.subtreeFlags=k.subtreeFlags&65011712,et!==null?w=_a(et,w):(w=Vs(w,f,r,null),w.flags|=2),w.return=a,l.return=a,l.sibling=w,a.child=l,il(null,l),l=a.child,w=e.child.memoizedState,w===null?w=Fd(r):(f=w.cachePool,f!==null?(k=mn._currentValue,f=f.parent!==k?{parent:k,pool:k}:f):f=A0(),w={baseLanes:w.baseLanes|r,cachePool:f}),l.memoizedState=w,l.childLanes=Bd(e,M,r),a.memoizedState=Od,il(e.child,l)):(ss(a),r=e.child,e=r.sibling,r=_a(r,{mode:"visible",children:l.children}),r.return=a,r.sibling=null,e!==null&&(M=a.deletions,M===null?(a.deletions=[e],a.flags|=16):M.push(e)),a.child=r,a.memoizedState=null,r)}function Id(e,a){return a=Pc({mode:"visible",children:a},e.mode),a.return=e,e.child=a}function Pc(e,a){return e=ci(22,e,null,a),e.lanes=0,e}function zd(e,a,r){return qs(a,e.child,null,r),e=Id(a,a.pendingProps.children),e.flags|=2,a.memoizedState=null,e}function z_(e,a,r){e.lanes|=a;var l=e.alternate;l!==null&&(l.lanes|=a),td(e.return,a,r)}function Vd(e,a,r,l,f,m){var M=e.memoizedState;M===null?e.memoizedState={isBackwards:a,rendering:null,renderingStartTime:0,last:l,tail:r,tailMode:f,treeForkCount:m}:(M.isBackwards=a,M.rendering=null,M.renderingStartTime=0,M.last=l,M.tail=r,M.tailMode=f,M.treeForkCount=m)}function V_(e,a,r){var l=a.pendingProps,f=l.revealOrder,m=l.tail;l=l.children;var M=fn.current,w=(M&2)!==0;if(w?(M=M&1|2,a.flags|=128):M&=1,St(fn,M),Pn(e,a,l,r),l=Me?jo:0,!w&&e!==null&&(e.flags&128)!==0)t:for(e=a.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&z_(e,r,a);else if(e.tag===19)z_(e,r,a);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===a)break t;for(;e.sibling===null;){if(e.return===null||e.return===a)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(f){case"forwards":for(r=a.child,f=null;r!==null;)e=r.alternate,e!==null&&Mc(e)===null&&(f=r),r=r.sibling;r=f,r===null?(f=a.child,a.child=null):(f=r.sibling,r.sibling=null),Vd(a,!1,f,r,m,l);break;case"backwards":case"unstable_legacy-backwards":for(r=null,f=a.child,a.child=null;f!==null;){if(e=f.alternate,e!==null&&Mc(e)===null){a.child=f;break}e=f.sibling,f.sibling=r,r=f,f=e}Vd(a,!0,r,null,m,l);break;case"together":Vd(a,!1,null,null,void 0,l);break;default:a.memoizedState=null}return a.child}function ba(e,a,r){if(e!==null&&(a.dependencies=e.dependencies),cs|=a.lanes,(r&a.childLanes)===0)if(e!==null){if(Dr(e,a,r,!1),(r&a.childLanes)===0)return null}else return null;if(e!==null&&a.child!==e.child)throw Error(s(153));if(a.child!==null){for(e=a.child,r=_a(e,e.pendingProps),a.child=r,r.return=a;e.sibling!==null;)e=e.sibling,r=r.sibling=_a(e,e.pendingProps),r.return=a;r.sibling=null}return a.child}function Hd(e,a){return(e.lanes&a)!==0?!0:(e=e.dependencies,!!(e!==null&&pc(e)))}function CT(e,a,r){switch(a.tag){case 3:Tt(a,a.stateNode.containerInfo),es(a,mn,e.memoizedState.cache),Hs();break;case 27:case 5:ee(a);break;case 4:Tt(a,a.stateNode.containerInfo);break;case 10:es(a,a.type,a.memoizedProps.value);break;case 31:if(a.memoizedState!==null)return a.flags|=128,dd(a),null;break;case 13:var l=a.memoizedState;if(l!==null)return l.dehydrated!==null?(ss(a),a.flags|=128,null):(r&a.child.childLanes)!==0?I_(e,a,r):(ss(a),e=ba(e,a,r),e!==null?e.sibling:null);ss(a);break;case 19:var f=(e.flags&128)!==0;if(l=(r&a.childLanes)!==0,l||(Dr(e,a,r,!1),l=(r&a.childLanes)!==0),f){if(l)return V_(e,a,r);a.flags|=128}if(f=a.memoizedState,f!==null&&(f.rendering=null,f.tail=null,f.lastEffect=null),St(fn,fn.current),l)break;return null;case 22:return a.lanes=0,L_(e,a,r,a.pendingProps);case 24:es(a,mn,e.memoizedState.cache)}return ba(e,a,r)}function H_(e,a,r){if(e!==null)if(e.memoizedProps!==a.pendingProps)_n=!0;else{if(!Hd(e,r)&&(a.flags&128)===0)return _n=!1,CT(e,a,r);_n=(e.flags&131072)!==0}else _n=!1,Me&&(a.flags&1048576)!==0&&x0(a,jo,a.index);switch(a.lanes=0,a.tag){case 16:t:{var l=a.pendingProps;if(e=Xs(a.elementType),a.type=e,typeof e=="function")Wf(e)?(l=Ks(e,l),a.tag=1,a=F_(null,a,e,l,r)):(a.tag=0,a=Pd(null,a,e,l,r));else{if(e!=null){var f=e.$$typeof;if(f===L){a.tag=11,a=w_(null,a,e,l,r);break t}else if(f===O){a.tag=14,a=D_(null,a,e,l,r);break t}}throw a=ct(e)||e,Error(s(306,a,""))}}return a;case 0:return Pd(e,a,a.type,a.pendingProps,r);case 1:return l=a.type,f=Ks(l,a.pendingProps),F_(e,a,l,f,r);case 3:t:{if(Tt(a,a.stateNode.containerInfo),e===null)throw Error(s(387));l=a.pendingProps;var m=a.memoizedState;f=m.element,od(e,a),Jo(a,l,null,r);var M=a.memoizedState;if(l=M.cache,es(a,mn,l),l!==m.cache&&ed(a,[mn],r,!0),Qo(),l=M.element,m.isDehydrated)if(m={element:l,isDehydrated:!1,cache:M.cache},a.updateQueue.baseState=m,a.memoizedState=m,a.flags&256){a=B_(e,a,l,r);break t}else if(l!==f){f=Si(Error(s(424)),a),Xo(f),a=B_(e,a,l,r);break t}else for(e=a.stateNode.containerInfo,e.nodeType===9?e=e.body:e=e.nodeName==="HTML"?e.ownerDocument.body:e,Qe=Ai(e.firstChild),Ln=a,Me=!0,$a=null,Ei=!0,r=L0(a,null,l,r),a.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling;else{if(Hs(),l===f){a=ba(e,a,r);break t}Pn(e,a,l,r)}a=a.child}return a;case 26:return Uc(e,a),e===null?(r=Jv(a.type,null,a.pendingProps,null))?a.memoizedState=r:Me||(r=a.type,e=a.pendingProps,l=Zc(ot.current).createElement(r),l[un]=a,l[Nn]=e,On(l,r,e),pn(l),a.stateNode=l):a.memoizedState=Jv(a.type,e.memoizedProps,a.pendingProps,e.memoizedState),null;case 27:return ee(a),e===null&&Me&&(l=a.stateNode=Kv(a.type,a.pendingProps,ot.current),Ln=a,Ei=!0,f=Qe,ps(a.type)?(yh=f,Qe=Ai(l.firstChild)):Qe=f),Pn(e,a,a.pendingProps.children,r),Uc(e,a),e===null&&(a.flags|=4194304),a.child;case 5:return e===null&&Me&&((f=l=Qe)&&(l=a1(l,a.type,a.pendingProps,Ei),l!==null?(a.stateNode=l,Ln=a,Qe=Ai(l.firstChild),Ei=!1,f=!0):f=!1),f||ts(a)),ee(a),f=a.type,m=a.pendingProps,M=e!==null?e.memoizedProps:null,l=m.children,mh(f,m)?l=null:M!==null&&mh(f,M)&&(a.flags|=32),a.memoizedState!==null&&(f=pd(e,a,xT,null,null,r),vl._currentValue=f),Uc(e,a),Pn(e,a,l,r),a.child;case 6:return e===null&&Me&&((e=r=Qe)&&(r=s1(r,a.pendingProps,Ei),r!==null?(a.stateNode=r,Ln=a,Qe=null,e=!0):e=!1),e||ts(a)),null;case 13:return I_(e,a,r);case 4:return Tt(a,a.stateNode.containerInfo),l=a.pendingProps,e===null?a.child=qs(a,null,l,r):Pn(e,a,l,r),a.child;case 11:return w_(e,a,a.type,a.pendingProps,r);case 7:return Pn(e,a,a.pendingProps,r),a.child;case 8:return Pn(e,a,a.pendingProps.children,r),a.child;case 12:return Pn(e,a,a.pendingProps.children,r),a.child;case 10:return l=a.pendingProps,es(a,a.type,l.value),Pn(e,a,l.children,r),a.child;case 9:return f=a.type._context,l=a.pendingProps.children,ks(a),f=Un(f),l=l(f),a.flags|=1,Pn(e,a,l,r),a.child;case 14:return D_(e,a,a.type,a.pendingProps,r);case 15:return N_(e,a,a.type,a.pendingProps,r);case 19:return V_(e,a,r);case 31:return RT(e,a,r);case 22:return L_(e,a,r,a.pendingProps);case 24:return ks(a),l=Un(mn),e===null?(f=ad(),f===null&&(f=qe,m=nd(),f.pooledCache=m,m.refCount++,m!==null&&(f.pooledCacheLanes|=r),f=m),a.memoizedState={parent:l,cache:f},rd(a),es(a,mn,f)):((e.lanes&r)!==0&&(od(e,a),Jo(a,null,null,r),Qo()),f=e.memoizedState,m=a.memoizedState,f.parent!==l?(f={parent:l,cache:l},a.memoizedState=f,a.lanes===0&&(a.memoizedState=a.updateQueue.baseState=f),es(a,mn,l)):(l=m.cache,es(a,mn,l),l!==f.cache&&ed(a,[mn],r,!0))),Pn(e,a,a.pendingProps.children,r),a.child;case 29:throw a.pendingProps}throw Error(s(156,a.tag))}function Ea(e){e.flags|=4}function Gd(e,a,r,l,f){if((a=(e.mode&32)!==0)&&(a=!1),a){if(e.flags|=16777216,(f&335544128)===f)if(e.stateNode.complete)e.flags|=8192;else if(pv())e.flags|=8192;else throw Ws=vc,sd}else e.flags&=-16777217}function G_(e,a){if(a.type!=="stylesheet"||(a.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!ix(a))if(pv())e.flags|=8192;else throw Ws=vc,sd}function Oc(e,a){a!==null&&(e.flags|=4),e.flags&16384&&(a=e.tag!==22?bt():536870912,e.lanes|=a,Gr|=a)}function al(e,a){if(!Me)switch(e.tailMode){case"hidden":a=e.tail;for(var r=null;a!==null;)a.alternate!==null&&(r=a),a=a.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var l=null;r!==null;)r.alternate!==null&&(l=r),r=r.sibling;l===null?a||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function Je(e){var a=e.alternate!==null&&e.alternate.child===e.child,r=0,l=0;if(a)for(var f=e.child;f!==null;)r|=f.lanes|f.childLanes,l|=f.subtreeFlags&65011712,l|=f.flags&65011712,f.return=e,f=f.sibling;else for(f=e.child;f!==null;)r|=f.lanes|f.childLanes,l|=f.subtreeFlags,l|=f.flags,f.return=e,f=f.sibling;return e.subtreeFlags|=l,e.childLanes=r,a}function wT(e,a,r){var l=a.pendingProps;switch(Zf(a),a.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Je(a),null;case 1:return Je(a),null;case 3:return r=a.stateNode,l=null,e!==null&&(l=e.memoizedState.cache),a.memoizedState.cache!==l&&(a.flags|=2048),ya(mn),Ht(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(wr(a)?Ea(a):e===null||e.memoizedState.isDehydrated&&(a.flags&256)===0||(a.flags|=1024,Jf())),Je(a),null;case 26:var f=a.type,m=a.memoizedState;return e===null?(Ea(a),m!==null?(Je(a),G_(a,m)):(Je(a),Gd(a,f,null,l,r))):m?m!==e.memoizedState?(Ea(a),Je(a),G_(a,m)):(Je(a),a.flags&=-16777217):(e=e.memoizedProps,e!==l&&Ea(a),Je(a),Gd(a,f,e,l,r)),null;case 27:if($t(a),r=ot.current,f=a.type,e!==null&&a.stateNode!=null)e.memoizedProps!==l&&Ea(a);else{if(!l){if(a.stateNode===null)throw Error(s(166));return Je(a),null}e=Rt.current,wr(a)?S0(a):(e=Kv(f,l,r),a.stateNode=e,Ea(a))}return Je(a),null;case 5:if($t(a),f=a.type,e!==null&&a.stateNode!=null)e.memoizedProps!==l&&Ea(a);else{if(!l){if(a.stateNode===null)throw Error(s(166));return Je(a),null}if(m=Rt.current,wr(a))S0(a);else{var M=Zc(ot.current);switch(m){case 1:m=M.createElementNS("http://www.w3.org/2000/svg",f);break;case 2:m=M.createElementNS("http://www.w3.org/1998/Math/MathML",f);break;default:switch(f){case"svg":m=M.createElementNS("http://www.w3.org/2000/svg",f);break;case"math":m=M.createElementNS("http://www.w3.org/1998/Math/MathML",f);break;case"script":m=M.createElement("div"),m.innerHTML="<script><\/script>",m=m.removeChild(m.firstChild);break;case"select":m=typeof l.is=="string"?M.createElement("select",{is:l.is}):M.createElement("select"),l.multiple?m.multiple=!0:l.size&&(m.size=l.size);break;default:m=typeof l.is=="string"?M.createElement(f,{is:l.is}):M.createElement(f)}}m[un]=a,m[Nn]=l;t:for(M=a.child;M!==null;){if(M.tag===5||M.tag===6)m.appendChild(M.stateNode);else if(M.tag!==4&&M.tag!==27&&M.child!==null){M.child.return=M,M=M.child;continue}if(M===a)break t;for(;M.sibling===null;){if(M.return===null||M.return===a)break t;M=M.return}M.sibling.return=M.return,M=M.sibling}a.stateNode=m;t:switch(On(m,f,l),f){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break t;case"img":l=!0;break t;default:l=!1}l&&Ea(a)}}return Je(a),Gd(a,a.type,e===null?null:e.memoizedProps,a.pendingProps,r),null;case 6:if(e&&a.stateNode!=null)e.memoizedProps!==l&&Ea(a);else{if(typeof l!="string"&&a.stateNode===null)throw Error(s(166));if(e=ot.current,wr(a)){if(e=a.stateNode,r=a.memoizedProps,l=null,f=Ln,f!==null)switch(f.tag){case 27:case 5:l=f.memoizedProps}e[un]=a,e=!!(e.nodeValue===r||l!==null&&l.suppressHydrationWarning===!0||Iv(e.nodeValue,r)),e||ts(a,!0)}else e=Zc(e).createTextNode(l),e[un]=a,a.stateNode=e}return Je(a),null;case 31:if(r=a.memoizedState,e===null||e.memoizedState!==null){if(l=wr(a),r!==null){if(e===null){if(!l)throw Error(s(318));if(e=a.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(557));e[un]=a}else Hs(),(a.flags&128)===0&&(a.memoizedState=null),a.flags|=4;Je(a),e=!1}else r=Jf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=r),e=!0;if(!e)return a.flags&256?(fi(a),a):(fi(a),null);if((a.flags&128)!==0)throw Error(s(558))}return Je(a),null;case 13:if(l=a.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(f=wr(a),l!==null&&l.dehydrated!==null){if(e===null){if(!f)throw Error(s(318));if(f=a.memoizedState,f=f!==null?f.dehydrated:null,!f)throw Error(s(317));f[un]=a}else Hs(),(a.flags&128)===0&&(a.memoizedState=null),a.flags|=4;Je(a),f=!1}else f=Jf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=f),f=!0;if(!f)return a.flags&256?(fi(a),a):(fi(a),null)}return fi(a),(a.flags&128)!==0?(a.lanes=r,a):(r=l!==null,e=e!==null&&e.memoizedState!==null,r&&(l=a.child,f=null,l.alternate!==null&&l.alternate.memoizedState!==null&&l.alternate.memoizedState.cachePool!==null&&(f=l.alternate.memoizedState.cachePool.pool),m=null,l.memoizedState!==null&&l.memoizedState.cachePool!==null&&(m=l.memoizedState.cachePool.pool),m!==f&&(l.flags|=2048)),r!==e&&r&&(a.child.flags|=8192),Oc(a,a.updateQueue),Je(a),null);case 4:return Ht(),e===null&&uh(a.stateNode.containerInfo),Je(a),null;case 10:return ya(a.type),Je(a),null;case 19:if(Q(fn),l=a.memoizedState,l===null)return Je(a),null;if(f=(a.flags&128)!==0,m=l.rendering,m===null)if(f)al(l,!1);else{if(on!==0||e!==null&&(e.flags&128)!==0)for(e=a.child;e!==null;){if(m=Mc(e),m!==null){for(a.flags|=128,al(l,!1),e=m.updateQueue,a.updateQueue=e,Oc(a,e),a.subtreeFlags=0,e=r,r=a.child;r!==null;)g0(r,e),r=r.sibling;return St(fn,fn.current&1|2),Me&&va(a,l.treeForkCount),a.child}e=e.sibling}l.tail!==null&&Ct()>Vc&&(a.flags|=128,f=!0,al(l,!1),a.lanes=4194304)}else{if(!f)if(e=Mc(m),e!==null){if(a.flags|=128,f=!0,e=e.updateQueue,a.updateQueue=e,Oc(a,e),al(l,!0),l.tail===null&&l.tailMode==="hidden"&&!m.alternate&&!Me)return Je(a),null}else 2*Ct()-l.renderingStartTime>Vc&&r!==536870912&&(a.flags|=128,f=!0,al(l,!1),a.lanes=4194304);l.isBackwards?(m.sibling=a.child,a.child=m):(e=l.last,e!==null?e.sibling=m:a.child=m,l.last=m)}return l.tail!==null?(e=l.tail,l.rendering=e,l.tail=e.sibling,l.renderingStartTime=Ct(),e.sibling=null,r=fn.current,St(fn,f?r&1|2:r&1),Me&&va(a,l.treeForkCount),e):(Je(a),null);case 22:case 23:return fi(a),fd(),l=a.memoizedState!==null,e!==null?e.memoizedState!==null!==l&&(a.flags|=8192):l&&(a.flags|=8192),l?(r&536870912)!==0&&(a.flags&128)===0&&(Je(a),a.subtreeFlags&6&&(a.flags|=8192)):Je(a),r=a.updateQueue,r!==null&&Oc(a,r.retryQueue),r=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),l=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(l=a.memoizedState.cachePool.pool),l!==r&&(a.flags|=2048),e!==null&&Q(js),null;case 24:return r=null,e!==null&&(r=e.memoizedState.cache),a.memoizedState.cache!==r&&(a.flags|=2048),ya(mn),Je(a),null;case 25:return null;case 30:return null}throw Error(s(156,a.tag))}function DT(e,a){switch(Zf(a),a.tag){case 1:return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 3:return ya(mn),Ht(),e=a.flags,(e&65536)!==0&&(e&128)===0?(a.flags=e&-65537|128,a):null;case 26:case 27:case 5:return $t(a),null;case 31:if(a.memoizedState!==null){if(fi(a),a.alternate===null)throw Error(s(340));Hs()}return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 13:if(fi(a),e=a.memoizedState,e!==null&&e.dehydrated!==null){if(a.alternate===null)throw Error(s(340));Hs()}return e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 19:return Q(fn),null;case 4:return Ht(),null;case 10:return ya(a.type),null;case 22:case 23:return fi(a),fd(),e!==null&&Q(js),e=a.flags,e&65536?(a.flags=e&-65537|128,a):null;case 24:return ya(mn),null;case 25:return null;default:return null}}function k_(e,a){switch(Zf(a),a.tag){case 3:ya(mn),Ht();break;case 26:case 27:case 5:$t(a);break;case 4:Ht();break;case 31:a.memoizedState!==null&&fi(a);break;case 13:fi(a);break;case 19:Q(fn);break;case 10:ya(a.type);break;case 22:case 23:fi(a),fd(),e!==null&&Q(js);break;case 24:ya(mn)}}function sl(e,a){try{var r=a.updateQueue,l=r!==null?r.lastEffect:null;if(l!==null){var f=l.next;r=f;do{if((r.tag&e)===e){l=void 0;var m=r.create,M=r.inst;l=m(),M.destroy=l}r=r.next}while(r!==f)}}catch(w){Ie(a,a.return,w)}}function os(e,a,r){try{var l=a.updateQueue,f=l!==null?l.lastEffect:null;if(f!==null){var m=f.next;l=m;do{if((l.tag&e)===e){var M=l.inst,w=M.destroy;if(w!==void 0){M.destroy=void 0,f=a;var k=r,et=w;try{et()}catch(pt){Ie(f,k,pt)}}}l=l.next}while(l!==m)}}catch(pt){Ie(a,a.return,pt)}}function j_(e){var a=e.updateQueue;if(a!==null){var r=e.stateNode;try{P0(a,r)}catch(l){Ie(e,e.return,l)}}}function X_(e,a,r){r.props=Ks(e.type,e.memoizedProps),r.state=e.memoizedState;try{r.componentWillUnmount()}catch(l){Ie(e,a,l)}}function rl(e,a){try{var r=e.ref;if(r!==null){switch(e.tag){case 26:case 27:case 5:var l=e.stateNode;break;case 30:l=e.stateNode;break;default:l=e.stateNode}typeof r=="function"?e.refCleanup=r(l):r.current=l}}catch(f){Ie(e,a,f)}}function Ji(e,a){var r=e.ref,l=e.refCleanup;if(r!==null)if(typeof l=="function")try{l()}catch(f){Ie(e,a,f)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof r=="function")try{r(null)}catch(f){Ie(e,a,f)}else r.current=null}function W_(e){var a=e.type,r=e.memoizedProps,l=e.stateNode;try{t:switch(a){case"button":case"input":case"select":case"textarea":r.autoFocus&&l.focus();break t;case"img":r.src?l.src=r.src:r.srcSet&&(l.srcset=r.srcSet)}}catch(f){Ie(e,e.return,f)}}function kd(e,a,r){try{var l=e.stateNode;JT(l,e.type,r,a),l[Nn]=a}catch(f){Ie(e,e.return,f)}}function q_(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&ps(e.type)||e.tag===4}function jd(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||q_(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&ps(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Xd(e,a,r){var l=e.tag;if(l===5||l===6)e=e.stateNode,a?(r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r).insertBefore(e,a):(a=r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r,a.appendChild(e),r=r._reactRootContainer,r!=null||a.onclick!==null||(a.onclick=ma));else if(l!==4&&(l===27&&ps(e.type)&&(r=e.stateNode,a=null),e=e.child,e!==null))for(Xd(e,a,r),e=e.sibling;e!==null;)Xd(e,a,r),e=e.sibling}function Fc(e,a,r){var l=e.tag;if(l===5||l===6)e=e.stateNode,a?r.insertBefore(e,a):r.appendChild(e);else if(l!==4&&(l===27&&ps(e.type)&&(r=e.stateNode),e=e.child,e!==null))for(Fc(e,a,r),e=e.sibling;e!==null;)Fc(e,a,r),e=e.sibling}function Y_(e){var a=e.stateNode,r=e.memoizedProps;try{for(var l=e.type,f=a.attributes;f.length;)a.removeAttributeNode(f[0]);On(a,l,r),a[un]=e,a[Nn]=r}catch(m){Ie(e,e.return,m)}}var Ta=!1,vn=!1,Wd=!1,K_=typeof WeakSet=="function"?WeakSet:Set,Cn=null;function NT(e,a){if(e=e.containerInfo,hh=iu,e=o0(e),zf(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else t:{r=(r=e.ownerDocument)&&r.defaultView||window;var l=r.getSelection&&r.getSelection();if(l&&l.rangeCount!==0){r=l.anchorNode;var f=l.anchorOffset,m=l.focusNode;l=l.focusOffset;try{r.nodeType,m.nodeType}catch{r=null;break t}var M=0,w=-1,k=-1,et=0,pt=0,vt=e,st=null;e:for(;;){for(var ut;vt!==r||f!==0&&vt.nodeType!==3||(w=M+f),vt!==m||l!==0&&vt.nodeType!==3||(k=M+l),vt.nodeType===3&&(M+=vt.nodeValue.length),(ut=vt.firstChild)!==null;)st=vt,vt=ut;for(;;){if(vt===e)break e;if(st===r&&++et===f&&(w=M),st===m&&++pt===l&&(k=M),(ut=vt.nextSibling)!==null)break;vt=st,st=vt.parentNode}vt=ut}r=w===-1||k===-1?null:{start:w,end:k}}else r=null}r=r||{start:0,end:0}}else r=null;for(ph={focusedElem:e,selectionRange:r},iu=!1,Cn=a;Cn!==null;)if(a=Cn,e=a.child,(a.subtreeFlags&1028)!==0&&e!==null)e.return=a,Cn=e;else for(;Cn!==null;){switch(a=Cn,m=a.alternate,e=a.flags,a.tag){case 0:if((e&4)!==0&&(e=a.updateQueue,e=e!==null?e.events:null,e!==null))for(r=0;r<e.length;r++)f=e[r],f.ref.impl=f.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&m!==null){e=void 0,r=a,f=m.memoizedProps,m=m.memoizedState,l=r.stateNode;try{var Wt=Ks(r.type,f);e=l.getSnapshotBeforeUpdate(Wt,m),l.__reactInternalSnapshotBeforeUpdate=e}catch(te){Ie(r,r.return,te)}}break;case 3:if((e&1024)!==0){if(e=a.stateNode.containerInfo,r=e.nodeType,r===9)_h(e);else if(r===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":_h(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(s(163))}if(e=a.sibling,e!==null){e.return=a.return,Cn=e;break}Cn=a.return}}function Z_(e,a,r){var l=r.flags;switch(r.tag){case 0:case 11:case 15:Ra(e,r),l&4&&sl(5,r);break;case 1:if(Ra(e,r),l&4)if(e=r.stateNode,a===null)try{e.componentDidMount()}catch(M){Ie(r,r.return,M)}else{var f=Ks(r.type,a.memoizedProps);a=a.memoizedState;try{e.componentDidUpdate(f,a,e.__reactInternalSnapshotBeforeUpdate)}catch(M){Ie(r,r.return,M)}}l&64&&j_(r),l&512&&rl(r,r.return);break;case 3:if(Ra(e,r),l&64&&(e=r.updateQueue,e!==null)){if(a=null,r.child!==null)switch(r.child.tag){case 27:case 5:a=r.child.stateNode;break;case 1:a=r.child.stateNode}try{P0(e,a)}catch(M){Ie(r,r.return,M)}}break;case 27:a===null&&l&4&&Y_(r);case 26:case 5:Ra(e,r),a===null&&l&4&&W_(r),l&512&&rl(r,r.return);break;case 12:Ra(e,r);break;case 31:Ra(e,r),l&4&&$_(e,r);break;case 13:Ra(e,r),l&4&&tv(e,r),l&64&&(e=r.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(r=VT.bind(null,r),r1(e,r))));break;case 22:if(l=r.memoizedState!==null||Ta,!l){a=a!==null&&a.memoizedState!==null||vn,f=Ta;var m=vn;Ta=l,(vn=a)&&!m?Ca(e,r,(r.subtreeFlags&8772)!==0):Ra(e,r),Ta=f,vn=m}break;case 30:break;default:Ra(e,r)}}function Q_(e){var a=e.alternate;a!==null&&(e.alternate=null,Q_(a)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(a=e.stateNode,a!==null&&Po(a)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var nn=null,Qn=!1;function Aa(e,a,r){for(r=r.child;r!==null;)J_(e,a,r),r=r.sibling}function J_(e,a,r){if(ht&&typeof ht.onCommitFiberUnmount=="function")try{ht.onCommitFiberUnmount(ft,r)}catch{}switch(r.tag){case 26:vn||Ji(r,a),Aa(e,a,r),r.memoizedState?r.memoizedState.count--:r.stateNode&&(r=r.stateNode,r.parentNode.removeChild(r));break;case 27:vn||Ji(r,a);var l=nn,f=Qn;ps(r.type)&&(nn=r.stateNode,Qn=!1),Aa(e,a,r),ml(r.stateNode),nn=l,Qn=f;break;case 5:vn||Ji(r,a);case 6:if(l=nn,f=Qn,nn=null,Aa(e,a,r),nn=l,Qn=f,nn!==null)if(Qn)try{(nn.nodeType===9?nn.body:nn.nodeName==="HTML"?nn.ownerDocument.body:nn).removeChild(r.stateNode)}catch(m){Ie(r,a,m)}else try{nn.removeChild(r.stateNode)}catch(m){Ie(r,a,m)}break;case 18:nn!==null&&(Qn?(e=nn,jv(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,r.stateNode),Zr(e)):jv(nn,r.stateNode));break;case 4:l=nn,f=Qn,nn=r.stateNode.containerInfo,Qn=!0,Aa(e,a,r),nn=l,Qn=f;break;case 0:case 11:case 14:case 15:os(2,r,a),vn||os(4,r,a),Aa(e,a,r);break;case 1:vn||(Ji(r,a),l=r.stateNode,typeof l.componentWillUnmount=="function"&&X_(r,a,l)),Aa(e,a,r);break;case 21:Aa(e,a,r);break;case 22:vn=(l=vn)||r.memoizedState!==null,Aa(e,a,r),vn=l;break;default:Aa(e,a,r)}}function $_(e,a){if(a.memoizedState===null&&(e=a.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{Zr(e)}catch(r){Ie(a,a.return,r)}}}function tv(e,a){if(a.memoizedState===null&&(e=a.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Zr(e)}catch(r){Ie(a,a.return,r)}}function LT(e){switch(e.tag){case 31:case 13:case 19:var a=e.stateNode;return a===null&&(a=e.stateNode=new K_),a;case 22:return e=e.stateNode,a=e._retryCache,a===null&&(a=e._retryCache=new K_),a;default:throw Error(s(435,e.tag))}}function Bc(e,a){var r=LT(e);a.forEach(function(l){if(!r.has(l)){r.add(l);var f=HT.bind(null,e,l);l.then(f,f)}})}function Jn(e,a){var r=a.deletions;if(r!==null)for(var l=0;l<r.length;l++){var f=r[l],m=e,M=a,w=M;t:for(;w!==null;){switch(w.tag){case 27:if(ps(w.type)){nn=w.stateNode,Qn=!1;break t}break;case 5:nn=w.stateNode,Qn=!1;break t;case 3:case 4:nn=w.stateNode.containerInfo,Qn=!0;break t}w=w.return}if(nn===null)throw Error(s(160));J_(m,M,f),nn=null,Qn=!1,m=f.alternate,m!==null&&(m.return=null),f.return=null}if(a.subtreeFlags&13886)for(a=a.child;a!==null;)ev(a,e),a=a.sibling}var Bi=null;function ev(e,a){var r=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Jn(a,e),$n(e),l&4&&(os(3,e,e.return),sl(3,e),os(5,e,e.return));break;case 1:Jn(a,e),$n(e),l&512&&(vn||r===null||Ji(r,r.return)),l&64&&Ta&&(e=e.updateQueue,e!==null&&(l=e.callbacks,l!==null&&(r=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=r===null?l:r.concat(l))));break;case 26:var f=Bi;if(Jn(a,e),$n(e),l&512&&(vn||r===null||Ji(r,r.return)),l&4){var m=r!==null?r.memoizedState:null;if(l=e.memoizedState,r===null)if(l===null)if(e.stateNode===null){t:{l=e.type,r=e.memoizedProps,f=f.ownerDocument||f;e:switch(l){case"title":m=f.getElementsByTagName("title")[0],(!m||m[Wa]||m[un]||m.namespaceURI==="http://www.w3.org/2000/svg"||m.hasAttribute("itemprop"))&&(m=f.createElement(l),f.head.insertBefore(m,f.querySelector("head > title"))),On(m,l,r),m[un]=e,pn(m),l=m;break t;case"link":var M=ex("link","href",f).get(l+(r.href||""));if(M){for(var w=0;w<M.length;w++)if(m=M[w],m.getAttribute("href")===(r.href==null||r.href===""?null:r.href)&&m.getAttribute("rel")===(r.rel==null?null:r.rel)&&m.getAttribute("title")===(r.title==null?null:r.title)&&m.getAttribute("crossorigin")===(r.crossOrigin==null?null:r.crossOrigin)){M.splice(w,1);break e}}m=f.createElement(l),On(m,l,r),f.head.appendChild(m);break;case"meta":if(M=ex("meta","content",f).get(l+(r.content||""))){for(w=0;w<M.length;w++)if(m=M[w],m.getAttribute("content")===(r.content==null?null:""+r.content)&&m.getAttribute("name")===(r.name==null?null:r.name)&&m.getAttribute("property")===(r.property==null?null:r.property)&&m.getAttribute("http-equiv")===(r.httpEquiv==null?null:r.httpEquiv)&&m.getAttribute("charset")===(r.charSet==null?null:r.charSet)){M.splice(w,1);break e}}m=f.createElement(l),On(m,l,r),f.head.appendChild(m);break;default:throw Error(s(468,l))}m[un]=e,pn(m),l=m}e.stateNode=l}else nx(f,e.type,e.stateNode);else e.stateNode=tx(f,l,e.memoizedProps);else m!==l?(m===null?r.stateNode!==null&&(r=r.stateNode,r.parentNode.removeChild(r)):m.count--,l===null?nx(f,e.type,e.stateNode):tx(f,l,e.memoizedProps)):l===null&&e.stateNode!==null&&kd(e,e.memoizedProps,r.memoizedProps)}break;case 27:Jn(a,e),$n(e),l&512&&(vn||r===null||Ji(r,r.return)),r!==null&&l&4&&kd(e,e.memoizedProps,r.memoizedProps);break;case 5:if(Jn(a,e),$n(e),l&512&&(vn||r===null||Ji(r,r.return)),e.flags&32){f=e.stateNode;try{oi(f,"")}catch(Wt){Ie(e,e.return,Wt)}}l&4&&e.stateNode!=null&&(f=e.memoizedProps,kd(e,f,r!==null?r.memoizedProps:f)),l&1024&&(Wd=!0);break;case 6:if(Jn(a,e),$n(e),l&4){if(e.stateNode===null)throw Error(s(162));l=e.memoizedProps,r=e.stateNode;try{r.nodeValue=l}catch(Wt){Ie(e,e.return,Wt)}}break;case 3:if($c=null,f=Bi,Bi=Qc(a.containerInfo),Jn(a,e),Bi=f,$n(e),l&4&&r!==null&&r.memoizedState.isDehydrated)try{Zr(a.containerInfo)}catch(Wt){Ie(e,e.return,Wt)}Wd&&(Wd=!1,nv(e));break;case 4:l=Bi,Bi=Qc(e.stateNode.containerInfo),Jn(a,e),$n(e),Bi=l;break;case 12:Jn(a,e),$n(e);break;case 31:Jn(a,e),$n(e),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,Bc(e,l)));break;case 13:Jn(a,e),$n(e),e.child.flags&8192&&e.memoizedState!==null!=(r!==null&&r.memoizedState!==null)&&(zc=Ct()),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,Bc(e,l)));break;case 22:f=e.memoizedState!==null;var k=r!==null&&r.memoizedState!==null,et=Ta,pt=vn;if(Ta=et||f,vn=pt||k,Jn(a,e),vn=pt,Ta=et,$n(e),l&8192)t:for(a=e.stateNode,a._visibility=f?a._visibility&-2:a._visibility|1,f&&(r===null||k||Ta||vn||Zs(e)),r=null,a=e;;){if(a.tag===5||a.tag===26){if(r===null){k=r=a;try{if(m=k.stateNode,f)M=m.style,typeof M.setProperty=="function"?M.setProperty("display","none","important"):M.display="none";else{w=k.stateNode;var vt=k.memoizedProps.style,st=vt!=null&&vt.hasOwnProperty("display")?vt.display:null;w.style.display=st==null||typeof st=="boolean"?"":(""+st).trim()}}catch(Wt){Ie(k,k.return,Wt)}}}else if(a.tag===6){if(r===null){k=a;try{k.stateNode.nodeValue=f?"":k.memoizedProps}catch(Wt){Ie(k,k.return,Wt)}}}else if(a.tag===18){if(r===null){k=a;try{var ut=k.stateNode;f?Xv(ut,!0):Xv(k.stateNode,!1)}catch(Wt){Ie(k,k.return,Wt)}}}else if((a.tag!==22&&a.tag!==23||a.memoizedState===null||a===e)&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===e)break t;for(;a.sibling===null;){if(a.return===null||a.return===e)break t;r===a&&(r=null),a=a.return}r===a&&(r=null),a.sibling.return=a.return,a=a.sibling}l&4&&(l=e.updateQueue,l!==null&&(r=l.retryQueue,r!==null&&(l.retryQueue=null,Bc(e,r))));break;case 19:Jn(a,e),$n(e),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,Bc(e,l)));break;case 30:break;case 21:break;default:Jn(a,e),$n(e)}}function $n(e){var a=e.flags;if(a&2){try{for(var r,l=e.return;l!==null;){if(q_(l)){r=l;break}l=l.return}if(r==null)throw Error(s(160));switch(r.tag){case 27:var f=r.stateNode,m=jd(e);Fc(e,m,f);break;case 5:var M=r.stateNode;r.flags&32&&(oi(M,""),r.flags&=-33);var w=jd(e);Fc(e,w,M);break;case 3:case 4:var k=r.stateNode.containerInfo,et=jd(e);Xd(e,et,k);break;default:throw Error(s(161))}}catch(pt){Ie(e,e.return,pt)}e.flags&=-3}a&4096&&(e.flags&=-4097)}function nv(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var a=e;nv(a),a.tag===5&&a.flags&1024&&a.stateNode.reset(),e=e.sibling}}function Ra(e,a){if(a.subtreeFlags&8772)for(a=a.child;a!==null;)Z_(e,a.alternate,a),a=a.sibling}function Zs(e){for(e=e.child;e!==null;){var a=e;switch(a.tag){case 0:case 11:case 14:case 15:os(4,a,a.return),Zs(a);break;case 1:Ji(a,a.return);var r=a.stateNode;typeof r.componentWillUnmount=="function"&&X_(a,a.return,r),Zs(a);break;case 27:ml(a.stateNode);case 26:case 5:Ji(a,a.return),Zs(a);break;case 22:a.memoizedState===null&&Zs(a);break;case 30:Zs(a);break;default:Zs(a)}e=e.sibling}}function Ca(e,a,r){for(r=r&&(a.subtreeFlags&8772)!==0,a=a.child;a!==null;){var l=a.alternate,f=e,m=a,M=m.flags;switch(m.tag){case 0:case 11:case 15:Ca(f,m,r),sl(4,m);break;case 1:if(Ca(f,m,r),l=m,f=l.stateNode,typeof f.componentDidMount=="function")try{f.componentDidMount()}catch(et){Ie(l,l.return,et)}if(l=m,f=l.updateQueue,f!==null){var w=l.stateNode;try{var k=f.shared.hiddenCallbacks;if(k!==null)for(f.shared.hiddenCallbacks=null,f=0;f<k.length;f++)U0(k[f],w)}catch(et){Ie(l,l.return,et)}}r&&M&64&&j_(m),rl(m,m.return);break;case 27:Y_(m);case 26:case 5:Ca(f,m,r),r&&l===null&&M&4&&W_(m),rl(m,m.return);break;case 12:Ca(f,m,r);break;case 31:Ca(f,m,r),r&&M&4&&$_(f,m);break;case 13:Ca(f,m,r),r&&M&4&&tv(f,m);break;case 22:m.memoizedState===null&&Ca(f,m,r),rl(m,m.return);break;case 30:break;default:Ca(f,m,r)}a=a.sibling}}function qd(e,a){var r=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),e=null,a.memoizedState!==null&&a.memoizedState.cachePool!==null&&(e=a.memoizedState.cachePool.pool),e!==r&&(e!=null&&e.refCount++,r!=null&&Wo(r))}function Yd(e,a){e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&Wo(e))}function Ii(e,a,r,l){if(a.subtreeFlags&10256)for(a=a.child;a!==null;)iv(e,a,r,l),a=a.sibling}function iv(e,a,r,l){var f=a.flags;switch(a.tag){case 0:case 11:case 15:Ii(e,a,r,l),f&2048&&sl(9,a);break;case 1:Ii(e,a,r,l);break;case 3:Ii(e,a,r,l),f&2048&&(e=null,a.alternate!==null&&(e=a.alternate.memoizedState.cache),a=a.memoizedState.cache,a!==e&&(a.refCount++,e!=null&&Wo(e)));break;case 12:if(f&2048){Ii(e,a,r,l),e=a.stateNode;try{var m=a.memoizedProps,M=m.id,w=m.onPostCommit;typeof w=="function"&&w(M,a.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(k){Ie(a,a.return,k)}}else Ii(e,a,r,l);break;case 31:Ii(e,a,r,l);break;case 13:Ii(e,a,r,l);break;case 23:break;case 22:m=a.stateNode,M=a.alternate,a.memoizedState!==null?m._visibility&2?Ii(e,a,r,l):ol(e,a):m._visibility&2?Ii(e,a,r,l):(m._visibility|=2,zr(e,a,r,l,(a.subtreeFlags&10256)!==0||!1)),f&2048&&qd(M,a);break;case 24:Ii(e,a,r,l),f&2048&&Yd(a.alternate,a);break;default:Ii(e,a,r,l)}}function zr(e,a,r,l,f){for(f=f&&((a.subtreeFlags&10256)!==0||!1),a=a.child;a!==null;){var m=e,M=a,w=r,k=l,et=M.flags;switch(M.tag){case 0:case 11:case 15:zr(m,M,w,k,f),sl(8,M);break;case 23:break;case 22:var pt=M.stateNode;M.memoizedState!==null?pt._visibility&2?zr(m,M,w,k,f):ol(m,M):(pt._visibility|=2,zr(m,M,w,k,f)),f&&et&2048&&qd(M.alternate,M);break;case 24:zr(m,M,w,k,f),f&&et&2048&&Yd(M.alternate,M);break;default:zr(m,M,w,k,f)}a=a.sibling}}function ol(e,a){if(a.subtreeFlags&10256)for(a=a.child;a!==null;){var r=e,l=a,f=l.flags;switch(l.tag){case 22:ol(r,l),f&2048&&qd(l.alternate,l);break;case 24:ol(r,l),f&2048&&Yd(l.alternate,l);break;default:ol(r,l)}a=a.sibling}}var ll=8192;function Vr(e,a,r){if(e.subtreeFlags&ll)for(e=e.child;e!==null;)av(e,a,r),e=e.sibling}function av(e,a,r){switch(e.tag){case 26:Vr(e,a,r),e.flags&ll&&e.memoizedState!==null&&v1(r,Bi,e.memoizedState,e.memoizedProps);break;case 5:Vr(e,a,r);break;case 3:case 4:var l=Bi;Bi=Qc(e.stateNode.containerInfo),Vr(e,a,r),Bi=l;break;case 22:e.memoizedState===null&&(l=e.alternate,l!==null&&l.memoizedState!==null?(l=ll,ll=16777216,Vr(e,a,r),ll=l):Vr(e,a,r));break;default:Vr(e,a,r)}}function sv(e){var a=e.alternate;if(a!==null&&(e=a.child,e!==null)){a.child=null;do a=e.sibling,e.sibling=null,e=a;while(e!==null)}}function cl(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var r=0;r<a.length;r++){var l=a[r];Cn=l,ov(l,e)}sv(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)rv(e),e=e.sibling}function rv(e){switch(e.tag){case 0:case 11:case 15:cl(e),e.flags&2048&&os(9,e,e.return);break;case 3:cl(e);break;case 12:cl(e);break;case 22:var a=e.stateNode;e.memoizedState!==null&&a._visibility&2&&(e.return===null||e.return.tag!==13)?(a._visibility&=-3,Ic(e)):cl(e);break;default:cl(e)}}function Ic(e){var a=e.deletions;if((e.flags&16)!==0){if(a!==null)for(var r=0;r<a.length;r++){var l=a[r];Cn=l,ov(l,e)}sv(e)}for(e=e.child;e!==null;){switch(a=e,a.tag){case 0:case 11:case 15:os(8,a,a.return),Ic(a);break;case 22:r=a.stateNode,r._visibility&2&&(r._visibility&=-3,Ic(a));break;default:Ic(a)}e=e.sibling}}function ov(e,a){for(;Cn!==null;){var r=Cn;switch(r.tag){case 0:case 11:case 15:os(8,r,a);break;case 23:case 22:if(r.memoizedState!==null&&r.memoizedState.cachePool!==null){var l=r.memoizedState.cachePool.pool;l!=null&&l.refCount++}break;case 24:Wo(r.memoizedState.cache)}if(l=r.child,l!==null)l.return=r,Cn=l;else t:for(r=e;Cn!==null;){l=Cn;var f=l.sibling,m=l.return;if(Q_(l),l===r){Cn=null;break t}if(f!==null){f.return=m,Cn=f;break t}Cn=m}}}var UT={getCacheForType:function(e){var a=Un(mn),r=a.data.get(e);return r===void 0&&(r=e(),a.data.set(e,r)),r},cacheSignal:function(){return Un(mn).controller.signal}},PT=typeof WeakMap=="function"?WeakMap:Map,De=0,qe=null,_e=null,ye=0,Be=0,di=null,ls=!1,Hr=!1,Kd=!1,wa=0,on=0,cs=0,Qs=0,Zd=0,hi=0,Gr=0,ul=null,ti=null,Qd=!1,zc=0,lv=0,Vc=1/0,Hc=null,us=null,En=0,fs=null,kr=null,Da=0,Jd=0,$d=null,cv=null,fl=0,th=null;function pi(){return(De&2)!==0&&ye!==0?ye&-ye:I.T!==null?rh():No()}function uv(){if(hi===0)if((ye&536870912)===0||Me){var e=me;me<<=1,(me&3932160)===0&&(me=262144),hi=e}else hi=536870912;return e=ui.current,e!==null&&(e.flags|=32),hi}function ei(e,a,r){(e===qe&&(Be===2||Be===9)||e.cancelPendingCommit!==null)&&(jr(e,0),ds(e,ye,hi,!1)),ne(e,r),((De&2)===0||e!==qe)&&(e===qe&&((De&2)===0&&(Qs|=r),on===4&&ds(e,ye,hi,!1)),$i(e))}function fv(e,a,r){if((De&6)!==0)throw Error(s(327));var l=!r&&(a&127)===0&&(a&e.expiredLanes)===0||zt(e,a),f=l?BT(e,a):nh(e,a,!0),m=l;do{if(f===0){Hr&&!l&&ds(e,a,0,!1);break}else{if(r=e.current.alternate,m&&!OT(r)){f=nh(e,a,!1),m=!1;continue}if(f===2){if(m=a,e.errorRecoveryDisabledLanes&m)var M=0;else M=e.pendingLanes&-536870913,M=M!==0?M:M&536870912?536870912:0;if(M!==0){a=M;t:{var w=e;f=ul;var k=w.current.memoizedState.isDehydrated;if(k&&(jr(w,M).flags|=256),M=nh(w,M,!1),M!==2){if(Kd&&!k){w.errorRecoveryDisabledLanes|=m,Qs|=m,f=4;break t}m=ti,ti=f,m!==null&&(ti===null?ti=m:ti.push.apply(ti,m))}f=M}if(m=!1,f!==2)continue}}if(f===1){jr(e,0),ds(e,a,0,!0);break}t:{switch(l=e,m=f,m){case 0:case 1:throw Error(s(345));case 4:if((a&4194048)!==a)break;case 6:ds(l,a,hi,!ls);break t;case 2:ti=null;break;case 3:case 5:break;default:throw Error(s(329))}if((a&62914560)===a&&(f=zc+300-Ct(),10<f)){if(ds(l,a,hi,!ls),mt(l,0,!0)!==0)break t;Da=a,l.timeoutHandle=Gv(dv.bind(null,l,r,ti,Hc,Qd,a,hi,Qs,Gr,ls,m,"Throttled",-0,0),f);break t}dv(l,r,ti,Hc,Qd,a,hi,Qs,Gr,ls,m,null,-0,0)}}break}while(!0);$i(e)}function dv(e,a,r,l,f,m,M,w,k,et,pt,vt,st,ut){if(e.timeoutHandle=-1,vt=a.subtreeFlags,vt&8192||(vt&16785408)===16785408){vt={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:ma},av(a,m,vt);var Wt=(m&62914560)===m?zc-Ct():(m&4194048)===m?lv-Ct():0;if(Wt=x1(vt,Wt),Wt!==null){Da=m,e.cancelPendingCommit=Wt(yv.bind(null,e,a,m,r,l,f,M,w,k,pt,vt,null,st,ut)),ds(e,m,M,!et);return}}yv(e,a,m,r,l,f,M,w,k)}function OT(e){for(var a=e;;){var r=a.tag;if((r===0||r===11||r===15)&&a.flags&16384&&(r=a.updateQueue,r!==null&&(r=r.stores,r!==null)))for(var l=0;l<r.length;l++){var f=r[l],m=f.getSnapshot;f=f.value;try{if(!li(m(),f))return!1}catch{return!1}}if(r=a.child,a.subtreeFlags&16384&&r!==null)r.return=a,a=r;else{if(a===e)break;for(;a.sibling===null;){if(a.return===null||a.return===e)return!0;a=a.return}a.sibling.return=a.return,a=a.sibling}}return!0}function ds(e,a,r,l){a&=~Zd,a&=~Qs,e.suspendedLanes|=a,e.pingedLanes&=~a,l&&(e.warmLanes|=a),l=e.expirationTimes;for(var f=a;0<f;){var m=31-Ft(f),M=1<<m;l[m]=-1,f&=~M}r!==0&&we(e,r,a)}function Gc(){return(De&6)===0?(dl(0),!1):!0}function eh(){if(_e!==null){if(Be===0)var e=_e.return;else e=_e,xa=Gs=null,_d(e),Pr=null,Yo=0,e=_e;for(;e!==null;)k_(e.alternate,e),e=e.return;_e=null}}function jr(e,a){var r=e.timeoutHandle;r!==-1&&(e.timeoutHandle=-1,e1(r)),r=e.cancelPendingCommit,r!==null&&(e.cancelPendingCommit=null,r()),Da=0,eh(),qe=e,_e=r=_a(e.current,null),ye=a,Be=0,di=null,ls=!1,Hr=zt(e,a),Kd=!1,Gr=hi=Zd=Qs=cs=on=0,ti=ul=null,Qd=!1,(a&8)!==0&&(a|=a&32);var l=e.entangledLanes;if(l!==0)for(e=e.entanglements,l&=a;0<l;){var f=31-Ft(l),m=1<<f;a|=e[f],l&=~m}return wa=a,cc(),r}function hv(e,a){ce=null,I.H=nl,a===Ur||a===_c?(a=w0(),Be=3):a===sd?(a=w0(),Be=4):Be=a===Ud?8:a!==null&&typeof a=="object"&&typeof a.then=="function"?6:1,di=a,_e===null&&(on=1,Nc(e,Si(a,e.current)))}function pv(){var e=ui.current;return e===null?!0:(ye&4194048)===ye?Ti===null:(ye&62914560)===ye||(ye&536870912)!==0?e===Ti:!1}function mv(){var e=I.H;return I.H=nl,e===null?nl:e}function gv(){var e=I.A;return I.A=UT,e}function kc(){on=4,ls||(ye&4194048)!==ye&&ui.current!==null||(Hr=!0),(cs&134217727)===0&&(Qs&134217727)===0||qe===null||ds(qe,ye,hi,!1)}function nh(e,a,r){var l=De;De|=2;var f=mv(),m=gv();(qe!==e||ye!==a)&&(Hc=null,jr(e,a)),a=!1;var M=on;t:do try{if(Be!==0&&_e!==null){var w=_e,k=di;switch(Be){case 8:eh(),M=6;break t;case 3:case 2:case 9:case 6:ui.current===null&&(a=!0);var et=Be;if(Be=0,di=null,Xr(e,w,k,et),r&&Hr){M=0;break t}break;default:et=Be,Be=0,di=null,Xr(e,w,k,et)}}FT(),M=on;break}catch(pt){hv(e,pt)}while(!0);return a&&e.shellSuspendCounter++,xa=Gs=null,De=l,I.H=f,I.A=m,_e===null&&(qe=null,ye=0,cc()),M}function FT(){for(;_e!==null;)_v(_e)}function BT(e,a){var r=De;De|=2;var l=mv(),f=gv();qe!==e||ye!==a?(Hc=null,Vc=Ct()+500,jr(e,a)):Hr=zt(e,a);t:do try{if(Be!==0&&_e!==null){a=_e;var m=di;e:switch(Be){case 1:Be=0,di=null,Xr(e,a,m,1);break;case 2:case 9:if(R0(m)){Be=0,di=null,vv(a);break}a=function(){Be!==2&&Be!==9||qe!==e||(Be=7),$i(e)},m.then(a,a);break t;case 3:Be=7;break t;case 4:Be=5;break t;case 7:R0(m)?(Be=0,di=null,vv(a)):(Be=0,di=null,Xr(e,a,m,7));break;case 5:var M=null;switch(_e.tag){case 26:M=_e.memoizedState;case 5:case 27:var w=_e;if(M?ix(M):w.stateNode.complete){Be=0,di=null;var k=w.sibling;if(k!==null)_e=k;else{var et=w.return;et!==null?(_e=et,jc(et)):_e=null}break e}}Be=0,di=null,Xr(e,a,m,5);break;case 6:Be=0,di=null,Xr(e,a,m,6);break;case 8:eh(),on=6;break t;default:throw Error(s(462))}}IT();break}catch(pt){hv(e,pt)}while(!0);return xa=Gs=null,I.H=l,I.A=f,De=r,_e!==null?0:(qe=null,ye=0,cc(),on)}function IT(){for(;_e!==null&&!pe();)_v(_e)}function _v(e){var a=H_(e.alternate,e,wa);e.memoizedProps=e.pendingProps,a===null?jc(e):_e=a}function vv(e){var a=e,r=a.alternate;switch(a.tag){case 15:case 0:a=O_(r,a,a.pendingProps,a.type,void 0,ye);break;case 11:a=O_(r,a,a.pendingProps,a.type.render,a.ref,ye);break;case 5:_d(a);default:k_(r,a),a=_e=g0(a,wa),a=H_(r,a,wa)}e.memoizedProps=e.pendingProps,a===null?jc(e):_e=a}function Xr(e,a,r,l){xa=Gs=null,_d(a),Pr=null,Yo=0;var f=a.return;try{if(AT(e,f,a,r,ye)){on=1,Nc(e,Si(r,e.current)),_e=null;return}}catch(m){if(f!==null)throw _e=f,m;on=1,Nc(e,Si(r,e.current)),_e=null;return}a.flags&32768?(Me||l===1?e=!0:Hr||(ye&536870912)!==0?e=!1:(ls=e=!0,(l===2||l===9||l===3||l===6)&&(l=ui.current,l!==null&&l.tag===13&&(l.flags|=16384))),xv(a,e)):jc(a)}function jc(e){var a=e;do{if((a.flags&32768)!==0){xv(a,ls);return}e=a.return;var r=wT(a.alternate,a,wa);if(r!==null){_e=r;return}if(a=a.sibling,a!==null){_e=a;return}_e=a=e}while(a!==null);on===0&&(on=5)}function xv(e,a){do{var r=DT(e.alternate,e);if(r!==null){r.flags&=32767,_e=r;return}if(r=e.return,r!==null&&(r.flags|=32768,r.subtreeFlags=0,r.deletions=null),!a&&(e=e.sibling,e!==null)){_e=e;return}_e=e=r}while(e!==null);on=6,_e=null}function yv(e,a,r,l,f,m,M,w,k){e.cancelPendingCommit=null;do Xc();while(En!==0);if((De&6)!==0)throw Error(s(327));if(a!==null){if(a===e.current)throw Error(s(177));if(m=a.lanes|a.childLanes,m|=jf,sn(e,r,m,M,w,k),e===qe&&(_e=qe=null,ye=0),kr=a,fs=e,Da=r,Jd=m,$d=f,cv=l,(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,GT(J,function(){return Tv(),null})):(e.callbackNode=null,e.callbackPriority=0),l=(a.flags&13878)!==0,(a.subtreeFlags&13878)!==0||l){l=I.T,I.T=null,f=G.p,G.p=2,M=De,De|=4;try{NT(e,a,r)}finally{De=M,G.p=f,I.T=l}}En=1,Sv(),Mv(),bv()}}function Sv(){if(En===1){En=0;var e=fs,a=kr,r=(a.flags&13878)!==0;if((a.subtreeFlags&13878)!==0||r){r=I.T,I.T=null;var l=G.p;G.p=2;var f=De;De|=4;try{ev(a,e);var m=ph,M=o0(e.containerInfo),w=m.focusedElem,k=m.selectionRange;if(M!==w&&w&&w.ownerDocument&&r0(w.ownerDocument.documentElement,w)){if(k!==null&&zf(w)){var et=k.start,pt=k.end;if(pt===void 0&&(pt=et),"selectionStart"in w)w.selectionStart=et,w.selectionEnd=Math.min(pt,w.value.length);else{var vt=w.ownerDocument||document,st=vt&&vt.defaultView||window;if(st.getSelection){var ut=st.getSelection(),Wt=w.textContent.length,te=Math.min(k.start,Wt),ke=k.end===void 0?te:Math.min(k.end,Wt);!ut.extend&&te>ke&&(M=ke,ke=te,te=M);var Z=s0(w,te),W=s0(w,ke);if(Z&&W&&(ut.rangeCount!==1||ut.anchorNode!==Z.node||ut.anchorOffset!==Z.offset||ut.focusNode!==W.node||ut.focusOffset!==W.offset)){var tt=vt.createRange();tt.setStart(Z.node,Z.offset),ut.removeAllRanges(),te>ke?(ut.addRange(tt),ut.extend(W.node,W.offset)):(tt.setEnd(W.node,W.offset),ut.addRange(tt))}}}}for(vt=[],ut=w;ut=ut.parentNode;)ut.nodeType===1&&vt.push({element:ut,left:ut.scrollLeft,top:ut.scrollTop});for(typeof w.focus=="function"&&w.focus(),w=0;w<vt.length;w++){var gt=vt[w];gt.element.scrollLeft=gt.left,gt.element.scrollTop=gt.top}}iu=!!hh,ph=hh=null}finally{De=f,G.p=l,I.T=r}}e.current=a,En=2}}function Mv(){if(En===2){En=0;var e=fs,a=kr,r=(a.flags&8772)!==0;if((a.subtreeFlags&8772)!==0||r){r=I.T,I.T=null;var l=G.p;G.p=2;var f=De;De|=4;try{Z_(e,a.alternate,a)}finally{De=f,G.p=l,I.T=r}}En=3}}function bv(){if(En===4||En===3){En=0,Ve();var e=fs,a=kr,r=Da,l=cv;(a.subtreeFlags&10256)!==0||(a.flags&10256)!==0?En=5:(En=0,kr=fs=null,Ev(e,e.pendingLanes));var f=e.pendingLanes;if(f===0&&(us=null),Do(r),a=a.stateNode,ht&&typeof ht.onCommitFiberRoot=="function")try{ht.onCommitFiberRoot(ft,a,void 0,(a.current.flags&128)===128)}catch{}if(l!==null){a=I.T,f=G.p,G.p=2,I.T=null;try{for(var m=e.onRecoverableError,M=0;M<l.length;M++){var w=l[M];m(w.value,{componentStack:w.stack})}}finally{I.T=a,G.p=f}}(Da&3)!==0&&Xc(),$i(e),f=e.pendingLanes,(r&261930)!==0&&(f&42)!==0?e===th?fl++:(fl=0,th=e):fl=0,dl(0)}}function Ev(e,a){(e.pooledCacheLanes&=a)===0&&(a=e.pooledCache,a!=null&&(e.pooledCache=null,Wo(a)))}function Xc(){return Sv(),Mv(),bv(),Tv()}function Tv(){if(En!==5)return!1;var e=fs,a=Jd;Jd=0;var r=Do(Da),l=I.T,f=G.p;try{G.p=32>r?32:r,I.T=null,r=$d,$d=null;var m=fs,M=Da;if(En=0,kr=fs=null,Da=0,(De&6)!==0)throw Error(s(331));var w=De;if(De|=4,rv(m.current),iv(m,m.current,M,r),De=w,dl(0,!1),ht&&typeof ht.onPostCommitFiberRoot=="function")try{ht.onPostCommitFiberRoot(ft,m)}catch{}return!0}finally{G.p=f,I.T=l,Ev(e,a)}}function Av(e,a,r){a=Si(r,a),a=Ld(e.stateNode,a,2),e=as(e,a,2),e!==null&&(ne(e,2),$i(e))}function Ie(e,a,r){if(e.tag===3)Av(e,e,r);else for(;a!==null;){if(a.tag===3){Av(a,e,r);break}else if(a.tag===1){var l=a.stateNode;if(typeof a.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&(us===null||!us.has(l))){e=Si(r,e),r=R_(2),l=as(a,r,2),l!==null&&(C_(r,l,a,e),ne(l,2),$i(l));break}}a=a.return}}function ih(e,a,r){var l=e.pingCache;if(l===null){l=e.pingCache=new PT;var f=new Set;l.set(a,f)}else f=l.get(a),f===void 0&&(f=new Set,l.set(a,f));f.has(r)||(Kd=!0,f.add(r),e=zT.bind(null,e,a,r),a.then(e,e))}function zT(e,a,r){var l=e.pingCache;l!==null&&l.delete(a),e.pingedLanes|=e.suspendedLanes&r,e.warmLanes&=~r,qe===e&&(ye&r)===r&&(on===4||on===3&&(ye&62914560)===ye&&300>Ct()-zc?(De&2)===0&&jr(e,0):Zd|=r,Gr===ye&&(Gr=0)),$i(e)}function Rv(e,a){a===0&&(a=bt()),e=zs(e,a),e!==null&&(ne(e,a),$i(e))}function VT(e){var a=e.memoizedState,r=0;a!==null&&(r=a.retryLane),Rv(e,r)}function HT(e,a){var r=0;switch(e.tag){case 31:case 13:var l=e.stateNode,f=e.memoizedState;f!==null&&(r=f.retryLane);break;case 19:l=e.stateNode;break;case 22:l=e.stateNode._retryCache;break;default:throw Error(s(314))}l!==null&&l.delete(a),Rv(e,r)}function GT(e,a){return Y(e,a)}var Wc=null,Wr=null,ah=!1,qc=!1,sh=!1,hs=0;function $i(e){e!==Wr&&e.next===null&&(Wr===null?Wc=Wr=e:Wr=Wr.next=e),qc=!0,ah||(ah=!0,jT())}function dl(e,a){if(!sh&&qc){sh=!0;do for(var r=!1,l=Wc;l!==null;){if(e!==0){var f=l.pendingLanes;if(f===0)var m=0;else{var M=l.suspendedLanes,w=l.pingedLanes;m=(1<<31-Ft(42|e)+1)-1,m&=f&~(M&~w),m=m&201326741?m&201326741|1:m?m|2:0}m!==0&&(r=!0,Nv(l,m))}else m=ye,m=mt(l,l===qe?m:0,l.cancelPendingCommit!==null||l.timeoutHandle!==-1),(m&3)===0||zt(l,m)||(r=!0,Nv(l,m));l=l.next}while(r);sh=!1}}function kT(){Cv()}function Cv(){qc=ah=!1;var e=0;hs!==0&&t1()&&(e=hs);for(var a=Ct(),r=null,l=Wc;l!==null;){var f=l.next,m=wv(l,a);m===0?(l.next=null,r===null?Wc=f:r.next=f,f===null&&(Wr=r)):(r=l,(e!==0||(m&3)!==0)&&(qc=!0)),l=f}En!==0&&En!==5||dl(e),hs!==0&&(hs=0)}function wv(e,a){for(var r=e.suspendedLanes,l=e.pingedLanes,f=e.expirationTimes,m=e.pendingLanes&-62914561;0<m;){var M=31-Ft(m),w=1<<M,k=f[M];k===-1?((w&r)===0||(w&l)!==0)&&(f[M]=Ut(w,a)):k<=a&&(e.expiredLanes|=w),m&=~w}if(a=qe,r=ye,r=mt(e,e===a?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),l=e.callbackNode,r===0||e===a&&(Be===2||Be===9)||e.cancelPendingCommit!==null)return l!==null&&l!==null&&an(l),e.callbackNode=null,e.callbackPriority=0;if((r&3)===0||zt(e,r)){if(a=r&-r,a===e.callbackPriority)return a;switch(l!==null&&an(l),Do(r)){case 2:case 8:r=T;break;case 32:r=J;break;case 268435456:r=Et;break;default:r=J}return l=Dv.bind(null,e),r=Y(r,l),e.callbackPriority=a,e.callbackNode=r,a}return l!==null&&l!==null&&an(l),e.callbackPriority=2,e.callbackNode=null,2}function Dv(e,a){if(En!==0&&En!==5)return e.callbackNode=null,e.callbackPriority=0,null;var r=e.callbackNode;if(Xc()&&e.callbackNode!==r)return null;var l=ye;return l=mt(e,e===qe?l:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),l===0?null:(fv(e,l,a),wv(e,Ct()),e.callbackNode!=null&&e.callbackNode===r?Dv.bind(null,e):null)}function Nv(e,a){if(Xc())return null;fv(e,a,!0)}function jT(){n1(function(){(De&6)!==0?Y(P,kT):Cv()})}function rh(){if(hs===0){var e=Nr;e===0&&(e=se,se<<=1,(se&261888)===0&&(se=256)),hs=e}return hs}function Lv(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:Os(""+e)}function Uv(e,a){var r=a.ownerDocument.createElement("input");return r.name=a.name,r.value=a.value,e.id&&r.setAttribute("form",e.id),a.parentNode.insertBefore(r,a),e=new FormData(e),r.parentNode.removeChild(r),e}function XT(e,a,r,l,f){if(a==="submit"&&r&&r.stateNode===f){var m=Lv((f[Nn]||null).action),M=l.submitter;M&&(a=(a=M[Nn]||null)?Lv(a.formAction):M.getAttribute("formAction"),a!==null&&(m=a,M=null));var w=new sc("action","action",null,l,f);e.push({event:w,listeners:[{instance:null,listener:function(){if(l.defaultPrevented){if(hs!==0){var k=M?Uv(f,M):new FormData(f);Ad(r,{pending:!0,data:k,method:f.method,action:m},null,k)}}else typeof m=="function"&&(w.preventDefault(),k=M?Uv(f,M):new FormData(f),Ad(r,{pending:!0,data:k,method:f.method,action:m},m,k))},currentTarget:f}]})}}for(var oh=0;oh<kf.length;oh++){var lh=kf[oh],WT=lh.toLowerCase(),qT=lh[0].toUpperCase()+lh.slice(1);Fi(WT,"on"+qT)}Fi(u0,"onAnimationEnd"),Fi(f0,"onAnimationIteration"),Fi(d0,"onAnimationStart"),Fi("dblclick","onDoubleClick"),Fi("focusin","onFocus"),Fi("focusout","onBlur"),Fi(cT,"onTransitionRun"),Fi(uT,"onTransitionStart"),Fi(fT,"onTransitionCancel"),Fi(h0,"onTransitionEnd"),at("onMouseEnter",["mouseout","mouseover"]),at("onMouseLeave",["mouseout","mouseover"]),at("onPointerEnter",["pointerout","pointerover"]),at("onPointerLeave",["pointerout","pointerover"]),K("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),K("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),K("onBeforeInput",["compositionend","keypress","textInput","paste"]),K("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),K("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),K("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var hl="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),YT=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(hl));function Pv(e,a){a=(a&4)!==0;for(var r=0;r<e.length;r++){var l=e[r],f=l.event;l=l.listeners;t:{var m=void 0;if(a)for(var M=l.length-1;0<=M;M--){var w=l[M],k=w.instance,et=w.currentTarget;if(w=w.listener,k!==m&&f.isPropagationStopped())break t;m=w,f.currentTarget=et;try{m(f)}catch(pt){lc(pt)}f.currentTarget=null,m=k}else for(M=0;M<l.length;M++){if(w=l[M],k=w.instance,et=w.currentTarget,w=w.listener,k!==m&&f.isPropagationStopped())break t;m=w,f.currentTarget=et;try{m(f)}catch(pt){lc(pt)}f.currentTarget=null,m=k}}}}function ve(e,a){var r=a[Xa];r===void 0&&(r=a[Xa]=new Set);var l=e+"__bubble";r.has(l)||(Ov(a,e,2,!1),r.add(l))}function ch(e,a,r){var l=0;a&&(l|=4),Ov(r,e,l,a)}var Yc="_reactListening"+Math.random().toString(36).slice(2);function uh(e){if(!e[Yc]){e[Yc]=!0,ec.forEach(function(r){r!=="selectionchange"&&(YT.has(r)||ch(r,!1,e),ch(r,!0,e))});var a=e.nodeType===9?e:e.ownerDocument;a===null||a[Yc]||(a[Yc]=!0,ch("selectionchange",!1,a))}}function Ov(e,a,r,l){switch(ux(a)){case 2:var f=M1;break;case 8:f=b1;break;default:f=Th}r=f.bind(null,a,r,e),f=void 0,!Df||a!=="touchstart"&&a!=="touchmove"&&a!=="wheel"||(f=!0),l?f!==void 0?e.addEventListener(a,r,{capture:!0,passive:f}):e.addEventListener(a,r,!0):f!==void 0?e.addEventListener(a,r,{passive:f}):e.addEventListener(a,r,!1)}function fh(e,a,r,l,f){var m=l;if((a&1)===0&&(a&2)===0&&l!==null)t:for(;;){if(l===null)return;var M=l.tag;if(M===3||M===4){var w=l.stateNode.containerInfo;if(w===f)break;if(M===4)for(M=l.return;M!==null;){var k=M.tag;if((k===3||k===4)&&M.stateNode.containerInfo===f)return;M=M.return}for(;w!==null;){if(M=qa(w),M===null)return;if(k=M.tag,k===5||k===6||k===26||k===27){l=m=M;continue t}w=w.parentNode}}l=l.return}Vg(function(){var et=m,pt=Cf(r),vt=[];t:{var st=p0.get(e);if(st!==void 0){var ut=sc,Wt=e;switch(e){case"keypress":if(ic(r)===0)break t;case"keydown":case"keyup":ut=HE;break;case"focusin":Wt="focus",ut=Pf;break;case"focusout":Wt="blur",ut=Pf;break;case"beforeblur":case"afterblur":ut=Pf;break;case"click":if(r.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":ut=kg;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":ut=wE;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":ut=jE;break;case u0:case f0:case d0:ut=LE;break;case h0:ut=WE;break;case"scroll":case"scrollend":ut=RE;break;case"wheel":ut=YE;break;case"copy":case"cut":case"paste":ut=PE;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":ut=Xg;break;case"toggle":case"beforetoggle":ut=ZE}var te=(a&4)!==0,ke=!te&&(e==="scroll"||e==="scrollend"),Z=te?st!==null?st+"Capture":null:st;te=[];for(var W=et,tt;W!==null;){var gt=W;if(tt=gt.stateNode,gt=gt.tag,gt!==5&&gt!==26&&gt!==27||tt===null||Z===null||(gt=Oo(W,Z),gt!=null&&te.push(pl(W,gt,tt))),ke)break;W=W.return}0<te.length&&(st=new ut(st,Wt,null,r,pt),vt.push({event:st,listeners:te}))}}if((a&7)===0){t:{if(st=e==="mouseover"||e==="pointerover",ut=e==="mouseout"||e==="pointerout",st&&r!==Rf&&(Wt=r.relatedTarget||r.fromElement)&&(qa(Wt)||Wt[pa]))break t;if((ut||st)&&(st=pt.window===pt?pt:(st=pt.ownerDocument)?st.defaultView||st.parentWindow:window,ut?(Wt=r.relatedTarget||r.toElement,ut=et,Wt=Wt?qa(Wt):null,Wt!==null&&(ke=c(Wt),te=Wt.tag,Wt!==ke||te!==5&&te!==27&&te!==6)&&(Wt=null)):(ut=null,Wt=et),ut!==Wt)){if(te=kg,gt="onMouseLeave",Z="onMouseEnter",W="mouse",(e==="pointerout"||e==="pointerover")&&(te=Xg,gt="onPointerLeave",Z="onPointerEnter",W="pointer"),ke=ut==null?st:Ps(ut),tt=Wt==null?st:Ps(Wt),st=new te(gt,W+"leave",ut,r,pt),st.target=ke,st.relatedTarget=tt,gt=null,qa(pt)===et&&(te=new te(Z,W+"enter",Wt,r,pt),te.target=tt,te.relatedTarget=ke,gt=te),ke=gt,ut&&Wt)e:{for(te=KT,Z=ut,W=Wt,tt=0,gt=Z;gt;gt=te(gt))tt++;gt=0;for(var Jt=W;Jt;Jt=te(Jt))gt++;for(;0<tt-gt;)Z=te(Z),tt--;for(;0<gt-tt;)W=te(W),gt--;for(;tt--;){if(Z===W||W!==null&&Z===W.alternate){te=Z;break e}Z=te(Z),W=te(W)}te=null}else te=null;ut!==null&&Fv(vt,st,ut,te,!1),Wt!==null&&ke!==null&&Fv(vt,ke,Wt,te,!0)}}t:{if(st=et?Ps(et):window,ut=st.nodeName&&st.nodeName.toLowerCase(),ut==="select"||ut==="input"&&st.type==="file")var Re=$g;else if(Qg(st))if(t0)Re=rT;else{Re=aT;var Kt=iT}else ut=st.nodeName,!ut||ut.toLowerCase()!=="input"||st.type!=="checkbox"&&st.type!=="radio"?et&&Ne(et.elementType)&&(Re=$g):Re=sT;if(Re&&(Re=Re(e,et))){Jg(vt,Re,r,pt);break t}Kt&&Kt(e,st,et),e==="focusout"&&et&&st.type==="number"&&et.memoizedProps.value!=null&&ge(st,"number",st.value)}switch(Kt=et?Ps(et):window,e){case"focusin":(Qg(Kt)||Kt.contentEditable==="true")&&(br=Kt,Vf=et,ko=null);break;case"focusout":ko=Vf=br=null;break;case"mousedown":Hf=!0;break;case"contextmenu":case"mouseup":case"dragend":Hf=!1,l0(vt,r,pt);break;case"selectionchange":if(lT)break;case"keydown":case"keyup":l0(vt,r,pt)}var fe;if(Ff)t:{switch(e){case"compositionstart":var Se="onCompositionStart";break t;case"compositionend":Se="onCompositionEnd";break t;case"compositionupdate":Se="onCompositionUpdate";break t}Se=void 0}else Mr?Kg(e,r)&&(Se="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(Se="onCompositionStart");Se&&(Wg&&r.locale!=="ko"&&(Mr||Se!=="onCompositionStart"?Se==="onCompositionEnd"&&Mr&&(fe=Hg()):(Qa=pt,Nf="value"in Qa?Qa.value:Qa.textContent,Mr=!0)),Kt=Kc(et,Se),0<Kt.length&&(Se=new jg(Se,e,null,r,pt),vt.push({event:Se,listeners:Kt}),fe?Se.data=fe:(fe=Zg(r),fe!==null&&(Se.data=fe)))),(fe=JE?$E(e,r):tT(e,r))&&(Se=Kc(et,"onBeforeInput"),0<Se.length&&(Kt=new jg("onBeforeInput","beforeinput",null,r,pt),vt.push({event:Kt,listeners:Se}),Kt.data=fe)),XT(vt,e,et,r,pt)}Pv(vt,a)})}function pl(e,a,r){return{instance:e,listener:a,currentTarget:r}}function Kc(e,a){for(var r=a+"Capture",l=[];e!==null;){var f=e,m=f.stateNode;if(f=f.tag,f!==5&&f!==26&&f!==27||m===null||(f=Oo(e,r),f!=null&&l.unshift(pl(e,f,m)),f=Oo(e,a),f!=null&&l.push(pl(e,f,m))),e.tag===3)return l;e=e.return}return[]}function KT(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function Fv(e,a,r,l,f){for(var m=a._reactName,M=[];r!==null&&r!==l;){var w=r,k=w.alternate,et=w.stateNode;if(w=w.tag,k!==null&&k===l)break;w!==5&&w!==26&&w!==27||et===null||(k=et,f?(et=Oo(r,m),et!=null&&M.unshift(pl(r,et,k))):f||(et=Oo(r,m),et!=null&&M.push(pl(r,et,k)))),r=r.return}M.length!==0&&e.push({event:a,listeners:M})}var ZT=/\r\n?/g,QT=/\u0000|\uFFFD/g;function Bv(e){return(typeof e=="string"?e:""+e).replace(ZT,`
`).replace(QT,"")}function Iv(e,a){return a=Bv(a),Bv(e)===a}function Ge(e,a,r,l,f,m){switch(r){case"children":typeof l=="string"?a==="body"||a==="textarea"&&l===""||oi(e,l):(typeof l=="number"||typeof l=="bigint")&&a!=="body"&&oi(e,""+l);break;case"className":Xt(e,"class",l);break;case"tabIndex":Xt(e,"tabindex",l);break;case"dir":case"role":case"viewBox":case"width":case"height":Xt(e,r,l);break;case"style":Oi(e,l,m);break;case"data":if(a!=="object"){Xt(e,"data",l);break}case"src":case"href":if(l===""&&(a!=="a"||r!=="href")){e.removeAttribute(r);break}if(l==null||typeof l=="function"||typeof l=="symbol"||typeof l=="boolean"){e.removeAttribute(r);break}l=Os(""+l),e.setAttribute(r,l);break;case"action":case"formAction":if(typeof l=="function"){e.setAttribute(r,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof m=="function"&&(r==="formAction"?(a!=="input"&&Ge(e,a,"name",f.name,f,null),Ge(e,a,"formEncType",f.formEncType,f,null),Ge(e,a,"formMethod",f.formMethod,f,null),Ge(e,a,"formTarget",f.formTarget,f,null)):(Ge(e,a,"encType",f.encType,f,null),Ge(e,a,"method",f.method,f,null),Ge(e,a,"target",f.target,f,null)));if(l==null||typeof l=="symbol"||typeof l=="boolean"){e.removeAttribute(r);break}l=Os(""+l),e.setAttribute(r,l);break;case"onClick":l!=null&&(e.onclick=ma);break;case"onScroll":l!=null&&ve("scroll",e);break;case"onScrollEnd":l!=null&&ve("scrollend",e);break;case"dangerouslySetInnerHTML":if(l!=null){if(typeof l!="object"||!("__html"in l))throw Error(s(61));if(r=l.__html,r!=null){if(f.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"multiple":e.multiple=l&&typeof l!="function"&&typeof l!="symbol";break;case"muted":e.muted=l&&typeof l!="function"&&typeof l!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(l==null||typeof l=="function"||typeof l=="boolean"||typeof l=="symbol"){e.removeAttribute("xlink:href");break}r=Os(""+l),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",r);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":l!=null&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,""+l):e.removeAttribute(r);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":l&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,""):e.removeAttribute(r);break;case"capture":case"download":l===!0?e.setAttribute(r,""):l!==!1&&l!=null&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,l):e.removeAttribute(r);break;case"cols":case"rows":case"size":case"span":l!=null&&typeof l!="function"&&typeof l!="symbol"&&!isNaN(l)&&1<=l?e.setAttribute(r,l):e.removeAttribute(r);break;case"rowSpan":case"start":l==null||typeof l=="function"||typeof l=="symbol"||isNaN(l)?e.removeAttribute(r):e.setAttribute(r,l);break;case"popover":ve("beforetoggle",e),ve("toggle",e),Bt(e,"popover",l);break;case"xlinkActuate":jt(e,"http://www.w3.org/1999/xlink","xlink:actuate",l);break;case"xlinkArcrole":jt(e,"http://www.w3.org/1999/xlink","xlink:arcrole",l);break;case"xlinkRole":jt(e,"http://www.w3.org/1999/xlink","xlink:role",l);break;case"xlinkShow":jt(e,"http://www.w3.org/1999/xlink","xlink:show",l);break;case"xlinkTitle":jt(e,"http://www.w3.org/1999/xlink","xlink:title",l);break;case"xlinkType":jt(e,"http://www.w3.org/1999/xlink","xlink:type",l);break;case"xmlBase":jt(e,"http://www.w3.org/XML/1998/namespace","xml:base",l);break;case"xmlLang":jt(e,"http://www.w3.org/XML/1998/namespace","xml:lang",l);break;case"xmlSpace":jt(e,"http://www.w3.org/XML/1998/namespace","xml:space",l);break;case"is":Bt(e,"is",l);break;case"innerText":case"textContent":break;default:(!(2<r.length)||r[0]!=="o"&&r[0]!=="O"||r[1]!=="n"&&r[1]!=="N")&&(r=Ki.get(r)||r,Bt(e,r,l))}}function dh(e,a,r,l,f,m){switch(r){case"style":Oi(e,l,m);break;case"dangerouslySetInnerHTML":if(l!=null){if(typeof l!="object"||!("__html"in l))throw Error(s(61));if(r=l.__html,r!=null){if(f.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"children":typeof l=="string"?oi(e,l):(typeof l=="number"||typeof l=="bigint")&&oi(e,""+l);break;case"onScroll":l!=null&&ve("scroll",e);break;case"onScrollEnd":l!=null&&ve("scrollend",e);break;case"onClick":l!=null&&(e.onclick=ma);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!C.hasOwnProperty(r))t:{if(r[0]==="o"&&r[1]==="n"&&(f=r.endsWith("Capture"),a=r.slice(2,f?r.length-7:void 0),m=e[Nn]||null,m=m!=null?m[r]:null,typeof m=="function"&&e.removeEventListener(a,m,f),typeof l=="function")){typeof m!="function"&&m!==null&&(r in e?e[r]=null:e.hasAttribute(r)&&e.removeAttribute(r)),e.addEventListener(a,l,f);break t}r in e?e[r]=l:l===!0?e.setAttribute(r,""):Bt(e,r,l)}}}function On(e,a,r){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":ve("error",e),ve("load",e);var l=!1,f=!1,m;for(m in r)if(r.hasOwnProperty(m)){var M=r[m];if(M!=null)switch(m){case"src":l=!0;break;case"srcSet":f=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(s(137,a));default:Ge(e,a,m,M,r,null)}}f&&Ge(e,a,"srcSet",r.srcSet,r,null),l&&Ge(e,a,"src",r.src,r,null);return;case"input":ve("invalid",e);var w=m=M=f=null,k=null,et=null;for(l in r)if(r.hasOwnProperty(l)){var pt=r[l];if(pt!=null)switch(l){case"name":f=pt;break;case"type":M=pt;break;case"checked":k=pt;break;case"defaultChecked":et=pt;break;case"value":m=pt;break;case"defaultValue":w=pt;break;case"children":case"dangerouslySetInnerHTML":if(pt!=null)throw Error(s(137,a));break;default:Ge(e,a,l,pt,r,null)}}Vn(e,m,w,k,et,M,f,!1);return;case"select":ve("invalid",e),l=M=m=null;for(f in r)if(r.hasOwnProperty(f)&&(w=r[f],w!=null))switch(f){case"value":m=w;break;case"defaultValue":M=w;break;case"multiple":l=w;default:Ge(e,a,f,w,r,null)}a=m,r=M,e.multiple=!!l,a!=null?bn(e,!!l,a,!1):r!=null&&bn(e,!!l,r,!0);return;case"textarea":ve("invalid",e),m=f=l=null;for(M in r)if(r.hasOwnProperty(M)&&(w=r[M],w!=null))switch(M){case"value":l=w;break;case"defaultValue":f=w;break;case"children":m=w;break;case"dangerouslySetInnerHTML":if(w!=null)throw Error(s(91));break;default:Ge(e,a,M,w,r,null)}Pi(e,l,f,m);return;case"option":for(k in r)r.hasOwnProperty(k)&&(l=r[k],l!=null)&&(k==="selected"?e.selected=l&&typeof l!="function"&&typeof l!="symbol":Ge(e,a,k,l,r,null));return;case"dialog":ve("beforetoggle",e),ve("toggle",e),ve("cancel",e),ve("close",e);break;case"iframe":case"object":ve("load",e);break;case"video":case"audio":for(l=0;l<hl.length;l++)ve(hl[l],e);break;case"image":ve("error",e),ve("load",e);break;case"details":ve("toggle",e);break;case"embed":case"source":case"link":ve("error",e),ve("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in r)if(r.hasOwnProperty(et)&&(l=r[et],l!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(s(137,a));default:Ge(e,a,et,l,r,null)}return;default:if(Ne(a)){for(pt in r)r.hasOwnProperty(pt)&&(l=r[pt],l!==void 0&&dh(e,a,pt,l,r,void 0));return}}for(w in r)r.hasOwnProperty(w)&&(l=r[w],l!=null&&Ge(e,a,w,l,r,null))}function JT(e,a,r,l){switch(a){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var f=null,m=null,M=null,w=null,k=null,et=null,pt=null;for(ut in r){var vt=r[ut];if(r.hasOwnProperty(ut)&&vt!=null)switch(ut){case"checked":break;case"value":break;case"defaultValue":k=vt;default:l.hasOwnProperty(ut)||Ge(e,a,ut,null,l,vt)}}for(var st in l){var ut=l[st];if(vt=r[st],l.hasOwnProperty(st)&&(ut!=null||vt!=null))switch(st){case"type":m=ut;break;case"name":f=ut;break;case"checked":et=ut;break;case"defaultChecked":pt=ut;break;case"value":M=ut;break;case"defaultValue":w=ut;break;case"children":case"dangerouslySetInnerHTML":if(ut!=null)throw Error(s(137,a));break;default:ut!==vt&&Ge(e,a,st,ut,l,vt)}}Gt(e,M,w,k,et,pt,m,f);return;case"select":ut=M=w=st=null;for(m in r)if(k=r[m],r.hasOwnProperty(m)&&k!=null)switch(m){case"value":break;case"multiple":ut=k;default:l.hasOwnProperty(m)||Ge(e,a,m,null,l,k)}for(f in l)if(m=l[f],k=r[f],l.hasOwnProperty(f)&&(m!=null||k!=null))switch(f){case"value":st=m;break;case"defaultValue":w=m;break;case"multiple":M=m;default:m!==k&&Ge(e,a,f,m,l,k)}a=w,r=M,l=ut,st!=null?bn(e,!!r,st,!1):!!l!=!!r&&(a!=null?bn(e,!!r,a,!0):bn(e,!!r,r?[]:"",!1));return;case"textarea":ut=st=null;for(w in r)if(f=r[w],r.hasOwnProperty(w)&&f!=null&&!l.hasOwnProperty(w))switch(w){case"value":break;case"children":break;default:Ge(e,a,w,null,l,f)}for(M in l)if(f=l[M],m=r[M],l.hasOwnProperty(M)&&(f!=null||m!=null))switch(M){case"value":st=f;break;case"defaultValue":ut=f;break;case"children":break;case"dangerouslySetInnerHTML":if(f!=null)throw Error(s(91));break;default:f!==m&&Ge(e,a,M,f,l,m)}ri(e,st,ut);return;case"option":for(var Wt in r)st=r[Wt],r.hasOwnProperty(Wt)&&st!=null&&!l.hasOwnProperty(Wt)&&(Wt==="selected"?e.selected=!1:Ge(e,a,Wt,null,l,st));for(k in l)st=l[k],ut=r[k],l.hasOwnProperty(k)&&st!==ut&&(st!=null||ut!=null)&&(k==="selected"?e.selected=st&&typeof st!="function"&&typeof st!="symbol":Ge(e,a,k,st,l,ut));return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var te in r)st=r[te],r.hasOwnProperty(te)&&st!=null&&!l.hasOwnProperty(te)&&Ge(e,a,te,null,l,st);for(et in l)if(st=l[et],ut=r[et],l.hasOwnProperty(et)&&st!==ut&&(st!=null||ut!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(st!=null)throw Error(s(137,a));break;default:Ge(e,a,et,st,l,ut)}return;default:if(Ne(a)){for(var ke in r)st=r[ke],r.hasOwnProperty(ke)&&st!==void 0&&!l.hasOwnProperty(ke)&&dh(e,a,ke,void 0,l,st);for(pt in l)st=l[pt],ut=r[pt],!l.hasOwnProperty(pt)||st===ut||st===void 0&&ut===void 0||dh(e,a,pt,st,l,ut);return}}for(var Z in r)st=r[Z],r.hasOwnProperty(Z)&&st!=null&&!l.hasOwnProperty(Z)&&Ge(e,a,Z,null,l,st);for(vt in l)st=l[vt],ut=r[vt],!l.hasOwnProperty(vt)||st===ut||st==null&&ut==null||Ge(e,a,vt,st,l,ut)}function zv(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function $T(){if(typeof performance.getEntriesByType=="function"){for(var e=0,a=0,r=performance.getEntriesByType("resource"),l=0;l<r.length;l++){var f=r[l],m=f.transferSize,M=f.initiatorType,w=f.duration;if(m&&w&&zv(M)){for(M=0,w=f.responseEnd,l+=1;l<r.length;l++){var k=r[l],et=k.startTime;if(et>w)break;var pt=k.transferSize,vt=k.initiatorType;pt&&zv(vt)&&(k=k.responseEnd,M+=pt*(k<w?1:(w-et)/(k-et)))}if(--l,a+=8*(m+M)/(f.duration/1e3),e++,10<e)break}}if(0<e)return a/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var hh=null,ph=null;function Zc(e){return e.nodeType===9?e:e.ownerDocument}function Vv(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function Hv(e,a){if(e===0)switch(a){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&a==="foreignObject"?0:e}function mh(e,a){return e==="textarea"||e==="noscript"||typeof a.children=="string"||typeof a.children=="number"||typeof a.children=="bigint"||typeof a.dangerouslySetInnerHTML=="object"&&a.dangerouslySetInnerHTML!==null&&a.dangerouslySetInnerHTML.__html!=null}var gh=null;function t1(){var e=window.event;return e&&e.type==="popstate"?e===gh?!1:(gh=e,!0):(gh=null,!1)}var Gv=typeof setTimeout=="function"?setTimeout:void 0,e1=typeof clearTimeout=="function"?clearTimeout:void 0,kv=typeof Promise=="function"?Promise:void 0,n1=typeof queueMicrotask=="function"?queueMicrotask:typeof kv<"u"?function(e){return kv.resolve(null).then(e).catch(i1)}:Gv;function i1(e){setTimeout(function(){throw e})}function ps(e){return e==="head"}function jv(e,a){var r=a,l=0;do{var f=r.nextSibling;if(e.removeChild(r),f&&f.nodeType===8)if(r=f.data,r==="/$"||r==="/&"){if(l===0){e.removeChild(f),Zr(a);return}l--}else if(r==="$"||r==="$?"||r==="$~"||r==="$!"||r==="&")l++;else if(r==="html")ml(e.ownerDocument.documentElement);else if(r==="head"){r=e.ownerDocument.head,ml(r);for(var m=r.firstChild;m;){var M=m.nextSibling,w=m.nodeName;m[Wa]||w==="SCRIPT"||w==="STYLE"||w==="LINK"&&m.rel.toLowerCase()==="stylesheet"||r.removeChild(m),m=M}}else r==="body"&&ml(e.ownerDocument.body);r=f}while(r);Zr(a)}function Xv(e,a){var r=e;e=0;do{var l=r.nextSibling;if(r.nodeType===1?a?(r._stashedDisplay=r.style.display,r.style.display="none"):(r.style.display=r._stashedDisplay||"",r.getAttribute("style")===""&&r.removeAttribute("style")):r.nodeType===3&&(a?(r._stashedText=r.nodeValue,r.nodeValue=""):r.nodeValue=r._stashedText||""),l&&l.nodeType===8)if(r=l.data,r==="/$"){if(e===0)break;e--}else r!=="$"&&r!=="$?"&&r!=="$~"&&r!=="$!"||e++;r=l}while(r)}function _h(e){var a=e.firstChild;for(a&&a.nodeType===10&&(a=a.nextSibling);a;){var r=a;switch(a=a.nextSibling,r.nodeName){case"HTML":case"HEAD":case"BODY":_h(r),Po(r);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(r.rel.toLowerCase()==="stylesheet")continue}e.removeChild(r)}}function a1(e,a,r,l){for(;e.nodeType===1;){var f=r;if(e.nodeName.toLowerCase()!==a.toLowerCase()){if(!l&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(l){if(!e[Wa])switch(a){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(m=e.getAttribute("rel"),m==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(m!==f.rel||e.getAttribute("href")!==(f.href==null||f.href===""?null:f.href)||e.getAttribute("crossorigin")!==(f.crossOrigin==null?null:f.crossOrigin)||e.getAttribute("title")!==(f.title==null?null:f.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(m=e.getAttribute("src"),(m!==(f.src==null?null:f.src)||e.getAttribute("type")!==(f.type==null?null:f.type)||e.getAttribute("crossorigin")!==(f.crossOrigin==null?null:f.crossOrigin))&&m&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(a==="input"&&e.type==="hidden"){var m=f.name==null?null:""+f.name;if(f.type==="hidden"&&e.getAttribute("name")===m)return e}else return e;if(e=Ai(e.nextSibling),e===null)break}return null}function s1(e,a,r){if(a==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!r||(e=Ai(e.nextSibling),e===null))return null;return e}function Wv(e,a){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!a||(e=Ai(e.nextSibling),e===null))return null;return e}function vh(e){return e.data==="$?"||e.data==="$~"}function xh(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function r1(e,a){var r=e.ownerDocument;if(e.data==="$~")e._reactRetry=a;else if(e.data!=="$?"||r.readyState!=="loading")a();else{var l=function(){a(),r.removeEventListener("DOMContentLoaded",l)};r.addEventListener("DOMContentLoaded",l),e._reactRetry=l}}function Ai(e){for(;e!=null;e=e.nextSibling){var a=e.nodeType;if(a===1||a===3)break;if(a===8){if(a=e.data,a==="$"||a==="$!"||a==="$?"||a==="$~"||a==="&"||a==="F!"||a==="F")break;if(a==="/$"||a==="/&")return null}}return e}var yh=null;function qv(e){e=e.nextSibling;for(var a=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"||r==="/&"){if(a===0)return Ai(e.nextSibling);a--}else r!=="$"&&r!=="$!"&&r!=="$?"&&r!=="$~"&&r!=="&"||a++}e=e.nextSibling}return null}function Yv(e){e=e.previousSibling;for(var a=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"||r==="$~"||r==="&"){if(a===0)return e;a--}else r!=="/$"&&r!=="/&"||a++}e=e.previousSibling}return null}function Kv(e,a,r){switch(a=Zc(r),e){case"html":if(e=a.documentElement,!e)throw Error(s(452));return e;case"head":if(e=a.head,!e)throw Error(s(453));return e;case"body":if(e=a.body,!e)throw Error(s(454));return e;default:throw Error(s(451))}}function ml(e){for(var a=e.attributes;a.length;)e.removeAttributeNode(a[0]);Po(e)}var Ri=new Map,Zv=new Set;function Qc(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var Na=G.d;G.d={f:o1,r:l1,D:c1,C:u1,L:f1,m:d1,X:p1,S:h1,M:m1};function o1(){var e=Na.f(),a=Gc();return e||a}function l1(e){var a=Ya(e);a!==null&&a.tag===5&&a.type==="form"?h_(a):Na.r(e)}var qr=typeof document>"u"?null:document;function Qv(e,a,r){var l=qr;if(l&&typeof a=="string"&&a){var f=Oe(a);f='link[rel="'+e+'"][href="'+f+'"]',typeof r=="string"&&(f+='[crossorigin="'+r+'"]'),Zv.has(f)||(Zv.add(f),e={rel:e,crossOrigin:r,href:a},l.querySelector(f)===null&&(a=l.createElement("link"),On(a,"link",e),pn(a),l.head.appendChild(a)))}}function c1(e){Na.D(e),Qv("dns-prefetch",e,null)}function u1(e,a){Na.C(e,a),Qv("preconnect",e,a)}function f1(e,a,r){Na.L(e,a,r);var l=qr;if(l&&e&&a){var f='link[rel="preload"][as="'+Oe(a)+'"]';a==="image"&&r&&r.imageSrcSet?(f+='[imagesrcset="'+Oe(r.imageSrcSet)+'"]',typeof r.imageSizes=="string"&&(f+='[imagesizes="'+Oe(r.imageSizes)+'"]')):f+='[href="'+Oe(e)+'"]';var m=f;switch(a){case"style":m=Yr(e);break;case"script":m=Kr(e)}Ri.has(m)||(e=_({rel:"preload",href:a==="image"&&r&&r.imageSrcSet?void 0:e,as:a},r),Ri.set(m,e),l.querySelector(f)!==null||a==="style"&&l.querySelector(gl(m))||a==="script"&&l.querySelector(_l(m))||(a=l.createElement("link"),On(a,"link",e),pn(a),l.head.appendChild(a)))}}function d1(e,a){Na.m(e,a);var r=qr;if(r&&e){var l=a&&typeof a.as=="string"?a.as:"script",f='link[rel="modulepreload"][as="'+Oe(l)+'"][href="'+Oe(e)+'"]',m=f;switch(l){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":m=Kr(e)}if(!Ri.has(m)&&(e=_({rel:"modulepreload",href:e},a),Ri.set(m,e),r.querySelector(f)===null)){switch(l){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(r.querySelector(_l(m)))return}l=r.createElement("link"),On(l,"link",e),pn(l),r.head.appendChild(l)}}}function h1(e,a,r){Na.S(e,a,r);var l=qr;if(l&&e){var f=Ka(l).hoistableStyles,m=Yr(e);a=a||"default";var M=f.get(m);if(!M){var w={loading:0,preload:null};if(M=l.querySelector(gl(m)))w.loading=5;else{e=_({rel:"stylesheet",href:e,"data-precedence":a},r),(r=Ri.get(m))&&Sh(e,r);var k=M=l.createElement("link");pn(k),On(k,"link",e),k._p=new Promise(function(et,pt){k.onload=et,k.onerror=pt}),k.addEventListener("load",function(){w.loading|=1}),k.addEventListener("error",function(){w.loading|=2}),w.loading|=4,Jc(M,a,l)}M={type:"stylesheet",instance:M,count:1,state:w},f.set(m,M)}}}function p1(e,a){Na.X(e,a);var r=qr;if(r&&e){var l=Ka(r).hoistableScripts,f=Kr(e),m=l.get(f);m||(m=r.querySelector(_l(f)),m||(e=_({src:e,async:!0},a),(a=Ri.get(f))&&Mh(e,a),m=r.createElement("script"),pn(m),On(m,"link",e),r.head.appendChild(m)),m={type:"script",instance:m,count:1,state:null},l.set(f,m))}}function m1(e,a){Na.M(e,a);var r=qr;if(r&&e){var l=Ka(r).hoistableScripts,f=Kr(e),m=l.get(f);m||(m=r.querySelector(_l(f)),m||(e=_({src:e,async:!0,type:"module"},a),(a=Ri.get(f))&&Mh(e,a),m=r.createElement("script"),pn(m),On(m,"link",e),r.head.appendChild(m)),m={type:"script",instance:m,count:1,state:null},l.set(f,m))}}function Jv(e,a,r,l){var f=(f=ot.current)?Qc(f):null;if(!f)throw Error(s(446));switch(e){case"meta":case"title":return null;case"style":return typeof r.precedence=="string"&&typeof r.href=="string"?(a=Yr(r.href),r=Ka(f).hoistableStyles,l=r.get(a),l||(l={type:"style",instance:null,count:0,state:null},r.set(a,l)),l):{type:"void",instance:null,count:0,state:null};case"link":if(r.rel==="stylesheet"&&typeof r.href=="string"&&typeof r.precedence=="string"){e=Yr(r.href);var m=Ka(f).hoistableStyles,M=m.get(e);if(M||(f=f.ownerDocument||f,M={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},m.set(e,M),(m=f.querySelector(gl(e)))&&!m._p&&(M.instance=m,M.state.loading=5),Ri.has(e)||(r={rel:"preload",as:"style",href:r.href,crossOrigin:r.crossOrigin,integrity:r.integrity,media:r.media,hrefLang:r.hrefLang,referrerPolicy:r.referrerPolicy},Ri.set(e,r),m||g1(f,e,r,M.state))),a&&l===null)throw Error(s(528,""));return M}if(a&&l!==null)throw Error(s(529,""));return null;case"script":return a=r.async,r=r.src,typeof r=="string"&&a&&typeof a!="function"&&typeof a!="symbol"?(a=Kr(r),r=Ka(f).hoistableScripts,l=r.get(a),l||(l={type:"script",instance:null,count:0,state:null},r.set(a,l)),l):{type:"void",instance:null,count:0,state:null};default:throw Error(s(444,e))}}function Yr(e){return'href="'+Oe(e)+'"'}function gl(e){return'link[rel="stylesheet"]['+e+"]"}function $v(e){return _({},e,{"data-precedence":e.precedence,precedence:null})}function g1(e,a,r,l){e.querySelector('link[rel="preload"][as="style"]['+a+"]")?l.loading=1:(a=e.createElement("link"),l.preload=a,a.addEventListener("load",function(){return l.loading|=1}),a.addEventListener("error",function(){return l.loading|=2}),On(a,"link",r),pn(a),e.head.appendChild(a))}function Kr(e){return'[src="'+Oe(e)+'"]'}function _l(e){return"script[async]"+e}function tx(e,a,r){if(a.count++,a.instance===null)switch(a.type){case"style":var l=e.querySelector('style[data-href~="'+Oe(r.href)+'"]');if(l)return a.instance=l,pn(l),l;var f=_({},r,{"data-href":r.href,"data-precedence":r.precedence,href:null,precedence:null});return l=(e.ownerDocument||e).createElement("style"),pn(l),On(l,"style",f),Jc(l,r.precedence,e),a.instance=l;case"stylesheet":f=Yr(r.href);var m=e.querySelector(gl(f));if(m)return a.state.loading|=4,a.instance=m,pn(m),m;l=$v(r),(f=Ri.get(f))&&Sh(l,f),m=(e.ownerDocument||e).createElement("link"),pn(m);var M=m;return M._p=new Promise(function(w,k){M.onload=w,M.onerror=k}),On(m,"link",l),a.state.loading|=4,Jc(m,r.precedence,e),a.instance=m;case"script":return m=Kr(r.src),(f=e.querySelector(_l(m)))?(a.instance=f,pn(f),f):(l=r,(f=Ri.get(m))&&(l=_({},r),Mh(l,f)),e=e.ownerDocument||e,f=e.createElement("script"),pn(f),On(f,"link",l),e.head.appendChild(f),a.instance=f);case"void":return null;default:throw Error(s(443,a.type))}else a.type==="stylesheet"&&(a.state.loading&4)===0&&(l=a.instance,a.state.loading|=4,Jc(l,r.precedence,e));return a.instance}function Jc(e,a,r){for(var l=r.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),f=l.length?l[l.length-1]:null,m=f,M=0;M<l.length;M++){var w=l[M];if(w.dataset.precedence===a)m=w;else if(m!==f)break}m?m.parentNode.insertBefore(e,m.nextSibling):(a=r.nodeType===9?r.head:r,a.insertBefore(e,a.firstChild))}function Sh(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.title==null&&(e.title=a.title)}function Mh(e,a){e.crossOrigin==null&&(e.crossOrigin=a.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=a.referrerPolicy),e.integrity==null&&(e.integrity=a.integrity)}var $c=null;function ex(e,a,r){if($c===null){var l=new Map,f=$c=new Map;f.set(r,l)}else f=$c,l=f.get(r),l||(l=new Map,f.set(r,l));if(l.has(e))return l;for(l.set(e,null),r=r.getElementsByTagName(e),f=0;f<r.length;f++){var m=r[f];if(!(m[Wa]||m[un]||e==="link"&&m.getAttribute("rel")==="stylesheet")&&m.namespaceURI!=="http://www.w3.org/2000/svg"){var M=m.getAttribute(a)||"";M=e+M;var w=l.get(M);w?w.push(m):l.set(M,[m])}}return l}function nx(e,a,r){e=e.ownerDocument||e,e.head.insertBefore(r,a==="title"?e.querySelector("head > title"):null)}function _1(e,a,r){if(r===1||a.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof a.precedence!="string"||typeof a.href!="string"||a.href==="")break;return!0;case"link":if(typeof a.rel!="string"||typeof a.href!="string"||a.href===""||a.onLoad||a.onError)break;return a.rel==="stylesheet"?(e=a.disabled,typeof a.precedence=="string"&&e==null):!0;case"script":if(a.async&&typeof a.async!="function"&&typeof a.async!="symbol"&&!a.onLoad&&!a.onError&&a.src&&typeof a.src=="string")return!0}return!1}function ix(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function v1(e,a,r,l){if(r.type==="stylesheet"&&(typeof l.media!="string"||matchMedia(l.media).matches!==!1)&&(r.state.loading&4)===0){if(r.instance===null){var f=Yr(l.href),m=a.querySelector(gl(f));if(m){a=m._p,a!==null&&typeof a=="object"&&typeof a.then=="function"&&(e.count++,e=tu.bind(e),a.then(e,e)),r.state.loading|=4,r.instance=m,pn(m);return}m=a.ownerDocument||a,l=$v(l),(f=Ri.get(f))&&Sh(l,f),m=m.createElement("link"),pn(m);var M=m;M._p=new Promise(function(w,k){M.onload=w,M.onerror=k}),On(m,"link",l),r.instance=m}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(r,a),(a=r.state.preload)&&(r.state.loading&3)===0&&(e.count++,r=tu.bind(e),a.addEventListener("load",r),a.addEventListener("error",r))}}var bh=0;function x1(e,a){return e.stylesheets&&e.count===0&&nu(e,e.stylesheets),0<e.count||0<e.imgCount?function(r){var l=setTimeout(function(){if(e.stylesheets&&nu(e,e.stylesheets),e.unsuspend){var m=e.unsuspend;e.unsuspend=null,m()}},6e4+a);0<e.imgBytes&&bh===0&&(bh=62500*$T());var f=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&nu(e,e.stylesheets),e.unsuspend)){var m=e.unsuspend;e.unsuspend=null,m()}},(e.imgBytes>bh?50:800)+a);return e.unsuspend=r,function(){e.unsuspend=null,clearTimeout(l),clearTimeout(f)}}:null}function tu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)nu(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var eu=null;function nu(e,a){e.stylesheets=null,e.unsuspend!==null&&(e.count++,eu=new Map,a.forEach(y1,e),eu=null,tu.call(e))}function y1(e,a){if(!(a.state.loading&4)){var r=eu.get(e);if(r)var l=r.get(null);else{r=new Map,eu.set(e,r);for(var f=e.querySelectorAll("link[data-precedence],style[data-precedence]"),m=0;m<f.length;m++){var M=f[m];(M.nodeName==="LINK"||M.getAttribute("media")!=="not all")&&(r.set(M.dataset.precedence,M),l=M)}l&&r.set(null,l)}f=a.instance,M=f.getAttribute("data-precedence"),m=r.get(M)||l,m===l&&r.set(null,f),r.set(M,f),this.count++,l=tu.bind(this),f.addEventListener("load",l),f.addEventListener("error",l),m?m.parentNode.insertBefore(f,m.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(f,e.firstChild)),a.state.loading|=4}}var vl={$$typeof:N,Provider:null,Consumer:null,_currentValue:$,_currentValue2:$,_threadCount:0};function S1(e,a,r,l,f,m,M,w,k){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Yt(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Yt(0),this.hiddenUpdates=Yt(null),this.identifierPrefix=l,this.onUncaughtError=f,this.onCaughtError=m,this.onRecoverableError=M,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=k,this.incompleteTransitions=new Map}function ax(e,a,r,l,f,m,M,w,k,et,pt,vt){return e=new S1(e,a,r,M,k,et,pt,vt,w),a=1,m===!0&&(a|=24),m=ci(3,null,null,a),e.current=m,m.stateNode=e,a=nd(),a.refCount++,e.pooledCache=a,a.refCount++,m.memoizedState={element:l,isDehydrated:r,cache:a},rd(m),e}function sx(e){return e?(e=Ar,e):Ar}function rx(e,a,r,l,f,m){f=sx(f),l.context===null?l.context=f:l.pendingContext=f,l=is(a),l.payload={element:r},m=m===void 0?null:m,m!==null&&(l.callback=m),r=as(e,l,a),r!==null&&(ei(r,e,a),Zo(r,e,a))}function ox(e,a){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<a?r:a}}function Eh(e,a){ox(e,a),(e=e.alternate)&&ox(e,a)}function lx(e){if(e.tag===13||e.tag===31){var a=zs(e,67108864);a!==null&&ei(a,e,67108864),Eh(e,67108864)}}function cx(e){if(e.tag===13||e.tag===31){var a=pi();a=Us(a);var r=zs(e,a);r!==null&&ei(r,e,a),Eh(e,a)}}var iu=!0;function M1(e,a,r,l){var f=I.T;I.T=null;var m=G.p;try{G.p=2,Th(e,a,r,l)}finally{G.p=m,I.T=f}}function b1(e,a,r,l){var f=I.T;I.T=null;var m=G.p;try{G.p=8,Th(e,a,r,l)}finally{G.p=m,I.T=f}}function Th(e,a,r,l){if(iu){var f=Ah(l);if(f===null)fh(e,a,l,au,r),fx(e,l);else if(T1(f,e,a,r,l))l.stopPropagation();else if(fx(e,l),a&4&&-1<E1.indexOf(e)){for(;f!==null;){var m=Ya(f);if(m!==null)switch(m.tag){case 3:if(m=m.stateNode,m.current.memoizedState.isDehydrated){var M=At(m.pendingLanes);if(M!==0){var w=m;for(w.pendingLanes|=2,w.entangledLanes|=2;M;){var k=1<<31-Ft(M);w.entanglements[1]|=k,M&=~k}$i(m),(De&6)===0&&(Vc=Ct()+500,dl(0))}}break;case 31:case 13:w=zs(m,2),w!==null&&ei(w,m,2),Gc(),Eh(m,2)}if(m=Ah(l),m===null&&fh(e,a,l,au,r),m===f)break;f=m}f!==null&&l.stopPropagation()}else fh(e,a,l,null,r)}}function Ah(e){return e=Cf(e),Rh(e)}var au=null;function Rh(e){if(au=null,e=qa(e),e!==null){var a=c(e);if(a===null)e=null;else{var r=a.tag;if(r===13){if(e=u(a),e!==null)return e;e=null}else if(r===31){if(e=d(a),e!==null)return e;e=null}else if(r===3){if(a.stateNode.current.memoizedState.isDehydrated)return a.tag===3?a.stateNode.containerInfo:null;e=null}else a!==e&&(e=null)}}return au=e,null}function ux(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch($e()){case P:return 2;case T:return 8;case J:case _t:return 32;case Et:return 268435456;default:return 32}default:return 32}}var Ch=!1,ms=null,gs=null,_s=null,xl=new Map,yl=new Map,vs=[],E1="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function fx(e,a){switch(e){case"focusin":case"focusout":ms=null;break;case"dragenter":case"dragleave":gs=null;break;case"mouseover":case"mouseout":_s=null;break;case"pointerover":case"pointerout":xl.delete(a.pointerId);break;case"gotpointercapture":case"lostpointercapture":yl.delete(a.pointerId)}}function Sl(e,a,r,l,f,m){return e===null||e.nativeEvent!==m?(e={blockedOn:a,domEventName:r,eventSystemFlags:l,nativeEvent:m,targetContainers:[f]},a!==null&&(a=Ya(a),a!==null&&lx(a)),e):(e.eventSystemFlags|=l,a=e.targetContainers,f!==null&&a.indexOf(f)===-1&&a.push(f),e)}function T1(e,a,r,l,f){switch(a){case"focusin":return ms=Sl(ms,e,a,r,l,f),!0;case"dragenter":return gs=Sl(gs,e,a,r,l,f),!0;case"mouseover":return _s=Sl(_s,e,a,r,l,f),!0;case"pointerover":var m=f.pointerId;return xl.set(m,Sl(xl.get(m)||null,e,a,r,l,f)),!0;case"gotpointercapture":return m=f.pointerId,yl.set(m,Sl(yl.get(m)||null,e,a,r,l,f)),!0}return!1}function dx(e){var a=qa(e.target);if(a!==null){var r=c(a);if(r!==null){if(a=r.tag,a===13){if(a=u(r),a!==null){e.blockedOn=a,Lo(e.priority,function(){cx(r)});return}}else if(a===31){if(a=d(r),a!==null){e.blockedOn=a,Lo(e.priority,function(){cx(r)});return}}else if(a===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function su(e){if(e.blockedOn!==null)return!1;for(var a=e.targetContainers;0<a.length;){var r=Ah(e.nativeEvent);if(r===null){r=e.nativeEvent;var l=new r.constructor(r.type,r);Rf=l,r.target.dispatchEvent(l),Rf=null}else return a=Ya(r),a!==null&&lx(a),e.blockedOn=r,!1;a.shift()}return!0}function hx(e,a,r){su(e)&&r.delete(a)}function A1(){Ch=!1,ms!==null&&su(ms)&&(ms=null),gs!==null&&su(gs)&&(gs=null),_s!==null&&su(_s)&&(_s=null),xl.forEach(hx),yl.forEach(hx)}function ru(e,a){e.blockedOn===a&&(e.blockedOn=null,Ch||(Ch=!0,i.unstable_scheduleCallback(i.unstable_NormalPriority,A1)))}var ou=null;function px(e){ou!==e&&(ou=e,i.unstable_scheduleCallback(i.unstable_NormalPriority,function(){ou===e&&(ou=null);for(var a=0;a<e.length;a+=3){var r=e[a],l=e[a+1],f=e[a+2];if(typeof l!="function"){if(Rh(l||r)===null)continue;break}var m=Ya(r);m!==null&&(e.splice(a,3),a-=3,Ad(m,{pending:!0,data:f,method:r.method,action:l},l,f))}}))}function Zr(e){function a(k){return ru(k,e)}ms!==null&&ru(ms,e),gs!==null&&ru(gs,e),_s!==null&&ru(_s,e),xl.forEach(a),yl.forEach(a);for(var r=0;r<vs.length;r++){var l=vs[r];l.blockedOn===e&&(l.blockedOn=null)}for(;0<vs.length&&(r=vs[0],r.blockedOn===null);)dx(r),r.blockedOn===null&&vs.shift();if(r=(e.ownerDocument||e).$$reactFormReplay,r!=null)for(l=0;l<r.length;l+=3){var f=r[l],m=r[l+1],M=f[Nn]||null;if(typeof m=="function")M||px(r);else if(M){var w=null;if(m&&m.hasAttribute("formAction")){if(f=m,M=m[Nn]||null)w=M.formAction;else if(Rh(f)!==null)continue}else w=M.action;typeof w=="function"?r[l+1]=w:(r.splice(l,3),l-=3),px(r)}}}function mx(){function e(m){m.canIntercept&&m.info==="react-transition"&&m.intercept({handler:function(){return new Promise(function(M){return f=M})},focusReset:"manual",scroll:"manual"})}function a(){f!==null&&(f(),f=null),l||setTimeout(r,20)}function r(){if(!l&&!navigation.transition){var m=navigation.currentEntry;m&&m.url!=null&&navigation.navigate(m.url,{state:m.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var l=!1,f=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",a),navigation.addEventListener("navigateerror",a),setTimeout(r,100),function(){l=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",a),navigation.removeEventListener("navigateerror",a),f!==null&&(f(),f=null)}}}function wh(e){this._internalRoot=e}lu.prototype.render=wh.prototype.render=function(e){var a=this._internalRoot;if(a===null)throw Error(s(409));var r=a.current,l=pi();rx(r,l,e,a,null,null)},lu.prototype.unmount=wh.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var a=e.containerInfo;rx(e.current,2,null,e,null,null),Gc(),a[pa]=null}};function lu(e){this._internalRoot=e}lu.prototype.unstable_scheduleHydration=function(e){if(e){var a=No();e={blockedOn:null,target:e,priority:a};for(var r=0;r<vs.length&&a!==0&&a<vs[r].priority;r++);vs.splice(r,0,e),r===0&&dx(e)}};var gx=t.version;if(gx!=="19.2.6")throw Error(s(527,gx,"19.2.6"));G.findDOMNode=function(e){var a=e._reactInternals;if(a===void 0)throw typeof e.render=="function"?Error(s(188)):(e=Object.keys(e).join(","),Error(s(268,e)));return e=h(a),e=e!==null?g(e):null,e=e===null?null:e.stateNode,e};var R1={bundleType:0,version:"19.2.6",rendererPackageName:"react-dom",currentDispatcherRef:I,reconcilerVersion:"19.2.6"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var cu=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!cu.isDisabled&&cu.supportsFiber)try{ft=cu.inject(R1),ht=cu}catch{}}return bl.createRoot=function(e,a){if(!o(e))throw Error(s(299));var r=!1,l="",f=b_,m=E_,M=T_;return a!=null&&(a.unstable_strictMode===!0&&(r=!0),a.identifierPrefix!==void 0&&(l=a.identifierPrefix),a.onUncaughtError!==void 0&&(f=a.onUncaughtError),a.onCaughtError!==void 0&&(m=a.onCaughtError),a.onRecoverableError!==void 0&&(M=a.onRecoverableError)),a=ax(e,1,!1,null,null,r,l,null,f,m,M,mx),e[pa]=a.current,uh(e),new wh(a)},bl.hydrateRoot=function(e,a,r){if(!o(e))throw Error(s(299));var l=!1,f="",m=b_,M=E_,w=T_,k=null;return r!=null&&(r.unstable_strictMode===!0&&(l=!0),r.identifierPrefix!==void 0&&(f=r.identifierPrefix),r.onUncaughtError!==void 0&&(m=r.onUncaughtError),r.onCaughtError!==void 0&&(M=r.onCaughtError),r.onRecoverableError!==void 0&&(w=r.onRecoverableError),r.formState!==void 0&&(k=r.formState)),a=ax(e,1,!0,a,r??null,l,f,k,m,M,w,mx),a.context=sx(null),r=a.current,l=pi(),l=Us(l),f=is(l),f.callback=null,as(r,f,l),r=l,a.current.lanes=r,ne(a,r),$i(a),e[pa]=a.current,uh(e),new lu(a)},bl.version="19.2.6",bl}var Ax;function z1(){if(Ax)return Lh.exports;Ax=1;function i(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(i)}catch(t){console.error(t)}}return i(),Lh.exports=I1(),Lh.exports}var V1=z1();const Zm="184",H1=0,Rx=1,G1=2,zu=1,k1=2,Ll=3,ws=0,ii=1,Ia=2,Va=0,go=1,Cx=2,wx=3,Dx=4,j1=5,sr=100,X1=101,W1=102,q1=103,Y1=104,K1=200,Z1=201,Q1=202,J1=203,Lp=204,Up=205,$1=206,tA=207,eA=208,nA=209,iA=210,aA=211,sA=212,rA=213,oA=214,Pp=0,Op=1,Fp=2,xo=3,Bp=4,Ip=5,zp=6,Vp=7,QS=0,lA=1,cA=2,oa=0,JS=1,$S=2,tM=3,eM=4,nM=5,iM=6,aM=7,sM=300,hr=301,yo=302,Fh=303,Bh=304,_f=306,Hp=1e3,za=1001,Gp=1002,Bn=1003,uA=1004,uu=1005,jn=1006,Ih=1007,or=1008,Ni=1009,rM=1010,oM=1011,zl=1012,Qm=1013,fa=1014,sa=1015,Ga=1016,Jm=1017,$m=1018,Vl=1020,lM=35902,cM=35899,uM=1021,fM=1022,Xi=1023,ka=1026,lr=1027,dM=1028,tg=1029,pr=1030,eg=1031,ng=1033,Vu=33776,Hu=33777,Gu=33778,ku=33779,kp=35840,jp=35841,Xp=35842,Wp=35843,qp=36196,Yp=37492,Kp=37496,Zp=37488,Qp=37489,$u=37490,Jp=37491,$p=37808,tm=37809,em=37810,nm=37811,im=37812,am=37813,sm=37814,rm=37815,om=37816,lm=37817,cm=37818,um=37819,fm=37820,dm=37821,hm=36492,pm=36494,mm=36495,gm=36283,_m=36284,tf=36285,vm=36286,fA=3200,Nx=0,dA=1,As="",wi="srgb",ef="srgb-linear",nf="linear",ze="srgb",Qr=7680,Lx=519,hA=512,pA=513,mA=514,ig=515,gA=516,_A=517,ag=518,vA=519,Ux=35044,Px="300 es",ra=2e3,af=2001;function xA(i){for(let t=i.length-1;t>=0;--t)if(i[t]>=65535)return!0;return!1}function sf(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function yA(){const i=sf("canvas");return i.style.display="block",i}const Ox={};function Fx(...i){const t="THREE."+i.shift();console.log(t,...i)}function hM(i){const t=i[0];if(typeof t=="string"&&t.startsWith("TSL:")){const n=i[1];n&&n.isStackTrace?i[0]+=" "+n.getLocation():i[1]='Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.'}return i}function ie(...i){i=hM(i);const t="THREE."+i.shift();{const n=i[0];n&&n.isStackTrace?console.warn(n.getError(t)):console.warn(t,...i)}}function Te(...i){i=hM(i);const t="THREE."+i.shift();{const n=i[0];n&&n.isStackTrace?console.error(n.getError(t)):console.error(t,...i)}}function xm(...i){const t=i.join(" ");t in Ox||(Ox[t]=!0,ie(...i))}function SA(i,t,n){return new Promise(function(s,o){function c(){switch(i.clientWaitSync(t,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:o();break;case i.TIMEOUT_EXPIRED:setTimeout(c,n);break;default:s()}}setTimeout(c,n)})}const MA={[Pp]:Op,[Fp]:zp,[Bp]:Vp,[xo]:Ip,[Op]:Pp,[zp]:Fp,[Vp]:Bp,[Ip]:xo};class vr{addEventListener(t,n){this._listeners===void 0&&(this._listeners={});const s=this._listeners;s[t]===void 0&&(s[t]=[]),s[t].indexOf(n)===-1&&s[t].push(n)}hasEventListener(t,n){const s=this._listeners;return s===void 0?!1:s[t]!==void 0&&s[t].indexOf(n)!==-1}removeEventListener(t,n){const s=this._listeners;if(s===void 0)return;const o=s[t];if(o!==void 0){const c=o.indexOf(n);c!==-1&&o.splice(c,1)}}dispatchEvent(t){const n=this._listeners;if(n===void 0)return;const s=n[t.type];if(s!==void 0){t.target=this;const o=s.slice(0);for(let c=0,u=o.length;c<u;c++)o[c].call(this,t);t.target=null}}}const Gn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],zh=Math.PI/180,ym=180/Math.PI;function Wl(){const i=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0,s=Math.random()*4294967295|0;return(Gn[i&255]+Gn[i>>8&255]+Gn[i>>16&255]+Gn[i>>24&255]+"-"+Gn[t&255]+Gn[t>>8&255]+"-"+Gn[t>>16&15|64]+Gn[t>>24&255]+"-"+Gn[n&63|128]+Gn[n>>8&255]+"-"+Gn[n>>16&255]+Gn[n>>24&255]+Gn[s&255]+Gn[s>>8&255]+Gn[s>>16&255]+Gn[s>>24&255]).toLowerCase()}function Ee(i,t,n){return Math.max(t,Math.min(n,i))}function bA(i,t){return(i%t+t)%t}function Vh(i,t,n){return(1-n)*i+n*t}function El(i,t){switch(t.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function ni(i,t){switch(t.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Pg=class Pg{constructor(t=0,n=0){this.x=t,this.y=n}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,n){return this.x=t,this.y=n,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const n=this.x,s=this.y,o=t.elements;return this.x=o[0]*n+o[3]*s+o[6],this.y=o[1]*n+o[4]*s+o[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,n){return this.x=Ee(this.x,t.x,n.x),this.y=Ee(this.y,t.y,n.y),this}clampScalar(t,n){return this.x=Ee(this.x,t,n),this.y=Ee(this.y,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(Ee(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(Ee(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y;return n*n+s*s}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this}rotateAround(t,n){const s=Math.cos(n),o=Math.sin(n),c=this.x-t.x,u=this.y-t.y;return this.x=c*s-u*o+t.x,this.y=c*o+u*s+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}};Pg.prototype.isVector2=!0;let je=Pg;class To{constructor(t=0,n=0,s=0,o=1){this.isQuaternion=!0,this._x=t,this._y=n,this._z=s,this._w=o}static slerpFlat(t,n,s,o,c,u,d){let p=s[o+0],h=s[o+1],g=s[o+2],_=s[o+3],v=c[u+0],y=c[u+1],b=c[u+2],R=c[u+3];if(_!==R||p!==v||h!==y||g!==b){let S=p*v+h*y+g*b+_*R;S<0&&(v=-v,y=-y,b=-b,R=-R,S=-S);let x=1-d;if(S<.9995){const A=Math.acos(S),N=Math.sin(A);x=Math.sin(x*A)/N,d=Math.sin(d*A)/N,p=p*x+v*d,h=h*x+y*d,g=g*x+b*d,_=_*x+R*d}else{p=p*x+v*d,h=h*x+y*d,g=g*x+b*d,_=_*x+R*d;const A=1/Math.sqrt(p*p+h*h+g*g+_*_);p*=A,h*=A,g*=A,_*=A}}t[n]=p,t[n+1]=h,t[n+2]=g,t[n+3]=_}static multiplyQuaternionsFlat(t,n,s,o,c,u){const d=s[o],p=s[o+1],h=s[o+2],g=s[o+3],_=c[u],v=c[u+1],y=c[u+2],b=c[u+3];return t[n]=d*b+g*_+p*y-h*v,t[n+1]=p*b+g*v+h*_-d*y,t[n+2]=h*b+g*y+d*v-p*_,t[n+3]=g*b-d*_-p*v-h*y,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,n,s,o){return this._x=t,this._y=n,this._z=s,this._w=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,n=!0){const s=t._x,o=t._y,c=t._z,u=t._order,d=Math.cos,p=Math.sin,h=d(s/2),g=d(o/2),_=d(c/2),v=p(s/2),y=p(o/2),b=p(c/2);switch(u){case"XYZ":this._x=v*g*_+h*y*b,this._y=h*y*_-v*g*b,this._z=h*g*b+v*y*_,this._w=h*g*_-v*y*b;break;case"YXZ":this._x=v*g*_+h*y*b,this._y=h*y*_-v*g*b,this._z=h*g*b-v*y*_,this._w=h*g*_+v*y*b;break;case"ZXY":this._x=v*g*_-h*y*b,this._y=h*y*_+v*g*b,this._z=h*g*b+v*y*_,this._w=h*g*_-v*y*b;break;case"ZYX":this._x=v*g*_-h*y*b,this._y=h*y*_+v*g*b,this._z=h*g*b-v*y*_,this._w=h*g*_+v*y*b;break;case"YZX":this._x=v*g*_+h*y*b,this._y=h*y*_+v*g*b,this._z=h*g*b-v*y*_,this._w=h*g*_-v*y*b;break;case"XZY":this._x=v*g*_-h*y*b,this._y=h*y*_-v*g*b,this._z=h*g*b+v*y*_,this._w=h*g*_+v*y*b;break;default:ie("Quaternion: .setFromEuler() encountered an unknown order: "+u)}return n===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,n){const s=n/2,o=Math.sin(s);return this._x=t.x*o,this._y=t.y*o,this._z=t.z*o,this._w=Math.cos(s),this._onChangeCallback(),this}setFromRotationMatrix(t){const n=t.elements,s=n[0],o=n[4],c=n[8],u=n[1],d=n[5],p=n[9],h=n[2],g=n[6],_=n[10],v=s+d+_;if(v>0){const y=.5/Math.sqrt(v+1);this._w=.25/y,this._x=(g-p)*y,this._y=(c-h)*y,this._z=(u-o)*y}else if(s>d&&s>_){const y=2*Math.sqrt(1+s-d-_);this._w=(g-p)/y,this._x=.25*y,this._y=(o+u)/y,this._z=(c+h)/y}else if(d>_){const y=2*Math.sqrt(1+d-s-_);this._w=(c-h)/y,this._x=(o+u)/y,this._y=.25*y,this._z=(p+g)/y}else{const y=2*Math.sqrt(1+_-s-d);this._w=(u-o)/y,this._x=(c+h)/y,this._y=(p+g)/y,this._z=.25*y}return this._onChangeCallback(),this}setFromUnitVectors(t,n){let s=t.dot(n)+1;return s<1e-8?(s=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=s):(this._x=0,this._y=-t.z,this._z=t.y,this._w=s)):(this._x=t.y*n.z-t.z*n.y,this._y=t.z*n.x-t.x*n.z,this._z=t.x*n.y-t.y*n.x,this._w=s),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(Ee(this.dot(t),-1,1)))}rotateTowards(t,n){const s=this.angleTo(t);if(s===0)return this;const o=Math.min(1,n/s);return this.slerp(t,o),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,n){const s=t._x,o=t._y,c=t._z,u=t._w,d=n._x,p=n._y,h=n._z,g=n._w;return this._x=s*g+u*d+o*h-c*p,this._y=o*g+u*p+c*d-s*h,this._z=c*g+u*h+s*p-o*d,this._w=u*g-s*d-o*p-c*h,this._onChangeCallback(),this}slerp(t,n){let s=t._x,o=t._y,c=t._z,u=t._w,d=this.dot(t);d<0&&(s=-s,o=-o,c=-c,u=-u,d=-d);let p=1-n;if(d<.9995){const h=Math.acos(d),g=Math.sin(h);p=Math.sin(p*h)/g,n=Math.sin(n*h)/g,this._x=this._x*p+s*n,this._y=this._y*p+o*n,this._z=this._z*p+c*n,this._w=this._w*p+u*n,this._onChangeCallback()}else this._x=this._x*p+s*n,this._y=this._y*p+o*n,this._z=this._z*p+c*n,this._w=this._w*p+u*n,this.normalize();return this}slerpQuaternions(t,n,s){return this.copy(t).slerp(n,s)}random(){const t=2*Math.PI*Math.random(),n=2*Math.PI*Math.random(),s=Math.random(),o=Math.sqrt(1-s),c=Math.sqrt(s);return this.set(o*Math.sin(t),o*Math.cos(t),c*Math.sin(n),c*Math.cos(n))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,n=0){return this._x=t[n],this._y=t[n+1],this._z=t[n+2],this._w=t[n+3],this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._w,t}fromBufferAttribute(t,n){return this._x=t.getX(n),this._y=t.getY(n),this._z=t.getZ(n),this._w=t.getW(n),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}const Og=class Og{constructor(t=0,n=0,s=0){this.x=t,this.y=n,this.z=s}set(t,n,s){return s===void 0&&(s=this.z),this.x=t,this.y=n,this.z=s,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,n){return this.x=t.x*n.x,this.y=t.y*n.y,this.z=t.z*n.z,this}applyEuler(t){return this.applyQuaternion(Bx.setFromEuler(t))}applyAxisAngle(t,n){return this.applyQuaternion(Bx.setFromAxisAngle(t,n))}applyMatrix3(t){const n=this.x,s=this.y,o=this.z,c=t.elements;return this.x=c[0]*n+c[3]*s+c[6]*o,this.y=c[1]*n+c[4]*s+c[7]*o,this.z=c[2]*n+c[5]*s+c[8]*o,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const n=this.x,s=this.y,o=this.z,c=t.elements,u=1/(c[3]*n+c[7]*s+c[11]*o+c[15]);return this.x=(c[0]*n+c[4]*s+c[8]*o+c[12])*u,this.y=(c[1]*n+c[5]*s+c[9]*o+c[13])*u,this.z=(c[2]*n+c[6]*s+c[10]*o+c[14])*u,this}applyQuaternion(t){const n=this.x,s=this.y,o=this.z,c=t.x,u=t.y,d=t.z,p=t.w,h=2*(u*o-d*s),g=2*(d*n-c*o),_=2*(c*s-u*n);return this.x=n+p*h+u*_-d*g,this.y=s+p*g+d*h-c*_,this.z=o+p*_+c*g-u*h,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const n=this.x,s=this.y,o=this.z,c=t.elements;return this.x=c[0]*n+c[4]*s+c[8]*o,this.y=c[1]*n+c[5]*s+c[9]*o,this.z=c[2]*n+c[6]*s+c[10]*o,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,n){return this.x=Ee(this.x,t.x,n.x),this.y=Ee(this.y,t.y,n.y),this.z=Ee(this.z,t.z,n.z),this}clampScalar(t,n){return this.x=Ee(this.x,t,n),this.y=Ee(this.y,t,n),this.z=Ee(this.z,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(Ee(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,n){const s=t.x,o=t.y,c=t.z,u=n.x,d=n.y,p=n.z;return this.x=o*p-c*d,this.y=c*u-s*p,this.z=s*d-o*u,this}projectOnVector(t){const n=t.lengthSq();if(n===0)return this.set(0,0,0);const s=t.dot(this)/n;return this.copy(t).multiplyScalar(s)}projectOnPlane(t){return Hh.copy(this).projectOnVector(t),this.sub(Hh)}reflect(t){return this.sub(Hh.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(Ee(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y,o=this.z-t.z;return n*n+s*s+o*o}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,n,s){const o=Math.sin(n)*t;return this.x=o*Math.sin(s),this.y=Math.cos(n)*t,this.z=o*Math.cos(s),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,n,s){return this.x=t*Math.sin(n),this.y=s,this.z=t*Math.cos(n),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this}setFromMatrixScale(t){const n=this.setFromMatrixColumn(t,0).length(),s=this.setFromMatrixColumn(t,1).length(),o=this.setFromMatrixColumn(t,2).length();return this.x=n,this.y=s,this.z=o,this}setFromMatrixColumn(t,n){return this.fromArray(t.elements,n*4)}setFromMatrix3Column(t,n){return this.fromArray(t.elements,n*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,n=Math.random()*2-1,s=Math.sqrt(1-n*n);return this.x=s*Math.cos(t),this.y=n,this.z=s*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}};Og.prototype.isVector3=!0;let rt=Og;const Hh=new rt,Bx=new To,Fg=class Fg{constructor(t,n,s,o,c,u,d,p,h){this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,n,s,o,c,u,d,p,h)}set(t,n,s,o,c,u,d,p,h){const g=this.elements;return g[0]=t,g[1]=o,g[2]=d,g[3]=n,g[4]=c,g[5]=p,g[6]=s,g[7]=u,g[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],this}extractBasis(t,n,s){return t.setFromMatrix3Column(this,0),n.setFromMatrix3Column(this,1),s.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const n=t.elements;return this.set(n[0],n[4],n[8],n[1],n[5],n[9],n[2],n[6],n[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,o=n.elements,c=this.elements,u=s[0],d=s[3],p=s[6],h=s[1],g=s[4],_=s[7],v=s[2],y=s[5],b=s[8],R=o[0],S=o[3],x=o[6],A=o[1],N=o[4],L=o[7],H=o[2],B=o[5],O=o[8];return c[0]=u*R+d*A+p*H,c[3]=u*S+d*N+p*B,c[6]=u*x+d*L+p*O,c[1]=h*R+g*A+_*H,c[4]=h*S+g*N+_*B,c[7]=h*x+g*L+_*O,c[2]=v*R+y*A+b*H,c[5]=v*S+y*N+b*B,c[8]=v*x+y*L+b*O,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[3]*=t,n[6]*=t,n[1]*=t,n[4]*=t,n[7]*=t,n[2]*=t,n[5]*=t,n[8]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],u=t[4],d=t[5],p=t[6],h=t[7],g=t[8];return n*u*g-n*d*h-s*c*g+s*d*p+o*c*h-o*u*p}invert(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],u=t[4],d=t[5],p=t[6],h=t[7],g=t[8],_=g*u-d*h,v=d*p-g*c,y=h*c-u*p,b=n*_+s*v+o*y;if(b===0)return this.set(0,0,0,0,0,0,0,0,0);const R=1/b;return t[0]=_*R,t[1]=(o*h-g*s)*R,t[2]=(d*s-o*u)*R,t[3]=v*R,t[4]=(g*n-o*p)*R,t[5]=(o*c-d*n)*R,t[6]=y*R,t[7]=(s*p-h*n)*R,t[8]=(u*n-s*c)*R,this}transpose(){let t;const n=this.elements;return t=n[1],n[1]=n[3],n[3]=t,t=n[2],n[2]=n[6],n[6]=t,t=n[5],n[5]=n[7],n[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const n=this.elements;return t[0]=n[0],t[1]=n[3],t[2]=n[6],t[3]=n[1],t[4]=n[4],t[5]=n[7],t[6]=n[2],t[7]=n[5],t[8]=n[8],this}setUvTransform(t,n,s,o,c,u,d){const p=Math.cos(c),h=Math.sin(c);return this.set(s*p,s*h,-s*(p*u+h*d)+u+t,-o*h,o*p,-o*(-h*u+p*d)+d+n,0,0,1),this}scale(t,n){return this.premultiply(Gh.makeScale(t,n)),this}rotate(t){return this.premultiply(Gh.makeRotation(-t)),this}translate(t,n){return this.premultiply(Gh.makeTranslation(t,n)),this}makeTranslation(t,n){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,n,0,0,1),this}makeRotation(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,s,n,0,0,0,1),this}makeScale(t,n){return this.set(t,0,0,0,n,0,0,0,1),this}equals(t){const n=this.elements,s=t.elements;for(let o=0;o<9;o++)if(n[o]!==s[o])return!1;return!0}fromArray(t,n=0){for(let s=0;s<9;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t}clone(){return new this.constructor().fromArray(this.elements)}};Fg.prototype.isMatrix3=!0;let oe=Fg;const Gh=new oe,Ix=new oe().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),zx=new oe().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function EA(){const i={enabled:!0,workingColorSpace:ef,spaces:{},convert:function(o,c,u){return this.enabled===!1||c===u||!c||!u||(this.spaces[c].transfer===ze&&(o.r=Ha(o.r),o.g=Ha(o.g),o.b=Ha(o.b)),this.spaces[c].primaries!==this.spaces[u].primaries&&(o.applyMatrix3(this.spaces[c].toXYZ),o.applyMatrix3(this.spaces[u].fromXYZ)),this.spaces[u].transfer===ze&&(o.r=_o(o.r),o.g=_o(o.g),o.b=_o(o.b))),o},workingToColorSpace:function(o,c){return this.convert(o,this.workingColorSpace,c)},colorSpaceToWorking:function(o,c){return this.convert(o,c,this.workingColorSpace)},getPrimaries:function(o){return this.spaces[o].primaries},getTransfer:function(o){return o===As?nf:this.spaces[o].transfer},getToneMappingMode:function(o){return this.spaces[o].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(o,c=this.workingColorSpace){return o.fromArray(this.spaces[c].luminanceCoefficients)},define:function(o){Object.assign(this.spaces,o)},_getMatrix:function(o,c,u){return o.copy(this.spaces[c].toXYZ).multiply(this.spaces[u].fromXYZ)},_getDrawingBufferColorSpace:function(o){return this.spaces[o].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(o=this.workingColorSpace){return this.spaces[o].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(o,c){return xm("ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),i.workingToColorSpace(o,c)},toWorkingColorSpace:function(o,c){return xm("ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),i.colorSpaceToWorking(o,c)}},t=[.64,.33,.3,.6,.15,.06],n=[.2126,.7152,.0722],s=[.3127,.329];return i.define({[ef]:{primaries:t,whitePoint:s,transfer:nf,toXYZ:Ix,fromXYZ:zx,luminanceCoefficients:n,workingColorSpaceConfig:{unpackColorSpace:wi},outputColorSpaceConfig:{drawingBufferColorSpace:wi}},[wi]:{primaries:t,whitePoint:s,transfer:ze,toXYZ:Ix,fromXYZ:zx,luminanceCoefficients:n,outputColorSpaceConfig:{drawingBufferColorSpace:wi}}}),i}const be=EA();function Ha(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function _o(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let Jr;class TA{static getDataURL(t,n="image/png"){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let s;if(t instanceof HTMLCanvasElement)s=t;else{Jr===void 0&&(Jr=sf("canvas")),Jr.width=t.width,Jr.height=t.height;const o=Jr.getContext("2d");t instanceof ImageData?o.putImageData(t,0,0):o.drawImage(t,0,0,t.width,t.height),s=Jr}return s.toDataURL(n)}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const n=sf("canvas");n.width=t.width,n.height=t.height;const s=n.getContext("2d");s.drawImage(t,0,0,t.width,t.height);const o=s.getImageData(0,0,t.width,t.height),c=o.data;for(let u=0;u<c.length;u++)c[u]=Ha(c[u]/255)*255;return s.putImageData(o,0,0),n}else if(t.data){const n=t.data.slice(0);for(let s=0;s<n.length;s++)n instanceof Uint8Array||n instanceof Uint8ClampedArray?n[s]=Math.floor(Ha(n[s]/255)*255):n[s]=Ha(n[s]);return{data:n,width:t.width,height:t.height}}else return ie("ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let AA=0;class sg{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:AA++}),this.uuid=Wl(),this.data=t,this.dataReady=!0,this.version=0}getSize(t){const n=this.data;return typeof HTMLVideoElement<"u"&&n instanceof HTMLVideoElement?t.set(n.videoWidth,n.videoHeight,0):typeof VideoFrame<"u"&&n instanceof VideoFrame?t.set(n.displayWidth,n.displayHeight,0):n!==null?t.set(n.width,n.height,n.depth||0):t.set(0,0,0),t}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const s={uuid:this.uuid,url:""},o=this.data;if(o!==null){let c;if(Array.isArray(o)){c=[];for(let u=0,d=o.length;u<d;u++)o[u].isDataTexture?c.push(kh(o[u].image)):c.push(kh(o[u]))}else c=kh(o);s.url=c}return n||(t.images[this.uuid]=s),s}}function kh(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?TA.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(ie("Texture: Unable to serialize Texture."),{})}let RA=0;const jh=new rt;class Kn extends vr{constructor(t=Kn.DEFAULT_IMAGE,n=Kn.DEFAULT_MAPPING,s=za,o=za,c=jn,u=or,d=Xi,p=Ni,h=Kn.DEFAULT_ANISOTROPY,g=As){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:RA++}),this.uuid=Wl(),this.name="",this.source=new sg(t),this.mipmaps=[],this.mapping=n,this.channel=0,this.wrapS=s,this.wrapT=o,this.magFilter=c,this.minFilter=u,this.anisotropy=h,this.format=d,this.internalFormat=null,this.type=p,this.offset=new je(0,0),this.repeat=new je(1,1),this.center=new je(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new oe,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=g,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(t&&t.depth&&t.depth>1),this.pmremVersion=0,this.normalized=!1}get width(){return this.source.getSize(jh).x}get height(){return this.source.getSize(jh).y}get depth(){return this.source.getSize(jh).z}get image(){return this.source.data}set image(t){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(t,n){this.updateRanges.push({start:t,count:n})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.normalized=t.normalized,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.renderTarget=t.renderTarget,this.isRenderTargetTexture=t.isRenderTargetTexture,this.isArrayTexture=t.isArrayTexture,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}setValues(t){for(const n in t){const s=t[n];if(s===void 0){ie(`Texture.setValues(): parameter '${n}' has value of undefined.`);continue}const o=this[n];if(o===void 0){ie(`Texture.setValues(): property '${n}' does not exist.`);continue}o&&s&&o.isVector2&&s.isVector2||o&&s&&o.isVector3&&s.isVector3||o&&s&&o.isMatrix3&&s.isMatrix3?o.copy(s):this[n]=s}}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const s={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,normalized:this.normalized,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(s.userData=this.userData),n||(t.textures[this.uuid]=s),s}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==sM)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case Hp:t.x=t.x-Math.floor(t.x);break;case za:t.x=t.x<0?0:1;break;case Gp:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case Hp:t.y=t.y-Math.floor(t.y);break;case za:t.y=t.y<0?0:1;break;case Gp:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}Kn.DEFAULT_IMAGE=null;Kn.DEFAULT_MAPPING=sM;Kn.DEFAULT_ANISOTROPY=1;const Bg=class Bg{constructor(t=0,n=0,s=0,o=1){this.x=t,this.y=n,this.z=s,this.w=o}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,n,s,o){return this.x=t,this.y=n,this.z=s,this.w=o,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;case 3:this.w=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this.w=t.w+n.w,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this.w+=t.w*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this.w=t.w-n.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const n=this.x,s=this.y,o=this.z,c=this.w,u=t.elements;return this.x=u[0]*n+u[4]*s+u[8]*o+u[12]*c,this.y=u[1]*n+u[5]*s+u[9]*o+u[13]*c,this.z=u[2]*n+u[6]*s+u[10]*o+u[14]*c,this.w=u[3]*n+u[7]*s+u[11]*o+u[15]*c,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const n=Math.sqrt(1-t.w*t.w);return n<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/n,this.y=t.y/n,this.z=t.z/n),this}setAxisAngleFromRotationMatrix(t){let n,s,o,c;const p=t.elements,h=p[0],g=p[4],_=p[8],v=p[1],y=p[5],b=p[9],R=p[2],S=p[6],x=p[10];if(Math.abs(g-v)<.01&&Math.abs(_-R)<.01&&Math.abs(b-S)<.01){if(Math.abs(g+v)<.1&&Math.abs(_+R)<.1&&Math.abs(b+S)<.1&&Math.abs(h+y+x-3)<.1)return this.set(1,0,0,0),this;n=Math.PI;const N=(h+1)/2,L=(y+1)/2,H=(x+1)/2,B=(g+v)/4,O=(_+R)/4,E=(b+S)/4;return N>L&&N>H?N<.01?(s=0,o=.707106781,c=.707106781):(s=Math.sqrt(N),o=B/s,c=O/s):L>H?L<.01?(s=.707106781,o=0,c=.707106781):(o=Math.sqrt(L),s=B/o,c=E/o):H<.01?(s=.707106781,o=.707106781,c=0):(c=Math.sqrt(H),s=O/c,o=E/c),this.set(s,o,c,n),this}let A=Math.sqrt((S-b)*(S-b)+(_-R)*(_-R)+(v-g)*(v-g));return Math.abs(A)<.001&&(A=1),this.x=(S-b)/A,this.y=(_-R)/A,this.z=(v-g)/A,this.w=Math.acos((h+y+x-1)/2),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this.w=n[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,n){return this.x=Ee(this.x,t.x,n.x),this.y=Ee(this.y,t.y,n.y),this.z=Ee(this.z,t.z,n.z),this.w=Ee(this.w,t.w,n.w),this}clampScalar(t,n){return this.x=Ee(this.x,t,n),this.y=Ee(this.y,t,n),this.z=Ee(this.z,t,n),this.w=Ee(this.w,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(Ee(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this.w+=(t.w-this.w)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this.w=t.w+(n.w-t.w)*s,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this.w=t[n+3],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t[n+3]=this.w,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this.w=t.getW(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}};Bg.prototype.isVector4=!0;let hn=Bg;class CA extends vr{constructor(t=1,n=1,s={}){super(),s=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:jn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1},s),this.isRenderTarget=!0,this.width=t,this.height=n,this.depth=s.depth,this.scissor=new hn(0,0,t,n),this.scissorTest=!1,this.viewport=new hn(0,0,t,n),this.textures=[];const o={width:t,height:n,depth:s.depth},c=new Kn(o),u=s.count;for(let d=0;d<u;d++)this.textures[d]=c.clone(),this.textures[d].isRenderTargetTexture=!0,this.textures[d].renderTarget=this;this._setTextureOptions(s),this.depthBuffer=s.depthBuffer,this.stencilBuffer=s.stencilBuffer,this.resolveDepthBuffer=s.resolveDepthBuffer,this.resolveStencilBuffer=s.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=s.depthTexture,this.samples=s.samples,this.multiview=s.multiview}_setTextureOptions(t={}){const n={minFilter:jn,generateMipmaps:!1,flipY:!1,internalFormat:null};t.mapping!==void 0&&(n.mapping=t.mapping),t.wrapS!==void 0&&(n.wrapS=t.wrapS),t.wrapT!==void 0&&(n.wrapT=t.wrapT),t.wrapR!==void 0&&(n.wrapR=t.wrapR),t.magFilter!==void 0&&(n.magFilter=t.magFilter),t.minFilter!==void 0&&(n.minFilter=t.minFilter),t.format!==void 0&&(n.format=t.format),t.type!==void 0&&(n.type=t.type),t.anisotropy!==void 0&&(n.anisotropy=t.anisotropy),t.colorSpace!==void 0&&(n.colorSpace=t.colorSpace),t.flipY!==void 0&&(n.flipY=t.flipY),t.generateMipmaps!==void 0&&(n.generateMipmaps=t.generateMipmaps),t.internalFormat!==void 0&&(n.internalFormat=t.internalFormat);for(let s=0;s<this.textures.length;s++)this.textures[s].setValues(n)}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}set depthTexture(t){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),t!==null&&(t.renderTarget=this),this._depthTexture=t}get depthTexture(){return this._depthTexture}setSize(t,n,s=1){if(this.width!==t||this.height!==n||this.depth!==s){this.width=t,this.height=n,this.depth=s;for(let o=0,c=this.textures.length;o<c;o++)this.textures[o].image.width=t,this.textures[o].image.height=n,this.textures[o].image.depth=s,this.textures[o].isData3DTexture!==!0&&(this.textures[o].isArrayTexture=this.textures[o].image.depth>1);this.dispose()}this.viewport.set(0,0,t,n),this.scissor.set(0,0,t,n)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let n=0,s=t.textures.length;n<s;n++){this.textures[n]=t.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0,this.textures[n].renderTarget=this;const o=Object.assign({},t.textures[n].image);this.textures[n].source=new sg(o)}return this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this.multiview=t.multiview,this}dispose(){this.dispatchEvent({type:"dispose"})}}class la extends CA{constructor(t=1,n=1,s={}){super(t,n,s),this.isWebGLRenderTarget=!0}}class pM extends Kn{constructor(t=null,n=1,s=1,o=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:n,height:s,depth:o},this.magFilter=Bn,this.minFilter=Bn,this.wrapR=za,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class wA extends Kn{constructor(t=null,n=1,s=1,o=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:n,height:s,depth:o},this.magFilter=Bn,this.minFilter=Bn,this.wrapR=za,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const gf=class gf{constructor(t,n,s,o,c,u,d,p,h,g,_,v,y,b,R,S){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,n,s,o,c,u,d,p,h,g,_,v,y,b,R,S)}set(t,n,s,o,c,u,d,p,h,g,_,v,y,b,R,S){const x=this.elements;return x[0]=t,x[4]=n,x[8]=s,x[12]=o,x[1]=c,x[5]=u,x[9]=d,x[13]=p,x[2]=h,x[6]=g,x[10]=_,x[14]=v,x[3]=y,x[7]=b,x[11]=R,x[15]=S,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new gf().fromArray(this.elements)}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],n[9]=s[9],n[10]=s[10],n[11]=s[11],n[12]=s[12],n[13]=s[13],n[14]=s[14],n[15]=s[15],this}copyPosition(t){const n=this.elements,s=t.elements;return n[12]=s[12],n[13]=s[13],n[14]=s[14],this}setFromMatrix3(t){const n=t.elements;return this.set(n[0],n[3],n[6],0,n[1],n[4],n[7],0,n[2],n[5],n[8],0,0,0,0,1),this}extractBasis(t,n,s){return this.determinant()===0?(t.set(1,0,0),n.set(0,1,0),s.set(0,0,1),this):(t.setFromMatrixColumn(this,0),n.setFromMatrixColumn(this,1),s.setFromMatrixColumn(this,2),this)}makeBasis(t,n,s){return this.set(t.x,n.x,s.x,0,t.y,n.y,s.y,0,t.z,n.z,s.z,0,0,0,0,1),this}extractRotation(t){if(t.determinant()===0)return this.identity();const n=this.elements,s=t.elements,o=1/$r.setFromMatrixColumn(t,0).length(),c=1/$r.setFromMatrixColumn(t,1).length(),u=1/$r.setFromMatrixColumn(t,2).length();return n[0]=s[0]*o,n[1]=s[1]*o,n[2]=s[2]*o,n[3]=0,n[4]=s[4]*c,n[5]=s[5]*c,n[6]=s[6]*c,n[7]=0,n[8]=s[8]*u,n[9]=s[9]*u,n[10]=s[10]*u,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromEuler(t){const n=this.elements,s=t.x,o=t.y,c=t.z,u=Math.cos(s),d=Math.sin(s),p=Math.cos(o),h=Math.sin(o),g=Math.cos(c),_=Math.sin(c);if(t.order==="XYZ"){const v=u*g,y=u*_,b=d*g,R=d*_;n[0]=p*g,n[4]=-p*_,n[8]=h,n[1]=y+b*h,n[5]=v-R*h,n[9]=-d*p,n[2]=R-v*h,n[6]=b+y*h,n[10]=u*p}else if(t.order==="YXZ"){const v=p*g,y=p*_,b=h*g,R=h*_;n[0]=v+R*d,n[4]=b*d-y,n[8]=u*h,n[1]=u*_,n[5]=u*g,n[9]=-d,n[2]=y*d-b,n[6]=R+v*d,n[10]=u*p}else if(t.order==="ZXY"){const v=p*g,y=p*_,b=h*g,R=h*_;n[0]=v-R*d,n[4]=-u*_,n[8]=b+y*d,n[1]=y+b*d,n[5]=u*g,n[9]=R-v*d,n[2]=-u*h,n[6]=d,n[10]=u*p}else if(t.order==="ZYX"){const v=u*g,y=u*_,b=d*g,R=d*_;n[0]=p*g,n[4]=b*h-y,n[8]=v*h+R,n[1]=p*_,n[5]=R*h+v,n[9]=y*h-b,n[2]=-h,n[6]=d*p,n[10]=u*p}else if(t.order==="YZX"){const v=u*p,y=u*h,b=d*p,R=d*h;n[0]=p*g,n[4]=R-v*_,n[8]=b*_+y,n[1]=_,n[5]=u*g,n[9]=-d*g,n[2]=-h*g,n[6]=y*_+b,n[10]=v-R*_}else if(t.order==="XZY"){const v=u*p,y=u*h,b=d*p,R=d*h;n[0]=p*g,n[4]=-_,n[8]=h*g,n[1]=v*_+R,n[5]=u*g,n[9]=y*_-b,n[2]=b*_-y,n[6]=d*g,n[10]=R*_+v}return n[3]=0,n[7]=0,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromQuaternion(t){return this.compose(DA,t,NA)}lookAt(t,n,s){const o=this.elements;return mi.subVectors(t,n),mi.lengthSq()===0&&(mi.z=1),mi.normalize(),ys.crossVectors(s,mi),ys.lengthSq()===0&&(Math.abs(s.z)===1?mi.x+=1e-4:mi.z+=1e-4,mi.normalize(),ys.crossVectors(s,mi)),ys.normalize(),fu.crossVectors(mi,ys),o[0]=ys.x,o[4]=fu.x,o[8]=mi.x,o[1]=ys.y,o[5]=fu.y,o[9]=mi.y,o[2]=ys.z,o[6]=fu.z,o[10]=mi.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,o=n.elements,c=this.elements,u=s[0],d=s[4],p=s[8],h=s[12],g=s[1],_=s[5],v=s[9],y=s[13],b=s[2],R=s[6],S=s[10],x=s[14],A=s[3],N=s[7],L=s[11],H=s[15],B=o[0],O=o[4],E=o[8],U=o[12],V=o[1],F=o[5],j=o[9],lt=o[13],ct=o[2],q=o[6],I=o[10],G=o[14],$=o[3],dt=o[7],xt=o[11],z=o[15];return c[0]=u*B+d*V+p*ct+h*$,c[4]=u*O+d*F+p*q+h*dt,c[8]=u*E+d*j+p*I+h*xt,c[12]=u*U+d*lt+p*G+h*z,c[1]=g*B+_*V+v*ct+y*$,c[5]=g*O+_*F+v*q+y*dt,c[9]=g*E+_*j+v*I+y*xt,c[13]=g*U+_*lt+v*G+y*z,c[2]=b*B+R*V+S*ct+x*$,c[6]=b*O+R*F+S*q+x*dt,c[10]=b*E+R*j+S*I+x*xt,c[14]=b*U+R*lt+S*G+x*z,c[3]=A*B+N*V+L*ct+H*$,c[7]=A*O+N*F+L*q+H*dt,c[11]=A*E+N*j+L*I+H*xt,c[15]=A*U+N*lt+L*G+H*z,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[4]*=t,n[8]*=t,n[12]*=t,n[1]*=t,n[5]*=t,n[9]*=t,n[13]*=t,n[2]*=t,n[6]*=t,n[10]*=t,n[14]*=t,n[3]*=t,n[7]*=t,n[11]*=t,n[15]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[4],o=t[8],c=t[12],u=t[1],d=t[5],p=t[9],h=t[13],g=t[2],_=t[6],v=t[10],y=t[14],b=t[3],R=t[7],S=t[11],x=t[15],A=p*y-h*v,N=d*y-h*_,L=d*v-p*_,H=u*y-h*g,B=u*v-p*g,O=u*_-d*g;return n*(R*A-S*N+x*L)-s*(b*A-S*H+x*B)+o*(b*N-R*H+x*O)-c*(b*L-R*B+S*O)}transpose(){const t=this.elements;let n;return n=t[1],t[1]=t[4],t[4]=n,n=t[2],t[2]=t[8],t[8]=n,n=t[6],t[6]=t[9],t[9]=n,n=t[3],t[3]=t[12],t[12]=n,n=t[7],t[7]=t[13],t[13]=n,n=t[11],t[11]=t[14],t[14]=n,this}setPosition(t,n,s){const o=this.elements;return t.isVector3?(o[12]=t.x,o[13]=t.y,o[14]=t.z):(o[12]=t,o[13]=n,o[14]=s),this}invert(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],u=t[4],d=t[5],p=t[6],h=t[7],g=t[8],_=t[9],v=t[10],y=t[11],b=t[12],R=t[13],S=t[14],x=t[15],A=n*d-s*u,N=n*p-o*u,L=n*h-c*u,H=s*p-o*d,B=s*h-c*d,O=o*h-c*p,E=g*R-_*b,U=g*S-v*b,V=g*x-y*b,F=_*S-v*R,j=_*x-y*R,lt=v*x-y*S,ct=A*lt-N*j+L*F+H*V-B*U+O*E;if(ct===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const q=1/ct;return t[0]=(d*lt-p*j+h*F)*q,t[1]=(o*j-s*lt-c*F)*q,t[2]=(R*O-S*B+x*H)*q,t[3]=(v*B-_*O-y*H)*q,t[4]=(p*V-u*lt-h*U)*q,t[5]=(n*lt-o*V+c*U)*q,t[6]=(S*L-b*O-x*N)*q,t[7]=(g*O-v*L+y*N)*q,t[8]=(u*j-d*V+h*E)*q,t[9]=(s*V-n*j-c*E)*q,t[10]=(b*B-R*L+x*A)*q,t[11]=(_*L-g*B-y*A)*q,t[12]=(d*U-u*F-p*E)*q,t[13]=(n*F-s*U+o*E)*q,t[14]=(R*N-b*H-S*A)*q,t[15]=(g*H-_*N+v*A)*q,this}scale(t){const n=this.elements,s=t.x,o=t.y,c=t.z;return n[0]*=s,n[4]*=o,n[8]*=c,n[1]*=s,n[5]*=o,n[9]*=c,n[2]*=s,n[6]*=o,n[10]*=c,n[3]*=s,n[7]*=o,n[11]*=c,this}getMaxScaleOnAxis(){const t=this.elements,n=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],s=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],o=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(n,s,o))}makeTranslation(t,n,s){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,n,0,0,1,s,0,0,0,1),this}makeRotationX(t){const n=Math.cos(t),s=Math.sin(t);return this.set(1,0,0,0,0,n,-s,0,0,s,n,0,0,0,0,1),this}makeRotationY(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,0,s,0,0,1,0,0,-s,0,n,0,0,0,0,1),this}makeRotationZ(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,0,s,n,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,n){const s=Math.cos(n),o=Math.sin(n),c=1-s,u=t.x,d=t.y,p=t.z,h=c*u,g=c*d;return this.set(h*u+s,h*d-o*p,h*p+o*d,0,h*d+o*p,g*d+s,g*p-o*u,0,h*p-o*d,g*p+o*u,c*p*p+s,0,0,0,0,1),this}makeScale(t,n,s){return this.set(t,0,0,0,0,n,0,0,0,0,s,0,0,0,0,1),this}makeShear(t,n,s,o,c,u){return this.set(1,s,c,0,t,1,u,0,n,o,1,0,0,0,0,1),this}compose(t,n,s){const o=this.elements,c=n._x,u=n._y,d=n._z,p=n._w,h=c+c,g=u+u,_=d+d,v=c*h,y=c*g,b=c*_,R=u*g,S=u*_,x=d*_,A=p*h,N=p*g,L=p*_,H=s.x,B=s.y,O=s.z;return o[0]=(1-(R+x))*H,o[1]=(y+L)*H,o[2]=(b-N)*H,o[3]=0,o[4]=(y-L)*B,o[5]=(1-(v+x))*B,o[6]=(S+A)*B,o[7]=0,o[8]=(b+N)*O,o[9]=(S-A)*O,o[10]=(1-(v+R))*O,o[11]=0,o[12]=t.x,o[13]=t.y,o[14]=t.z,o[15]=1,this}decompose(t,n,s){const o=this.elements;t.x=o[12],t.y=o[13],t.z=o[14];const c=this.determinant();if(c===0)return s.set(1,1,1),n.identity(),this;let u=$r.set(o[0],o[1],o[2]).length();const d=$r.set(o[4],o[5],o[6]).length(),p=$r.set(o[8],o[9],o[10]).length();c<0&&(u=-u),zi.copy(this);const h=1/u,g=1/d,_=1/p;return zi.elements[0]*=h,zi.elements[1]*=h,zi.elements[2]*=h,zi.elements[4]*=g,zi.elements[5]*=g,zi.elements[6]*=g,zi.elements[8]*=_,zi.elements[9]*=_,zi.elements[10]*=_,n.setFromRotationMatrix(zi),s.x=u,s.y=d,s.z=p,this}makePerspective(t,n,s,o,c,u,d=ra,p=!1){const h=this.elements,g=2*c/(n-t),_=2*c/(s-o),v=(n+t)/(n-t),y=(s+o)/(s-o);let b,R;if(p)b=c/(u-c),R=u*c/(u-c);else if(d===ra)b=-(u+c)/(u-c),R=-2*u*c/(u-c);else if(d===af)b=-u/(u-c),R=-u*c/(u-c);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+d);return h[0]=g,h[4]=0,h[8]=v,h[12]=0,h[1]=0,h[5]=_,h[9]=y,h[13]=0,h[2]=0,h[6]=0,h[10]=b,h[14]=R,h[3]=0,h[7]=0,h[11]=-1,h[15]=0,this}makeOrthographic(t,n,s,o,c,u,d=ra,p=!1){const h=this.elements,g=2/(n-t),_=2/(s-o),v=-(n+t)/(n-t),y=-(s+o)/(s-o);let b,R;if(p)b=1/(u-c),R=u/(u-c);else if(d===ra)b=-2/(u-c),R=-(u+c)/(u-c);else if(d===af)b=-1/(u-c),R=-c/(u-c);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+d);return h[0]=g,h[4]=0,h[8]=0,h[12]=v,h[1]=0,h[5]=_,h[9]=0,h[13]=y,h[2]=0,h[6]=0,h[10]=b,h[14]=R,h[3]=0,h[7]=0,h[11]=0,h[15]=1,this}equals(t){const n=this.elements,s=t.elements;for(let o=0;o<16;o++)if(n[o]!==s[o])return!1;return!0}fromArray(t,n=0){for(let s=0;s<16;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t[n+9]=s[9],t[n+10]=s[10],t[n+11]=s[11],t[n+12]=s[12],t[n+13]=s[13],t[n+14]=s[14],t[n+15]=s[15],t}};gf.prototype.isMatrix4=!0;let Sn=gf;const $r=new rt,zi=new Sn,DA=new rt(0,0,0),NA=new rt(1,1,1),ys=new rt,fu=new rt,mi=new rt,Vx=new Sn,Hx=new To;class mr{constructor(t=0,n=0,s=0,o=mr.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=n,this._z=s,this._order=o}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,n,s,o=this._order){return this._x=t,this._y=n,this._z=s,this._order=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,n=this._order,s=!0){const o=t.elements,c=o[0],u=o[4],d=o[8],p=o[1],h=o[5],g=o[9],_=o[2],v=o[6],y=o[10];switch(n){case"XYZ":this._y=Math.asin(Ee(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(-g,y),this._z=Math.atan2(-u,c)):(this._x=Math.atan2(v,h),this._z=0);break;case"YXZ":this._x=Math.asin(-Ee(g,-1,1)),Math.abs(g)<.9999999?(this._y=Math.atan2(d,y),this._z=Math.atan2(p,h)):(this._y=Math.atan2(-_,c),this._z=0);break;case"ZXY":this._x=Math.asin(Ee(v,-1,1)),Math.abs(v)<.9999999?(this._y=Math.atan2(-_,y),this._z=Math.atan2(-u,h)):(this._y=0,this._z=Math.atan2(p,c));break;case"ZYX":this._y=Math.asin(-Ee(_,-1,1)),Math.abs(_)<.9999999?(this._x=Math.atan2(v,y),this._z=Math.atan2(p,c)):(this._x=0,this._z=Math.atan2(-u,h));break;case"YZX":this._z=Math.asin(Ee(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-g,h),this._y=Math.atan2(-_,c)):(this._x=0,this._y=Math.atan2(d,y));break;case"XZY":this._z=Math.asin(-Ee(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(v,h),this._y=Math.atan2(d,c)):(this._x=Math.atan2(-g,y),this._y=0);break;default:ie("Euler: .setFromRotationMatrix() encountered an unknown order: "+n)}return this._order=n,s===!0&&this._onChangeCallback(),this}setFromQuaternion(t,n,s){return Vx.makeRotationFromQuaternion(t),this.setFromRotationMatrix(Vx,n,s)}setFromVector3(t,n=this._order){return this.set(t.x,t.y,t.z,n)}reorder(t){return Hx.setFromEuler(this),this.setFromQuaternion(Hx,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}mr.DEFAULT_ORDER="XYZ";class mM{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let LA=0;const Gx=new rt,to=new To,La=new Sn,du=new rt,Tl=new rt,UA=new rt,PA=new To,kx=new rt(1,0,0),jx=new rt(0,1,0),Xx=new rt(0,0,1),Wx={type:"added"},OA={type:"removed"},eo={type:"childadded",child:null},Xh={type:"childremoved",child:null};class ai extends vr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:LA++}),this.uuid=Wl(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=ai.DEFAULT_UP.clone();const t=new rt,n=new mr,s=new To,o=new rt(1,1,1);function c(){s.setFromEuler(n,!1)}function u(){n.setFromQuaternion(s,void 0,!1)}n._onChange(c),s._onChange(u),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:n},quaternion:{configurable:!0,enumerable:!0,value:s},scale:{configurable:!0,enumerable:!0,value:o},modelViewMatrix:{value:new Sn},normalMatrix:{value:new oe}}),this.matrix=new Sn,this.matrixWorld=new Sn,this.matrixAutoUpdate=ai.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=ai.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new mM,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,n){this.quaternion.setFromAxisAngle(t,n)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,n){return to.setFromAxisAngle(t,n),this.quaternion.multiply(to),this}rotateOnWorldAxis(t,n){return to.setFromAxisAngle(t,n),this.quaternion.premultiply(to),this}rotateX(t){return this.rotateOnAxis(kx,t)}rotateY(t){return this.rotateOnAxis(jx,t)}rotateZ(t){return this.rotateOnAxis(Xx,t)}translateOnAxis(t,n){return Gx.copy(t).applyQuaternion(this.quaternion),this.position.add(Gx.multiplyScalar(n)),this}translateX(t){return this.translateOnAxis(kx,t)}translateY(t){return this.translateOnAxis(jx,t)}translateZ(t){return this.translateOnAxis(Xx,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(La.copy(this.matrixWorld).invert())}lookAt(t,n,s){t.isVector3?du.copy(t):du.set(t,n,s);const o=this.parent;this.updateWorldMatrix(!0,!1),Tl.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?La.lookAt(Tl,du,this.up):La.lookAt(du,Tl,this.up),this.quaternion.setFromRotationMatrix(La),o&&(La.extractRotation(o.matrixWorld),to.setFromRotationMatrix(La),this.quaternion.premultiply(to.invert()))}add(t){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.add(arguments[n]);return this}return t===this?(Te("Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(Wx),eo.child=t,this.dispatchEvent(eo),eo.child=null):Te("Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let s=0;s<arguments.length;s++)this.remove(arguments[s]);return this}const n=this.children.indexOf(t);return n!==-1&&(t.parent=null,this.children.splice(n,1),t.dispatchEvent(OA),Xh.child=t,this.dispatchEvent(Xh),Xh.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),La.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),La.multiply(t.parent.matrixWorld)),t.applyMatrix4(La),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(Wx),eo.child=t,this.dispatchEvent(eo),eo.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,n){if(this[t]===n)return this;for(let s=0,o=this.children.length;s<o;s++){const u=this.children[s].getObjectByProperty(t,n);if(u!==void 0)return u}}getObjectsByProperty(t,n,s=[]){this[t]===n&&s.push(this);const o=this.children;for(let c=0,u=o.length;c<u;c++)o[c].getObjectsByProperty(t,n,s);return s}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Tl,t,UA),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Tl,PA,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const n=this.matrixWorld.elements;return t.set(n[8],n[9],n[10]).normalize()}raycast(){}traverse(t){t(this);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].traverseVisible(t)}traverseAncestors(t){const n=this.parent;n!==null&&(t(n),n.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);const t=this.pivot;if(t!==null){const n=t.x,s=t.y,o=t.z,c=this.matrix.elements;c[12]+=n-c[0]*n-c[4]*s-c[8]*o,c[13]+=s-c[1]*n-c[5]*s-c[9]*o,c[14]+=o-c[2]*n-c[6]*s-c[10]*o}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].updateMatrixWorld(t)}updateWorldMatrix(t,n){const s=this.parent;if(t===!0&&s!==null&&s.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),n===!0){const o=this.children;for(let c=0,u=o.length;c<u;c++)o[c].updateWorldMatrix(!1,!0)}}toJSON(t){const n=t===void 0||typeof t=="string",s={};n&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},s.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const o={};o.uuid=this.uuid,o.type=this.type,this.name!==""&&(o.name=this.name),this.castShadow===!0&&(o.castShadow=!0),this.receiveShadow===!0&&(o.receiveShadow=!0),this.visible===!1&&(o.visible=!1),this.frustumCulled===!1&&(o.frustumCulled=!1),this.renderOrder!==0&&(o.renderOrder=this.renderOrder),this.static!==!1&&(o.static=this.static),Object.keys(this.userData).length>0&&(o.userData=this.userData),o.layers=this.layers.mask,o.matrix=this.matrix.toArray(),o.up=this.up.toArray(),this.pivot!==null&&(o.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(o.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(o.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(o.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(o.type="InstancedMesh",o.count=this.count,o.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(o.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(o.type="BatchedMesh",o.perObjectFrustumCulled=this.perObjectFrustumCulled,o.sortObjects=this.sortObjects,o.drawRanges=this._drawRanges,o.reservedRanges=this._reservedRanges,o.geometryInfo=this._geometryInfo.map(d=>({...d,boundingBox:d.boundingBox?d.boundingBox.toJSON():void 0,boundingSphere:d.boundingSphere?d.boundingSphere.toJSON():void 0})),o.instanceInfo=this._instanceInfo.map(d=>({...d})),o.availableInstanceIds=this._availableInstanceIds.slice(),o.availableGeometryIds=this._availableGeometryIds.slice(),o.nextIndexStart=this._nextIndexStart,o.nextVertexStart=this._nextVertexStart,o.geometryCount=this._geometryCount,o.maxInstanceCount=this._maxInstanceCount,o.maxVertexCount=this._maxVertexCount,o.maxIndexCount=this._maxIndexCount,o.geometryInitialized=this._geometryInitialized,o.matricesTexture=this._matricesTexture.toJSON(t),o.indirectTexture=this._indirectTexture.toJSON(t),this._colorsTexture!==null&&(o.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(o.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(o.boundingBox=this.boundingBox.toJSON()));function c(d,p){return d[p.uuid]===void 0&&(d[p.uuid]=p.toJSON(t)),p.uuid}if(this.isScene)this.background&&(this.background.isColor?o.background=this.background.toJSON():this.background.isTexture&&(o.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(o.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){o.geometry=c(t.geometries,this.geometry);const d=this.geometry.parameters;if(d!==void 0&&d.shapes!==void 0){const p=d.shapes;if(Array.isArray(p))for(let h=0,g=p.length;h<g;h++){const _=p[h];c(t.shapes,_)}else c(t.shapes,p)}}if(this.isSkinnedMesh&&(o.bindMode=this.bindMode,o.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(c(t.skeletons,this.skeleton),o.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const d=[];for(let p=0,h=this.material.length;p<h;p++)d.push(c(t.materials,this.material[p]));o.material=d}else o.material=c(t.materials,this.material);if(this.children.length>0){o.children=[];for(let d=0;d<this.children.length;d++)o.children.push(this.children[d].toJSON(t).object)}if(this.animations.length>0){o.animations=[];for(let d=0;d<this.animations.length;d++){const p=this.animations[d];o.animations.push(c(t.animations,p))}}if(n){const d=u(t.geometries),p=u(t.materials),h=u(t.textures),g=u(t.images),_=u(t.shapes),v=u(t.skeletons),y=u(t.animations),b=u(t.nodes);d.length>0&&(s.geometries=d),p.length>0&&(s.materials=p),h.length>0&&(s.textures=h),g.length>0&&(s.images=g),_.length>0&&(s.shapes=_),v.length>0&&(s.skeletons=v),y.length>0&&(s.animations=y),b.length>0&&(s.nodes=b)}return s.object=o,s;function u(d){const p=[];for(const h in d){const g=d[h];delete g.metadata,p.push(g)}return p}}clone(t){return new this.constructor().copy(this,t)}copy(t,n=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.pivot=t.pivot!==null?t.pivot.clone():null,this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.static=t.static,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),n===!0)for(let s=0;s<t.children.length;s++){const o=t.children[s];this.add(o.clone())}return this}}ai.DEFAULT_UP=new rt(0,1,0);ai.DEFAULT_MATRIX_AUTO_UPDATE=!0;ai.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;class hu extends ai{constructor(){super(),this.isGroup=!0,this.type="Group"}}const FA={type:"move"};class Wh{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new hu,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new hu,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new rt,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new rt),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new hu,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new rt,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new rt,this._grip.eventsEnabled=!1),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const n=this._hand;if(n)for(const s of t.hand.values())this._getHandJoint(n,s)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,n,s){let o=null,c=null,u=null;const d=this._targetRay,p=this._grip,h=this._hand;if(t&&n.session.visibilityState!=="visible-blurred"){if(h&&t.hand){u=!0;for(const R of t.hand.values()){const S=n.getJointPose(R,s),x=this._getHandJoint(h,R);S!==null&&(x.matrix.fromArray(S.transform.matrix),x.matrix.decompose(x.position,x.rotation,x.scale),x.matrixWorldNeedsUpdate=!0,x.jointRadius=S.radius),x.visible=S!==null}const g=h.joints["index-finger-tip"],_=h.joints["thumb-tip"],v=g.position.distanceTo(_.position),y=.02,b=.005;h.inputState.pinching&&v>y+b?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!h.inputState.pinching&&v<=y-b&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else p!==null&&t.gripSpace&&(c=n.getPose(t.gripSpace,s),c!==null&&(p.matrix.fromArray(c.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,c.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(c.linearVelocity)):p.hasLinearVelocity=!1,c.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(c.angularVelocity)):p.hasAngularVelocity=!1,p.eventsEnabled&&p.dispatchEvent({type:"gripUpdated",data:t,target:this})));d!==null&&(o=n.getPose(t.targetRaySpace,s),o===null&&c!==null&&(o=c),o!==null&&(d.matrix.fromArray(o.transform.matrix),d.matrix.decompose(d.position,d.rotation,d.scale),d.matrixWorldNeedsUpdate=!0,o.linearVelocity?(d.hasLinearVelocity=!0,d.linearVelocity.copy(o.linearVelocity)):d.hasLinearVelocity=!1,o.angularVelocity?(d.hasAngularVelocity=!0,d.angularVelocity.copy(o.angularVelocity)):d.hasAngularVelocity=!1,this.dispatchEvent(FA)))}return d!==null&&(d.visible=o!==null),p!==null&&(p.visible=c!==null),h!==null&&(h.visible=u!==null),this}_getHandJoint(t,n){if(t.joints[n.jointName]===void 0){const s=new hu;s.matrixAutoUpdate=!1,s.visible=!1,t.joints[n.jointName]=s,t.add(s)}return t.joints[n.jointName]}}const gM={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Ss={h:0,s:0,l:0},pu={h:0,s:0,l:0};function qh(i,t,n){return n<0&&(n+=1),n>1&&(n-=1),n<1/6?i+(t-i)*6*n:n<1/2?t:n<2/3?i+(t-i)*6*(2/3-n):i}class Le{constructor(t,n,s){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,n,s)}set(t,n,s){if(n===void 0&&s===void 0){const o=t;o&&o.isColor?this.copy(o):typeof o=="number"?this.setHex(o):typeof o=="string"&&this.setStyle(o)}else this.setRGB(t,n,s);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,n=wi){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,be.colorSpaceToWorking(this,n),this}setRGB(t,n,s,o=be.workingColorSpace){return this.r=t,this.g=n,this.b=s,be.colorSpaceToWorking(this,o),this}setHSL(t,n,s,o=be.workingColorSpace){if(t=bA(t,1),n=Ee(n,0,1),s=Ee(s,0,1),n===0)this.r=this.g=this.b=s;else{const c=s<=.5?s*(1+n):s+n-s*n,u=2*s-c;this.r=qh(u,c,t+1/3),this.g=qh(u,c,t),this.b=qh(u,c,t-1/3)}return be.colorSpaceToWorking(this,o),this}setStyle(t,n=wi){function s(c){c!==void 0&&parseFloat(c)<1&&ie("Color: Alpha component of "+t+" will be ignored.")}let o;if(o=/^(\w+)\(([^\)]*)\)/.exec(t)){let c;const u=o[1],d=o[2];switch(u){case"rgb":case"rgba":if(c=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(255,parseInt(c[1],10))/255,Math.min(255,parseInt(c[2],10))/255,Math.min(255,parseInt(c[3],10))/255,n);if(c=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(100,parseInt(c[1],10))/100,Math.min(100,parseInt(c[2],10))/100,Math.min(100,parseInt(c[3],10))/100,n);break;case"hsl":case"hsla":if(c=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setHSL(parseFloat(c[1])/360,parseFloat(c[2])/100,parseFloat(c[3])/100,n);break;default:ie("Color: Unknown color model "+t)}}else if(o=/^\#([A-Fa-f\d]+)$/.exec(t)){const c=o[1],u=c.length;if(u===3)return this.setRGB(parseInt(c.charAt(0),16)/15,parseInt(c.charAt(1),16)/15,parseInt(c.charAt(2),16)/15,n);if(u===6)return this.setHex(parseInt(c,16),n);ie("Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,n);return this}setColorName(t,n=wi){const s=gM[t.toLowerCase()];return s!==void 0?this.setHex(s,n):ie("Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=Ha(t.r),this.g=Ha(t.g),this.b=Ha(t.b),this}copyLinearToSRGB(t){return this.r=_o(t.r),this.g=_o(t.g),this.b=_o(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=wi){return be.workingToColorSpace(kn.copy(this),t),Math.round(Ee(kn.r*255,0,255))*65536+Math.round(Ee(kn.g*255,0,255))*256+Math.round(Ee(kn.b*255,0,255))}getHexString(t=wi){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,n=be.workingColorSpace){be.workingToColorSpace(kn.copy(this),n);const s=kn.r,o=kn.g,c=kn.b,u=Math.max(s,o,c),d=Math.min(s,o,c);let p,h;const g=(d+u)/2;if(d===u)p=0,h=0;else{const _=u-d;switch(h=g<=.5?_/(u+d):_/(2-u-d),u){case s:p=(o-c)/_+(o<c?6:0);break;case o:p=(c-s)/_+2;break;case c:p=(s-o)/_+4;break}p/=6}return t.h=p,t.s=h,t.l=g,t}getRGB(t,n=be.workingColorSpace){return be.workingToColorSpace(kn.copy(this),n),t.r=kn.r,t.g=kn.g,t.b=kn.b,t}getStyle(t=wi){be.workingToColorSpace(kn.copy(this),t);const n=kn.r,s=kn.g,o=kn.b;return t!==wi?`color(${t} ${n.toFixed(3)} ${s.toFixed(3)} ${o.toFixed(3)})`:`rgb(${Math.round(n*255)},${Math.round(s*255)},${Math.round(o*255)})`}offsetHSL(t,n,s){return this.getHSL(Ss),this.setHSL(Ss.h+t,Ss.s+n,Ss.l+s)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,n){return this.r=t.r+n.r,this.g=t.g+n.g,this.b=t.b+n.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,n){return this.r+=(t.r-this.r)*n,this.g+=(t.g-this.g)*n,this.b+=(t.b-this.b)*n,this}lerpColors(t,n,s){return this.r=t.r+(n.r-t.r)*s,this.g=t.g+(n.g-t.g)*s,this.b=t.b+(n.b-t.b)*s,this}lerpHSL(t,n){this.getHSL(Ss),t.getHSL(pu);const s=Vh(Ss.h,pu.h,n),o=Vh(Ss.s,pu.s,n),c=Vh(Ss.l,pu.l,n);return this.setHSL(s,o,c),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const n=this.r,s=this.g,o=this.b,c=t.elements;return this.r=c[0]*n+c[3]*s+c[6]*o,this.g=c[1]*n+c[4]*s+c[7]*o,this.b=c[2]*n+c[5]*s+c[8]*o,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,n=0){return this.r=t[n],this.g=t[n+1],this.b=t[n+2],this}toArray(t=[],n=0){return t[n]=this.r,t[n+1]=this.g,t[n+2]=this.b,t}fromBufferAttribute(t,n){return this.r=t.getX(n),this.g=t.getY(n),this.b=t.getZ(n),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const kn=new Le;Le.NAMES=gM;class rg{constructor(t,n=1,s=1e3){this.isFog=!0,this.name="",this.color=new Le(t),this.near=n,this.far=s}clone(){return new rg(this.color,this.near,this.far)}toJSON(){return{type:"Fog",name:this.name,color:this.color.getHex(),near:this.near,far:this.far}}}class BA extends ai{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new mr,this.environmentIntensity=1,this.environmentRotation=new mr,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,n){return super.copy(t,n),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const n=super.toJSON(t);return this.fog!==null&&(n.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(n.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(n.object.backgroundIntensity=this.backgroundIntensity),n.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(n.object.environmentIntensity=this.environmentIntensity),n.object.environmentRotation=this.environmentRotation.toArray(),n}}const Vi=new rt,Ua=new rt,Yh=new rt,Pa=new rt,no=new rt,io=new rt,qx=new rt,Kh=new rt,Zh=new rt,Qh=new rt,Jh=new hn,$h=new hn,tp=new hn;class ji{constructor(t=new rt,n=new rt,s=new rt){this.a=t,this.b=n,this.c=s}static getNormal(t,n,s,o){o.subVectors(s,n),Vi.subVectors(t,n),o.cross(Vi);const c=o.lengthSq();return c>0?o.multiplyScalar(1/Math.sqrt(c)):o.set(0,0,0)}static getBarycoord(t,n,s,o,c){Vi.subVectors(o,n),Ua.subVectors(s,n),Yh.subVectors(t,n);const u=Vi.dot(Vi),d=Vi.dot(Ua),p=Vi.dot(Yh),h=Ua.dot(Ua),g=Ua.dot(Yh),_=u*h-d*d;if(_===0)return c.set(0,0,0),null;const v=1/_,y=(h*p-d*g)*v,b=(u*g-d*p)*v;return c.set(1-y-b,b,y)}static containsPoint(t,n,s,o){return this.getBarycoord(t,n,s,o,Pa)===null?!1:Pa.x>=0&&Pa.y>=0&&Pa.x+Pa.y<=1}static getInterpolation(t,n,s,o,c,u,d,p){return this.getBarycoord(t,n,s,o,Pa)===null?(p.x=0,p.y=0,"z"in p&&(p.z=0),"w"in p&&(p.w=0),null):(p.setScalar(0),p.addScaledVector(c,Pa.x),p.addScaledVector(u,Pa.y),p.addScaledVector(d,Pa.z),p)}static getInterpolatedAttribute(t,n,s,o,c,u){return Jh.setScalar(0),$h.setScalar(0),tp.setScalar(0),Jh.fromBufferAttribute(t,n),$h.fromBufferAttribute(t,s),tp.fromBufferAttribute(t,o),u.setScalar(0),u.addScaledVector(Jh,c.x),u.addScaledVector($h,c.y),u.addScaledVector(tp,c.z),u}static isFrontFacing(t,n,s,o){return Vi.subVectors(s,n),Ua.subVectors(t,n),Vi.cross(Ua).dot(o)<0}set(t,n,s){return this.a.copy(t),this.b.copy(n),this.c.copy(s),this}setFromPointsAndIndices(t,n,s,o){return this.a.copy(t[n]),this.b.copy(t[s]),this.c.copy(t[o]),this}setFromAttributeAndIndices(t,n,s,o){return this.a.fromBufferAttribute(t,n),this.b.fromBufferAttribute(t,s),this.c.fromBufferAttribute(t,o),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return Vi.subVectors(this.c,this.b),Ua.subVectors(this.a,this.b),Vi.cross(Ua).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return ji.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,n){return ji.getBarycoord(t,this.a,this.b,this.c,n)}getInterpolation(t,n,s,o,c){return ji.getInterpolation(t,this.a,this.b,this.c,n,s,o,c)}containsPoint(t){return ji.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return ji.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,n){const s=this.a,o=this.b,c=this.c;let u,d;no.subVectors(o,s),io.subVectors(c,s),Kh.subVectors(t,s);const p=no.dot(Kh),h=io.dot(Kh);if(p<=0&&h<=0)return n.copy(s);Zh.subVectors(t,o);const g=no.dot(Zh),_=io.dot(Zh);if(g>=0&&_<=g)return n.copy(o);const v=p*_-g*h;if(v<=0&&p>=0&&g<=0)return u=p/(p-g),n.copy(s).addScaledVector(no,u);Qh.subVectors(t,c);const y=no.dot(Qh),b=io.dot(Qh);if(b>=0&&y<=b)return n.copy(c);const R=y*h-p*b;if(R<=0&&h>=0&&b<=0)return d=h/(h-b),n.copy(s).addScaledVector(io,d);const S=g*b-y*_;if(S<=0&&_-g>=0&&y-b>=0)return qx.subVectors(c,o),d=(_-g)/(_-g+(y-b)),n.copy(o).addScaledVector(qx,d);const x=1/(S+R+v);return u=R*x,d=v*x,n.copy(s).addScaledVector(no,u).addScaledVector(io,d)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}class ql{constructor(t=new rt(1/0,1/0,1/0),n=new rt(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=n}set(t,n){return this.min.copy(t),this.max.copy(n),this}setFromArray(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n+=3)this.expandByPoint(Hi.fromArray(t,n));return this}setFromBufferAttribute(t){this.makeEmpty();for(let n=0,s=t.count;n<s;n++)this.expandByPoint(Hi.fromBufferAttribute(t,n));return this}setFromPoints(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n++)this.expandByPoint(t[n]);return this}setFromCenterAndSize(t,n){const s=Hi.copy(n).multiplyScalar(.5);return this.min.copy(t).sub(s),this.max.copy(t).add(s),this}setFromObject(t,n=!1){return this.makeEmpty(),this.expandByObject(t,n)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,n=!1){t.updateWorldMatrix(!1,!1);const s=t.geometry;if(s!==void 0){const c=s.getAttribute("position");if(n===!0&&c!==void 0&&t.isInstancedMesh!==!0)for(let u=0,d=c.count;u<d;u++)t.isMesh===!0?t.getVertexPosition(u,Hi):Hi.fromBufferAttribute(c,u),Hi.applyMatrix4(t.matrixWorld),this.expandByPoint(Hi);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),mu.copy(t.boundingBox)):(s.boundingBox===null&&s.computeBoundingBox(),mu.copy(s.boundingBox)),mu.applyMatrix4(t.matrixWorld),this.union(mu)}const o=t.children;for(let c=0,u=o.length;c<u;c++)this.expandByObject(o[c],n);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,n){return n.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Hi),Hi.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let n,s;return t.normal.x>0?(n=t.normal.x*this.min.x,s=t.normal.x*this.max.x):(n=t.normal.x*this.max.x,s=t.normal.x*this.min.x),t.normal.y>0?(n+=t.normal.y*this.min.y,s+=t.normal.y*this.max.y):(n+=t.normal.y*this.max.y,s+=t.normal.y*this.min.y),t.normal.z>0?(n+=t.normal.z*this.min.z,s+=t.normal.z*this.max.z):(n+=t.normal.z*this.max.z,s+=t.normal.z*this.min.z),n<=-t.constant&&s>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Al),gu.subVectors(this.max,Al),ao.subVectors(t.a,Al),so.subVectors(t.b,Al),ro.subVectors(t.c,Al),Ms.subVectors(so,ao),bs.subVectors(ro,so),Js.subVectors(ao,ro);let n=[0,-Ms.z,Ms.y,0,-bs.z,bs.y,0,-Js.z,Js.y,Ms.z,0,-Ms.x,bs.z,0,-bs.x,Js.z,0,-Js.x,-Ms.y,Ms.x,0,-bs.y,bs.x,0,-Js.y,Js.x,0];return!ep(n,ao,so,ro,gu)||(n=[1,0,0,0,1,0,0,0,1],!ep(n,ao,so,ro,gu))?!1:(_u.crossVectors(Ms,bs),n=[_u.x,_u.y,_u.z],ep(n,ao,so,ro,gu))}clampPoint(t,n){return n.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Hi).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Hi).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(Oa[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),Oa[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),Oa[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),Oa[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),Oa[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),Oa[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),Oa[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),Oa[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(Oa),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(t){return this.min.fromArray(t.min),this.max.fromArray(t.max),this}}const Oa=[new rt,new rt,new rt,new rt,new rt,new rt,new rt,new rt],Hi=new rt,mu=new ql,ao=new rt,so=new rt,ro=new rt,Ms=new rt,bs=new rt,Js=new rt,Al=new rt,gu=new rt,_u=new rt,$s=new rt;function ep(i,t,n,s,o){for(let c=0,u=i.length-3;c<=u;c+=3){$s.fromArray(i,c);const d=o.x*Math.abs($s.x)+o.y*Math.abs($s.y)+o.z*Math.abs($s.z),p=t.dot($s),h=n.dot($s),g=s.dot($s);if(Math.max(-Math.max(p,h,g),Math.min(p,h,g))>d)return!1}return!0}const xn=new rt,vu=new je;let IA=0;class ca extends vr{constructor(t,n,s=!1){if(super(),Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:IA++}),this.name="",this.array=t,this.itemSize=n,this.count=t!==void 0?t.length/n:0,this.normalized=s,this.usage=Ux,this.updateRanges=[],this.gpuType=sa,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,n){this.updateRanges.push({start:t,count:n})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,n,s){t*=this.itemSize,s*=n.itemSize;for(let o=0,c=this.itemSize;o<c;o++)this.array[t+o]=n.array[s+o];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let n=0,s=this.count;n<s;n++)vu.fromBufferAttribute(this,n),vu.applyMatrix3(t),this.setXY(n,vu.x,vu.y);else if(this.itemSize===3)for(let n=0,s=this.count;n<s;n++)xn.fromBufferAttribute(this,n),xn.applyMatrix3(t),this.setXYZ(n,xn.x,xn.y,xn.z);return this}applyMatrix4(t){for(let n=0,s=this.count;n<s;n++)xn.fromBufferAttribute(this,n),xn.applyMatrix4(t),this.setXYZ(n,xn.x,xn.y,xn.z);return this}applyNormalMatrix(t){for(let n=0,s=this.count;n<s;n++)xn.fromBufferAttribute(this,n),xn.applyNormalMatrix(t),this.setXYZ(n,xn.x,xn.y,xn.z);return this}transformDirection(t){for(let n=0,s=this.count;n<s;n++)xn.fromBufferAttribute(this,n),xn.transformDirection(t),this.setXYZ(n,xn.x,xn.y,xn.z);return this}set(t,n=0){return this.array.set(t,n),this}getComponent(t,n){let s=this.array[t*this.itemSize+n];return this.normalized&&(s=El(s,this.array)),s}setComponent(t,n,s){return this.normalized&&(s=ni(s,this.array)),this.array[t*this.itemSize+n]=s,this}getX(t){let n=this.array[t*this.itemSize];return this.normalized&&(n=El(n,this.array)),n}setX(t,n){return this.normalized&&(n=ni(n,this.array)),this.array[t*this.itemSize]=n,this}getY(t){let n=this.array[t*this.itemSize+1];return this.normalized&&(n=El(n,this.array)),n}setY(t,n){return this.normalized&&(n=ni(n,this.array)),this.array[t*this.itemSize+1]=n,this}getZ(t){let n=this.array[t*this.itemSize+2];return this.normalized&&(n=El(n,this.array)),n}setZ(t,n){return this.normalized&&(n=ni(n,this.array)),this.array[t*this.itemSize+2]=n,this}getW(t){let n=this.array[t*this.itemSize+3];return this.normalized&&(n=El(n,this.array)),n}setW(t,n){return this.normalized&&(n=ni(n,this.array)),this.array[t*this.itemSize+3]=n,this}setXY(t,n,s){return t*=this.itemSize,this.normalized&&(n=ni(n,this.array),s=ni(s,this.array)),this.array[t+0]=n,this.array[t+1]=s,this}setXYZ(t,n,s,o){return t*=this.itemSize,this.normalized&&(n=ni(n,this.array),s=ni(s,this.array),o=ni(o,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=o,this}setXYZW(t,n,s,o,c){return t*=this.itemSize,this.normalized&&(n=ni(n,this.array),s=ni(s,this.array),o=ni(o,this.array),c=ni(c,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=o,this.array[t+3]=c,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==Ux&&(t.usage=this.usage),t}dispose(){this.dispatchEvent({type:"dispose"})}}class _M extends ca{constructor(t,n,s){super(new Uint16Array(t),n,s)}}class vM extends ca{constructor(t,n,s){super(new Uint32Array(t),n,s)}}class Wi extends ca{constructor(t,n,s){super(new Float32Array(t),n,s)}}const zA=new ql,Rl=new rt,np=new rt;class vf{constructor(t=new rt,n=-1){this.isSphere=!0,this.center=t,this.radius=n}set(t,n){return this.center.copy(t),this.radius=n,this}setFromPoints(t,n){const s=this.center;n!==void 0?s.copy(n):zA.setFromPoints(t).getCenter(s);let o=0;for(let c=0,u=t.length;c<u;c++)o=Math.max(o,s.distanceToSquared(t[c]));return this.radius=Math.sqrt(o),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const n=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=n*n}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,n){const s=this.center.distanceToSquared(t);return n.copy(t),s>this.radius*this.radius&&(n.sub(this.center).normalize(),n.multiplyScalar(this.radius).add(this.center)),n}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Rl.subVectors(t,this.center);const n=Rl.lengthSq();if(n>this.radius*this.radius){const s=Math.sqrt(n),o=(s-this.radius)*.5;this.center.addScaledVector(Rl,o/s),this.radius+=o}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(np.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Rl.copy(t.center).add(np)),this.expandByPoint(Rl.copy(t.center).sub(np))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(t){return this.radius=t.radius,this.center.fromArray(t.center),this}}let VA=0;const Ci=new Sn,ip=new ai,oo=new rt,gi=new ql,Cl=new ql,wn=new rt;class Yi extends vr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:VA++}),this.uuid=Wl(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(xA(t)?vM:_M)(t,1):this.index=t,this}setIndirect(t,n=0){return this.indirect=t,this.indirectOffset=n,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,n){return this.attributes[t]=n,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,n,s=0){this.groups.push({start:t,count:n,materialIndex:s})}clearGroups(){this.groups=[]}setDrawRange(t,n){this.drawRange.start=t,this.drawRange.count=n}applyMatrix4(t){const n=this.attributes.position;n!==void 0&&(n.applyMatrix4(t),n.needsUpdate=!0);const s=this.attributes.normal;if(s!==void 0){const c=new oe().getNormalMatrix(t);s.applyNormalMatrix(c),s.needsUpdate=!0}const o=this.attributes.tangent;return o!==void 0&&(o.transformDirection(t),o.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return Ci.makeRotationFromQuaternion(t),this.applyMatrix4(Ci),this}rotateX(t){return Ci.makeRotationX(t),this.applyMatrix4(Ci),this}rotateY(t){return Ci.makeRotationY(t),this.applyMatrix4(Ci),this}rotateZ(t){return Ci.makeRotationZ(t),this.applyMatrix4(Ci),this}translate(t,n,s){return Ci.makeTranslation(t,n,s),this.applyMatrix4(Ci),this}scale(t,n,s){return Ci.makeScale(t,n,s),this.applyMatrix4(Ci),this}lookAt(t){return ip.lookAt(t),ip.updateMatrix(),this.applyMatrix4(ip.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(oo).negate(),this.translate(oo.x,oo.y,oo.z),this}setFromPoints(t){const n=this.getAttribute("position");if(n===void 0){const s=[];for(let o=0,c=t.length;o<c;o++){const u=t[o];s.push(u.x,u.y,u.z||0)}this.setAttribute("position",new Wi(s,3))}else{const s=Math.min(t.length,n.count);for(let o=0;o<s;o++){const c=t[o];n.setXYZ(o,c.x,c.y,c.z||0)}t.length>n.count&&ie("BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),n.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new ql);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){Te("BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new rt(-1/0,-1/0,-1/0),new rt(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),n)for(let s=0,o=n.length;s<o;s++){const c=n[s];gi.setFromBufferAttribute(c),this.morphTargetsRelative?(wn.addVectors(this.boundingBox.min,gi.min),this.boundingBox.expandByPoint(wn),wn.addVectors(this.boundingBox.max,gi.max),this.boundingBox.expandByPoint(wn)):(this.boundingBox.expandByPoint(gi.min),this.boundingBox.expandByPoint(gi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&Te('BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new vf);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){Te("BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new rt,1/0);return}if(t){const s=this.boundingSphere.center;if(gi.setFromBufferAttribute(t),n)for(let c=0,u=n.length;c<u;c++){const d=n[c];Cl.setFromBufferAttribute(d),this.morphTargetsRelative?(wn.addVectors(gi.min,Cl.min),gi.expandByPoint(wn),wn.addVectors(gi.max,Cl.max),gi.expandByPoint(wn)):(gi.expandByPoint(Cl.min),gi.expandByPoint(Cl.max))}gi.getCenter(s);let o=0;for(let c=0,u=t.count;c<u;c++)wn.fromBufferAttribute(t,c),o=Math.max(o,s.distanceToSquared(wn));if(n)for(let c=0,u=n.length;c<u;c++){const d=n[c],p=this.morphTargetsRelative;for(let h=0,g=d.count;h<g;h++)wn.fromBufferAttribute(d,h),p&&(oo.fromBufferAttribute(t,h),wn.add(oo)),o=Math.max(o,s.distanceToSquared(wn))}this.boundingSphere.radius=Math.sqrt(o),isNaN(this.boundingSphere.radius)&&Te('BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,n=this.attributes;if(t===null||n.position===void 0||n.normal===void 0||n.uv===void 0){Te("BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const s=n.position,o=n.normal,c=n.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ca(new Float32Array(4*s.count),4));const u=this.getAttribute("tangent"),d=[],p=[];for(let E=0;E<s.count;E++)d[E]=new rt,p[E]=new rt;const h=new rt,g=new rt,_=new rt,v=new je,y=new je,b=new je,R=new rt,S=new rt;function x(E,U,V){h.fromBufferAttribute(s,E),g.fromBufferAttribute(s,U),_.fromBufferAttribute(s,V),v.fromBufferAttribute(c,E),y.fromBufferAttribute(c,U),b.fromBufferAttribute(c,V),g.sub(h),_.sub(h),y.sub(v),b.sub(v);const F=1/(y.x*b.y-b.x*y.y);isFinite(F)&&(R.copy(g).multiplyScalar(b.y).addScaledVector(_,-y.y).multiplyScalar(F),S.copy(_).multiplyScalar(y.x).addScaledVector(g,-b.x).multiplyScalar(F),d[E].add(R),d[U].add(R),d[V].add(R),p[E].add(S),p[U].add(S),p[V].add(S))}let A=this.groups;A.length===0&&(A=[{start:0,count:t.count}]);for(let E=0,U=A.length;E<U;++E){const V=A[E],F=V.start,j=V.count;for(let lt=F,ct=F+j;lt<ct;lt+=3)x(t.getX(lt+0),t.getX(lt+1),t.getX(lt+2))}const N=new rt,L=new rt,H=new rt,B=new rt;function O(E){H.fromBufferAttribute(o,E),B.copy(H);const U=d[E];N.copy(U),N.sub(H.multiplyScalar(H.dot(U))).normalize(),L.crossVectors(B,U);const F=L.dot(p[E])<0?-1:1;u.setXYZW(E,N.x,N.y,N.z,F)}for(let E=0,U=A.length;E<U;++E){const V=A[E],F=V.start,j=V.count;for(let lt=F,ct=F+j;lt<ct;lt+=3)O(t.getX(lt+0)),O(t.getX(lt+1)),O(t.getX(lt+2))}}computeVertexNormals(){const t=this.index,n=this.getAttribute("position");if(n!==void 0){let s=this.getAttribute("normal");if(s===void 0)s=new ca(new Float32Array(n.count*3),3),this.setAttribute("normal",s);else for(let v=0,y=s.count;v<y;v++)s.setXYZ(v,0,0,0);const o=new rt,c=new rt,u=new rt,d=new rt,p=new rt,h=new rt,g=new rt,_=new rt;if(t)for(let v=0,y=t.count;v<y;v+=3){const b=t.getX(v+0),R=t.getX(v+1),S=t.getX(v+2);o.fromBufferAttribute(n,b),c.fromBufferAttribute(n,R),u.fromBufferAttribute(n,S),g.subVectors(u,c),_.subVectors(o,c),g.cross(_),d.fromBufferAttribute(s,b),p.fromBufferAttribute(s,R),h.fromBufferAttribute(s,S),d.add(g),p.add(g),h.add(g),s.setXYZ(b,d.x,d.y,d.z),s.setXYZ(R,p.x,p.y,p.z),s.setXYZ(S,h.x,h.y,h.z)}else for(let v=0,y=n.count;v<y;v+=3)o.fromBufferAttribute(n,v+0),c.fromBufferAttribute(n,v+1),u.fromBufferAttribute(n,v+2),g.subVectors(u,c),_.subVectors(o,c),g.cross(_),s.setXYZ(v+0,g.x,g.y,g.z),s.setXYZ(v+1,g.x,g.y,g.z),s.setXYZ(v+2,g.x,g.y,g.z);this.normalizeNormals(),s.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let n=0,s=t.count;n<s;n++)wn.fromBufferAttribute(t,n),wn.normalize(),t.setXYZ(n,wn.x,wn.y,wn.z)}toNonIndexed(){function t(d,p){const h=d.array,g=d.itemSize,_=d.normalized,v=new h.constructor(p.length*g);let y=0,b=0;for(let R=0,S=p.length;R<S;R++){d.isInterleavedBufferAttribute?y=p[R]*d.data.stride+d.offset:y=p[R]*g;for(let x=0;x<g;x++)v[b++]=h[y++]}return new ca(v,g,_)}if(this.index===null)return ie("BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const n=new Yi,s=this.index.array,o=this.attributes;for(const d in o){const p=o[d],h=t(p,s);n.setAttribute(d,h)}const c=this.morphAttributes;for(const d in c){const p=[],h=c[d];for(let g=0,_=h.length;g<_;g++){const v=h[g],y=t(v,s);p.push(y)}n.morphAttributes[d]=p}n.morphTargetsRelative=this.morphTargetsRelative;const u=this.groups;for(let d=0,p=u.length;d<p;d++){const h=u[d];n.addGroup(h.start,h.count,h.materialIndex)}return n}toJSON(){const t={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const p=this.parameters;for(const h in p)p[h]!==void 0&&(t[h]=p[h]);return t}t.data={attributes:{}};const n=this.index;n!==null&&(t.data.index={type:n.array.constructor.name,array:Array.prototype.slice.call(n.array)});const s=this.attributes;for(const p in s){const h=s[p];t.data.attributes[p]=h.toJSON(t.data)}const o={};let c=!1;for(const p in this.morphAttributes){const h=this.morphAttributes[p],g=[];for(let _=0,v=h.length;_<v;_++){const y=h[_];g.push(y.toJSON(t.data))}g.length>0&&(o[p]=g,c=!0)}c&&(t.data.morphAttributes=o,t.data.morphTargetsRelative=this.morphTargetsRelative);const u=this.groups;u.length>0&&(t.data.groups=JSON.parse(JSON.stringify(u)));const d=this.boundingSphere;return d!==null&&(t.data.boundingSphere=d.toJSON()),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const n={};this.name=t.name;const s=t.index;s!==null&&this.setIndex(s.clone());const o=t.attributes;for(const h in o){const g=o[h];this.setAttribute(h,g.clone(n))}const c=t.morphAttributes;for(const h in c){const g=[],_=c[h];for(let v=0,y=_.length;v<y;v++)g.push(_[v].clone(n));this.morphAttributes[h]=g}this.morphTargetsRelative=t.morphTargetsRelative;const u=t.groups;for(let h=0,g=u.length;h<g;h++){const _=u[h];this.addGroup(_.start,_.count,_.materialIndex)}const d=t.boundingBox;d!==null&&(this.boundingBox=d.clone());const p=t.boundingSphere;return p!==null&&(this.boundingSphere=p.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}let HA=0;class Yl extends vr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:HA++}),this.uuid=Wl(),this.name="",this.type="Material",this.blending=go,this.side=ws,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Lp,this.blendDst=Up,this.blendEquation=sr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Le(0,0,0),this.blendAlpha=0,this.depthFunc=xo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Lx,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Qr,this.stencilZFail=Qr,this.stencilZPass=Qr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const n in t){const s=t[n];if(s===void 0){ie(`Material: parameter '${n}' has value of undefined.`);continue}const o=this[n];if(o===void 0){ie(`Material: '${n}' is not a property of THREE.${this.type}.`);continue}o&&o.isColor?o.set(s):o&&o.isVector3&&s&&s.isVector3?o.copy(s):this[n]=s}}toJSON(t){const n=t===void 0||typeof t=="string";n&&(t={textures:{},images:{}});const s={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.color&&this.color.isColor&&(s.color=this.color.getHex()),this.roughness!==void 0&&(s.roughness=this.roughness),this.metalness!==void 0&&(s.metalness=this.metalness),this.sheen!==void 0&&(s.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(s.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(s.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(s.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(s.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(s.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(s.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(s.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(s.shininess=this.shininess),this.clearcoat!==void 0&&(s.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(s.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(s.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(s.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(s.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,s.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(s.sheenColorMap=this.sheenColorMap.toJSON(t).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(s.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(t).uuid),this.dispersion!==void 0&&(s.dispersion=this.dispersion),this.iridescence!==void 0&&(s.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(s.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(s.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(s.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(s.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(s.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(s.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(s.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(s.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(s.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(s.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(s.lightMap=this.lightMap.toJSON(t).uuid,s.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(s.aoMap=this.aoMap.toJSON(t).uuid,s.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(s.bumpMap=this.bumpMap.toJSON(t).uuid,s.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(s.normalMap=this.normalMap.toJSON(t).uuid,s.normalMapType=this.normalMapType,s.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(s.displacementMap=this.displacementMap.toJSON(t).uuid,s.displacementScale=this.displacementScale,s.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(s.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(s.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(s.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(s.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(s.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(s.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(s.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(s.combine=this.combine)),this.envMapRotation!==void 0&&(s.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(s.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(s.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(s.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(s.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(s.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(s.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(s.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(s.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(s.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(s.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(s.size=this.size),this.shadowSide!==null&&(s.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(s.sizeAttenuation=this.sizeAttenuation),this.blending!==go&&(s.blending=this.blending),this.side!==ws&&(s.side=this.side),this.vertexColors===!0&&(s.vertexColors=!0),this.opacity<1&&(s.opacity=this.opacity),this.transparent===!0&&(s.transparent=!0),this.blendSrc!==Lp&&(s.blendSrc=this.blendSrc),this.blendDst!==Up&&(s.blendDst=this.blendDst),this.blendEquation!==sr&&(s.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(s.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(s.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(s.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(s.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(s.blendAlpha=this.blendAlpha),this.depthFunc!==xo&&(s.depthFunc=this.depthFunc),this.depthTest===!1&&(s.depthTest=this.depthTest),this.depthWrite===!1&&(s.depthWrite=this.depthWrite),this.colorWrite===!1&&(s.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(s.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Lx&&(s.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(s.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(s.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Qr&&(s.stencilFail=this.stencilFail),this.stencilZFail!==Qr&&(s.stencilZFail=this.stencilZFail),this.stencilZPass!==Qr&&(s.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(s.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(s.rotation=this.rotation),this.polygonOffset===!0&&(s.polygonOffset=!0),this.polygonOffsetFactor!==0&&(s.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(s.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(s.linewidth=this.linewidth),this.dashSize!==void 0&&(s.dashSize=this.dashSize),this.gapSize!==void 0&&(s.gapSize=this.gapSize),this.scale!==void 0&&(s.scale=this.scale),this.dithering===!0&&(s.dithering=!0),this.alphaTest>0&&(s.alphaTest=this.alphaTest),this.alphaHash===!0&&(s.alphaHash=!0),this.alphaToCoverage===!0&&(s.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(s.premultipliedAlpha=!0),this.forceSinglePass===!0&&(s.forceSinglePass=!0),this.allowOverride===!1&&(s.allowOverride=!1),this.wireframe===!0&&(s.wireframe=!0),this.wireframeLinewidth>1&&(s.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(s.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(s.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(s.flatShading=!0),this.visible===!1&&(s.visible=!1),this.toneMapped===!1&&(s.toneMapped=!1),this.fog===!1&&(s.fog=!1),Object.keys(this.userData).length>0&&(s.userData=this.userData);function o(c){const u=[];for(const d in c){const p=c[d];delete p.metadata,u.push(p)}return u}if(n){const c=o(t.textures),u=o(t.images);c.length>0&&(s.textures=c),u.length>0&&(s.images=u)}return s}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const n=t.clippingPlanes;let s=null;if(n!==null){const o=n.length;s=new Array(o);for(let c=0;c!==o;++c)s[c]=n[c].clone()}return this.clippingPlanes=s,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.allowOverride=t.allowOverride,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}}const Fa=new rt,ap=new rt,xu=new rt,Es=new rt,sp=new rt,yu=new rt,rp=new rt;class xM{constructor(t=new rt,n=new rt(0,0,-1)){this.origin=t,this.direction=n}set(t,n){return this.origin.copy(t),this.direction.copy(n),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,n){return n.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,Fa)),this}closestPointToPoint(t,n){n.subVectors(t,this.origin);const s=n.dot(this.direction);return s<0?n.copy(this.origin):n.copy(this.origin).addScaledVector(this.direction,s)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const n=Fa.subVectors(t,this.origin).dot(this.direction);return n<0?this.origin.distanceToSquared(t):(Fa.copy(this.origin).addScaledVector(this.direction,n),Fa.distanceToSquared(t))}distanceSqToSegment(t,n,s,o){ap.copy(t).add(n).multiplyScalar(.5),xu.copy(n).sub(t).normalize(),Es.copy(this.origin).sub(ap);const c=t.distanceTo(n)*.5,u=-this.direction.dot(xu),d=Es.dot(this.direction),p=-Es.dot(xu),h=Es.lengthSq(),g=Math.abs(1-u*u);let _,v,y,b;if(g>0)if(_=u*p-d,v=u*d-p,b=c*g,_>=0)if(v>=-b)if(v<=b){const R=1/g;_*=R,v*=R,y=_*(_+u*v+2*d)+v*(u*_+v+2*p)+h}else v=c,_=Math.max(0,-(u*v+d)),y=-_*_+v*(v+2*p)+h;else v=-c,_=Math.max(0,-(u*v+d)),y=-_*_+v*(v+2*p)+h;else v<=-b?(_=Math.max(0,-(-u*c+d)),v=_>0?-c:Math.min(Math.max(-c,-p),c),y=-_*_+v*(v+2*p)+h):v<=b?(_=0,v=Math.min(Math.max(-c,-p),c),y=v*(v+2*p)+h):(_=Math.max(0,-(u*c+d)),v=_>0?c:Math.min(Math.max(-c,-p),c),y=-_*_+v*(v+2*p)+h);else v=u>0?-c:c,_=Math.max(0,-(u*v+d)),y=-_*_+v*(v+2*p)+h;return s&&s.copy(this.origin).addScaledVector(this.direction,_),o&&o.copy(ap).addScaledVector(xu,v),y}intersectSphere(t,n){Fa.subVectors(t.center,this.origin);const s=Fa.dot(this.direction),o=Fa.dot(Fa)-s*s,c=t.radius*t.radius;if(o>c)return null;const u=Math.sqrt(c-o),d=s-u,p=s+u;return p<0?null:d<0?this.at(p,n):this.at(d,n)}intersectsSphere(t){return t.radius<0?!1:this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const n=t.normal.dot(this.direction);if(n===0)return t.distanceToPoint(this.origin)===0?0:null;const s=-(this.origin.dot(t.normal)+t.constant)/n;return s>=0?s:null}intersectPlane(t,n){const s=this.distanceToPlane(t);return s===null?null:this.at(s,n)}intersectsPlane(t){const n=t.distanceToPoint(this.origin);return n===0||t.normal.dot(this.direction)*n<0}intersectBox(t,n){let s,o,c,u,d,p;const h=1/this.direction.x,g=1/this.direction.y,_=1/this.direction.z,v=this.origin;return h>=0?(s=(t.min.x-v.x)*h,o=(t.max.x-v.x)*h):(s=(t.max.x-v.x)*h,o=(t.min.x-v.x)*h),g>=0?(c=(t.min.y-v.y)*g,u=(t.max.y-v.y)*g):(c=(t.max.y-v.y)*g,u=(t.min.y-v.y)*g),s>u||c>o||((c>s||isNaN(s))&&(s=c),(u<o||isNaN(o))&&(o=u),_>=0?(d=(t.min.z-v.z)*_,p=(t.max.z-v.z)*_):(d=(t.max.z-v.z)*_,p=(t.min.z-v.z)*_),s>p||d>o)||((d>s||s!==s)&&(s=d),(p<o||o!==o)&&(o=p),o<0)?null:this.at(s>=0?s:o,n)}intersectsBox(t){return this.intersectBox(t,Fa)!==null}intersectTriangle(t,n,s,o,c){sp.subVectors(n,t),yu.subVectors(s,t),rp.crossVectors(sp,yu);let u=this.direction.dot(rp),d;if(u>0){if(o)return null;d=1}else if(u<0)d=-1,u=-u;else return null;Es.subVectors(this.origin,t);const p=d*this.direction.dot(yu.crossVectors(Es,yu));if(p<0)return null;const h=d*this.direction.dot(sp.cross(Es));if(h<0||p+h>u)return null;const g=-d*Es.dot(rp);return g<0?null:this.at(g/u,c)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class yM extends Yl{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Le(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new mr,this.combine=QS,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const Yx=new Sn,tr=new xM,Su=new vf,Kx=new rt,Mu=new rt,bu=new rt,Eu=new rt,op=new rt,Tu=new rt,Zx=new rt,Au=new rt;class ja extends ai{constructor(t=new Yi,n=new yM){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=n,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(t,n){return super.copy(t,n),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const n=this.geometry.morphAttributes,s=Object.keys(n);if(s.length>0){const o=n[s[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,u=o.length;c<u;c++){const d=o[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}getVertexPosition(t,n){const s=this.geometry,o=s.attributes.position,c=s.morphAttributes.position,u=s.morphTargetsRelative;n.fromBufferAttribute(o,t);const d=this.morphTargetInfluences;if(c&&d){Tu.set(0,0,0);for(let p=0,h=c.length;p<h;p++){const g=d[p],_=c[p];g!==0&&(op.fromBufferAttribute(_,t),u?Tu.addScaledVector(op,g):Tu.addScaledVector(op.sub(n),g))}n.add(Tu)}return n}raycast(t,n){const s=this.geometry,o=this.material,c=this.matrixWorld;o!==void 0&&(s.boundingSphere===null&&s.computeBoundingSphere(),Su.copy(s.boundingSphere),Su.applyMatrix4(c),tr.copy(t.ray).recast(t.near),!(Su.containsPoint(tr.origin)===!1&&(tr.intersectSphere(Su,Kx)===null||tr.origin.distanceToSquared(Kx)>(t.far-t.near)**2))&&(Yx.copy(c).invert(),tr.copy(t.ray).applyMatrix4(Yx),!(s.boundingBox!==null&&tr.intersectsBox(s.boundingBox)===!1)&&this._computeIntersections(t,n,tr)))}_computeIntersections(t,n,s){let o;const c=this.geometry,u=this.material,d=c.index,p=c.attributes.position,h=c.attributes.uv,g=c.attributes.uv1,_=c.attributes.normal,v=c.groups,y=c.drawRange;if(d!==null)if(Array.isArray(u))for(let b=0,R=v.length;b<R;b++){const S=v[b],x=u[S.materialIndex],A=Math.max(S.start,y.start),N=Math.min(d.count,Math.min(S.start+S.count,y.start+y.count));for(let L=A,H=N;L<H;L+=3){const B=d.getX(L),O=d.getX(L+1),E=d.getX(L+2);o=Ru(this,x,t,s,h,g,_,B,O,E),o&&(o.faceIndex=Math.floor(L/3),o.face.materialIndex=S.materialIndex,n.push(o))}}else{const b=Math.max(0,y.start),R=Math.min(d.count,y.start+y.count);for(let S=b,x=R;S<x;S+=3){const A=d.getX(S),N=d.getX(S+1),L=d.getX(S+2);o=Ru(this,u,t,s,h,g,_,A,N,L),o&&(o.faceIndex=Math.floor(S/3),n.push(o))}}else if(p!==void 0)if(Array.isArray(u))for(let b=0,R=v.length;b<R;b++){const S=v[b],x=u[S.materialIndex],A=Math.max(S.start,y.start),N=Math.min(p.count,Math.min(S.start+S.count,y.start+y.count));for(let L=A,H=N;L<H;L+=3){const B=L,O=L+1,E=L+2;o=Ru(this,x,t,s,h,g,_,B,O,E),o&&(o.faceIndex=Math.floor(L/3),o.face.materialIndex=S.materialIndex,n.push(o))}}else{const b=Math.max(0,y.start),R=Math.min(p.count,y.start+y.count);for(let S=b,x=R;S<x;S+=3){const A=S,N=S+1,L=S+2;o=Ru(this,u,t,s,h,g,_,A,N,L),o&&(o.faceIndex=Math.floor(S/3),n.push(o))}}}}function GA(i,t,n,s,o,c,u,d){let p;if(t.side===ii?p=s.intersectTriangle(u,c,o,!0,d):p=s.intersectTriangle(o,c,u,t.side===ws,d),p===null)return null;Au.copy(d),Au.applyMatrix4(i.matrixWorld);const h=n.ray.origin.distanceTo(Au);return h<n.near||h>n.far?null:{distance:h,point:Au.clone(),object:i}}function Ru(i,t,n,s,o,c,u,d,p,h){i.getVertexPosition(d,Mu),i.getVertexPosition(p,bu),i.getVertexPosition(h,Eu);const g=GA(i,t,n,s,Mu,bu,Eu,Zx);if(g){const _=new rt;ji.getBarycoord(Zx,Mu,bu,Eu,_),o&&(g.uv=ji.getInterpolatedAttribute(o,d,p,h,_,new je)),c&&(g.uv1=ji.getInterpolatedAttribute(c,d,p,h,_,new je)),u&&(g.normal=ji.getInterpolatedAttribute(u,d,p,h,_,new rt),g.normal.dot(s.direction)>0&&g.normal.multiplyScalar(-1));const v={a:d,b:p,c:h,normal:new rt,materialIndex:0};ji.getNormal(Mu,bu,Eu,v.normal),g.face=v,g.barycoord=_}return g}class kA extends Kn{constructor(t=null,n=1,s=1,o,c,u,d,p,h=Bn,g=Bn,_,v){super(null,u,d,p,h,g,o,c,_,v),this.isDataTexture=!0,this.image={data:t,width:n,height:s},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const lp=new rt,jA=new rt,XA=new oe;class ir{constructor(t=new rt(1,0,0),n=0){this.isPlane=!0,this.normal=t,this.constant=n}set(t,n){return this.normal.copy(t),this.constant=n,this}setComponents(t,n,s,o){return this.normal.set(t,n,s),this.constant=o,this}setFromNormalAndCoplanarPoint(t,n){return this.normal.copy(t),this.constant=-n.dot(this.normal),this}setFromCoplanarPoints(t,n,s){const o=lp.subVectors(s,n).cross(jA.subVectors(t,n)).normalize();return this.setFromNormalAndCoplanarPoint(o,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,n){return n.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,n,s=!0){const o=t.delta(lp),c=this.normal.dot(o);if(c===0)return this.distanceToPoint(t.start)===0?n.copy(t.start):null;const u=-(t.start.dot(this.normal)+this.constant)/c;return s===!0&&(u<0||u>1)?null:n.copy(t.start).addScaledVector(o,u)}intersectsLine(t){const n=this.distanceToPoint(t.start),s=this.distanceToPoint(t.end);return n<0&&s>0||s<0&&n>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,n){const s=n||XA.getNormalMatrix(t),o=this.coplanarPoint(lp).applyMatrix4(t),c=this.normal.applyMatrix3(s).normalize();return this.constant=-o.dot(c),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const er=new vf,WA=new je(.5,.5),Cu=new rt;class SM{constructor(t=new ir,n=new ir,s=new ir,o=new ir,c=new ir,u=new ir){this.planes=[t,n,s,o,c,u]}set(t,n,s,o,c,u){const d=this.planes;return d[0].copy(t),d[1].copy(n),d[2].copy(s),d[3].copy(o),d[4].copy(c),d[5].copy(u),this}copy(t){const n=this.planes;for(let s=0;s<6;s++)n[s].copy(t.planes[s]);return this}setFromProjectionMatrix(t,n=ra,s=!1){const o=this.planes,c=t.elements,u=c[0],d=c[1],p=c[2],h=c[3],g=c[4],_=c[5],v=c[6],y=c[7],b=c[8],R=c[9],S=c[10],x=c[11],A=c[12],N=c[13],L=c[14],H=c[15];if(o[0].setComponents(h-u,y-g,x-b,H-A).normalize(),o[1].setComponents(h+u,y+g,x+b,H+A).normalize(),o[2].setComponents(h+d,y+_,x+R,H+N).normalize(),o[3].setComponents(h-d,y-_,x-R,H-N).normalize(),s)o[4].setComponents(p,v,S,L).normalize(),o[5].setComponents(h-p,y-v,x-S,H-L).normalize();else if(o[4].setComponents(h-p,y-v,x-S,H-L).normalize(),n===ra)o[5].setComponents(h+p,y+v,x+S,H+L).normalize();else if(n===af)o[5].setComponents(p,v,S,L).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+n);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),er.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const n=t.geometry;n.boundingSphere===null&&n.computeBoundingSphere(),er.copy(n.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(er)}intersectsSprite(t){er.center.set(0,0,0);const n=WA.distanceTo(t.center);return er.radius=.7071067811865476+n,er.applyMatrix4(t.matrixWorld),this.intersectsSphere(er)}intersectsSphere(t){const n=this.planes,s=t.center,o=-t.radius;for(let c=0;c<6;c++)if(n[c].distanceToPoint(s)<o)return!1;return!0}intersectsBox(t){const n=this.planes;for(let s=0;s<6;s++){const o=n[s];if(Cu.x=o.normal.x>0?t.max.x:t.min.x,Cu.y=o.normal.y>0?t.max.y:t.min.y,Cu.z=o.normal.z>0?t.max.z:t.min.z,o.distanceToPoint(Cu)<0)return!1}return!0}containsPoint(t){const n=this.planes;for(let s=0;s<6;s++)if(n[s].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class MM extends Yl{constructor(t){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new Le(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.alphaMap=t.alphaMap,this.size=t.size,this.sizeAttenuation=t.sizeAttenuation,this.fog=t.fog,this}}const Qx=new Sn,Sm=new xM,wu=new vf,Du=new rt;class qA extends ai{constructor(t=new Yi,n=new MM){super(),this.isPoints=!0,this.type="Points",this.geometry=t,this.material=n,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(t,n){return super.copy(t,n),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}raycast(t,n){const s=this.geometry,o=this.matrixWorld,c=t.params.Points.threshold,u=s.drawRange;if(s.boundingSphere===null&&s.computeBoundingSphere(),wu.copy(s.boundingSphere),wu.applyMatrix4(o),wu.radius+=c,t.ray.intersectsSphere(wu)===!1)return;Qx.copy(o).invert(),Sm.copy(t.ray).applyMatrix4(Qx);const d=c/((this.scale.x+this.scale.y+this.scale.z)/3),p=d*d,h=s.index,_=s.attributes.position;if(h!==null){const v=Math.max(0,u.start),y=Math.min(h.count,u.start+u.count);for(let b=v,R=y;b<R;b++){const S=h.getX(b);Du.fromBufferAttribute(_,S),Jx(Du,S,p,o,t,n,this)}}else{const v=Math.max(0,u.start),y=Math.min(_.count,u.start+u.count);for(let b=v,R=y;b<R;b++)Du.fromBufferAttribute(_,b),Jx(Du,b,p,o,t,n,this)}}updateMorphTargets(){const n=this.geometry.morphAttributes,s=Object.keys(n);if(s.length>0){const o=n[s[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,u=o.length;c<u;c++){const d=o[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}}function Jx(i,t,n,s,o,c,u){const d=Sm.distanceSqToPoint(i);if(d<n){const p=new rt;Sm.closestPointToPoint(i,p),p.applyMatrix4(s);const h=o.ray.origin.distanceTo(p);if(h<o.near||h>o.far)return;c.push({distance:h,distanceToRay:Math.sqrt(d),point:p,index:t,face:null,faceIndex:null,barycoord:null,object:u})}}class bM extends Kn{constructor(t=[],n=hr,s,o,c,u,d,p,h,g){super(t,n,s,o,c,u,d,p,h,g),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class So extends Kn{constructor(t,n,s=fa,o,c,u,d=Bn,p=Bn,h,g=ka,_=1){if(g!==ka&&g!==lr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const v={width:t,height:n,depth:_};super(v,o,c,u,d,p,g,s,h),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.source=new sg(Object.assign({},t.image)),this.compareFunction=t.compareFunction,this}toJSON(t){const n=super.toJSON(t);return this.compareFunction!==null&&(n.compareFunction=this.compareFunction),n}}class YA extends So{constructor(t,n=fa,s=hr,o,c,u=Bn,d=Bn,p,h=ka){const g={width:t,height:t,depth:1},_=[g,g,g,g,g,g];super(t,t,n,s,o,c,u,d,p,h),this.image=_,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(t){this.image=t}}class EM extends Kn{constructor(t=null){super(),this.sourceTexture=t,this.isExternalTexture=!0}copy(t){return super.copy(t),this.sourceTexture=t.sourceTexture,this}}class Kl extends Yi{constructor(t=1,n=1,s=1,o=1,c=1,u=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:n,depth:s,widthSegments:o,heightSegments:c,depthSegments:u};const d=this;o=Math.floor(o),c=Math.floor(c),u=Math.floor(u);const p=[],h=[],g=[],_=[];let v=0,y=0;b("z","y","x",-1,-1,s,n,t,u,c,0),b("z","y","x",1,-1,s,n,-t,u,c,1),b("x","z","y",1,1,t,s,n,o,u,2),b("x","z","y",1,-1,t,s,-n,o,u,3),b("x","y","z",1,-1,t,n,s,o,c,4),b("x","y","z",-1,-1,t,n,-s,o,c,5),this.setIndex(p),this.setAttribute("position",new Wi(h,3)),this.setAttribute("normal",new Wi(g,3)),this.setAttribute("uv",new Wi(_,2));function b(R,S,x,A,N,L,H,B,O,E,U){const V=L/O,F=H/E,j=L/2,lt=H/2,ct=B/2,q=O+1,I=E+1;let G=0,$=0;const dt=new rt;for(let xt=0;xt<I;xt++){const z=xt*F-lt;for(let Q=0;Q<q;Q++){const St=Q*V-j;dt[R]=St*A,dt[S]=z*N,dt[x]=ct,h.push(dt.x,dt.y,dt.z),dt[R]=0,dt[S]=0,dt[x]=B>0?1:-1,g.push(dt.x,dt.y,dt.z),_.push(Q/O),_.push(1-xt/E),G+=1}}for(let xt=0;xt<E;xt++)for(let z=0;z<O;z++){const Q=v+z+q*xt,St=v+z+q*(xt+1),Rt=v+(z+1)+q*(xt+1),Nt=v+(z+1)+q*xt;p.push(Q,St,Nt),p.push(St,Rt,Nt),$+=6}d.addGroup(y,$,U),y+=$,v+=G}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new Kl(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}class xf extends Yi{constructor(t=1,n=1,s=1,o=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:n,widthSegments:s,heightSegments:o};const c=t/2,u=n/2,d=Math.floor(s),p=Math.floor(o),h=d+1,g=p+1,_=t/d,v=n/p,y=[],b=[],R=[],S=[];for(let x=0;x<g;x++){const A=x*v-u;for(let N=0;N<h;N++){const L=N*_-c;b.push(L,-A,0),R.push(0,0,1),S.push(N/d),S.push(1-x/p)}}for(let x=0;x<p;x++)for(let A=0;A<d;A++){const N=A+h*x,L=A+h*(x+1),H=A+1+h*(x+1),B=A+1+h*x;y.push(N,L,B),y.push(L,H,B)}this.setIndex(y),this.setAttribute("position",new Wi(b,3)),this.setAttribute("normal",new Wi(R,3)),this.setAttribute("uv",new Wi(S,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new xf(t.width,t.height,t.widthSegments,t.heightSegments)}}function Mo(i){const t={};for(const n in i){t[n]={};for(const s in i[n]){const o=i[n][s];if($x(o))o.isRenderTargetTexture?(ie("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[n][s]=null):t[n][s]=o.clone();else if(Array.isArray(o))if($x(o[0])){const c=[];for(let u=0,d=o.length;u<d;u++)c[u]=o[u].clone();t[n][s]=c}else t[n][s]=o.slice();else t[n][s]=o}}return t}function Wn(i){const t={};for(let n=0;n<i.length;n++){const s=Mo(i[n]);for(const o in s)t[o]=s[o]}return t}function $x(i){return i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)}function KA(i){const t=[];for(let n=0;n<i.length;n++)t.push(i[n].clone());return t}function TM(i){const t=i.getRenderTarget();return t===null?i.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:be.workingColorSpace}const ZA={clone:Mo,merge:Wn};var QA=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,JA=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class da extends Yl{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=QA,this.fragmentShader=JA,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Mo(t.uniforms),this.uniformsGroups=KA(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this.defaultAttributeValues=Object.assign({},t.defaultAttributeValues),this.index0AttributeName=t.index0AttributeName,this.uniformsNeedUpdate=t.uniformsNeedUpdate,this}toJSON(t){const n=super.toJSON(t);n.glslVersion=this.glslVersion,n.uniforms={};for(const o in this.uniforms){const u=this.uniforms[o].value;u&&u.isTexture?n.uniforms[o]={type:"t",value:u.toJSON(t).uuid}:u&&u.isColor?n.uniforms[o]={type:"c",value:u.getHex()}:u&&u.isVector2?n.uniforms[o]={type:"v2",value:u.toArray()}:u&&u.isVector3?n.uniforms[o]={type:"v3",value:u.toArray()}:u&&u.isVector4?n.uniforms[o]={type:"v4",value:u.toArray()}:u&&u.isMatrix3?n.uniforms[o]={type:"m3",value:u.toArray()}:u&&u.isMatrix4?n.uniforms[o]={type:"m4",value:u.toArray()}:n.uniforms[o]={value:u}}Object.keys(this.defines).length>0&&(n.defines=this.defines),n.vertexShader=this.vertexShader,n.fragmentShader=this.fragmentShader,n.lights=this.lights,n.clipping=this.clipping;const s={};for(const o in this.extensions)this.extensions[o]===!0&&(s[o]=!0);return Object.keys(s).length>0&&(n.extensions=s),n}}class $A extends da{constructor(t){super(t),this.isRawShaderMaterial=!0,this.type="RawShaderMaterial"}}class tR extends Yl{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=fA,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class eR extends Yl{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}const Nu=new rt,Lu=new To,ta=new rt;class AM extends ai{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Sn,this.projectionMatrix=new Sn,this.projectionMatrixInverse=new Sn,this.coordinateSystem=ra,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(t,n){return super.copy(t,n),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorld.decompose(Nu,Lu,ta),ta.x===1&&ta.y===1&&ta.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Nu,Lu,ta.set(1,1,1)).invert()}updateWorldMatrix(t,n){super.updateWorldMatrix(t,n),this.matrixWorld.decompose(Nu,Lu,ta),ta.x===1&&ta.y===1&&ta.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Nu,Lu,ta.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}}const Ts=new rt,ty=new je,ey=new je;class Di extends AM{constructor(t=50,n=1,s=.1,o=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=s,this.far=o,this.focus=10,this.aspect=n,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const n=.5*this.getFilmHeight()/t;this.fov=ym*2*Math.atan(n),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(zh*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return ym*2*Math.atan(Math.tan(zh*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,n,s){Ts.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Ts.x,Ts.y).multiplyScalar(-t/Ts.z),Ts.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),s.set(Ts.x,Ts.y).multiplyScalar(-t/Ts.z)}getViewSize(t,n){return this.getViewBounds(t,ty,ey),n.subVectors(ey,ty)}setViewOffset(t,n,s,o,c,u){this.aspect=t/n,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=o,this.view.width=c,this.view.height=u,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let n=t*Math.tan(zh*.5*this.fov)/this.zoom,s=2*n,o=this.aspect*s,c=-.5*o;const u=this.view;if(this.view!==null&&this.view.enabled){const p=u.fullWidth,h=u.fullHeight;c+=u.offsetX*o/p,n-=u.offsetY*s/h,o*=u.width/p,s*=u.height/h}const d=this.filmOffset;d!==0&&(c+=t*d/this.getFilmWidth()),this.projectionMatrix.makePerspective(c,c+o,n,n-s,t,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.fov=this.fov,n.object.zoom=this.zoom,n.object.near=this.near,n.object.far=this.far,n.object.focus=this.focus,n.object.aspect=this.aspect,this.view!==null&&(n.object.view=Object.assign({},this.view)),n.object.filmGauge=this.filmGauge,n.object.filmOffset=this.filmOffset,n}}class RM extends AM{constructor(t=-1,n=1,s=1,o=-1,c=.1,u=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=n,this.top=s,this.bottom=o,this.near=c,this.far=u,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,n,s,o,c,u){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=o,this.view.width=c,this.view.height=u,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),n=(this.top-this.bottom)/(2*this.zoom),s=(this.right+this.left)/2,o=(this.top+this.bottom)/2;let c=s-t,u=s+t,d=o+n,p=o-n;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,g=(this.top-this.bottom)/this.view.fullHeight/this.zoom;c+=h*this.view.offsetX,u=c+h*this.view.width,d-=g*this.view.offsetY,p=d-g*this.view.height}this.projectionMatrix.makeOrthographic(c,u,d,p,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.zoom=this.zoom,n.object.left=this.left,n.object.right=this.right,n.object.top=this.top,n.object.bottom=this.bottom,n.object.near=this.near,n.object.far=this.far,this.view!==null&&(n.object.view=Object.assign({},this.view)),n}}const lo=-90,co=1;class nR extends ai{constructor(t,n,s){super(),this.type="CubeCamera",this.renderTarget=s,this.coordinateSystem=null,this.activeMipmapLevel=0;const o=new Di(lo,co,t,n);o.layers=this.layers,this.add(o);const c=new Di(lo,co,t,n);c.layers=this.layers,this.add(c);const u=new Di(lo,co,t,n);u.layers=this.layers,this.add(u);const d=new Di(lo,co,t,n);d.layers=this.layers,this.add(d);const p=new Di(lo,co,t,n);p.layers=this.layers,this.add(p);const h=new Di(lo,co,t,n);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const t=this.coordinateSystem,n=this.children.concat(),[s,o,c,u,d,p]=n;for(const h of n)this.remove(h);if(t===ra)s.up.set(0,1,0),s.lookAt(1,0,0),o.up.set(0,1,0),o.lookAt(-1,0,0),c.up.set(0,0,-1),c.lookAt(0,1,0),u.up.set(0,0,1),u.lookAt(0,-1,0),d.up.set(0,1,0),d.lookAt(0,0,1),p.up.set(0,1,0),p.lookAt(0,0,-1);else if(t===af)s.up.set(0,-1,0),s.lookAt(-1,0,0),o.up.set(0,-1,0),o.lookAt(1,0,0),c.up.set(0,0,1),c.lookAt(0,1,0),u.up.set(0,0,-1),u.lookAt(0,-1,0),d.up.set(0,-1,0),d.lookAt(0,0,1),p.up.set(0,-1,0),p.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const h of n)this.add(h),h.updateMatrixWorld()}update(t,n){this.parent===null&&this.updateMatrixWorld();const{renderTarget:s,activeMipmapLevel:o}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[c,u,d,p,h,g]=this.children,_=t.getRenderTarget(),v=t.getActiveCubeFace(),y=t.getActiveMipmapLevel(),b=t.xr.enabled;t.xr.enabled=!1;const R=s.texture.generateMipmaps;s.texture.generateMipmaps=!1;let S=!1;t.isWebGLRenderer===!0?S=t.state.buffers.depth.getReversed():S=t.reversedDepthBuffer,t.setRenderTarget(s,0,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,c),t.setRenderTarget(s,1,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,u),t.setRenderTarget(s,2,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,d),t.setRenderTarget(s,3,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,p),t.setRenderTarget(s,4,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,h),s.texture.generateMipmaps=R,t.setRenderTarget(s,5,o),S&&t.autoClear===!1&&t.clearDepth(),t.render(n,g),t.setRenderTarget(_,v,y),t.xr.enabled=b,s.texture.needsPMREMUpdate=!0}}class iR extends Di{constructor(t=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=t}}const Ig=class Ig{constructor(t,n,s,o){this.elements=[1,0,0,1],t!==void 0&&this.set(t,n,s,o)}identity(){return this.set(1,0,0,1),this}fromArray(t,n=0){for(let s=0;s<4;s++)this.elements[s]=t[s+n];return this}set(t,n,s,o){const c=this.elements;return c[0]=t,c[2]=n,c[1]=s,c[3]=o,this}};Ig.prototype.isMatrix2=!0;let ny=Ig;function iy(i,t,n,s){const o=aR(s);switch(n){case uM:return i*t;case dM:return i*t/o.components*o.byteLength;case tg:return i*t/o.components*o.byteLength;case pr:return i*t*2/o.components*o.byteLength;case eg:return i*t*2/o.components*o.byteLength;case fM:return i*t*3/o.components*o.byteLength;case Xi:return i*t*4/o.components*o.byteLength;case ng:return i*t*4/o.components*o.byteLength;case Vu:case Hu:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*8;case Gu:case ku:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case jp:case Wp:return Math.max(i,16)*Math.max(t,8)/4;case kp:case Xp:return Math.max(i,8)*Math.max(t,8)/2;case qp:case Yp:case Zp:case Qp:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*8;case Kp:case $u:case Jp:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case $p:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case tm:return Math.floor((i+4)/5)*Math.floor((t+3)/4)*16;case em:return Math.floor((i+4)/5)*Math.floor((t+4)/5)*16;case nm:return Math.floor((i+5)/6)*Math.floor((t+4)/5)*16;case im:return Math.floor((i+5)/6)*Math.floor((t+5)/6)*16;case am:return Math.floor((i+7)/8)*Math.floor((t+4)/5)*16;case sm:return Math.floor((i+7)/8)*Math.floor((t+5)/6)*16;case rm:return Math.floor((i+7)/8)*Math.floor((t+7)/8)*16;case om:return Math.floor((i+9)/10)*Math.floor((t+4)/5)*16;case lm:return Math.floor((i+9)/10)*Math.floor((t+5)/6)*16;case cm:return Math.floor((i+9)/10)*Math.floor((t+7)/8)*16;case um:return Math.floor((i+9)/10)*Math.floor((t+9)/10)*16;case fm:return Math.floor((i+11)/12)*Math.floor((t+9)/10)*16;case dm:return Math.floor((i+11)/12)*Math.floor((t+11)/12)*16;case hm:case pm:case mm:return Math.ceil(i/4)*Math.ceil(t/4)*16;case gm:case _m:return Math.ceil(i/4)*Math.ceil(t/4)*8;case tf:case vm:return Math.ceil(i/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${n} format.`)}function aR(i){switch(i){case Ni:case rM:return{byteLength:1,components:1};case zl:case oM:case Ga:return{byteLength:2,components:1};case Jm:case $m:return{byteLength:2,components:4};case fa:case Qm:case sa:return{byteLength:4,components:1};case lM:case cM:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Zm}}));typeof window<"u"&&(window.__THREE__?ie("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Zm);function CM(){let i=null,t=!1,n=null,s=null;function o(c,u){n(c,u),s=i.requestAnimationFrame(o)}return{start:function(){t!==!0&&n!==null&&i!==null&&(s=i.requestAnimationFrame(o),t=!0)},stop:function(){i!==null&&i.cancelAnimationFrame(s),t=!1},setAnimationLoop:function(c){n=c},setContext:function(c){i=c}}}function sR(i){const t=new WeakMap;function n(d,p){const h=d.array,g=d.usage,_=h.byteLength,v=i.createBuffer();i.bindBuffer(p,v),i.bufferData(p,h,g),d.onUploadCallback();let y;if(h instanceof Float32Array)y=i.FLOAT;else if(typeof Float16Array<"u"&&h instanceof Float16Array)y=i.HALF_FLOAT;else if(h instanceof Uint16Array)d.isFloat16BufferAttribute?y=i.HALF_FLOAT:y=i.UNSIGNED_SHORT;else if(h instanceof Int16Array)y=i.SHORT;else if(h instanceof Uint32Array)y=i.UNSIGNED_INT;else if(h instanceof Int32Array)y=i.INT;else if(h instanceof Int8Array)y=i.BYTE;else if(h instanceof Uint8Array)y=i.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)y=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:v,type:y,bytesPerElement:h.BYTES_PER_ELEMENT,version:d.version,size:_}}function s(d,p,h){const g=p.array,_=p.updateRanges;if(i.bindBuffer(h,d),_.length===0)i.bufferSubData(h,0,g);else{_.sort((y,b)=>y.start-b.start);let v=0;for(let y=1;y<_.length;y++){const b=_[v],R=_[y];R.start<=b.start+b.count+1?b.count=Math.max(b.count,R.start+R.count-b.start):(++v,_[v]=R)}_.length=v+1;for(let y=0,b=_.length;y<b;y++){const R=_[y];i.bufferSubData(h,R.start*g.BYTES_PER_ELEMENT,g,R.start,R.count)}p.clearUpdateRanges()}p.onUploadCallback()}function o(d){return d.isInterleavedBufferAttribute&&(d=d.data),t.get(d)}function c(d){d.isInterleavedBufferAttribute&&(d=d.data);const p=t.get(d);p&&(i.deleteBuffer(p.buffer),t.delete(d))}function u(d,p){if(d.isInterleavedBufferAttribute&&(d=d.data),d.isGLBufferAttribute){const g=t.get(d);(!g||g.version<d.version)&&t.set(d,{buffer:d.buffer,type:d.type,bytesPerElement:d.elementSize,version:d.version});return}const h=t.get(d);if(h===void 0)t.set(d,n(d,p));else if(h.version<d.version){if(h.size!==d.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");s(h.buffer,d,p),h.version=d.version}}return{get:o,remove:c,update:u}}var rR=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,oR=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,lR=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,cR=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,uR=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,fR=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,dR=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,hR=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,pR=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,mR=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,gR=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,_R=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,vR=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,xR=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,yR=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,SR=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,MR=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,bR=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,ER=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,TR=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,AR=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,RR=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,CR=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,wR=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,DR=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,NR=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,LR=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,UR=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,PR=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,OR=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,FR="gl_FragColor = linearToOutputTexel( gl_FragColor );",BR=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,IR=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * reflectVec );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,zR=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,VR=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,HR=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,GR=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,kR=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,jR=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,XR=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,WR=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,qR=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,YR=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,KR=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,ZR=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,QR=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif
#include <lightprobes_pars_fragment>`,JR=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,$R=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,tC=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,eC=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,nC=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,iC=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,aC=`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		return 0.5 / max( gv + gl, EPSILON );
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,sC=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
	#ifdef USE_LIGHT_PROBES_GRID
		vec3 probeWorldPos = ( ( vec4( geometryPosition, 1.0 ) - viewMatrix[ 3 ] ) * viewMatrix ).xyz;
		vec3 probeWorldNormal = inverseTransformDirection( geometryNormal, viewMatrix );
		irradiance += getLightProbeGridIrradiance( probeWorldPos, probeWorldNormal );
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,rC=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,oC=`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,lC=`#ifdef USE_LIGHT_PROBES_GRID
uniform highp sampler3D probesSH;
uniform vec3 probesMin;
uniform vec3 probesMax;
uniform vec3 probesResolution;
vec3 getLightProbeGridIrradiance( vec3 worldPos, vec3 worldNormal ) {
	vec3 res = probesResolution;
	vec3 gridRange = probesMax - probesMin;
	vec3 resMinusOne = res - 1.0;
	vec3 probeSpacing = gridRange / resMinusOne;
	vec3 samplePos = worldPos + worldNormal * probeSpacing * 0.5;
	vec3 uvw = clamp( ( samplePos - probesMin ) / gridRange, 0.0, 1.0 );
	uvw = uvw * resMinusOne / res + 0.5 / res;
	float nz          = res.z;
	float paddedSlices = nz + 2.0;
	float atlasDepth  = 7.0 * paddedSlices;
	float uvZBase     = uvw.z * nz + 1.0;
	vec4 s0 = texture( probesSH, vec3( uvw.xy, ( uvZBase                       ) / atlasDepth ) );
	vec4 s1 = texture( probesSH, vec3( uvw.xy, ( uvZBase +       paddedSlices   ) / atlasDepth ) );
	vec4 s2 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 2.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s3 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 3.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s4 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 4.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s5 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 5.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s6 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 6.0 * paddedSlices   ) / atlasDepth ) );
	vec3 c0 = s0.xyz;
	vec3 c1 = vec3( s0.w, s1.xy );
	vec3 c2 = vec3( s1.zw, s2.x );
	vec3 c3 = s2.yzw;
	vec3 c4 = s3.xyz;
	vec3 c5 = vec3( s3.w, s4.xy );
	vec3 c6 = vec3( s4.zw, s5.x );
	vec3 c7 = s5.yzw;
	vec3 c8 = s6.xyz;
	float x = worldNormal.x, y = worldNormal.y, z = worldNormal.z;
	vec3 result = c0 * 0.886227;
	result += c1 * 2.0 * 0.511664 * y;
	result += c2 * 2.0 * 0.511664 * z;
	result += c3 * 2.0 * 0.511664 * x;
	result += c4 * 2.0 * 0.429043 * x * y;
	result += c5 * 2.0 * 0.429043 * y * z;
	result += c6 * ( 0.743125 * z * z - 0.247708 );
	result += c7 * 2.0 * 0.429043 * x * z;
	result += c8 * 0.429043 * ( x * x - y * y );
	return max( result, vec3( 0.0 ) );
}
#endif`,cC=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,uC=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,fC=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,dC=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,hC=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,pC=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,mC=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,gC=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,_C=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,vC=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,xC=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,yC=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,SC=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,MC=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,bC=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,EC=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,TC=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#if defined( USE_PACKED_NORMALMAP )
		mapN = vec3( mapN.xy, sqrt( saturate( 1.0 - dot( mapN.xy, mapN.xy ) ) ) );
	#endif
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,AC=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,RC=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,CC=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,wC=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,DC=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,NC=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,LC=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,UC=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,PC=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,OC=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,FC=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,BC=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,IC=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,zC=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,VC=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,HC=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,GC=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,kC=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,jC=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	#ifdef HAS_NORMAL
		vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	#else
		vec3 shadowWorldNormal = vec3( 0.0 );
	#endif
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,XC=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,WC=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,qC=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,YC=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,KC=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,ZC=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,QC=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,JC=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,$C=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,tw=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,ew=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,nw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,iw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,aw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,sw=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const rw=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,ow=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,lw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,cw=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vWorldDirection );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,uw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,fw=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,dw=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,hw=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,pw=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,mw=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,gw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,_w=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,vw=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,xw=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,yw=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,Sw=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Mw=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,bw=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Ew=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,Tw=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Aw=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,Rw=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,Cw=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,ww=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Dw=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,Nw=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Lw=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Uw=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Pw=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Ow=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Fw=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Bw=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Iw=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,zw=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,de={alphahash_fragment:rR,alphahash_pars_fragment:oR,alphamap_fragment:lR,alphamap_pars_fragment:cR,alphatest_fragment:uR,alphatest_pars_fragment:fR,aomap_fragment:dR,aomap_pars_fragment:hR,batching_pars_vertex:pR,batching_vertex:mR,begin_vertex:gR,beginnormal_vertex:_R,bsdfs:vR,iridescence_fragment:xR,bumpmap_pars_fragment:yR,clipping_planes_fragment:SR,clipping_planes_pars_fragment:MR,clipping_planes_pars_vertex:bR,clipping_planes_vertex:ER,color_fragment:TR,color_pars_fragment:AR,color_pars_vertex:RR,color_vertex:CR,common:wR,cube_uv_reflection_fragment:DR,defaultnormal_vertex:NR,displacementmap_pars_vertex:LR,displacementmap_vertex:UR,emissivemap_fragment:PR,emissivemap_pars_fragment:OR,colorspace_fragment:FR,colorspace_pars_fragment:BR,envmap_fragment:IR,envmap_common_pars_fragment:zR,envmap_pars_fragment:VR,envmap_pars_vertex:HR,envmap_physical_pars_fragment:JR,envmap_vertex:GR,fog_vertex:kR,fog_pars_vertex:jR,fog_fragment:XR,fog_pars_fragment:WR,gradientmap_pars_fragment:qR,lightmap_pars_fragment:YR,lights_lambert_fragment:KR,lights_lambert_pars_fragment:ZR,lights_pars_begin:QR,lights_toon_fragment:$R,lights_toon_pars_fragment:tC,lights_phong_fragment:eC,lights_phong_pars_fragment:nC,lights_physical_fragment:iC,lights_physical_pars_fragment:aC,lights_fragment_begin:sC,lights_fragment_maps:rC,lights_fragment_end:oC,lightprobes_pars_fragment:lC,logdepthbuf_fragment:cC,logdepthbuf_pars_fragment:uC,logdepthbuf_pars_vertex:fC,logdepthbuf_vertex:dC,map_fragment:hC,map_pars_fragment:pC,map_particle_fragment:mC,map_particle_pars_fragment:gC,metalnessmap_fragment:_C,metalnessmap_pars_fragment:vC,morphinstance_vertex:xC,morphcolor_vertex:yC,morphnormal_vertex:SC,morphtarget_pars_vertex:MC,morphtarget_vertex:bC,normal_fragment_begin:EC,normal_fragment_maps:TC,normal_pars_fragment:AC,normal_pars_vertex:RC,normal_vertex:CC,normalmap_pars_fragment:wC,clearcoat_normal_fragment_begin:DC,clearcoat_normal_fragment_maps:NC,clearcoat_pars_fragment:LC,iridescence_pars_fragment:UC,opaque_fragment:PC,packing:OC,premultiplied_alpha_fragment:FC,project_vertex:BC,dithering_fragment:IC,dithering_pars_fragment:zC,roughnessmap_fragment:VC,roughnessmap_pars_fragment:HC,shadowmap_pars_fragment:GC,shadowmap_pars_vertex:kC,shadowmap_vertex:jC,shadowmask_pars_fragment:XC,skinbase_vertex:WC,skinning_pars_vertex:qC,skinning_vertex:YC,skinnormal_vertex:KC,specularmap_fragment:ZC,specularmap_pars_fragment:QC,tonemapping_fragment:JC,tonemapping_pars_fragment:$C,transmission_fragment:tw,transmission_pars_fragment:ew,uv_pars_fragment:nw,uv_pars_vertex:iw,uv_vertex:aw,worldpos_vertex:sw,background_vert:rw,background_frag:ow,backgroundCube_vert:lw,backgroundCube_frag:cw,cube_vert:uw,cube_frag:fw,depth_vert:dw,depth_frag:hw,distance_vert:pw,distance_frag:mw,equirect_vert:gw,equirect_frag:_w,linedashed_vert:vw,linedashed_frag:xw,meshbasic_vert:yw,meshbasic_frag:Sw,meshlambert_vert:Mw,meshlambert_frag:bw,meshmatcap_vert:Ew,meshmatcap_frag:Tw,meshnormal_vert:Aw,meshnormal_frag:Rw,meshphong_vert:Cw,meshphong_frag:ww,meshphysical_vert:Dw,meshphysical_frag:Nw,meshtoon_vert:Lw,meshtoon_frag:Uw,points_vert:Pw,points_frag:Ow,shadow_vert:Fw,shadow_frag:Bw,sprite_vert:Iw,sprite_frag:zw},Vt={common:{diffuse:{value:new Le(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new oe},alphaMap:{value:null},alphaMapTransform:{value:new oe},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new oe}},envmap:{envMap:{value:null},envMapRotation:{value:new oe},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new oe}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new oe}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new oe},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new oe},normalScale:{value:new je(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new oe},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new oe}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new oe}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new oe}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Le(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null},probesSH:{value:null},probesMin:{value:new rt},probesMax:{value:new rt},probesResolution:{value:new rt}},points:{diffuse:{value:new Le(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new oe},alphaTest:{value:0},uvTransform:{value:new oe}},sprite:{diffuse:{value:new Le(16777215)},opacity:{value:1},center:{value:new je(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new oe},alphaMap:{value:null},alphaMapTransform:{value:new oe},alphaTest:{value:0}}},ia={basic:{uniforms:Wn([Vt.common,Vt.specularmap,Vt.envmap,Vt.aomap,Vt.lightmap,Vt.fog]),vertexShader:de.meshbasic_vert,fragmentShader:de.meshbasic_frag},lambert:{uniforms:Wn([Vt.common,Vt.specularmap,Vt.envmap,Vt.aomap,Vt.lightmap,Vt.emissivemap,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,Vt.fog,Vt.lights,{emissive:{value:new Le(0)},envMapIntensity:{value:1}}]),vertexShader:de.meshlambert_vert,fragmentShader:de.meshlambert_frag},phong:{uniforms:Wn([Vt.common,Vt.specularmap,Vt.envmap,Vt.aomap,Vt.lightmap,Vt.emissivemap,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,Vt.fog,Vt.lights,{emissive:{value:new Le(0)},specular:{value:new Le(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:de.meshphong_vert,fragmentShader:de.meshphong_frag},standard:{uniforms:Wn([Vt.common,Vt.envmap,Vt.aomap,Vt.lightmap,Vt.emissivemap,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,Vt.roughnessmap,Vt.metalnessmap,Vt.fog,Vt.lights,{emissive:{value:new Le(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:de.meshphysical_vert,fragmentShader:de.meshphysical_frag},toon:{uniforms:Wn([Vt.common,Vt.aomap,Vt.lightmap,Vt.emissivemap,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,Vt.gradientmap,Vt.fog,Vt.lights,{emissive:{value:new Le(0)}}]),vertexShader:de.meshtoon_vert,fragmentShader:de.meshtoon_frag},matcap:{uniforms:Wn([Vt.common,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,Vt.fog,{matcap:{value:null}}]),vertexShader:de.meshmatcap_vert,fragmentShader:de.meshmatcap_frag},points:{uniforms:Wn([Vt.points,Vt.fog]),vertexShader:de.points_vert,fragmentShader:de.points_frag},dashed:{uniforms:Wn([Vt.common,Vt.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:de.linedashed_vert,fragmentShader:de.linedashed_frag},depth:{uniforms:Wn([Vt.common,Vt.displacementmap]),vertexShader:de.depth_vert,fragmentShader:de.depth_frag},normal:{uniforms:Wn([Vt.common,Vt.bumpmap,Vt.normalmap,Vt.displacementmap,{opacity:{value:1}}]),vertexShader:de.meshnormal_vert,fragmentShader:de.meshnormal_frag},sprite:{uniforms:Wn([Vt.sprite,Vt.fog]),vertexShader:de.sprite_vert,fragmentShader:de.sprite_frag},background:{uniforms:{uvTransform:{value:new oe},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:de.background_vert,fragmentShader:de.background_frag},backgroundCube:{uniforms:{envMap:{value:null},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new oe}},vertexShader:de.backgroundCube_vert,fragmentShader:de.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:de.cube_vert,fragmentShader:de.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:de.equirect_vert,fragmentShader:de.equirect_frag},distance:{uniforms:Wn([Vt.common,Vt.displacementmap,{referencePosition:{value:new rt},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:de.distance_vert,fragmentShader:de.distance_frag},shadow:{uniforms:Wn([Vt.lights,Vt.fog,{color:{value:new Le(0)},opacity:{value:1}}]),vertexShader:de.shadow_vert,fragmentShader:de.shadow_frag}};ia.physical={uniforms:Wn([ia.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new oe},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new oe},clearcoatNormalScale:{value:new je(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new oe},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new oe},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new oe},sheen:{value:0},sheenColor:{value:new Le(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new oe},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new oe},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new oe},transmissionSamplerSize:{value:new je},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new oe},attenuationDistance:{value:0},attenuationColor:{value:new Le(0)},specularColor:{value:new Le(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new oe},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new oe},anisotropyVector:{value:new je},anisotropyMap:{value:null},anisotropyMapTransform:{value:new oe}}]),vertexShader:de.meshphysical_vert,fragmentShader:de.meshphysical_frag};const Uu={r:0,b:0,g:0},Vw=new Sn,wM=new oe;wM.set(-1,0,0,0,1,0,0,0,1);function Hw(i,t,n,s,o,c){const u=new Le(0);let d=o===!0?0:1,p,h,g=null,_=0,v=null;function y(A){let N=A.isScene===!0?A.background:null;if(N&&N.isTexture){const L=A.backgroundBlurriness>0;N=t.get(N,L)}return N}function b(A){let N=!1;const L=y(A);L===null?S(u,d):L&&L.isColor&&(S(L,1),N=!0);const H=i.xr.getEnvironmentBlendMode();H==="additive"?n.buffers.color.setClear(0,0,0,1,c):H==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,c),(i.autoClear||N)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function R(A,N){const L=y(N);L&&(L.isCubeTexture||L.mapping===_f)?(h===void 0&&(h=new ja(new Kl(1,1,1),new da({name:"BackgroundCubeMaterial",uniforms:Mo(ia.backgroundCube.uniforms),vertexShader:ia.backgroundCube.vertexShader,fragmentShader:ia.backgroundCube.fragmentShader,side:ii,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(H,B,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),h.material.uniforms.envMap.value=L,h.material.uniforms.backgroundBlurriness.value=N.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=N.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(Vw.makeRotationFromEuler(N.backgroundRotation)).transpose(),L.isCubeTexture&&L.isRenderTargetTexture===!1&&h.material.uniforms.backgroundRotation.value.premultiply(wM),h.material.toneMapped=be.getTransfer(L.colorSpace)!==ze,(g!==L||_!==L.version||v!==i.toneMapping)&&(h.material.needsUpdate=!0,g=L,_=L.version,v=i.toneMapping),h.layers.enableAll(),A.unshift(h,h.geometry,h.material,0,0,null)):L&&L.isTexture&&(p===void 0&&(p=new ja(new xf(2,2),new da({name:"BackgroundMaterial",uniforms:Mo(ia.background.uniforms),vertexShader:ia.background.vertexShader,fragmentShader:ia.background.fragmentShader,side:ws,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),p.geometry.deleteAttribute("normal"),Object.defineProperty(p.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(p)),p.material.uniforms.t2D.value=L,p.material.uniforms.backgroundIntensity.value=N.backgroundIntensity,p.material.toneMapped=be.getTransfer(L.colorSpace)!==ze,L.matrixAutoUpdate===!0&&L.updateMatrix(),p.material.uniforms.uvTransform.value.copy(L.matrix),(g!==L||_!==L.version||v!==i.toneMapping)&&(p.material.needsUpdate=!0,g=L,_=L.version,v=i.toneMapping),p.layers.enableAll(),A.unshift(p,p.geometry,p.material,0,0,null))}function S(A,N){A.getRGB(Uu,TM(i)),n.buffers.color.setClear(Uu.r,Uu.g,Uu.b,N,c)}function x(){h!==void 0&&(h.geometry.dispose(),h.material.dispose(),h=void 0),p!==void 0&&(p.geometry.dispose(),p.material.dispose(),p=void 0)}return{getClearColor:function(){return u},setClearColor:function(A,N=1){u.set(A),d=N,S(u,d)},getClearAlpha:function(){return d},setClearAlpha:function(A){d=A,S(u,d)},render:b,addToRenderList:R,dispose:x}}function Gw(i,t){const n=i.getParameter(i.MAX_VERTEX_ATTRIBS),s={},o=v(null);let c=o,u=!1;function d(F,j,lt,ct,q){let I=!1;const G=_(F,ct,lt,j);c!==G&&(c=G,h(c.object)),I=y(F,ct,lt,q),I&&b(F,ct,lt,q),q!==null&&t.update(q,i.ELEMENT_ARRAY_BUFFER),(I||u)&&(u=!1,L(F,j,lt,ct),q!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,t.get(q).buffer))}function p(){return i.createVertexArray()}function h(F){return i.bindVertexArray(F)}function g(F){return i.deleteVertexArray(F)}function _(F,j,lt,ct){const q=ct.wireframe===!0;let I=s[j.id];I===void 0&&(I={},s[j.id]=I);const G=F.isInstancedMesh===!0?F.id:0;let $=I[G];$===void 0&&($={},I[G]=$);let dt=$[lt.id];dt===void 0&&(dt={},$[lt.id]=dt);let xt=dt[q];return xt===void 0&&(xt=v(p()),dt[q]=xt),xt}function v(F){const j=[],lt=[],ct=[];for(let q=0;q<n;q++)j[q]=0,lt[q]=0,ct[q]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:j,enabledAttributes:lt,attributeDivisors:ct,object:F,attributes:{},index:null}}function y(F,j,lt,ct){const q=c.attributes,I=j.attributes;let G=0;const $=lt.getAttributes();for(const dt in $)if($[dt].location>=0){const z=q[dt];let Q=I[dt];if(Q===void 0&&(dt==="instanceMatrix"&&F.instanceMatrix&&(Q=F.instanceMatrix),dt==="instanceColor"&&F.instanceColor&&(Q=F.instanceColor)),z===void 0||z.attribute!==Q||Q&&z.data!==Q.data)return!0;G++}return c.attributesNum!==G||c.index!==ct}function b(F,j,lt,ct){const q={},I=j.attributes;let G=0;const $=lt.getAttributes();for(const dt in $)if($[dt].location>=0){let z=I[dt];z===void 0&&(dt==="instanceMatrix"&&F.instanceMatrix&&(z=F.instanceMatrix),dt==="instanceColor"&&F.instanceColor&&(z=F.instanceColor));const Q={};Q.attribute=z,z&&z.data&&(Q.data=z.data),q[dt]=Q,G++}c.attributes=q,c.attributesNum=G,c.index=ct}function R(){const F=c.newAttributes;for(let j=0,lt=F.length;j<lt;j++)F[j]=0}function S(F){x(F,0)}function x(F,j){const lt=c.newAttributes,ct=c.enabledAttributes,q=c.attributeDivisors;lt[F]=1,ct[F]===0&&(i.enableVertexAttribArray(F),ct[F]=1),q[F]!==j&&(i.vertexAttribDivisor(F,j),q[F]=j)}function A(){const F=c.newAttributes,j=c.enabledAttributes;for(let lt=0,ct=j.length;lt<ct;lt++)j[lt]!==F[lt]&&(i.disableVertexAttribArray(lt),j[lt]=0)}function N(F,j,lt,ct,q,I,G){G===!0?i.vertexAttribIPointer(F,j,lt,q,I):i.vertexAttribPointer(F,j,lt,ct,q,I)}function L(F,j,lt,ct){R();const q=ct.attributes,I=lt.getAttributes(),G=j.defaultAttributeValues;for(const $ in I){const dt=I[$];if(dt.location>=0){let xt=q[$];if(xt===void 0&&($==="instanceMatrix"&&F.instanceMatrix&&(xt=F.instanceMatrix),$==="instanceColor"&&F.instanceColor&&(xt=F.instanceColor)),xt!==void 0){const z=xt.normalized,Q=xt.itemSize,St=t.get(xt);if(St===void 0)continue;const Rt=St.buffer,Nt=St.type,ot=St.bytesPerElement,Mt=Nt===i.INT||Nt===i.UNSIGNED_INT||xt.gpuType===Qm;if(xt.isInterleavedBufferAttribute){const Tt=xt.data,Ht=Tt.stride,ee=xt.offset;if(Tt.isInstancedInterleavedBuffer){for(let $t=0;$t<dt.locationSize;$t++)x(dt.location+$t,Tt.meshPerAttribute);F.isInstancedMesh!==!0&&ct._maxInstanceCount===void 0&&(ct._maxInstanceCount=Tt.meshPerAttribute*Tt.count)}else for(let $t=0;$t<dt.locationSize;$t++)S(dt.location+$t);i.bindBuffer(i.ARRAY_BUFFER,Rt);for(let $t=0;$t<dt.locationSize;$t++)N(dt.location+$t,Q/dt.locationSize,Nt,z,Ht*ot,(ee+Q/dt.locationSize*$t)*ot,Mt)}else{if(xt.isInstancedBufferAttribute){for(let Tt=0;Tt<dt.locationSize;Tt++)x(dt.location+Tt,xt.meshPerAttribute);F.isInstancedMesh!==!0&&ct._maxInstanceCount===void 0&&(ct._maxInstanceCount=xt.meshPerAttribute*xt.count)}else for(let Tt=0;Tt<dt.locationSize;Tt++)S(dt.location+Tt);i.bindBuffer(i.ARRAY_BUFFER,Rt);for(let Tt=0;Tt<dt.locationSize;Tt++)N(dt.location+Tt,Q/dt.locationSize,Nt,z,Q*ot,Q/dt.locationSize*Tt*ot,Mt)}}else if(G!==void 0){const z=G[$];if(z!==void 0)switch(z.length){case 2:i.vertexAttrib2fv(dt.location,z);break;case 3:i.vertexAttrib3fv(dt.location,z);break;case 4:i.vertexAttrib4fv(dt.location,z);break;default:i.vertexAttrib1fv(dt.location,z)}}}}A()}function H(){U();for(const F in s){const j=s[F];for(const lt in j){const ct=j[lt];for(const q in ct){const I=ct[q];for(const G in I)g(I[G].object),delete I[G];delete ct[q]}}delete s[F]}}function B(F){if(s[F.id]===void 0)return;const j=s[F.id];for(const lt in j){const ct=j[lt];for(const q in ct){const I=ct[q];for(const G in I)g(I[G].object),delete I[G];delete ct[q]}}delete s[F.id]}function O(F){for(const j in s){const lt=s[j];for(const ct in lt){const q=lt[ct];if(q[F.id]===void 0)continue;const I=q[F.id];for(const G in I)g(I[G].object),delete I[G];delete q[F.id]}}}function E(F){for(const j in s){const lt=s[j],ct=F.isInstancedMesh===!0?F.id:0,q=lt[ct];if(q!==void 0){for(const I in q){const G=q[I];for(const $ in G)g(G[$].object),delete G[$];delete q[I]}delete lt[ct],Object.keys(lt).length===0&&delete s[j]}}}function U(){V(),u=!0,c!==o&&(c=o,h(c.object))}function V(){o.geometry=null,o.program=null,o.wireframe=!1}return{setup:d,reset:U,resetDefaultState:V,dispose:H,releaseStatesOfGeometry:B,releaseStatesOfObject:E,releaseStatesOfProgram:O,initAttributes:R,enableAttribute:S,disableUnusedAttributes:A}}function kw(i,t,n){let s;function o(p){s=p}function c(p,h){i.drawArrays(s,p,h),n.update(h,s,1)}function u(p,h,g){g!==0&&(i.drawArraysInstanced(s,p,h,g),n.update(h,s,g))}function d(p,h,g){if(g===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(s,p,0,h,0,g);let v=0;for(let y=0;y<g;y++)v+=h[y];n.update(v,s,1)}this.setMode=o,this.render=c,this.renderInstances=u,this.renderMultiDraw=d}function jw(i,t,n,s){let o;function c(){if(o!==void 0)return o;if(t.has("EXT_texture_filter_anisotropic")===!0){const O=t.get("EXT_texture_filter_anisotropic");o=i.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else o=0;return o}function u(O){return!(O!==Xi&&s.convert(O)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function d(O){const E=O===Ga&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(O!==Ni&&s.convert(O)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==sa&&!E)}function p(O){if(O==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=n.precision!==void 0?n.precision:"highp";const g=p(h);g!==h&&(ie("WebGLRenderer:",h,"not supported, using",g,"instead."),h=g);const _=n.logarithmicDepthBuffer===!0,v=n.reversedDepthBuffer===!0&&t.has("EXT_clip_control");n.reversedDepthBuffer===!0&&v===!1&&ie("WebGLRenderer: Unable to use reversed depth buffer due to missing EXT_clip_control extension. Fallback to default depth buffer.");const y=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),b=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),R=i.getParameter(i.MAX_TEXTURE_SIZE),S=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),x=i.getParameter(i.MAX_VERTEX_ATTRIBS),A=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),N=i.getParameter(i.MAX_VARYING_VECTORS),L=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),H=i.getParameter(i.MAX_SAMPLES),B=i.getParameter(i.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:c,getMaxPrecision:p,textureFormatReadable:u,textureTypeReadable:d,precision:h,logarithmicDepthBuffer:_,reversedDepthBuffer:v,maxTextures:y,maxVertexTextures:b,maxTextureSize:R,maxCubemapSize:S,maxAttributes:x,maxVertexUniforms:A,maxVaryings:N,maxFragmentUniforms:L,maxSamples:H,samples:B}}function Xw(i){const t=this;let n=null,s=0,o=!1,c=!1;const u=new ir,d=new oe,p={value:null,needsUpdate:!1};this.uniform=p,this.numPlanes=0,this.numIntersection=0,this.init=function(_,v){const y=_.length!==0||v||s!==0||o;return o=v,s=_.length,y},this.beginShadows=function(){c=!0,g(null)},this.endShadows=function(){c=!1},this.setGlobalState=function(_,v){n=g(_,v,0)},this.setState=function(_,v,y){const b=_.clippingPlanes,R=_.clipIntersection,S=_.clipShadows,x=i.get(_);if(!o||b===null||b.length===0||c&&!S)c?g(null):h();else{const A=c?0:s,N=A*4;let L=x.clippingState||null;p.value=L,L=g(b,v,N,y);for(let H=0;H!==N;++H)L[H]=n[H];x.clippingState=L,this.numIntersection=R?this.numPlanes:0,this.numPlanes+=A}};function h(){p.value!==n&&(p.value=n,p.needsUpdate=s>0),t.numPlanes=s,t.numIntersection=0}function g(_,v,y,b){const R=_!==null?_.length:0;let S=null;if(R!==0){if(S=p.value,b!==!0||S===null){const x=y+R*4,A=v.matrixWorldInverse;d.getNormalMatrix(A),(S===null||S.length<x)&&(S=new Float32Array(x));for(let N=0,L=y;N!==R;++N,L+=4)u.copy(_[N]).applyMatrix4(A,d),u.normal.toArray(S,L),S[L+3]=u.constant}p.value=S,p.needsUpdate=!0}return t.numPlanes=R,t.numIntersection=0,S}}const Rs=4,ay=[.125,.215,.35,.446,.526,.582],rr=20,Ww=256,wl=new RM,sy=new Le;let cp=null,up=0,fp=0,dp=!1;const qw=new rt;class ry{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(t,n=0,s=.1,o=100,c={}){const{size:u=256,position:d=qw}=c;cp=this._renderer.getRenderTarget(),up=this._renderer.getActiveCubeFace(),fp=this._renderer.getActiveMipmapLevel(),dp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(u);const p=this._allocateTargets();return p.depthBuffer=!0,this._sceneToCubeUV(t,s,o,p,d),n>0&&this._blur(p,0,0,n),this._applyPMREM(p),this._cleanup(p),p}fromEquirectangular(t,n=null){return this._fromTexture(t,n)}fromCubemap(t,n=null){return this._fromTexture(t,n)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=cy(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=ly(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodMeshes.length;t++)this._lodMeshes[t].geometry.dispose()}_cleanup(t){this._renderer.setRenderTarget(cp,up,fp),this._renderer.xr.enabled=dp,t.scissorTest=!1,uo(t,0,0,t.width,t.height)}_fromTexture(t,n){t.mapping===hr||t.mapping===yo?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),cp=this._renderer.getRenderTarget(),up=this._renderer.getActiveCubeFace(),fp=this._renderer.getActiveMipmapLevel(),dp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const s=n||this._allocateTargets();return this._textureToCubeUV(t,s),this._applyPMREM(s),this._cleanup(s),s}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),n=4*this._cubeSize,s={magFilter:jn,minFilter:jn,generateMipmaps:!1,type:Ga,format:Xi,colorSpace:ef,depthBuffer:!1},o=oy(t,n,s);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==n){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=oy(t,n,s);const{_lodMax:c}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=Yw(c)),this._blurMaterial=Zw(c,t,n),this._ggxMaterial=Kw(c,t,n)}return o}_compileMaterial(t){const n=new ja(new Yi,t);this._renderer.compile(n,wl)}_sceneToCubeUV(t,n,s,o,c){const p=new Di(90,1,n,s),h=[1,-1,1,1,1,1],g=[1,1,1,-1,-1,-1],_=this._renderer,v=_.autoClear,y=_.toneMapping;_.getClearColor(sy),_.toneMapping=oa,_.autoClear=!1,_.state.buffers.depth.getReversed()&&(_.setRenderTarget(o),_.clearDepth(),_.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new ja(new Kl,new yM({name:"PMREM.Background",side:ii,depthWrite:!1,depthTest:!1})));const R=this._backgroundBox,S=R.material;let x=!1;const A=t.background;A?A.isColor&&(S.color.copy(A),t.background=null,x=!0):(S.color.copy(sy),x=!0);for(let N=0;N<6;N++){const L=N%3;L===0?(p.up.set(0,h[N],0),p.position.set(c.x,c.y,c.z),p.lookAt(c.x+g[N],c.y,c.z)):L===1?(p.up.set(0,0,h[N]),p.position.set(c.x,c.y,c.z),p.lookAt(c.x,c.y+g[N],c.z)):(p.up.set(0,h[N],0),p.position.set(c.x,c.y,c.z),p.lookAt(c.x,c.y,c.z+g[N]));const H=this._cubeSize;uo(o,L*H,N>2?H:0,H,H),_.setRenderTarget(o),x&&_.render(R,p),_.render(t,p)}_.toneMapping=y,_.autoClear=v,t.background=A}_textureToCubeUV(t,n){const s=this._renderer,o=t.mapping===hr||t.mapping===yo;o?(this._cubemapMaterial===null&&(this._cubemapMaterial=cy()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=ly());const c=o?this._cubemapMaterial:this._equirectMaterial,u=this._lodMeshes[0];u.material=c;const d=c.uniforms;d.envMap.value=t;const p=this._cubeSize;uo(n,0,0,3*p,2*p),s.setRenderTarget(n),s.render(u,wl)}_applyPMREM(t){const n=this._renderer,s=n.autoClear;n.autoClear=!1;const o=this._lodMeshes.length;for(let c=1;c<o;c++)this._applyGGXFilter(t,c-1,c);n.autoClear=s}_applyGGXFilter(t,n,s){const o=this._renderer,c=this._pingPongRenderTarget,u=this._ggxMaterial,d=this._lodMeshes[s];d.material=u;const p=u.uniforms,h=s/(this._lodMeshes.length-1),g=n/(this._lodMeshes.length-1),_=Math.sqrt(h*h-g*g),v=0+h*1.25,y=_*v,{_lodMax:b}=this,R=this._sizeLods[s],S=3*R*(s>b-Rs?s-b+Rs:0),x=4*(this._cubeSize-R);p.envMap.value=t.texture,p.roughness.value=y,p.mipInt.value=b-n,uo(c,S,x,3*R,2*R),o.setRenderTarget(c),o.render(d,wl),p.envMap.value=c.texture,p.roughness.value=0,p.mipInt.value=b-s,uo(t,S,x,3*R,2*R),o.setRenderTarget(t),o.render(d,wl)}_blur(t,n,s,o,c){const u=this._pingPongRenderTarget;this._halfBlur(t,u,n,s,o,"latitudinal",c),this._halfBlur(u,t,s,s,o,"longitudinal",c)}_halfBlur(t,n,s,o,c,u,d){const p=this._renderer,h=this._blurMaterial;u!=="latitudinal"&&u!=="longitudinal"&&Te("blur direction must be either latitudinal or longitudinal!");const g=3,_=this._lodMeshes[o];_.material=h;const v=h.uniforms,y=this._sizeLods[s]-1,b=isFinite(c)?Math.PI/(2*y):2*Math.PI/(2*rr-1),R=c/b,S=isFinite(c)?1+Math.floor(g*R):rr;S>rr&&ie(`sigmaRadians, ${c}, is too large and will clip, as it requested ${S} samples when the maximum is set to ${rr}`);const x=[];let A=0;for(let O=0;O<rr;++O){const E=O/R,U=Math.exp(-E*E/2);x.push(U),O===0?A+=U:O<S&&(A+=2*U)}for(let O=0;O<x.length;O++)x[O]=x[O]/A;v.envMap.value=t.texture,v.samples.value=S,v.weights.value=x,v.latitudinal.value=u==="latitudinal",d&&(v.poleAxis.value=d);const{_lodMax:N}=this;v.dTheta.value=b,v.mipInt.value=N-s;const L=this._sizeLods[o],H=3*L*(o>N-Rs?o-N+Rs:0),B=4*(this._cubeSize-L);uo(n,H,B,3*L,2*L),p.setRenderTarget(n),p.render(_,wl)}}function Yw(i){const t=[],n=[],s=[];let o=i;const c=i-Rs+1+ay.length;for(let u=0;u<c;u++){const d=Math.pow(2,o);t.push(d);let p=1/d;u>i-Rs?p=ay[u-i+Rs-1]:u===0&&(p=0),n.push(p);const h=1/(d-2),g=-h,_=1+h,v=[g,g,_,g,_,_,g,g,_,_,g,_],y=6,b=6,R=3,S=2,x=1,A=new Float32Array(R*b*y),N=new Float32Array(S*b*y),L=new Float32Array(x*b*y);for(let B=0;B<y;B++){const O=B%3*2/3-1,E=B>2?0:-1,U=[O,E,0,O+2/3,E,0,O+2/3,E+1,0,O,E,0,O+2/3,E+1,0,O,E+1,0];A.set(U,R*b*B),N.set(v,S*b*B);const V=[B,B,B,B,B,B];L.set(V,x*b*B)}const H=new Yi;H.setAttribute("position",new ca(A,R)),H.setAttribute("uv",new ca(N,S)),H.setAttribute("faceIndex",new ca(L,x)),s.push(new ja(H,null)),o>Rs&&o--}return{lodMeshes:s,sizeLods:t,sigmas:n}}function oy(i,t,n){const s=new la(i,t,n);return s.texture.mapping=_f,s.texture.name="PMREM.cubeUv",s.scissorTest=!0,s}function uo(i,t,n,s,o){i.viewport.set(t,n,s,o),i.scissor.set(t,n,s,o)}function Kw(i,t,n){return new da({name:"PMREMGGXConvolution",defines:{GGX_SAMPLES:Ww,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:yf(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:Va,depthTest:!1,depthWrite:!1})}function Zw(i,t,n){const s=new Float32Array(rr),o=new rt(0,1,0);return new da({name:"SphericalGaussianBlur",defines:{n:rr,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:s},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:o}},vertexShader:yf(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Va,depthTest:!1,depthWrite:!1})}function ly(){return new da({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:yf(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Va,depthTest:!1,depthWrite:!1})}function cy(){return new da({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:yf(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Va,depthTest:!1,depthWrite:!1})}function yf(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}class DM extends la{constructor(t=1,n={}){super(t,t,n),this.isWebGLCubeRenderTarget=!0;const s={width:t,height:t,depth:1},o=[s,s,s,s,s,s];this.texture=new bM(o),this._setTextureOptions(n),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(t,n){this.texture.type=n.type,this.texture.colorSpace=n.colorSpace,this.texture.generateMipmaps=n.generateMipmaps,this.texture.minFilter=n.minFilter,this.texture.magFilter=n.magFilter;const s={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},o=new Kl(5,5,5),c=new da({name:"CubemapFromEquirect",uniforms:Mo(s.uniforms),vertexShader:s.vertexShader,fragmentShader:s.fragmentShader,side:ii,blending:Va});c.uniforms.tEquirect.value=n;const u=new ja(o,c),d=n.minFilter;return n.minFilter===or&&(n.minFilter=jn),new nR(1,10,this).update(t,u),n.minFilter=d,u.geometry.dispose(),u.material.dispose(),this}clear(t,n=!0,s=!0,o=!0){const c=t.getRenderTarget();for(let u=0;u<6;u++)t.setRenderTarget(this,u),t.clear(n,s,o);t.setRenderTarget(c)}}function Qw(i){let t=new WeakMap,n=new WeakMap,s=null;function o(v,y=!1){return v==null?null:y?u(v):c(v)}function c(v){if(v&&v.isTexture){const y=v.mapping;if(y===Fh||y===Bh)if(t.has(v)){const b=t.get(v).texture;return d(b,v.mapping)}else{const b=v.image;if(b&&b.height>0){const R=new DM(b.height);return R.fromEquirectangularTexture(i,v),t.set(v,R),v.addEventListener("dispose",h),d(R.texture,v.mapping)}else return null}}return v}function u(v){if(v&&v.isTexture){const y=v.mapping,b=y===Fh||y===Bh,R=y===hr||y===yo;if(b||R){let S=n.get(v);const x=S!==void 0?S.texture.pmremVersion:0;if(v.isRenderTargetTexture&&v.pmremVersion!==x)return s===null&&(s=new ry(i)),S=b?s.fromEquirectangular(v,S):s.fromCubemap(v,S),S.texture.pmremVersion=v.pmremVersion,n.set(v,S),S.texture;if(S!==void 0)return S.texture;{const A=v.image;return b&&A&&A.height>0||R&&A&&p(A)?(s===null&&(s=new ry(i)),S=b?s.fromEquirectangular(v):s.fromCubemap(v),S.texture.pmremVersion=v.pmremVersion,n.set(v,S),v.addEventListener("dispose",g),S.texture):null}}}return v}function d(v,y){return y===Fh?v.mapping=hr:y===Bh&&(v.mapping=yo),v}function p(v){let y=0;const b=6;for(let R=0;R<b;R++)v[R]!==void 0&&y++;return y===b}function h(v){const y=v.target;y.removeEventListener("dispose",h);const b=t.get(y);b!==void 0&&(t.delete(y),b.dispose())}function g(v){const y=v.target;y.removeEventListener("dispose",g);const b=n.get(y);b!==void 0&&(n.delete(y),b.dispose())}function _(){t=new WeakMap,n=new WeakMap,s!==null&&(s.dispose(),s=null)}return{get:o,dispose:_}}function Jw(i){const t={};function n(s){if(t[s]!==void 0)return t[s];const o=i.getExtension(s);return t[s]=o,o}return{has:function(s){return n(s)!==null},init:function(){n("EXT_color_buffer_float"),n("WEBGL_clip_cull_distance"),n("OES_texture_float_linear"),n("EXT_color_buffer_half_float"),n("WEBGL_multisampled_render_to_texture"),n("WEBGL_render_shared_exponent")},get:function(s){const o=n(s);return o===null&&xm("WebGLRenderer: "+s+" extension not supported."),o}}}function $w(i,t,n,s){const o={},c=new WeakMap;function u(_){const v=_.target;v.index!==null&&t.remove(v.index);for(const b in v.attributes)t.remove(v.attributes[b]);v.removeEventListener("dispose",u),delete o[v.id];const y=c.get(v);y&&(t.remove(y),c.delete(v)),s.releaseStatesOfGeometry(v),v.isInstancedBufferGeometry===!0&&delete v._maxInstanceCount,n.memory.geometries--}function d(_,v){return o[v.id]===!0||(v.addEventListener("dispose",u),o[v.id]=!0,n.memory.geometries++),v}function p(_){const v=_.attributes;for(const y in v)t.update(v[y],i.ARRAY_BUFFER)}function h(_){const v=[],y=_.index,b=_.attributes.position;let R=0;if(b===void 0)return;if(y!==null){const A=y.array;R=y.version;for(let N=0,L=A.length;N<L;N+=3){const H=A[N+0],B=A[N+1],O=A[N+2];v.push(H,B,B,O,O,H)}}else{const A=b.array;R=b.version;for(let N=0,L=A.length/3-1;N<L;N+=3){const H=N+0,B=N+1,O=N+2;v.push(H,B,B,O,O,H)}}const S=new(b.count>=65535?vM:_M)(v,1);S.version=R;const x=c.get(_);x&&t.remove(x),c.set(_,S)}function g(_){const v=c.get(_);if(v){const y=_.index;y!==null&&v.version<y.version&&h(_)}else h(_);return c.get(_)}return{get:d,update:p,getWireframeAttribute:g}}function t2(i,t,n){let s;function o(_){s=_}let c,u;function d(_){c=_.type,u=_.bytesPerElement}function p(_,v){i.drawElements(s,v,c,_*u),n.update(v,s,1)}function h(_,v,y){y!==0&&(i.drawElementsInstanced(s,v,c,_*u,y),n.update(v,s,y))}function g(_,v,y){if(y===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(s,v,0,c,_,0,y);let R=0;for(let S=0;S<y;S++)R+=v[S];n.update(R,s,1)}this.setMode=o,this.setIndex=d,this.render=p,this.renderInstances=h,this.renderMultiDraw=g}function e2(i){const t={geometries:0,textures:0},n={frame:0,calls:0,triangles:0,points:0,lines:0};function s(c,u,d){switch(n.calls++,u){case i.TRIANGLES:n.triangles+=d*(c/3);break;case i.LINES:n.lines+=d*(c/2);break;case i.LINE_STRIP:n.lines+=d*(c-1);break;case i.LINE_LOOP:n.lines+=d*c;break;case i.POINTS:n.points+=d*c;break;default:Te("WebGLInfo: Unknown draw mode:",u);break}}function o(){n.calls=0,n.triangles=0,n.points=0,n.lines=0}return{memory:t,render:n,programs:null,autoReset:!0,reset:o,update:s}}function n2(i,t,n){const s=new WeakMap,o=new hn;function c(u,d,p){const h=u.morphTargetInfluences,g=d.morphAttributes.position||d.morphAttributes.normal||d.morphAttributes.color,_=g!==void 0?g.length:0;let v=s.get(d);if(v===void 0||v.count!==_){let V=function(){E.dispose(),s.delete(d),d.removeEventListener("dispose",V)};var y=V;v!==void 0&&v.texture.dispose();const b=d.morphAttributes.position!==void 0,R=d.morphAttributes.normal!==void 0,S=d.morphAttributes.color!==void 0,x=d.morphAttributes.position||[],A=d.morphAttributes.normal||[],N=d.morphAttributes.color||[];let L=0;b===!0&&(L=1),R===!0&&(L=2),S===!0&&(L=3);let H=d.attributes.position.count*L,B=1;H>t.maxTextureSize&&(B=Math.ceil(H/t.maxTextureSize),H=t.maxTextureSize);const O=new Float32Array(H*B*4*_),E=new pM(O,H,B,_);E.type=sa,E.needsUpdate=!0;const U=L*4;for(let F=0;F<_;F++){const j=x[F],lt=A[F],ct=N[F],q=H*B*4*F;for(let I=0;I<j.count;I++){const G=I*U;b===!0&&(o.fromBufferAttribute(j,I),O[q+G+0]=o.x,O[q+G+1]=o.y,O[q+G+2]=o.z,O[q+G+3]=0),R===!0&&(o.fromBufferAttribute(lt,I),O[q+G+4]=o.x,O[q+G+5]=o.y,O[q+G+6]=o.z,O[q+G+7]=0),S===!0&&(o.fromBufferAttribute(ct,I),O[q+G+8]=o.x,O[q+G+9]=o.y,O[q+G+10]=o.z,O[q+G+11]=ct.itemSize===4?o.w:1)}}v={count:_,texture:E,size:new je(H,B)},s.set(d,v),d.addEventListener("dispose",V)}if(u.isInstancedMesh===!0&&u.morphTexture!==null)p.getUniforms().setValue(i,"morphTexture",u.morphTexture,n);else{let b=0;for(let S=0;S<h.length;S++)b+=h[S];const R=d.morphTargetsRelative?1:1-b;p.getUniforms().setValue(i,"morphTargetBaseInfluence",R),p.getUniforms().setValue(i,"morphTargetInfluences",h)}p.getUniforms().setValue(i,"morphTargetsTexture",v.texture,n),p.getUniforms().setValue(i,"morphTargetsTextureSize",v.size)}return{update:c}}function i2(i,t,n,s,o){let c=new WeakMap;function u(h){const g=o.render.frame,_=h.geometry,v=t.get(h,_);if(c.get(v)!==g&&(t.update(v),c.set(v,g)),h.isInstancedMesh&&(h.hasEventListener("dispose",p)===!1&&h.addEventListener("dispose",p),c.get(h)!==g&&(n.update(h.instanceMatrix,i.ARRAY_BUFFER),h.instanceColor!==null&&n.update(h.instanceColor,i.ARRAY_BUFFER),c.set(h,g))),h.isSkinnedMesh){const y=h.skeleton;c.get(y)!==g&&(y.update(),c.set(y,g))}return v}function d(){c=new WeakMap}function p(h){const g=h.target;g.removeEventListener("dispose",p),s.releaseStatesOfObject(g),n.remove(g.instanceMatrix),g.instanceColor!==null&&n.remove(g.instanceColor)}return{update:u,dispose:d}}const a2={[JS]:"LINEAR_TONE_MAPPING",[$S]:"REINHARD_TONE_MAPPING",[tM]:"CINEON_TONE_MAPPING",[eM]:"ACES_FILMIC_TONE_MAPPING",[iM]:"AGX_TONE_MAPPING",[aM]:"NEUTRAL_TONE_MAPPING",[nM]:"CUSTOM_TONE_MAPPING"};function s2(i,t,n,s,o){const c=new la(t,n,{type:i,depthBuffer:s,stencilBuffer:o,depthTexture:s?new So(t,n):void 0}),u=new la(t,n,{type:Ga,depthBuffer:!1,stencilBuffer:!1}),d=new Yi;d.setAttribute("position",new Wi([-1,3,0,-1,-1,0,3,-1,0],3)),d.setAttribute("uv",new Wi([0,2,0,0,2,0],2));const p=new $A({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),h=new ja(d,p),g=new RM(-1,1,1,-1,0,1);let _=null,v=null,y=!1,b,R=null,S=[],x=!1;this.setSize=function(A,N){c.setSize(A,N),u.setSize(A,N);for(let L=0;L<S.length;L++){const H=S[L];H.setSize&&H.setSize(A,N)}},this.setEffects=function(A){S=A,x=S.length>0&&S[0].isRenderPass===!0;const N=c.width,L=c.height;for(let H=0;H<S.length;H++){const B=S[H];B.setSize&&B.setSize(N,L)}},this.begin=function(A,N){if(y||A.toneMapping===oa&&S.length===0)return!1;if(R=N,N!==null){const L=N.width,H=N.height;(c.width!==L||c.height!==H)&&this.setSize(L,H)}return x===!1&&A.setRenderTarget(c),b=A.toneMapping,A.toneMapping=oa,!0},this.hasRenderPass=function(){return x},this.end=function(A,N){A.toneMapping=b,y=!0;let L=c,H=u;for(let B=0;B<S.length;B++){const O=S[B];if(O.enabled!==!1&&(O.render(A,H,L,N),O.needsSwap!==!1)){const E=L;L=H,H=E}}if(_!==A.outputColorSpace||v!==A.toneMapping){_=A.outputColorSpace,v=A.toneMapping,p.defines={},be.getTransfer(_)===ze&&(p.defines.SRGB_TRANSFER="");const B=a2[v];B&&(p.defines[B]=""),p.needsUpdate=!0}p.uniforms.tDiffuse.value=L.texture,A.setRenderTarget(R),A.render(h,g),R=null,y=!1},this.isCompositing=function(){return y},this.dispose=function(){c.depthTexture&&c.depthTexture.dispose(),c.dispose(),u.dispose(),d.dispose(),p.dispose()}}const NM=new Kn,Mm=new So(1,1),LM=new pM,UM=new wA,PM=new bM,uy=[],fy=[],dy=new Float32Array(16),hy=new Float32Array(9),py=new Float32Array(4);function Ao(i,t,n){const s=i[0];if(s<=0||s>0)return i;const o=t*n;let c=uy[o];if(c===void 0&&(c=new Float32Array(o),uy[o]=c),t!==0){s.toArray(c,0);for(let u=1,d=0;u!==t;++u)d+=n,i[u].toArray(c,d)}return c}function An(i,t){if(i.length!==t.length)return!1;for(let n=0,s=i.length;n<s;n++)if(i[n]!==t[n])return!1;return!0}function Rn(i,t){for(let n=0,s=t.length;n<s;n++)i[n]=t[n]}function Sf(i,t){let n=fy[t];n===void 0&&(n=new Int32Array(t),fy[t]=n);for(let s=0;s!==t;++s)n[s]=i.allocateTextureUnit();return n}function r2(i,t){const n=this.cache;n[0]!==t&&(i.uniform1f(this.addr,t),n[0]=t)}function o2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(i.uniform2f(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(An(n,t))return;i.uniform2fv(this.addr,t),Rn(n,t)}}function l2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(i.uniform3f(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else if(t.r!==void 0)(n[0]!==t.r||n[1]!==t.g||n[2]!==t.b)&&(i.uniform3f(this.addr,t.r,t.g,t.b),n[0]=t.r,n[1]=t.g,n[2]=t.b);else{if(An(n,t))return;i.uniform3fv(this.addr,t),Rn(n,t)}}function c2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(i.uniform4f(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(An(n,t))return;i.uniform4fv(this.addr,t),Rn(n,t)}}function u2(i,t){const n=this.cache,s=t.elements;if(s===void 0){if(An(n,t))return;i.uniformMatrix2fv(this.addr,!1,t),Rn(n,t)}else{if(An(n,s))return;py.set(s),i.uniformMatrix2fv(this.addr,!1,py),Rn(n,s)}}function f2(i,t){const n=this.cache,s=t.elements;if(s===void 0){if(An(n,t))return;i.uniformMatrix3fv(this.addr,!1,t),Rn(n,t)}else{if(An(n,s))return;hy.set(s),i.uniformMatrix3fv(this.addr,!1,hy),Rn(n,s)}}function d2(i,t){const n=this.cache,s=t.elements;if(s===void 0){if(An(n,t))return;i.uniformMatrix4fv(this.addr,!1,t),Rn(n,t)}else{if(An(n,s))return;dy.set(s),i.uniformMatrix4fv(this.addr,!1,dy),Rn(n,s)}}function h2(i,t){const n=this.cache;n[0]!==t&&(i.uniform1i(this.addr,t),n[0]=t)}function p2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(i.uniform2i(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(An(n,t))return;i.uniform2iv(this.addr,t),Rn(n,t)}}function m2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(i.uniform3i(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(An(n,t))return;i.uniform3iv(this.addr,t),Rn(n,t)}}function g2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(i.uniform4i(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(An(n,t))return;i.uniform4iv(this.addr,t),Rn(n,t)}}function _2(i,t){const n=this.cache;n[0]!==t&&(i.uniform1ui(this.addr,t),n[0]=t)}function v2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(i.uniform2ui(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(An(n,t))return;i.uniform2uiv(this.addr,t),Rn(n,t)}}function x2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(i.uniform3ui(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(An(n,t))return;i.uniform3uiv(this.addr,t),Rn(n,t)}}function y2(i,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(i.uniform4ui(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(An(n,t))return;i.uniform4uiv(this.addr,t),Rn(n,t)}}function S2(i,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(i.uniform1i(this.addr,o),s[0]=o);let c;this.type===i.SAMPLER_2D_SHADOW?(Mm.compareFunction=n.isReversedDepthBuffer()?ag:ig,c=Mm):c=NM,n.setTexture2D(t||c,o)}function M2(i,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(i.uniform1i(this.addr,o),s[0]=o),n.setTexture3D(t||UM,o)}function b2(i,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(i.uniform1i(this.addr,o),s[0]=o),n.setTextureCube(t||PM,o)}function E2(i,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(i.uniform1i(this.addr,o),s[0]=o),n.setTexture2DArray(t||LM,o)}function T2(i){switch(i){case 5126:return r2;case 35664:return o2;case 35665:return l2;case 35666:return c2;case 35674:return u2;case 35675:return f2;case 35676:return d2;case 5124:case 35670:return h2;case 35667:case 35671:return p2;case 35668:case 35672:return m2;case 35669:case 35673:return g2;case 5125:return _2;case 36294:return v2;case 36295:return x2;case 36296:return y2;case 35678:case 36198:case 36298:case 36306:case 35682:return S2;case 35679:case 36299:case 36307:return M2;case 35680:case 36300:case 36308:case 36293:return b2;case 36289:case 36303:case 36311:case 36292:return E2}}function A2(i,t){i.uniform1fv(this.addr,t)}function R2(i,t){const n=Ao(t,this.size,2);i.uniform2fv(this.addr,n)}function C2(i,t){const n=Ao(t,this.size,3);i.uniform3fv(this.addr,n)}function w2(i,t){const n=Ao(t,this.size,4);i.uniform4fv(this.addr,n)}function D2(i,t){const n=Ao(t,this.size,4);i.uniformMatrix2fv(this.addr,!1,n)}function N2(i,t){const n=Ao(t,this.size,9);i.uniformMatrix3fv(this.addr,!1,n)}function L2(i,t){const n=Ao(t,this.size,16);i.uniformMatrix4fv(this.addr,!1,n)}function U2(i,t){i.uniform1iv(this.addr,t)}function P2(i,t){i.uniform2iv(this.addr,t)}function O2(i,t){i.uniform3iv(this.addr,t)}function F2(i,t){i.uniform4iv(this.addr,t)}function B2(i,t){i.uniform1uiv(this.addr,t)}function I2(i,t){i.uniform2uiv(this.addr,t)}function z2(i,t){i.uniform3uiv(this.addr,t)}function V2(i,t){i.uniform4uiv(this.addr,t)}function H2(i,t,n){const s=this.cache,o=t.length,c=Sf(n,o);An(s,c)||(i.uniform1iv(this.addr,c),Rn(s,c));let u;this.type===i.SAMPLER_2D_SHADOW?u=Mm:u=NM;for(let d=0;d!==o;++d)n.setTexture2D(t[d]||u,c[d])}function G2(i,t,n){const s=this.cache,o=t.length,c=Sf(n,o);An(s,c)||(i.uniform1iv(this.addr,c),Rn(s,c));for(let u=0;u!==o;++u)n.setTexture3D(t[u]||UM,c[u])}function k2(i,t,n){const s=this.cache,o=t.length,c=Sf(n,o);An(s,c)||(i.uniform1iv(this.addr,c),Rn(s,c));for(let u=0;u!==o;++u)n.setTextureCube(t[u]||PM,c[u])}function j2(i,t,n){const s=this.cache,o=t.length,c=Sf(n,o);An(s,c)||(i.uniform1iv(this.addr,c),Rn(s,c));for(let u=0;u!==o;++u)n.setTexture2DArray(t[u]||LM,c[u])}function X2(i){switch(i){case 5126:return A2;case 35664:return R2;case 35665:return C2;case 35666:return w2;case 35674:return D2;case 35675:return N2;case 35676:return L2;case 5124:case 35670:return U2;case 35667:case 35671:return P2;case 35668:case 35672:return O2;case 35669:case 35673:return F2;case 5125:return B2;case 36294:return I2;case 36295:return z2;case 36296:return V2;case 35678:case 36198:case 36298:case 36306:case 35682:return H2;case 35679:case 36299:case 36307:return G2;case 35680:case 36300:case 36308:case 36293:return k2;case 36289:case 36303:case 36311:case 36292:return j2}}class W2{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.setValue=T2(n.type)}}class q2{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.size=n.size,this.setValue=X2(n.type)}}class Y2{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,n,s){const o=this.seq;for(let c=0,u=o.length;c!==u;++c){const d=o[c];d.setValue(t,n[d.id],s)}}}const hp=/(\w+)(\])?(\[|\.)?/g;function my(i,t){i.seq.push(t),i.map[t.id]=t}function K2(i,t,n){const s=i.name,o=s.length;for(hp.lastIndex=0;;){const c=hp.exec(s),u=hp.lastIndex;let d=c[1];const p=c[2]==="]",h=c[3];if(p&&(d=d|0),h===void 0||h==="["&&u+2===o){my(n,h===void 0?new W2(d,i,t):new q2(d,i,t));break}else{let _=n.map[d];_===void 0&&(_=new Y2(d),my(n,_)),n=_}}}class ju{constructor(t,n){this.seq=[],this.map={};const s=t.getProgramParameter(n,t.ACTIVE_UNIFORMS);for(let u=0;u<s;++u){const d=t.getActiveUniform(n,u),p=t.getUniformLocation(n,d.name);K2(d,p,this)}const o=[],c=[];for(const u of this.seq)u.type===t.SAMPLER_2D_SHADOW||u.type===t.SAMPLER_CUBE_SHADOW||u.type===t.SAMPLER_2D_ARRAY_SHADOW?o.push(u):c.push(u);o.length>0&&(this.seq=o.concat(c))}setValue(t,n,s,o){const c=this.map[n];c!==void 0&&c.setValue(t,s,o)}setOptional(t,n,s){const o=n[s];o!==void 0&&this.setValue(t,s,o)}static upload(t,n,s,o){for(let c=0,u=n.length;c!==u;++c){const d=n[c],p=s[d.id];p.needsUpdate!==!1&&d.setValue(t,p.value,o)}}static seqWithValue(t,n){const s=[];for(let o=0,c=t.length;o!==c;++o){const u=t[o];u.id in n&&s.push(u)}return s}}function gy(i,t,n){const s=i.createShader(t);return i.shaderSource(s,n),i.compileShader(s),s}const Z2=37297;let Q2=0;function J2(i,t){const n=i.split(`
`),s=[],o=Math.max(t-6,0),c=Math.min(t+6,n.length);for(let u=o;u<c;u++){const d=u+1;s.push(`${d===t?">":" "} ${d}: ${n[u]}`)}return s.join(`
`)}const _y=new oe;function $2(i){be._getMatrix(_y,be.workingColorSpace,i);const t=`mat3( ${_y.elements.map(n=>n.toFixed(4))} )`;switch(be.getTransfer(i)){case nf:return[t,"LinearTransferOETF"];case ze:return[t,"sRGBTransferOETF"];default:return ie("WebGLProgram: Unsupported color space: ",i),[t,"LinearTransferOETF"]}}function vy(i,t,n){const s=i.getShaderParameter(t,i.COMPILE_STATUS),c=(i.getShaderInfoLog(t)||"").trim();if(s&&c==="")return"";const u=/ERROR: 0:(\d+)/.exec(c);if(u){const d=parseInt(u[1]);return n.toUpperCase()+`

`+c+`

`+J2(i.getShaderSource(t),d)}else return c}function t3(i,t){const n=$2(t);return[`vec4 ${i}( vec4 value ) {`,`	return ${n[1]}( vec4( value.rgb * ${n[0]}, value.a ) );`,"}"].join(`
`)}const e3={[JS]:"Linear",[$S]:"Reinhard",[tM]:"Cineon",[eM]:"ACESFilmic",[iM]:"AgX",[aM]:"Neutral",[nM]:"Custom"};function n3(i,t){const n=e3[t];return n===void 0?(ie("WebGLProgram: Unsupported toneMapping:",t),"vec3 "+i+"( vec3 color ) { return LinearToneMapping( color ); }"):"vec3 "+i+"( vec3 color ) { return "+n+"ToneMapping( color ); }"}const Pu=new rt;function i3(){be.getLuminanceCoefficients(Pu);const i=Pu.x.toFixed(4),t=Pu.y.toFixed(4),n=Pu.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${t}, ${n} );`,"	return dot( weights, rgb );","}"].join(`
`)}function a3(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Ul).join(`
`)}function s3(i){const t=[];for(const n in i){const s=i[n];s!==!1&&t.push("#define "+n+" "+s)}return t.join(`
`)}function r3(i,t){const n={},s=i.getProgramParameter(t,i.ACTIVE_ATTRIBUTES);for(let o=0;o<s;o++){const c=i.getActiveAttrib(t,o),u=c.name;let d=1;c.type===i.FLOAT_MAT2&&(d=2),c.type===i.FLOAT_MAT3&&(d=3),c.type===i.FLOAT_MAT4&&(d=4),n[u]={type:c.type,location:i.getAttribLocation(t,u),locationSize:d}}return n}function Ul(i){return i!==""}function xy(i,t){const n=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,n).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function yy(i,t){return i.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const o3=/^[ \t]*#include +<([\w\d./]+)>/gm;function bm(i){return i.replace(o3,c3)}const l3=new Map;function c3(i,t){let n=de[t];if(n===void 0){const s=l3.get(t);if(s!==void 0)n=de[s],ie('WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,s);else throw new Error("Can not resolve #include <"+t+">")}return bm(n)}const u3=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Sy(i){return i.replace(u3,f3)}function f3(i,t,n,s){let o="";for(let c=parseInt(t);c<parseInt(n);c++)o+=s.replace(/\[\s*i\s*\]/g,"[ "+c+" ]").replace(/UNROLLED_LOOP_INDEX/g,c);return o}function My(i){let t=`precision ${i.precision} float;
	precision ${i.precision} int;
	precision ${i.precision} sampler2D;
	precision ${i.precision} samplerCube;
	precision ${i.precision} sampler3D;
	precision ${i.precision} sampler2DArray;
	precision ${i.precision} sampler2DShadow;
	precision ${i.precision} samplerCubeShadow;
	precision ${i.precision} sampler2DArrayShadow;
	precision ${i.precision} isampler2D;
	precision ${i.precision} isampler3D;
	precision ${i.precision} isamplerCube;
	precision ${i.precision} isampler2DArray;
	precision ${i.precision} usampler2D;
	precision ${i.precision} usampler3D;
	precision ${i.precision} usamplerCube;
	precision ${i.precision} usampler2DArray;
	`;return i.precision==="highp"?t+=`
#define HIGH_PRECISION`:i.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:i.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}const d3={[zu]:"SHADOWMAP_TYPE_PCF",[Ll]:"SHADOWMAP_TYPE_VSM"};function h3(i){return d3[i.shadowMapType]||"SHADOWMAP_TYPE_BASIC"}const p3={[hr]:"ENVMAP_TYPE_CUBE",[yo]:"ENVMAP_TYPE_CUBE",[_f]:"ENVMAP_TYPE_CUBE_UV"};function m3(i){return i.envMap===!1?"ENVMAP_TYPE_CUBE":p3[i.envMapMode]||"ENVMAP_TYPE_CUBE"}const g3={[yo]:"ENVMAP_MODE_REFRACTION"};function _3(i){return i.envMap===!1?"ENVMAP_MODE_REFLECTION":g3[i.envMapMode]||"ENVMAP_MODE_REFLECTION"}const v3={[QS]:"ENVMAP_BLENDING_MULTIPLY",[lA]:"ENVMAP_BLENDING_MIX",[cA]:"ENVMAP_BLENDING_ADD"};function x3(i){return i.envMap===!1?"ENVMAP_BLENDING_NONE":v3[i.combine]||"ENVMAP_BLENDING_NONE"}function y3(i){const t=i.envMapCubeUVHeight;if(t===null)return null;const n=Math.log2(t)-2,s=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,n),112)),texelHeight:s,maxMip:n}}function S3(i,t,n,s){const o=i.getContext(),c=n.defines;let u=n.vertexShader,d=n.fragmentShader;const p=h3(n),h=m3(n),g=_3(n),_=x3(n),v=y3(n),y=a3(n),b=s3(c),R=o.createProgram();let S,x,A=n.glslVersion?"#version "+n.glslVersion+`
`:"";n.isRawShaderMaterial?(S=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b].filter(Ul).join(`
`),S.length>0&&(S+=`
`),x=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b].filter(Ul).join(`
`),x.length>0&&(x+=`
`)):(S=[My(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b,n.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",n.batching?"#define USE_BATCHING":"",n.batchingColor?"#define USE_BATCHING_COLOR":"",n.instancing?"#define USE_INSTANCING":"",n.instancingColor?"#define USE_INSTANCING_COLOR":"",n.instancingMorph?"#define USE_INSTANCING_MORPH":"",n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.map?"#define USE_MAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+g:"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.displacementMap?"#define USE_DISPLACEMENTMAP":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.mapUv?"#define MAP_UV "+n.mapUv:"",n.alphaMapUv?"#define ALPHAMAP_UV "+n.alphaMapUv:"",n.lightMapUv?"#define LIGHTMAP_UV "+n.lightMapUv:"",n.aoMapUv?"#define AOMAP_UV "+n.aoMapUv:"",n.emissiveMapUv?"#define EMISSIVEMAP_UV "+n.emissiveMapUv:"",n.bumpMapUv?"#define BUMPMAP_UV "+n.bumpMapUv:"",n.normalMapUv?"#define NORMALMAP_UV "+n.normalMapUv:"",n.displacementMapUv?"#define DISPLACEMENTMAP_UV "+n.displacementMapUv:"",n.metalnessMapUv?"#define METALNESSMAP_UV "+n.metalnessMapUv:"",n.roughnessMapUv?"#define ROUGHNESSMAP_UV "+n.roughnessMapUv:"",n.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+n.anisotropyMapUv:"",n.clearcoatMapUv?"#define CLEARCOATMAP_UV "+n.clearcoatMapUv:"",n.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+n.clearcoatNormalMapUv:"",n.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+n.clearcoatRoughnessMapUv:"",n.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+n.iridescenceMapUv:"",n.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+n.iridescenceThicknessMapUv:"",n.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+n.sheenColorMapUv:"",n.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+n.sheenRoughnessMapUv:"",n.specularMapUv?"#define SPECULARMAP_UV "+n.specularMapUv:"",n.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+n.specularColorMapUv:"",n.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+n.specularIntensityMapUv:"",n.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+n.transmissionMapUv:"",n.thicknessMapUv?"#define THICKNESSMAP_UV "+n.thicknessMapUv:"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexNormals?"#define HAS_NORMAL":"",n.vertexColors?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.flatShading?"#define FLAT_SHADED":"",n.skinning?"#define USE_SKINNING":"",n.morphTargets?"#define USE_MORPHTARGETS":"",n.morphNormals&&n.flatShading===!1?"#define USE_MORPHNORMALS":"",n.morphColors?"#define USE_MORPHCOLORS":"",n.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+n.morphTextureStride:"",n.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+n.morphTargetsCount:"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.sizeAttenuation?"#define USE_SIZEATTENUATION":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",n.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Ul).join(`
`),x=[My(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b,n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",n.map?"#define USE_MAP":"",n.matcap?"#define USE_MATCAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+h:"",n.envMap?"#define "+g:"",n.envMap?"#define "+_:"",v?"#define CUBEUV_TEXEL_WIDTH "+v.texelWidth:"",v?"#define CUBEUV_TEXEL_HEIGHT "+v.texelHeight:"",v?"#define CUBEUV_MAX_MIP "+v.maxMip+".0":"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.packedNormalMap?"#define USE_PACKED_NORMALMAP":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoat?"#define USE_CLEARCOAT":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.dispersion?"#define USE_DISPERSION":"",n.iridescence?"#define USE_IRIDESCENCE":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaTest?"#define USE_ALPHATEST":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.sheen?"#define USE_SHEEN":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors||n.instancingColor?"#define USE_COLOR":"",n.vertexAlphas||n.batchingColor?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.gradientMap?"#define USE_GRADIENTMAP":"",n.flatShading?"#define FLAT_SHADED":"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.numLightProbeGrids>0?"#define USE_LIGHT_PROBES_GRID":"",n.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",n.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",n.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",n.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",n.toneMapping!==oa?"#define TONE_MAPPING":"",n.toneMapping!==oa?de.tonemapping_pars_fragment:"",n.toneMapping!==oa?n3("toneMapping",n.toneMapping):"",n.dithering?"#define DITHERING":"",n.opaque?"#define OPAQUE":"",de.colorspace_pars_fragment,t3("linearToOutputTexel",n.outputColorSpace),i3(),n.useDepthPacking?"#define DEPTH_PACKING "+n.depthPacking:"",`
`].filter(Ul).join(`
`)),u=bm(u),u=xy(u,n),u=yy(u,n),d=bm(d),d=xy(d,n),d=yy(d,n),u=Sy(u),d=Sy(d),n.isRawShaderMaterial!==!0&&(A=`#version 300 es
`,S=[y,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+S,x=["#define varying in",n.glslVersion===Px?"":"layout(location = 0) out highp vec4 pc_fragColor;",n.glslVersion===Px?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+x);const N=A+S+u,L=A+x+d,H=gy(o,o.VERTEX_SHADER,N),B=gy(o,o.FRAGMENT_SHADER,L);o.attachShader(R,H),o.attachShader(R,B),n.index0AttributeName!==void 0?o.bindAttribLocation(R,0,n.index0AttributeName):n.morphTargets===!0&&o.bindAttribLocation(R,0,"position"),o.linkProgram(R);function O(F){if(i.debug.checkShaderErrors){const j=o.getProgramInfoLog(R)||"",lt=o.getShaderInfoLog(H)||"",ct=o.getShaderInfoLog(B)||"",q=j.trim(),I=lt.trim(),G=ct.trim();let $=!0,dt=!0;if(o.getProgramParameter(R,o.LINK_STATUS)===!1)if($=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(o,R,H,B);else{const xt=vy(o,H,"vertex"),z=vy(o,B,"fragment");Te("THREE.WebGLProgram: Shader Error "+o.getError()+" - VALIDATE_STATUS "+o.getProgramParameter(R,o.VALIDATE_STATUS)+`

Material Name: `+F.name+`
Material Type: `+F.type+`

Program Info Log: `+q+`
`+xt+`
`+z)}else q!==""?ie("WebGLProgram: Program Info Log:",q):(I===""||G==="")&&(dt=!1);dt&&(F.diagnostics={runnable:$,programLog:q,vertexShader:{log:I,prefix:S},fragmentShader:{log:G,prefix:x}})}o.deleteShader(H),o.deleteShader(B),E=new ju(o,R),U=r3(o,R)}let E;this.getUniforms=function(){return E===void 0&&O(this),E};let U;this.getAttributes=function(){return U===void 0&&O(this),U};let V=n.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return V===!1&&(V=o.getProgramParameter(R,Z2)),V},this.destroy=function(){s.releaseStatesOfProgram(this),o.deleteProgram(R),this.program=void 0},this.type=n.shaderType,this.name=n.shaderName,this.id=Q2++,this.cacheKey=t,this.usedTimes=1,this.program=R,this.vertexShader=H,this.fragmentShader=B,this}let M3=0;class b3{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const n=t.vertexShader,s=t.fragmentShader,o=this._getShaderStage(n),c=this._getShaderStage(s),u=this._getShaderCacheForMaterial(t);return u.has(o)===!1&&(u.add(o),o.usedTimes++),u.has(c)===!1&&(u.add(c),c.usedTimes++),this}remove(t){const n=this.materialCache.get(t);for(const s of n)s.usedTimes--,s.usedTimes===0&&this.shaderCache.delete(s.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const n=this.materialCache;let s=n.get(t);return s===void 0&&(s=new Set,n.set(t,s)),s}_getShaderStage(t){const n=this.shaderCache;let s=n.get(t);return s===void 0&&(s=new E3(t),n.set(t,s)),s}}class E3{constructor(t){this.id=M3++,this.code=t,this.usedTimes=0}}function T3(i){return i===pr||i===$u||i===tf}function A3(i,t,n,s,o,c){const u=new mM,d=new b3,p=new Set,h=[],g=new Map,_=s.logarithmicDepthBuffer;let v=s.precision;const y={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distance",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function b(E){return p.add(E),E===0?"uv":`uv${E}`}function R(E,U,V,F,j,lt){const ct=F.fog,q=j.geometry,I=E.isMeshStandardMaterial||E.isMeshLambertMaterial||E.isMeshPhongMaterial?F.environment:null,G=E.isMeshStandardMaterial||E.isMeshLambertMaterial&&!E.envMap||E.isMeshPhongMaterial&&!E.envMap,$=t.get(E.envMap||I,G),dt=$&&$.mapping===_f?$.image.height:null,xt=y[E.type];E.precision!==null&&(v=s.getMaxPrecision(E.precision),v!==E.precision&&ie("WebGLProgram.getParameters:",E.precision,"not supported, using",v,"instead."));const z=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,Q=z!==void 0?z.length:0;let St=0;q.morphAttributes.position!==void 0&&(St=1),q.morphAttributes.normal!==void 0&&(St=2),q.morphAttributes.color!==void 0&&(St=3);let Rt,Nt,ot,Mt;if(xt){const ne=ia[xt];Rt=ne.vertexShader,Nt=ne.fragmentShader}else Rt=E.vertexShader,Nt=E.fragmentShader,d.update(E),ot=d.getVertexShaderID(E),Mt=d.getFragmentShaderID(E);const Tt=i.getRenderTarget(),Ht=i.state.buffers.depth.getReversed(),ee=j.isInstancedMesh===!0,$t=j.isBatchedMesh===!0,Xe=!!E.map,he=!!E.matcap,xe=!!$,Ue=!!E.aoMap,ue=!!E.lightMap,cn=!!E.bumpMap,Ze=!!E.normalMap,Dn=!!E.displacementMap,Y=!!E.emissiveMap,an=!!E.metalnessMap,pe=!!E.roughnessMap,Ve=E.anisotropy>0,Ct=E.clearcoat>0,$e=E.dispersion>0,P=E.iridescence>0,T=E.sheen>0,J=E.transmission>0,_t=Ve&&!!E.anisotropyMap,Et=Ct&&!!E.clearcoatMap,wt=Ct&&!!E.clearcoatNormalMap,Pt=Ct&&!!E.clearcoatRoughnessMap,ft=P&&!!E.iridescenceMap,ht=P&&!!E.iridescenceThicknessMap,Ot=T&&!!E.sheenColorMap,Ft=T&&!!E.sheenRoughnessMap,Lt=!!E.specularMap,Dt=!!E.specularColorMap,ae=!!E.specularIntensityMap,se=J&&!!E.transmissionMap,me=J&&!!E.thicknessMap,X=!!E.gradientMap,At=!!E.alphaMap,mt=E.alphaTest>0,zt=!!E.alphaHash,Ut=!!E.extensions;let bt=oa;E.toneMapped&&(Tt===null||Tt.isXRRenderTarget===!0)&&(bt=i.toneMapping);const Yt={shaderID:xt,shaderType:E.type,shaderName:E.name,vertexShader:Rt,fragmentShader:Nt,defines:E.defines,customVertexShaderID:ot,customFragmentShaderID:Mt,isRawShaderMaterial:E.isRawShaderMaterial===!0,glslVersion:E.glslVersion,precision:v,batching:$t,batchingColor:$t&&j._colorsTexture!==null,instancing:ee,instancingColor:ee&&j.instanceColor!==null,instancingMorph:ee&&j.morphTexture!==null,outputColorSpace:Tt===null?i.outputColorSpace:Tt.isXRRenderTarget===!0?Tt.texture.colorSpace:be.workingColorSpace,alphaToCoverage:!!E.alphaToCoverage,map:Xe,matcap:he,envMap:xe,envMapMode:xe&&$.mapping,envMapCubeUVHeight:dt,aoMap:Ue,lightMap:ue,bumpMap:cn,normalMap:Ze,displacementMap:Dn,emissiveMap:Y,normalMapObjectSpace:Ze&&E.normalMapType===dA,normalMapTangentSpace:Ze&&E.normalMapType===Nx,packedNormalMap:Ze&&E.normalMapType===Nx&&T3(E.normalMap.format),metalnessMap:an,roughnessMap:pe,anisotropy:Ve,anisotropyMap:_t,clearcoat:Ct,clearcoatMap:Et,clearcoatNormalMap:wt,clearcoatRoughnessMap:Pt,dispersion:$e,iridescence:P,iridescenceMap:ft,iridescenceThicknessMap:ht,sheen:T,sheenColorMap:Ot,sheenRoughnessMap:Ft,specularMap:Lt,specularColorMap:Dt,specularIntensityMap:ae,transmission:J,transmissionMap:se,thicknessMap:me,gradientMap:X,opaque:E.transparent===!1&&E.blending===go&&E.alphaToCoverage===!1,alphaMap:At,alphaTest:mt,alphaHash:zt,combine:E.combine,mapUv:Xe&&b(E.map.channel),aoMapUv:Ue&&b(E.aoMap.channel),lightMapUv:ue&&b(E.lightMap.channel),bumpMapUv:cn&&b(E.bumpMap.channel),normalMapUv:Ze&&b(E.normalMap.channel),displacementMapUv:Dn&&b(E.displacementMap.channel),emissiveMapUv:Y&&b(E.emissiveMap.channel),metalnessMapUv:an&&b(E.metalnessMap.channel),roughnessMapUv:pe&&b(E.roughnessMap.channel),anisotropyMapUv:_t&&b(E.anisotropyMap.channel),clearcoatMapUv:Et&&b(E.clearcoatMap.channel),clearcoatNormalMapUv:wt&&b(E.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Pt&&b(E.clearcoatRoughnessMap.channel),iridescenceMapUv:ft&&b(E.iridescenceMap.channel),iridescenceThicknessMapUv:ht&&b(E.iridescenceThicknessMap.channel),sheenColorMapUv:Ot&&b(E.sheenColorMap.channel),sheenRoughnessMapUv:Ft&&b(E.sheenRoughnessMap.channel),specularMapUv:Lt&&b(E.specularMap.channel),specularColorMapUv:Dt&&b(E.specularColorMap.channel),specularIntensityMapUv:ae&&b(E.specularIntensityMap.channel),transmissionMapUv:se&&b(E.transmissionMap.channel),thicknessMapUv:me&&b(E.thicknessMap.channel),alphaMapUv:At&&b(E.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(Ze||Ve),vertexNormals:!!q.attributes.normal,vertexColors:E.vertexColors,vertexAlphas:E.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:j.isPoints===!0&&!!q.attributes.uv&&(Xe||At),fog:!!ct,useFog:E.fog===!0,fogExp2:!!ct&&ct.isFogExp2,flatShading:E.wireframe===!1&&(E.flatShading===!0||q.attributes.normal===void 0&&Ze===!1&&(E.isMeshLambertMaterial||E.isMeshPhongMaterial||E.isMeshStandardMaterial||E.isMeshPhysicalMaterial)),sizeAttenuation:E.sizeAttenuation===!0,logarithmicDepthBuffer:_,reversedDepthBuffer:Ht,skinning:j.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:Q,morphTextureStride:St,numDirLights:U.directional.length,numPointLights:U.point.length,numSpotLights:U.spot.length,numSpotLightMaps:U.spotLightMap.length,numRectAreaLights:U.rectArea.length,numHemiLights:U.hemi.length,numDirLightShadows:U.directionalShadowMap.length,numPointLightShadows:U.pointShadowMap.length,numSpotLightShadows:U.spotShadowMap.length,numSpotLightShadowsWithMaps:U.numSpotLightShadowsWithMaps,numLightProbes:U.numLightProbes,numLightProbeGrids:lt.length,numClippingPlanes:c.numPlanes,numClipIntersection:c.numIntersection,dithering:E.dithering,shadowMapEnabled:i.shadowMap.enabled&&V.length>0,shadowMapType:i.shadowMap.type,toneMapping:bt,decodeVideoTexture:Xe&&E.map.isVideoTexture===!0&&be.getTransfer(E.map.colorSpace)===ze,decodeVideoTextureEmissive:Y&&E.emissiveMap.isVideoTexture===!0&&be.getTransfer(E.emissiveMap.colorSpace)===ze,premultipliedAlpha:E.premultipliedAlpha,doubleSided:E.side===Ia,flipSided:E.side===ii,useDepthPacking:E.depthPacking>=0,depthPacking:E.depthPacking||0,index0AttributeName:E.index0AttributeName,extensionClipCullDistance:Ut&&E.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Ut&&E.extensions.multiDraw===!0||$t)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:E.customProgramCacheKey()};return Yt.vertexUv1s=p.has(1),Yt.vertexUv2s=p.has(2),Yt.vertexUv3s=p.has(3),p.clear(),Yt}function S(E){const U=[];if(E.shaderID?U.push(E.shaderID):(U.push(E.customVertexShaderID),U.push(E.customFragmentShaderID)),E.defines!==void 0)for(const V in E.defines)U.push(V),U.push(E.defines[V]);return E.isRawShaderMaterial===!1&&(x(U,E),A(U,E),U.push(i.outputColorSpace)),U.push(E.customProgramCacheKey),U.join()}function x(E,U){E.push(U.precision),E.push(U.outputColorSpace),E.push(U.envMapMode),E.push(U.envMapCubeUVHeight),E.push(U.mapUv),E.push(U.alphaMapUv),E.push(U.lightMapUv),E.push(U.aoMapUv),E.push(U.bumpMapUv),E.push(U.normalMapUv),E.push(U.displacementMapUv),E.push(U.emissiveMapUv),E.push(U.metalnessMapUv),E.push(U.roughnessMapUv),E.push(U.anisotropyMapUv),E.push(U.clearcoatMapUv),E.push(U.clearcoatNormalMapUv),E.push(U.clearcoatRoughnessMapUv),E.push(U.iridescenceMapUv),E.push(U.iridescenceThicknessMapUv),E.push(U.sheenColorMapUv),E.push(U.sheenRoughnessMapUv),E.push(U.specularMapUv),E.push(U.specularColorMapUv),E.push(U.specularIntensityMapUv),E.push(U.transmissionMapUv),E.push(U.thicknessMapUv),E.push(U.combine),E.push(U.fogExp2),E.push(U.sizeAttenuation),E.push(U.morphTargetsCount),E.push(U.morphAttributeCount),E.push(U.numDirLights),E.push(U.numPointLights),E.push(U.numSpotLights),E.push(U.numSpotLightMaps),E.push(U.numHemiLights),E.push(U.numRectAreaLights),E.push(U.numDirLightShadows),E.push(U.numPointLightShadows),E.push(U.numSpotLightShadows),E.push(U.numSpotLightShadowsWithMaps),E.push(U.numLightProbes),E.push(U.shadowMapType),E.push(U.toneMapping),E.push(U.numClippingPlanes),E.push(U.numClipIntersection),E.push(U.depthPacking)}function A(E,U){u.disableAll(),U.instancing&&u.enable(0),U.instancingColor&&u.enable(1),U.instancingMorph&&u.enable(2),U.matcap&&u.enable(3),U.envMap&&u.enable(4),U.normalMapObjectSpace&&u.enable(5),U.normalMapTangentSpace&&u.enable(6),U.clearcoat&&u.enable(7),U.iridescence&&u.enable(8),U.alphaTest&&u.enable(9),U.vertexColors&&u.enable(10),U.vertexAlphas&&u.enable(11),U.vertexUv1s&&u.enable(12),U.vertexUv2s&&u.enable(13),U.vertexUv3s&&u.enable(14),U.vertexTangents&&u.enable(15),U.anisotropy&&u.enable(16),U.alphaHash&&u.enable(17),U.batching&&u.enable(18),U.dispersion&&u.enable(19),U.batchingColor&&u.enable(20),U.gradientMap&&u.enable(21),U.packedNormalMap&&u.enable(22),U.vertexNormals&&u.enable(23),E.push(u.mask),u.disableAll(),U.fog&&u.enable(0),U.useFog&&u.enable(1),U.flatShading&&u.enable(2),U.logarithmicDepthBuffer&&u.enable(3),U.reversedDepthBuffer&&u.enable(4),U.skinning&&u.enable(5),U.morphTargets&&u.enable(6),U.morphNormals&&u.enable(7),U.morphColors&&u.enable(8),U.premultipliedAlpha&&u.enable(9),U.shadowMapEnabled&&u.enable(10),U.doubleSided&&u.enable(11),U.flipSided&&u.enable(12),U.useDepthPacking&&u.enable(13),U.dithering&&u.enable(14),U.transmission&&u.enable(15),U.sheen&&u.enable(16),U.opaque&&u.enable(17),U.pointsUvs&&u.enable(18),U.decodeVideoTexture&&u.enable(19),U.decodeVideoTextureEmissive&&u.enable(20),U.alphaToCoverage&&u.enable(21),U.numLightProbeGrids>0&&u.enable(22),E.push(u.mask)}function N(E){const U=y[E.type];let V;if(U){const F=ia[U];V=ZA.clone(F.uniforms)}else V=E.uniforms;return V}function L(E,U){let V=g.get(U);return V!==void 0?++V.usedTimes:(V=new S3(i,U,E,o),h.push(V),g.set(U,V)),V}function H(E){if(--E.usedTimes===0){const U=h.indexOf(E);h[U]=h[h.length-1],h.pop(),g.delete(E.cacheKey),E.destroy()}}function B(E){d.remove(E)}function O(){d.dispose()}return{getParameters:R,getProgramCacheKey:S,getUniforms:N,acquireProgram:L,releaseProgram:H,releaseShaderCache:B,programs:h,dispose:O}}function R3(){let i=new WeakMap;function t(u){return i.has(u)}function n(u){let d=i.get(u);return d===void 0&&(d={},i.set(u,d)),d}function s(u){i.delete(u)}function o(u,d,p){i.get(u)[d]=p}function c(){i=new WeakMap}return{has:t,get:n,remove:s,update:o,dispose:c}}function C3(i,t){return i.groupOrder!==t.groupOrder?i.groupOrder-t.groupOrder:i.renderOrder!==t.renderOrder?i.renderOrder-t.renderOrder:i.material.id!==t.material.id?i.material.id-t.material.id:i.materialVariant!==t.materialVariant?i.materialVariant-t.materialVariant:i.z!==t.z?i.z-t.z:i.id-t.id}function by(i,t){return i.groupOrder!==t.groupOrder?i.groupOrder-t.groupOrder:i.renderOrder!==t.renderOrder?i.renderOrder-t.renderOrder:i.z!==t.z?t.z-i.z:i.id-t.id}function Ey(){const i=[];let t=0;const n=[],s=[],o=[];function c(){t=0,n.length=0,s.length=0,o.length=0}function u(v){let y=0;return v.isInstancedMesh&&(y+=2),v.isSkinnedMesh&&(y+=1),y}function d(v,y,b,R,S,x){let A=i[t];return A===void 0?(A={id:v.id,object:v,geometry:y,material:b,materialVariant:u(v),groupOrder:R,renderOrder:v.renderOrder,z:S,group:x},i[t]=A):(A.id=v.id,A.object=v,A.geometry=y,A.material=b,A.materialVariant=u(v),A.groupOrder=R,A.renderOrder=v.renderOrder,A.z=S,A.group=x),t++,A}function p(v,y,b,R,S,x){const A=d(v,y,b,R,S,x);b.transmission>0?s.push(A):b.transparent===!0?o.push(A):n.push(A)}function h(v,y,b,R,S,x){const A=d(v,y,b,R,S,x);b.transmission>0?s.unshift(A):b.transparent===!0?o.unshift(A):n.unshift(A)}function g(v,y){n.length>1&&n.sort(v||C3),s.length>1&&s.sort(y||by),o.length>1&&o.sort(y||by)}function _(){for(let v=t,y=i.length;v<y;v++){const b=i[v];if(b.id===null)break;b.id=null,b.object=null,b.geometry=null,b.material=null,b.group=null}}return{opaque:n,transmissive:s,transparent:o,init:c,push:p,unshift:h,finish:_,sort:g}}function w3(){let i=new WeakMap;function t(s,o){const c=i.get(s);let u;return c===void 0?(u=new Ey,i.set(s,[u])):o>=c.length?(u=new Ey,c.push(u)):u=c[o],u}function n(){i=new WeakMap}return{get:t,dispose:n}}function D3(){const i={};return{get:function(t){if(i[t.id]!==void 0)return i[t.id];let n;switch(t.type){case"DirectionalLight":n={direction:new rt,color:new Le};break;case"SpotLight":n={position:new rt,direction:new rt,color:new Le,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":n={position:new rt,color:new Le,distance:0,decay:0};break;case"HemisphereLight":n={direction:new rt,skyColor:new Le,groundColor:new Le};break;case"RectAreaLight":n={color:new Le,position:new rt,halfWidth:new rt,halfHeight:new rt};break}return i[t.id]=n,n}}}function N3(){const i={};return{get:function(t){if(i[t.id]!==void 0)return i[t.id];let n;switch(t.type){case"DirectionalLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new je};break;case"SpotLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new je};break;case"PointLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new je,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[t.id]=n,n}}}let L3=0;function U3(i,t){return(t.castShadow?2:0)-(i.castShadow?2:0)+(t.map?1:0)-(i.map?1:0)}function P3(i){const t=new D3,n=N3(),s={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)s.probe.push(new rt);const o=new rt,c=new Sn,u=new Sn;function d(h){let g=0,_=0,v=0;for(let U=0;U<9;U++)s.probe[U].set(0,0,0);let y=0,b=0,R=0,S=0,x=0,A=0,N=0,L=0,H=0,B=0,O=0;h.sort(U3);for(let U=0,V=h.length;U<V;U++){const F=h[U],j=F.color,lt=F.intensity,ct=F.distance;let q=null;if(F.shadow&&F.shadow.map&&(F.shadow.map.texture.format===pr?q=F.shadow.map.texture:q=F.shadow.map.depthTexture||F.shadow.map.texture),F.isAmbientLight)g+=j.r*lt,_+=j.g*lt,v+=j.b*lt;else if(F.isLightProbe){for(let I=0;I<9;I++)s.probe[I].addScaledVector(F.sh.coefficients[I],lt);O++}else if(F.isDirectionalLight){const I=t.get(F);if(I.color.copy(F.color).multiplyScalar(F.intensity),F.castShadow){const G=F.shadow,$=n.get(F);$.shadowIntensity=G.intensity,$.shadowBias=G.bias,$.shadowNormalBias=G.normalBias,$.shadowRadius=G.radius,$.shadowMapSize=G.mapSize,s.directionalShadow[y]=$,s.directionalShadowMap[y]=q,s.directionalShadowMatrix[y]=F.shadow.matrix,A++}s.directional[y]=I,y++}else if(F.isSpotLight){const I=t.get(F);I.position.setFromMatrixPosition(F.matrixWorld),I.color.copy(j).multiplyScalar(lt),I.distance=ct,I.coneCos=Math.cos(F.angle),I.penumbraCos=Math.cos(F.angle*(1-F.penumbra)),I.decay=F.decay,s.spot[R]=I;const G=F.shadow;if(F.map&&(s.spotLightMap[H]=F.map,H++,G.updateMatrices(F),F.castShadow&&B++),s.spotLightMatrix[R]=G.matrix,F.castShadow){const $=n.get(F);$.shadowIntensity=G.intensity,$.shadowBias=G.bias,$.shadowNormalBias=G.normalBias,$.shadowRadius=G.radius,$.shadowMapSize=G.mapSize,s.spotShadow[R]=$,s.spotShadowMap[R]=q,L++}R++}else if(F.isRectAreaLight){const I=t.get(F);I.color.copy(j).multiplyScalar(lt),I.halfWidth.set(F.width*.5,0,0),I.halfHeight.set(0,F.height*.5,0),s.rectArea[S]=I,S++}else if(F.isPointLight){const I=t.get(F);if(I.color.copy(F.color).multiplyScalar(F.intensity),I.distance=F.distance,I.decay=F.decay,F.castShadow){const G=F.shadow,$=n.get(F);$.shadowIntensity=G.intensity,$.shadowBias=G.bias,$.shadowNormalBias=G.normalBias,$.shadowRadius=G.radius,$.shadowMapSize=G.mapSize,$.shadowCameraNear=G.camera.near,$.shadowCameraFar=G.camera.far,s.pointShadow[b]=$,s.pointShadowMap[b]=q,s.pointShadowMatrix[b]=F.shadow.matrix,N++}s.point[b]=I,b++}else if(F.isHemisphereLight){const I=t.get(F);I.skyColor.copy(F.color).multiplyScalar(lt),I.groundColor.copy(F.groundColor).multiplyScalar(lt),s.hemi[x]=I,x++}}S>0&&(i.has("OES_texture_float_linear")===!0?(s.rectAreaLTC1=Vt.LTC_FLOAT_1,s.rectAreaLTC2=Vt.LTC_FLOAT_2):(s.rectAreaLTC1=Vt.LTC_HALF_1,s.rectAreaLTC2=Vt.LTC_HALF_2)),s.ambient[0]=g,s.ambient[1]=_,s.ambient[2]=v;const E=s.hash;(E.directionalLength!==y||E.pointLength!==b||E.spotLength!==R||E.rectAreaLength!==S||E.hemiLength!==x||E.numDirectionalShadows!==A||E.numPointShadows!==N||E.numSpotShadows!==L||E.numSpotMaps!==H||E.numLightProbes!==O)&&(s.directional.length=y,s.spot.length=R,s.rectArea.length=S,s.point.length=b,s.hemi.length=x,s.directionalShadow.length=A,s.directionalShadowMap.length=A,s.pointShadow.length=N,s.pointShadowMap.length=N,s.spotShadow.length=L,s.spotShadowMap.length=L,s.directionalShadowMatrix.length=A,s.pointShadowMatrix.length=N,s.spotLightMatrix.length=L+H-B,s.spotLightMap.length=H,s.numSpotLightShadowsWithMaps=B,s.numLightProbes=O,E.directionalLength=y,E.pointLength=b,E.spotLength=R,E.rectAreaLength=S,E.hemiLength=x,E.numDirectionalShadows=A,E.numPointShadows=N,E.numSpotShadows=L,E.numSpotMaps=H,E.numLightProbes=O,s.version=L3++)}function p(h,g){let _=0,v=0,y=0,b=0,R=0;const S=g.matrixWorldInverse;for(let x=0,A=h.length;x<A;x++){const N=h[x];if(N.isDirectionalLight){const L=s.directional[_];L.direction.setFromMatrixPosition(N.matrixWorld),o.setFromMatrixPosition(N.target.matrixWorld),L.direction.sub(o),L.direction.transformDirection(S),_++}else if(N.isSpotLight){const L=s.spot[y];L.position.setFromMatrixPosition(N.matrixWorld),L.position.applyMatrix4(S),L.direction.setFromMatrixPosition(N.matrixWorld),o.setFromMatrixPosition(N.target.matrixWorld),L.direction.sub(o),L.direction.transformDirection(S),y++}else if(N.isRectAreaLight){const L=s.rectArea[b];L.position.setFromMatrixPosition(N.matrixWorld),L.position.applyMatrix4(S),u.identity(),c.copy(N.matrixWorld),c.premultiply(S),u.extractRotation(c),L.halfWidth.set(N.width*.5,0,0),L.halfHeight.set(0,N.height*.5,0),L.halfWidth.applyMatrix4(u),L.halfHeight.applyMatrix4(u),b++}else if(N.isPointLight){const L=s.point[v];L.position.setFromMatrixPosition(N.matrixWorld),L.position.applyMatrix4(S),v++}else if(N.isHemisphereLight){const L=s.hemi[R];L.direction.setFromMatrixPosition(N.matrixWorld),L.direction.transformDirection(S),R++}}}return{setup:d,setupView:p,state:s}}function Ty(i){const t=new P3(i),n=[],s=[],o=[];function c(v){_.camera=v,n.length=0,s.length=0,o.length=0}function u(v){n.push(v)}function d(v){s.push(v)}function p(v){o.push(v)}function h(){t.setup(n)}function g(v){t.setupView(n,v)}const _={lightsArray:n,shadowsArray:s,lightProbeGridArray:o,camera:null,lights:t,transmissionRenderTarget:{},textureUnits:0};return{init:c,state:_,setupLights:h,setupLightsView:g,pushLight:u,pushShadow:d,pushLightProbeGrid:p}}function O3(i){let t=new WeakMap;function n(o,c=0){const u=t.get(o);let d;return u===void 0?(d=new Ty(i),t.set(o,[d])):c>=u.length?(d=new Ty(i),u.push(d)):d=u[c],d}function s(){t=new WeakMap}return{get:n,dispose:s}}const F3=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,B3=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,I3=[new rt(1,0,0),new rt(-1,0,0),new rt(0,1,0),new rt(0,-1,0),new rt(0,0,1),new rt(0,0,-1)],z3=[new rt(0,-1,0),new rt(0,-1,0),new rt(0,0,1),new rt(0,0,-1),new rt(0,-1,0),new rt(0,-1,0)],Ay=new Sn,Dl=new rt,pp=new rt;function V3(i,t,n){let s=new SM;const o=new je,c=new je,u=new hn,d=new tR,p=new eR,h={},g=n.maxTextureSize,_={[ws]:ii,[ii]:ws,[Ia]:Ia},v=new da({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new je},radius:{value:4}},vertexShader:F3,fragmentShader:B3}),y=v.clone();y.defines.HORIZONTAL_PASS=1;const b=new Yi;b.setAttribute("position",new ca(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const R=new ja(b,v),S=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=zu;let x=this.type;this.render=function(B,O,E){if(S.enabled===!1||S.autoUpdate===!1&&S.needsUpdate===!1||B.length===0)return;this.type===k1&&(ie("WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead."),this.type=zu);const U=i.getRenderTarget(),V=i.getActiveCubeFace(),F=i.getActiveMipmapLevel(),j=i.state;j.setBlending(Va),j.buffers.depth.getReversed()===!0?j.buffers.color.setClear(0,0,0,0):j.buffers.color.setClear(1,1,1,1),j.buffers.depth.setTest(!0),j.setScissorTest(!1);const lt=x!==this.type;lt&&O.traverse(function(ct){ct.material&&(Array.isArray(ct.material)?ct.material.forEach(q=>q.needsUpdate=!0):ct.material.needsUpdate=!0)});for(let ct=0,q=B.length;ct<q;ct++){const I=B[ct],G=I.shadow;if(G===void 0){ie("WebGLShadowMap:",I,"has no shadow.");continue}if(G.autoUpdate===!1&&G.needsUpdate===!1)continue;o.copy(G.mapSize);const $=G.getFrameExtents();o.multiply($),c.copy(G.mapSize),(o.x>g||o.y>g)&&(o.x>g&&(c.x=Math.floor(g/$.x),o.x=c.x*$.x,G.mapSize.x=c.x),o.y>g&&(c.y=Math.floor(g/$.y),o.y=c.y*$.y,G.mapSize.y=c.y));const dt=i.state.buffers.depth.getReversed();if(G.camera._reversedDepth=dt,G.map===null||lt===!0){if(G.map!==null&&(G.map.depthTexture!==null&&(G.map.depthTexture.dispose(),G.map.depthTexture=null),G.map.dispose()),this.type===Ll){if(I.isPointLight){ie("WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.");continue}G.map=new la(o.x,o.y,{format:pr,type:Ga,minFilter:jn,magFilter:jn,generateMipmaps:!1}),G.map.texture.name=I.name+".shadowMap",G.map.depthTexture=new So(o.x,o.y,sa),G.map.depthTexture.name=I.name+".shadowMapDepth",G.map.depthTexture.format=ka,G.map.depthTexture.compareFunction=null,G.map.depthTexture.minFilter=Bn,G.map.depthTexture.magFilter=Bn}else I.isPointLight?(G.map=new DM(o.x),G.map.depthTexture=new YA(o.x,fa)):(G.map=new la(o.x,o.y),G.map.depthTexture=new So(o.x,o.y,fa)),G.map.depthTexture.name=I.name+".shadowMap",G.map.depthTexture.format=ka,this.type===zu?(G.map.depthTexture.compareFunction=dt?ag:ig,G.map.depthTexture.minFilter=jn,G.map.depthTexture.magFilter=jn):(G.map.depthTexture.compareFunction=null,G.map.depthTexture.minFilter=Bn,G.map.depthTexture.magFilter=Bn);G.camera.updateProjectionMatrix()}const xt=G.map.isWebGLCubeRenderTarget?6:1;for(let z=0;z<xt;z++){if(G.map.isWebGLCubeRenderTarget)i.setRenderTarget(G.map,z),i.clear();else{z===0&&(i.setRenderTarget(G.map),i.clear());const Q=G.getViewport(z);u.set(c.x*Q.x,c.y*Q.y,c.x*Q.z,c.y*Q.w),j.viewport(u)}if(I.isPointLight){const Q=G.camera,St=G.matrix,Rt=I.distance||Q.far;Rt!==Q.far&&(Q.far=Rt,Q.updateProjectionMatrix()),Dl.setFromMatrixPosition(I.matrixWorld),Q.position.copy(Dl),pp.copy(Q.position),pp.add(I3[z]),Q.up.copy(z3[z]),Q.lookAt(pp),Q.updateMatrixWorld(),St.makeTranslation(-Dl.x,-Dl.y,-Dl.z),Ay.multiplyMatrices(Q.projectionMatrix,Q.matrixWorldInverse),G._frustum.setFromProjectionMatrix(Ay,Q.coordinateSystem,Q.reversedDepth)}else G.updateMatrices(I);s=G.getFrustum(),L(O,E,G.camera,I,this.type)}G.isPointLightShadow!==!0&&this.type===Ll&&A(G,E),G.needsUpdate=!1}x=this.type,S.needsUpdate=!1,i.setRenderTarget(U,V,F)};function A(B,O){const E=t.update(R);v.defines.VSM_SAMPLES!==B.blurSamples&&(v.defines.VSM_SAMPLES=B.blurSamples,y.defines.VSM_SAMPLES=B.blurSamples,v.needsUpdate=!0,y.needsUpdate=!0),B.mapPass===null&&(B.mapPass=new la(o.x,o.y,{format:pr,type:Ga})),v.uniforms.shadow_pass.value=B.map.depthTexture,v.uniforms.resolution.value=B.mapSize,v.uniforms.radius.value=B.radius,i.setRenderTarget(B.mapPass),i.clear(),i.renderBufferDirect(O,null,E,v,R,null),y.uniforms.shadow_pass.value=B.mapPass.texture,y.uniforms.resolution.value=B.mapSize,y.uniforms.radius.value=B.radius,i.setRenderTarget(B.map),i.clear(),i.renderBufferDirect(O,null,E,y,R,null)}function N(B,O,E,U){let V=null;const F=E.isPointLight===!0?B.customDistanceMaterial:B.customDepthMaterial;if(F!==void 0)V=F;else if(V=E.isPointLight===!0?p:d,i.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0||O.alphaToCoverage===!0){const j=V.uuid,lt=O.uuid;let ct=h[j];ct===void 0&&(ct={},h[j]=ct);let q=ct[lt];q===void 0&&(q=V.clone(),ct[lt]=q,O.addEventListener("dispose",H)),V=q}if(V.visible=O.visible,V.wireframe=O.wireframe,U===Ll?V.side=O.shadowSide!==null?O.shadowSide:O.side:V.side=O.shadowSide!==null?O.shadowSide:_[O.side],V.alphaMap=O.alphaMap,V.alphaTest=O.alphaToCoverage===!0?.5:O.alphaTest,V.map=O.map,V.clipShadows=O.clipShadows,V.clippingPlanes=O.clippingPlanes,V.clipIntersection=O.clipIntersection,V.displacementMap=O.displacementMap,V.displacementScale=O.displacementScale,V.displacementBias=O.displacementBias,V.wireframeLinewidth=O.wireframeLinewidth,V.linewidth=O.linewidth,E.isPointLight===!0&&V.isMeshDistanceMaterial===!0){const j=i.properties.get(V);j.light=E}return V}function L(B,O,E,U,V){if(B.visible===!1)return;if(B.layers.test(O.layers)&&(B.isMesh||B.isLine||B.isPoints)&&(B.castShadow||B.receiveShadow&&V===Ll)&&(!B.frustumCulled||s.intersectsObject(B))){B.modelViewMatrix.multiplyMatrices(E.matrixWorldInverse,B.matrixWorld);const lt=t.update(B),ct=B.material;if(Array.isArray(ct)){const q=lt.groups;for(let I=0,G=q.length;I<G;I++){const $=q[I],dt=ct[$.materialIndex];if(dt&&dt.visible){const xt=N(B,dt,U,V);B.onBeforeShadow(i,B,O,E,lt,xt,$),i.renderBufferDirect(E,null,lt,xt,B,$),B.onAfterShadow(i,B,O,E,lt,xt,$)}}}else if(ct.visible){const q=N(B,ct,U,V);B.onBeforeShadow(i,B,O,E,lt,q,null),i.renderBufferDirect(E,null,lt,q,B,null),B.onAfterShadow(i,B,O,E,lt,q,null)}}const j=B.children;for(let lt=0,ct=j.length;lt<ct;lt++)L(j[lt],O,E,U,V)}function H(B){B.target.removeEventListener("dispose",H);for(const E in h){const U=h[E],V=B.target.uuid;V in U&&(U[V].dispose(),delete U[V])}}}function H3(i,t){function n(){let X=!1;const At=new hn;let mt=null;const zt=new hn(0,0,0,0);return{setMask:function(Ut){mt!==Ut&&!X&&(i.colorMask(Ut,Ut,Ut,Ut),mt=Ut)},setLocked:function(Ut){X=Ut},setClear:function(Ut,bt,Yt,ne,sn){sn===!0&&(Ut*=ne,bt*=ne,Yt*=ne),At.set(Ut,bt,Yt,ne),zt.equals(At)===!1&&(i.clearColor(Ut,bt,Yt,ne),zt.copy(At))},reset:function(){X=!1,mt=null,zt.set(-1,0,0,0)}}}function s(){let X=!1,At=!1,mt=null,zt=null,Ut=null;return{setReversed:function(bt){if(At!==bt){const Yt=t.get("EXT_clip_control");bt?Yt.clipControlEXT(Yt.LOWER_LEFT_EXT,Yt.ZERO_TO_ONE_EXT):Yt.clipControlEXT(Yt.LOWER_LEFT_EXT,Yt.NEGATIVE_ONE_TO_ONE_EXT),At=bt;const ne=Ut;Ut=null,this.setClear(ne)}},getReversed:function(){return At},setTest:function(bt){bt?Tt(i.DEPTH_TEST):Ht(i.DEPTH_TEST)},setMask:function(bt){mt!==bt&&!X&&(i.depthMask(bt),mt=bt)},setFunc:function(bt){if(At&&(bt=MA[bt]),zt!==bt){switch(bt){case Pp:i.depthFunc(i.NEVER);break;case Op:i.depthFunc(i.ALWAYS);break;case Fp:i.depthFunc(i.LESS);break;case xo:i.depthFunc(i.LEQUAL);break;case Bp:i.depthFunc(i.EQUAL);break;case Ip:i.depthFunc(i.GEQUAL);break;case zp:i.depthFunc(i.GREATER);break;case Vp:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}zt=bt}},setLocked:function(bt){X=bt},setClear:function(bt){Ut!==bt&&(Ut=bt,At&&(bt=1-bt),i.clearDepth(bt))},reset:function(){X=!1,mt=null,zt=null,Ut=null,At=!1}}}function o(){let X=!1,At=null,mt=null,zt=null,Ut=null,bt=null,Yt=null,ne=null,sn=null;return{setTest:function(we){X||(we?Tt(i.STENCIL_TEST):Ht(i.STENCIL_TEST))},setMask:function(we){At!==we&&!X&&(i.stencilMask(we),At=we)},setFunc:function(we,xi,si){(mt!==we||zt!==xi||Ut!==si)&&(i.stencilFunc(we,xi,si),mt=we,zt=xi,Ut=si)},setOp:function(we,xi,si){(bt!==we||Yt!==xi||ne!==si)&&(i.stencilOp(we,xi,si),bt=we,Yt=xi,ne=si)},setLocked:function(we){X=we},setClear:function(we){sn!==we&&(i.clearStencil(we),sn=we)},reset:function(){X=!1,At=null,mt=null,zt=null,Ut=null,bt=null,Yt=null,ne=null,sn=null}}}const c=new n,u=new s,d=new o,p=new WeakMap,h=new WeakMap;let g={},_={},v={},y=new WeakMap,b=[],R=null,S=!1,x=null,A=null,N=null,L=null,H=null,B=null,O=null,E=new Le(0,0,0),U=0,V=!1,F=null,j=null,lt=null,ct=null,q=null;const I=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let G=!1,$=0;const dt=i.getParameter(i.VERSION);dt.indexOf("WebGL")!==-1?($=parseFloat(/^WebGL (\d)/.exec(dt)[1]),G=$>=1):dt.indexOf("OpenGL ES")!==-1&&($=parseFloat(/^OpenGL ES (\d)/.exec(dt)[1]),G=$>=2);let xt=null,z={};const Q=i.getParameter(i.SCISSOR_BOX),St=i.getParameter(i.VIEWPORT),Rt=new hn().fromArray(Q),Nt=new hn().fromArray(St);function ot(X,At,mt,zt){const Ut=new Uint8Array(4),bt=i.createTexture();i.bindTexture(X,bt),i.texParameteri(X,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(X,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let Yt=0;Yt<mt;Yt++)X===i.TEXTURE_3D||X===i.TEXTURE_2D_ARRAY?i.texImage3D(At,0,i.RGBA,1,1,zt,0,i.RGBA,i.UNSIGNED_BYTE,Ut):i.texImage2D(At+Yt,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,Ut);return bt}const Mt={};Mt[i.TEXTURE_2D]=ot(i.TEXTURE_2D,i.TEXTURE_2D,1),Mt[i.TEXTURE_CUBE_MAP]=ot(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),Mt[i.TEXTURE_2D_ARRAY]=ot(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),Mt[i.TEXTURE_3D]=ot(i.TEXTURE_3D,i.TEXTURE_3D,1,1),c.setClear(0,0,0,1),u.setClear(1),d.setClear(0),Tt(i.DEPTH_TEST),u.setFunc(xo),cn(!1),Ze(Rx),Tt(i.CULL_FACE),Ue(Va);function Tt(X){g[X]!==!0&&(i.enable(X),g[X]=!0)}function Ht(X){g[X]!==!1&&(i.disable(X),g[X]=!1)}function ee(X,At){return v[X]!==At?(i.bindFramebuffer(X,At),v[X]=At,X===i.DRAW_FRAMEBUFFER&&(v[i.FRAMEBUFFER]=At),X===i.FRAMEBUFFER&&(v[i.DRAW_FRAMEBUFFER]=At),!0):!1}function $t(X,At){let mt=b,zt=!1;if(X){mt=y.get(At),mt===void 0&&(mt=[],y.set(At,mt));const Ut=X.textures;if(mt.length!==Ut.length||mt[0]!==i.COLOR_ATTACHMENT0){for(let bt=0,Yt=Ut.length;bt<Yt;bt++)mt[bt]=i.COLOR_ATTACHMENT0+bt;mt.length=Ut.length,zt=!0}}else mt[0]!==i.BACK&&(mt[0]=i.BACK,zt=!0);zt&&i.drawBuffers(mt)}function Xe(X){return R!==X?(i.useProgram(X),R=X,!0):!1}const he={[sr]:i.FUNC_ADD,[X1]:i.FUNC_SUBTRACT,[W1]:i.FUNC_REVERSE_SUBTRACT};he[q1]=i.MIN,he[Y1]=i.MAX;const xe={[K1]:i.ZERO,[Z1]:i.ONE,[Q1]:i.SRC_COLOR,[Lp]:i.SRC_ALPHA,[iA]:i.SRC_ALPHA_SATURATE,[eA]:i.DST_COLOR,[$1]:i.DST_ALPHA,[J1]:i.ONE_MINUS_SRC_COLOR,[Up]:i.ONE_MINUS_SRC_ALPHA,[nA]:i.ONE_MINUS_DST_COLOR,[tA]:i.ONE_MINUS_DST_ALPHA,[aA]:i.CONSTANT_COLOR,[sA]:i.ONE_MINUS_CONSTANT_COLOR,[rA]:i.CONSTANT_ALPHA,[oA]:i.ONE_MINUS_CONSTANT_ALPHA};function Ue(X,At,mt,zt,Ut,bt,Yt,ne,sn,we){if(X===Va){S===!0&&(Ht(i.BLEND),S=!1);return}if(S===!1&&(Tt(i.BLEND),S=!0),X!==j1){if(X!==x||we!==V){if((A!==sr||H!==sr)&&(i.blendEquation(i.FUNC_ADD),A=sr,H=sr),we)switch(X){case go:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Cx:i.blendFunc(i.ONE,i.ONE);break;case wx:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Dx:i.blendFuncSeparate(i.DST_COLOR,i.ONE_MINUS_SRC_ALPHA,i.ZERO,i.ONE);break;default:Te("WebGLState: Invalid blending: ",X);break}else switch(X){case go:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Cx:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE,i.ONE,i.ONE);break;case wx:Te("WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case Dx:Te("WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:Te("WebGLState: Invalid blending: ",X);break}N=null,L=null,B=null,O=null,E.set(0,0,0),U=0,x=X,V=we}return}Ut=Ut||At,bt=bt||mt,Yt=Yt||zt,(At!==A||Ut!==H)&&(i.blendEquationSeparate(he[At],he[Ut]),A=At,H=Ut),(mt!==N||zt!==L||bt!==B||Yt!==O)&&(i.blendFuncSeparate(xe[mt],xe[zt],xe[bt],xe[Yt]),N=mt,L=zt,B=bt,O=Yt),(ne.equals(E)===!1||sn!==U)&&(i.blendColor(ne.r,ne.g,ne.b,sn),E.copy(ne),U=sn),x=X,V=!1}function ue(X,At){X.side===Ia?Ht(i.CULL_FACE):Tt(i.CULL_FACE);let mt=X.side===ii;At&&(mt=!mt),cn(mt),X.blending===go&&X.transparent===!1?Ue(Va):Ue(X.blending,X.blendEquation,X.blendSrc,X.blendDst,X.blendEquationAlpha,X.blendSrcAlpha,X.blendDstAlpha,X.blendColor,X.blendAlpha,X.premultipliedAlpha),u.setFunc(X.depthFunc),u.setTest(X.depthTest),u.setMask(X.depthWrite),c.setMask(X.colorWrite);const zt=X.stencilWrite;d.setTest(zt),zt&&(d.setMask(X.stencilWriteMask),d.setFunc(X.stencilFunc,X.stencilRef,X.stencilFuncMask),d.setOp(X.stencilFail,X.stencilZFail,X.stencilZPass)),Y(X.polygonOffset,X.polygonOffsetFactor,X.polygonOffsetUnits),X.alphaToCoverage===!0?Tt(i.SAMPLE_ALPHA_TO_COVERAGE):Ht(i.SAMPLE_ALPHA_TO_COVERAGE)}function cn(X){F!==X&&(X?i.frontFace(i.CW):i.frontFace(i.CCW),F=X)}function Ze(X){X!==H1?(Tt(i.CULL_FACE),X!==j&&(X===Rx?i.cullFace(i.BACK):X===G1?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):Ht(i.CULL_FACE),j=X}function Dn(X){X!==lt&&(G&&i.lineWidth(X),lt=X)}function Y(X,At,mt){X?(Tt(i.POLYGON_OFFSET_FILL),(ct!==At||q!==mt)&&(ct=At,q=mt,u.getReversed()&&(At=-At),i.polygonOffset(At,mt))):Ht(i.POLYGON_OFFSET_FILL)}function an(X){X?Tt(i.SCISSOR_TEST):Ht(i.SCISSOR_TEST)}function pe(X){X===void 0&&(X=i.TEXTURE0+I-1),xt!==X&&(i.activeTexture(X),xt=X)}function Ve(X,At,mt){mt===void 0&&(xt===null?mt=i.TEXTURE0+I-1:mt=xt);let zt=z[mt];zt===void 0&&(zt={type:void 0,texture:void 0},z[mt]=zt),(zt.type!==X||zt.texture!==At)&&(xt!==mt&&(i.activeTexture(mt),xt=mt),i.bindTexture(X,At||Mt[X]),zt.type=X,zt.texture=At)}function Ct(){const X=z[xt];X!==void 0&&X.type!==void 0&&(i.bindTexture(X.type,null),X.type=void 0,X.texture=void 0)}function $e(){try{i.compressedTexImage2D(...arguments)}catch(X){Te("WebGLState:",X)}}function P(){try{i.compressedTexImage3D(...arguments)}catch(X){Te("WebGLState:",X)}}function T(){try{i.texSubImage2D(...arguments)}catch(X){Te("WebGLState:",X)}}function J(){try{i.texSubImage3D(...arguments)}catch(X){Te("WebGLState:",X)}}function _t(){try{i.compressedTexSubImage2D(...arguments)}catch(X){Te("WebGLState:",X)}}function Et(){try{i.compressedTexSubImage3D(...arguments)}catch(X){Te("WebGLState:",X)}}function wt(){try{i.texStorage2D(...arguments)}catch(X){Te("WebGLState:",X)}}function Pt(){try{i.texStorage3D(...arguments)}catch(X){Te("WebGLState:",X)}}function ft(){try{i.texImage2D(...arguments)}catch(X){Te("WebGLState:",X)}}function ht(){try{i.texImage3D(...arguments)}catch(X){Te("WebGLState:",X)}}function Ot(X){return _[X]!==void 0?_[X]:i.getParameter(X)}function Ft(X,At){_[X]!==At&&(i.pixelStorei(X,At),_[X]=At)}function Lt(X){Rt.equals(X)===!1&&(i.scissor(X.x,X.y,X.z,X.w),Rt.copy(X))}function Dt(X){Nt.equals(X)===!1&&(i.viewport(X.x,X.y,X.z,X.w),Nt.copy(X))}function ae(X,At){let mt=h.get(At);mt===void 0&&(mt=new WeakMap,h.set(At,mt));let zt=mt.get(X);zt===void 0&&(zt=i.getUniformBlockIndex(At,X.name),mt.set(X,zt))}function se(X,At){const zt=h.get(At).get(X);p.get(At)!==zt&&(i.uniformBlockBinding(At,zt,X.__bindingPointIndex),p.set(At,zt))}function me(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),u.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),i.pixelStorei(i.PACK_ALIGNMENT,4),i.pixelStorei(i.UNPACK_ALIGNMENT,4),i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,!1),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,!1),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,i.BROWSER_DEFAULT_WEBGL),i.pixelStorei(i.PACK_ROW_LENGTH,0),i.pixelStorei(i.PACK_SKIP_PIXELS,0),i.pixelStorei(i.PACK_SKIP_ROWS,0),i.pixelStorei(i.UNPACK_ROW_LENGTH,0),i.pixelStorei(i.UNPACK_IMAGE_HEIGHT,0),i.pixelStorei(i.UNPACK_SKIP_PIXELS,0),i.pixelStorei(i.UNPACK_SKIP_ROWS,0),i.pixelStorei(i.UNPACK_SKIP_IMAGES,0),g={},_={},xt=null,z={},v={},y=new WeakMap,b=[],R=null,S=!1,x=null,A=null,N=null,L=null,H=null,B=null,O=null,E=new Le(0,0,0),U=0,V=!1,F=null,j=null,lt=null,ct=null,q=null,Rt.set(0,0,i.canvas.width,i.canvas.height),Nt.set(0,0,i.canvas.width,i.canvas.height),c.reset(),u.reset(),d.reset()}return{buffers:{color:c,depth:u,stencil:d},enable:Tt,disable:Ht,bindFramebuffer:ee,drawBuffers:$t,useProgram:Xe,setBlending:Ue,setMaterial:ue,setFlipSided:cn,setCullFace:Ze,setLineWidth:Dn,setPolygonOffset:Y,setScissorTest:an,activeTexture:pe,bindTexture:Ve,unbindTexture:Ct,compressedTexImage2D:$e,compressedTexImage3D:P,texImage2D:ft,texImage3D:ht,pixelStorei:Ft,getParameter:Ot,updateUBOMapping:ae,uniformBlockBinding:se,texStorage2D:wt,texStorage3D:Pt,texSubImage2D:T,texSubImage3D:J,compressedTexSubImage2D:_t,compressedTexSubImage3D:Et,scissor:Lt,viewport:Dt,reset:me}}function G3(i,t,n,s,o,c,u){const d=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new je,g=new WeakMap,_=new Set;let v;const y=new WeakMap;let b=!1;try{b=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function R(P,T){return b?new OffscreenCanvas(P,T):sf("canvas")}function S(P,T,J){let _t=1;const Et=$e(P);if((Et.width>J||Et.height>J)&&(_t=J/Math.max(Et.width,Et.height)),_t<1)if(typeof HTMLImageElement<"u"&&P instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&P instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&P instanceof ImageBitmap||typeof VideoFrame<"u"&&P instanceof VideoFrame){const wt=Math.floor(_t*Et.width),Pt=Math.floor(_t*Et.height);v===void 0&&(v=R(wt,Pt));const ft=T?R(wt,Pt):v;return ft.width=wt,ft.height=Pt,ft.getContext("2d").drawImage(P,0,0,wt,Pt),ie("WebGLRenderer: Texture has been resized from ("+Et.width+"x"+Et.height+") to ("+wt+"x"+Pt+")."),ft}else return"data"in P&&ie("WebGLRenderer: Image in DataTexture is too big ("+Et.width+"x"+Et.height+")."),P;return P}function x(P){return P.generateMipmaps}function A(P){i.generateMipmap(P)}function N(P){return P.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:P.isWebGL3DRenderTarget?i.TEXTURE_3D:P.isWebGLArrayRenderTarget||P.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function L(P,T,J,_t,Et,wt=!1){if(P!==null){if(i[P]!==void 0)return i[P];ie("WebGLRenderer: Attempt to use non-existing WebGL internal format '"+P+"'")}let Pt;_t&&(Pt=t.get("EXT_texture_norm16"),Pt||ie("WebGLRenderer: Unable to use normalized textures without EXT_texture_norm16 extension"));let ft=T;if(T===i.RED&&(J===i.FLOAT&&(ft=i.R32F),J===i.HALF_FLOAT&&(ft=i.R16F),J===i.UNSIGNED_BYTE&&(ft=i.R8),J===i.UNSIGNED_SHORT&&Pt&&(ft=Pt.R16_EXT),J===i.SHORT&&Pt&&(ft=Pt.R16_SNORM_EXT)),T===i.RED_INTEGER&&(J===i.UNSIGNED_BYTE&&(ft=i.R8UI),J===i.UNSIGNED_SHORT&&(ft=i.R16UI),J===i.UNSIGNED_INT&&(ft=i.R32UI),J===i.BYTE&&(ft=i.R8I),J===i.SHORT&&(ft=i.R16I),J===i.INT&&(ft=i.R32I)),T===i.RG&&(J===i.FLOAT&&(ft=i.RG32F),J===i.HALF_FLOAT&&(ft=i.RG16F),J===i.UNSIGNED_BYTE&&(ft=i.RG8),J===i.UNSIGNED_SHORT&&Pt&&(ft=Pt.RG16_EXT),J===i.SHORT&&Pt&&(ft=Pt.RG16_SNORM_EXT)),T===i.RG_INTEGER&&(J===i.UNSIGNED_BYTE&&(ft=i.RG8UI),J===i.UNSIGNED_SHORT&&(ft=i.RG16UI),J===i.UNSIGNED_INT&&(ft=i.RG32UI),J===i.BYTE&&(ft=i.RG8I),J===i.SHORT&&(ft=i.RG16I),J===i.INT&&(ft=i.RG32I)),T===i.RGB_INTEGER&&(J===i.UNSIGNED_BYTE&&(ft=i.RGB8UI),J===i.UNSIGNED_SHORT&&(ft=i.RGB16UI),J===i.UNSIGNED_INT&&(ft=i.RGB32UI),J===i.BYTE&&(ft=i.RGB8I),J===i.SHORT&&(ft=i.RGB16I),J===i.INT&&(ft=i.RGB32I)),T===i.RGBA_INTEGER&&(J===i.UNSIGNED_BYTE&&(ft=i.RGBA8UI),J===i.UNSIGNED_SHORT&&(ft=i.RGBA16UI),J===i.UNSIGNED_INT&&(ft=i.RGBA32UI),J===i.BYTE&&(ft=i.RGBA8I),J===i.SHORT&&(ft=i.RGBA16I),J===i.INT&&(ft=i.RGBA32I)),T===i.RGB&&(J===i.UNSIGNED_SHORT&&Pt&&(ft=Pt.RGB16_EXT),J===i.SHORT&&Pt&&(ft=Pt.RGB16_SNORM_EXT),J===i.UNSIGNED_INT_5_9_9_9_REV&&(ft=i.RGB9_E5),J===i.UNSIGNED_INT_10F_11F_11F_REV&&(ft=i.R11F_G11F_B10F)),T===i.RGBA){const ht=wt?nf:be.getTransfer(Et);J===i.FLOAT&&(ft=i.RGBA32F),J===i.HALF_FLOAT&&(ft=i.RGBA16F),J===i.UNSIGNED_BYTE&&(ft=ht===ze?i.SRGB8_ALPHA8:i.RGBA8),J===i.UNSIGNED_SHORT&&Pt&&(ft=Pt.RGBA16_EXT),J===i.SHORT&&Pt&&(ft=Pt.RGBA16_SNORM_EXT),J===i.UNSIGNED_SHORT_4_4_4_4&&(ft=i.RGBA4),J===i.UNSIGNED_SHORT_5_5_5_1&&(ft=i.RGB5_A1)}return(ft===i.R16F||ft===i.R32F||ft===i.RG16F||ft===i.RG32F||ft===i.RGBA16F||ft===i.RGBA32F)&&t.get("EXT_color_buffer_float"),ft}function H(P,T){let J;return P?T===null||T===fa||T===Vl?J=i.DEPTH24_STENCIL8:T===sa?J=i.DEPTH32F_STENCIL8:T===zl&&(J=i.DEPTH24_STENCIL8,ie("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):T===null||T===fa||T===Vl?J=i.DEPTH_COMPONENT24:T===sa?J=i.DEPTH_COMPONENT32F:T===zl&&(J=i.DEPTH_COMPONENT16),J}function B(P,T){return x(P)===!0||P.isFramebufferTexture&&P.minFilter!==Bn&&P.minFilter!==jn?Math.log2(Math.max(T.width,T.height))+1:P.mipmaps!==void 0&&P.mipmaps.length>0?P.mipmaps.length:P.isCompressedTexture&&Array.isArray(P.image)?T.mipmaps.length:1}function O(P){const T=P.target;T.removeEventListener("dispose",O),U(T),T.isVideoTexture&&g.delete(T),T.isHTMLTexture&&_.delete(T)}function E(P){const T=P.target;T.removeEventListener("dispose",E),F(T)}function U(P){const T=s.get(P);if(T.__webglInit===void 0)return;const J=P.source,_t=y.get(J);if(_t){const Et=_t[T.__cacheKey];Et.usedTimes--,Et.usedTimes===0&&V(P),Object.keys(_t).length===0&&y.delete(J)}s.remove(P)}function V(P){const T=s.get(P);i.deleteTexture(T.__webglTexture);const J=P.source,_t=y.get(J);delete _t[T.__cacheKey],u.memory.textures--}function F(P){const T=s.get(P);if(P.depthTexture&&(P.depthTexture.dispose(),s.remove(P.depthTexture)),P.isWebGLCubeRenderTarget)for(let _t=0;_t<6;_t++){if(Array.isArray(T.__webglFramebuffer[_t]))for(let Et=0;Et<T.__webglFramebuffer[_t].length;Et++)i.deleteFramebuffer(T.__webglFramebuffer[_t][Et]);else i.deleteFramebuffer(T.__webglFramebuffer[_t]);T.__webglDepthbuffer&&i.deleteRenderbuffer(T.__webglDepthbuffer[_t])}else{if(Array.isArray(T.__webglFramebuffer))for(let _t=0;_t<T.__webglFramebuffer.length;_t++)i.deleteFramebuffer(T.__webglFramebuffer[_t]);else i.deleteFramebuffer(T.__webglFramebuffer);if(T.__webglDepthbuffer&&i.deleteRenderbuffer(T.__webglDepthbuffer),T.__webglMultisampledFramebuffer&&i.deleteFramebuffer(T.__webglMultisampledFramebuffer),T.__webglColorRenderbuffer)for(let _t=0;_t<T.__webglColorRenderbuffer.length;_t++)T.__webglColorRenderbuffer[_t]&&i.deleteRenderbuffer(T.__webglColorRenderbuffer[_t]);T.__webglDepthRenderbuffer&&i.deleteRenderbuffer(T.__webglDepthRenderbuffer)}const J=P.textures;for(let _t=0,Et=J.length;_t<Et;_t++){const wt=s.get(J[_t]);wt.__webglTexture&&(i.deleteTexture(wt.__webglTexture),u.memory.textures--),s.remove(J[_t])}s.remove(P)}let j=0;function lt(){j=0}function ct(){return j}function q(P){j=P}function I(){const P=j;return P>=o.maxTextures&&ie("WebGLTextures: Trying to use "+P+" texture units while this GPU supports only "+o.maxTextures),j+=1,P}function G(P){const T=[];return T.push(P.wrapS),T.push(P.wrapT),T.push(P.wrapR||0),T.push(P.magFilter),T.push(P.minFilter),T.push(P.anisotropy),T.push(P.internalFormat),T.push(P.format),T.push(P.type),T.push(P.generateMipmaps),T.push(P.premultiplyAlpha),T.push(P.flipY),T.push(P.unpackAlignment),T.push(P.colorSpace),T.join()}function $(P,T){const J=s.get(P);if(P.isVideoTexture&&Ve(P),P.isRenderTargetTexture===!1&&P.isExternalTexture!==!0&&P.version>0&&J.__version!==P.version){const _t=P.image;if(_t===null)ie("WebGLRenderer: Texture marked for update but no image data found.");else if(_t.complete===!1)ie("WebGLRenderer: Texture marked for update but image is incomplete");else{Ht(J,P,T);return}}else P.isExternalTexture&&(J.__webglTexture=P.sourceTexture?P.sourceTexture:null);n.bindTexture(i.TEXTURE_2D,J.__webglTexture,i.TEXTURE0+T)}function dt(P,T){const J=s.get(P);if(P.isRenderTargetTexture===!1&&P.version>0&&J.__version!==P.version){Ht(J,P,T);return}else P.isExternalTexture&&(J.__webglTexture=P.sourceTexture?P.sourceTexture:null);n.bindTexture(i.TEXTURE_2D_ARRAY,J.__webglTexture,i.TEXTURE0+T)}function xt(P,T){const J=s.get(P);if(P.isRenderTargetTexture===!1&&P.version>0&&J.__version!==P.version){Ht(J,P,T);return}n.bindTexture(i.TEXTURE_3D,J.__webglTexture,i.TEXTURE0+T)}function z(P,T){const J=s.get(P);if(P.isCubeDepthTexture!==!0&&P.version>0&&J.__version!==P.version){ee(J,P,T);return}n.bindTexture(i.TEXTURE_CUBE_MAP,J.__webglTexture,i.TEXTURE0+T)}const Q={[Hp]:i.REPEAT,[za]:i.CLAMP_TO_EDGE,[Gp]:i.MIRRORED_REPEAT},St={[Bn]:i.NEAREST,[uA]:i.NEAREST_MIPMAP_NEAREST,[uu]:i.NEAREST_MIPMAP_LINEAR,[jn]:i.LINEAR,[Ih]:i.LINEAR_MIPMAP_NEAREST,[or]:i.LINEAR_MIPMAP_LINEAR},Rt={[hA]:i.NEVER,[vA]:i.ALWAYS,[pA]:i.LESS,[ig]:i.LEQUAL,[mA]:i.EQUAL,[ag]:i.GEQUAL,[gA]:i.GREATER,[_A]:i.NOTEQUAL};function Nt(P,T){if(T.type===sa&&t.has("OES_texture_float_linear")===!1&&(T.magFilter===jn||T.magFilter===Ih||T.magFilter===uu||T.magFilter===or||T.minFilter===jn||T.minFilter===Ih||T.minFilter===uu||T.minFilter===or)&&ie("WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(P,i.TEXTURE_WRAP_S,Q[T.wrapS]),i.texParameteri(P,i.TEXTURE_WRAP_T,Q[T.wrapT]),(P===i.TEXTURE_3D||P===i.TEXTURE_2D_ARRAY)&&i.texParameteri(P,i.TEXTURE_WRAP_R,Q[T.wrapR]),i.texParameteri(P,i.TEXTURE_MAG_FILTER,St[T.magFilter]),i.texParameteri(P,i.TEXTURE_MIN_FILTER,St[T.minFilter]),T.compareFunction&&(i.texParameteri(P,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(P,i.TEXTURE_COMPARE_FUNC,Rt[T.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(T.magFilter===Bn||T.minFilter!==uu&&T.minFilter!==or||T.type===sa&&t.has("OES_texture_float_linear")===!1)return;if(T.anisotropy>1||s.get(T).__currentAnisotropy){const J=t.get("EXT_texture_filter_anisotropic");i.texParameterf(P,J.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(T.anisotropy,o.getMaxAnisotropy())),s.get(T).__currentAnisotropy=T.anisotropy}}}function ot(P,T){let J=!1;P.__webglInit===void 0&&(P.__webglInit=!0,T.addEventListener("dispose",O));const _t=T.source;let Et=y.get(_t);Et===void 0&&(Et={},y.set(_t,Et));const wt=G(T);if(wt!==P.__cacheKey){Et[wt]===void 0&&(Et[wt]={texture:i.createTexture(),usedTimes:0},u.memory.textures++,J=!0),Et[wt].usedTimes++;const Pt=Et[P.__cacheKey];Pt!==void 0&&(Et[P.__cacheKey].usedTimes--,Pt.usedTimes===0&&V(T)),P.__cacheKey=wt,P.__webglTexture=Et[wt].texture}return J}function Mt(P,T,J){return Math.floor(Math.floor(P/J)/T)}function Tt(P,T,J,_t){const wt=P.updateRanges;if(wt.length===0)n.texSubImage2D(i.TEXTURE_2D,0,0,0,T.width,T.height,J,_t,T.data);else{wt.sort((Ft,Lt)=>Ft.start-Lt.start);let Pt=0;for(let Ft=1;Ft<wt.length;Ft++){const Lt=wt[Pt],Dt=wt[Ft],ae=Lt.start+Lt.count,se=Mt(Dt.start,T.width,4),me=Mt(Lt.start,T.width,4);Dt.start<=ae+1&&se===me&&Mt(Dt.start+Dt.count-1,T.width,4)===se?Lt.count=Math.max(Lt.count,Dt.start+Dt.count-Lt.start):(++Pt,wt[Pt]=Dt)}wt.length=Pt+1;const ft=n.getParameter(i.UNPACK_ROW_LENGTH),ht=n.getParameter(i.UNPACK_SKIP_PIXELS),Ot=n.getParameter(i.UNPACK_SKIP_ROWS);n.pixelStorei(i.UNPACK_ROW_LENGTH,T.width);for(let Ft=0,Lt=wt.length;Ft<Lt;Ft++){const Dt=wt[Ft],ae=Math.floor(Dt.start/4),se=Math.ceil(Dt.count/4),me=ae%T.width,X=Math.floor(ae/T.width),At=se,mt=1;n.pixelStorei(i.UNPACK_SKIP_PIXELS,me),n.pixelStorei(i.UNPACK_SKIP_ROWS,X),n.texSubImage2D(i.TEXTURE_2D,0,me,X,At,mt,J,_t,T.data)}P.clearUpdateRanges(),n.pixelStorei(i.UNPACK_ROW_LENGTH,ft),n.pixelStorei(i.UNPACK_SKIP_PIXELS,ht),n.pixelStorei(i.UNPACK_SKIP_ROWS,Ot)}}function Ht(P,T,J){let _t=i.TEXTURE_2D;(T.isDataArrayTexture||T.isCompressedArrayTexture)&&(_t=i.TEXTURE_2D_ARRAY),T.isData3DTexture&&(_t=i.TEXTURE_3D);const Et=ot(P,T),wt=T.source;n.bindTexture(_t,P.__webglTexture,i.TEXTURE0+J);const Pt=s.get(wt);if(wt.version!==Pt.__version||Et===!0){if(n.activeTexture(i.TEXTURE0+J),(typeof ImageBitmap<"u"&&T.image instanceof ImageBitmap)===!1){const mt=be.getPrimaries(be.workingColorSpace),zt=T.colorSpace===As?null:be.getPrimaries(T.colorSpace),Ut=T.colorSpace===As||mt===zt?i.NONE:i.BROWSER_DEFAULT_WEBGL;n.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,T.flipY),n.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),n.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ut)}n.pixelStorei(i.UNPACK_ALIGNMENT,T.unpackAlignment);let ht=S(T.image,!1,o.maxTextureSize);ht=Ct(T,ht);const Ot=c.convert(T.format,T.colorSpace),Ft=c.convert(T.type);let Lt=L(T.internalFormat,Ot,Ft,T.normalized,T.colorSpace,T.isVideoTexture);Nt(_t,T);let Dt;const ae=T.mipmaps,se=T.isVideoTexture!==!0,me=Pt.__version===void 0||Et===!0,X=wt.dataReady,At=B(T,ht);if(T.isDepthTexture)Lt=H(T.format===lr,T.type),me&&(se?n.texStorage2D(i.TEXTURE_2D,1,Lt,ht.width,ht.height):n.texImage2D(i.TEXTURE_2D,0,Lt,ht.width,ht.height,0,Ot,Ft,null));else if(T.isDataTexture)if(ae.length>0){se&&me&&n.texStorage2D(i.TEXTURE_2D,At,Lt,ae[0].width,ae[0].height);for(let mt=0,zt=ae.length;mt<zt;mt++)Dt=ae[mt],se?X&&n.texSubImage2D(i.TEXTURE_2D,mt,0,0,Dt.width,Dt.height,Ot,Ft,Dt.data):n.texImage2D(i.TEXTURE_2D,mt,Lt,Dt.width,Dt.height,0,Ot,Ft,Dt.data);T.generateMipmaps=!1}else se?(me&&n.texStorage2D(i.TEXTURE_2D,At,Lt,ht.width,ht.height),X&&Tt(T,ht,Ot,Ft)):n.texImage2D(i.TEXTURE_2D,0,Lt,ht.width,ht.height,0,Ot,Ft,ht.data);else if(T.isCompressedTexture)if(T.isCompressedArrayTexture){se&&me&&n.texStorage3D(i.TEXTURE_2D_ARRAY,At,Lt,ae[0].width,ae[0].height,ht.depth);for(let mt=0,zt=ae.length;mt<zt;mt++)if(Dt=ae[mt],T.format!==Xi)if(Ot!==null)if(se){if(X)if(T.layerUpdates.size>0){const Ut=iy(Dt.width,Dt.height,T.format,T.type);for(const bt of T.layerUpdates){const Yt=Dt.data.subarray(bt*Ut/Dt.data.BYTES_PER_ELEMENT,(bt+1)*Ut/Dt.data.BYTES_PER_ELEMENT);n.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,mt,0,0,bt,Dt.width,Dt.height,1,Ot,Yt)}T.clearLayerUpdates()}else n.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,mt,0,0,0,Dt.width,Dt.height,ht.depth,Ot,Dt.data)}else n.compressedTexImage3D(i.TEXTURE_2D_ARRAY,mt,Lt,Dt.width,Dt.height,ht.depth,0,Dt.data,0,0);else ie("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else se?X&&n.texSubImage3D(i.TEXTURE_2D_ARRAY,mt,0,0,0,Dt.width,Dt.height,ht.depth,Ot,Ft,Dt.data):n.texImage3D(i.TEXTURE_2D_ARRAY,mt,Lt,Dt.width,Dt.height,ht.depth,0,Ot,Ft,Dt.data)}else{se&&me&&n.texStorage2D(i.TEXTURE_2D,At,Lt,ae[0].width,ae[0].height);for(let mt=0,zt=ae.length;mt<zt;mt++)Dt=ae[mt],T.format!==Xi?Ot!==null?se?X&&n.compressedTexSubImage2D(i.TEXTURE_2D,mt,0,0,Dt.width,Dt.height,Ot,Dt.data):n.compressedTexImage2D(i.TEXTURE_2D,mt,Lt,Dt.width,Dt.height,0,Dt.data):ie("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):se?X&&n.texSubImage2D(i.TEXTURE_2D,mt,0,0,Dt.width,Dt.height,Ot,Ft,Dt.data):n.texImage2D(i.TEXTURE_2D,mt,Lt,Dt.width,Dt.height,0,Ot,Ft,Dt.data)}else if(T.isDataArrayTexture)if(se){if(me&&n.texStorage3D(i.TEXTURE_2D_ARRAY,At,Lt,ht.width,ht.height,ht.depth),X)if(T.layerUpdates.size>0){const mt=iy(ht.width,ht.height,T.format,T.type);for(const zt of T.layerUpdates){const Ut=ht.data.subarray(zt*mt/ht.data.BYTES_PER_ELEMENT,(zt+1)*mt/ht.data.BYTES_PER_ELEMENT);n.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,zt,ht.width,ht.height,1,Ot,Ft,Ut)}T.clearLayerUpdates()}else n.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,ht.width,ht.height,ht.depth,Ot,Ft,ht.data)}else n.texImage3D(i.TEXTURE_2D_ARRAY,0,Lt,ht.width,ht.height,ht.depth,0,Ot,Ft,ht.data);else if(T.isData3DTexture)se?(me&&n.texStorage3D(i.TEXTURE_3D,At,Lt,ht.width,ht.height,ht.depth),X&&n.texSubImage3D(i.TEXTURE_3D,0,0,0,0,ht.width,ht.height,ht.depth,Ot,Ft,ht.data)):n.texImage3D(i.TEXTURE_3D,0,Lt,ht.width,ht.height,ht.depth,0,Ot,Ft,ht.data);else if(T.isFramebufferTexture){if(me)if(se)n.texStorage2D(i.TEXTURE_2D,At,Lt,ht.width,ht.height);else{let mt=ht.width,zt=ht.height;for(let Ut=0;Ut<At;Ut++)n.texImage2D(i.TEXTURE_2D,Ut,Lt,mt,zt,0,Ot,Ft,null),mt>>=1,zt>>=1}}else if(T.isHTMLTexture){if("texElementImage2D"in i){const mt=i.canvas;if(mt.hasAttribute("layoutsubtree")||mt.setAttribute("layoutsubtree","true"),ht.parentNode!==mt){mt.appendChild(ht),_.add(T),mt.onpaint=ne=>{const sn=ne.changedElements;for(const we of _)sn.includes(we.image)&&(we.needsUpdate=!0)},mt.requestPaint();return}const zt=0,Ut=i.RGBA,bt=i.RGBA,Yt=i.UNSIGNED_BYTE;i.texElementImage2D(i.TEXTURE_2D,zt,Ut,bt,Yt,ht),i.texParameteri(i.TEXTURE_2D,i.TEXTURE_MIN_FILTER,i.LINEAR),i.texParameteri(i.TEXTURE_2D,i.TEXTURE_WRAP_S,i.CLAMP_TO_EDGE),i.texParameteri(i.TEXTURE_2D,i.TEXTURE_WRAP_T,i.CLAMP_TO_EDGE)}}else if(ae.length>0){if(se&&me){const mt=$e(ae[0]);n.texStorage2D(i.TEXTURE_2D,At,Lt,mt.width,mt.height)}for(let mt=0,zt=ae.length;mt<zt;mt++)Dt=ae[mt],se?X&&n.texSubImage2D(i.TEXTURE_2D,mt,0,0,Ot,Ft,Dt):n.texImage2D(i.TEXTURE_2D,mt,Lt,Ot,Ft,Dt);T.generateMipmaps=!1}else if(se){if(me){const mt=$e(ht);n.texStorage2D(i.TEXTURE_2D,At,Lt,mt.width,mt.height)}X&&n.texSubImage2D(i.TEXTURE_2D,0,0,0,Ot,Ft,ht)}else n.texImage2D(i.TEXTURE_2D,0,Lt,Ot,Ft,ht);x(T)&&A(_t),Pt.__version=wt.version,T.onUpdate&&T.onUpdate(T)}P.__version=T.version}function ee(P,T,J){if(T.image.length!==6)return;const _t=ot(P,T),Et=T.source;n.bindTexture(i.TEXTURE_CUBE_MAP,P.__webglTexture,i.TEXTURE0+J);const wt=s.get(Et);if(Et.version!==wt.__version||_t===!0){n.activeTexture(i.TEXTURE0+J);const Pt=be.getPrimaries(be.workingColorSpace),ft=T.colorSpace===As?null:be.getPrimaries(T.colorSpace),ht=T.colorSpace===As||Pt===ft?i.NONE:i.BROWSER_DEFAULT_WEBGL;n.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,T.flipY),n.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),n.pixelStorei(i.UNPACK_ALIGNMENT,T.unpackAlignment),n.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,ht);const Ot=T.isCompressedTexture||T.image[0].isCompressedTexture,Ft=T.image[0]&&T.image[0].isDataTexture,Lt=[];for(let bt=0;bt<6;bt++)!Ot&&!Ft?Lt[bt]=S(T.image[bt],!0,o.maxCubemapSize):Lt[bt]=Ft?T.image[bt].image:T.image[bt],Lt[bt]=Ct(T,Lt[bt]);const Dt=Lt[0],ae=c.convert(T.format,T.colorSpace),se=c.convert(T.type),me=L(T.internalFormat,ae,se,T.normalized,T.colorSpace),X=T.isVideoTexture!==!0,At=wt.__version===void 0||_t===!0,mt=Et.dataReady;let zt=B(T,Dt);Nt(i.TEXTURE_CUBE_MAP,T);let Ut;if(Ot){X&&At&&n.texStorage2D(i.TEXTURE_CUBE_MAP,zt,me,Dt.width,Dt.height);for(let bt=0;bt<6;bt++){Ut=Lt[bt].mipmaps;for(let Yt=0;Yt<Ut.length;Yt++){const ne=Ut[Yt];T.format!==Xi?ae!==null?X?mt&&n.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt,0,0,ne.width,ne.height,ae,ne.data):n.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt,me,ne.width,ne.height,0,ne.data):ie("WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):X?mt&&n.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt,0,0,ne.width,ne.height,ae,se,ne.data):n.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt,me,ne.width,ne.height,0,ae,se,ne.data)}}}else{if(Ut=T.mipmaps,X&&At){Ut.length>0&&zt++;const bt=$e(Lt[0]);n.texStorage2D(i.TEXTURE_CUBE_MAP,zt,me,bt.width,bt.height)}for(let bt=0;bt<6;bt++)if(Ft){X?mt&&n.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,0,0,0,Lt[bt].width,Lt[bt].height,ae,se,Lt[bt].data):n.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,0,me,Lt[bt].width,Lt[bt].height,0,ae,se,Lt[bt].data);for(let Yt=0;Yt<Ut.length;Yt++){const sn=Ut[Yt].image[bt].image;X?mt&&n.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt+1,0,0,sn.width,sn.height,ae,se,sn.data):n.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt+1,me,sn.width,sn.height,0,ae,se,sn.data)}}else{X?mt&&n.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,0,0,0,ae,se,Lt[bt]):n.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,0,me,ae,se,Lt[bt]);for(let Yt=0;Yt<Ut.length;Yt++){const ne=Ut[Yt];X?mt&&n.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt+1,0,0,ae,se,ne.image[bt]):n.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+bt,Yt+1,me,ae,se,ne.image[bt])}}}x(T)&&A(i.TEXTURE_CUBE_MAP),wt.__version=Et.version,T.onUpdate&&T.onUpdate(T)}P.__version=T.version}function $t(P,T,J,_t,Et,wt){const Pt=c.convert(J.format,J.colorSpace),ft=c.convert(J.type),ht=L(J.internalFormat,Pt,ft,J.normalized,J.colorSpace),Ot=s.get(T),Ft=s.get(J);if(Ft.__renderTarget=T,!Ot.__hasExternalTextures){const Lt=Math.max(1,T.width>>wt),Dt=Math.max(1,T.height>>wt);Et===i.TEXTURE_3D||Et===i.TEXTURE_2D_ARRAY?n.texImage3D(Et,wt,ht,Lt,Dt,T.depth,0,Pt,ft,null):n.texImage2D(Et,wt,ht,Lt,Dt,0,Pt,ft,null)}n.bindFramebuffer(i.FRAMEBUFFER,P),pe(T)?d.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,_t,Et,Ft.__webglTexture,0,an(T)):(Et===i.TEXTURE_2D||Et>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&Et<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,_t,Et,Ft.__webglTexture,wt),n.bindFramebuffer(i.FRAMEBUFFER,null)}function Xe(P,T,J){if(i.bindRenderbuffer(i.RENDERBUFFER,P),T.depthBuffer){const _t=T.depthTexture,Et=_t&&_t.isDepthTexture?_t.type:null,wt=H(T.stencilBuffer,Et),Pt=T.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;pe(T)?d.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,an(T),wt,T.width,T.height):J?i.renderbufferStorageMultisample(i.RENDERBUFFER,an(T),wt,T.width,T.height):i.renderbufferStorage(i.RENDERBUFFER,wt,T.width,T.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Pt,i.RENDERBUFFER,P)}else{const _t=T.textures;for(let Et=0;Et<_t.length;Et++){const wt=_t[Et],Pt=c.convert(wt.format,wt.colorSpace),ft=c.convert(wt.type),ht=L(wt.internalFormat,Pt,ft,wt.normalized,wt.colorSpace);pe(T)?d.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,an(T),ht,T.width,T.height):J?i.renderbufferStorageMultisample(i.RENDERBUFFER,an(T),ht,T.width,T.height):i.renderbufferStorage(i.RENDERBUFFER,ht,T.width,T.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function he(P,T,J){const _t=T.isWebGLCubeRenderTarget===!0;if(n.bindFramebuffer(i.FRAMEBUFFER,P),!(T.depthTexture&&T.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const Et=s.get(T.depthTexture);if(Et.__renderTarget=T,(!Et.__webglTexture||T.depthTexture.image.width!==T.width||T.depthTexture.image.height!==T.height)&&(T.depthTexture.image.width=T.width,T.depthTexture.image.height=T.height,T.depthTexture.needsUpdate=!0),_t){if(Et.__webglInit===void 0&&(Et.__webglInit=!0,T.depthTexture.addEventListener("dispose",O)),Et.__webglTexture===void 0){Et.__webglTexture=i.createTexture(),n.bindTexture(i.TEXTURE_CUBE_MAP,Et.__webglTexture),Nt(i.TEXTURE_CUBE_MAP,T.depthTexture);const Ot=c.convert(T.depthTexture.format),Ft=c.convert(T.depthTexture.type);let Lt;T.depthTexture.format===ka?Lt=i.DEPTH_COMPONENT24:T.depthTexture.format===lr&&(Lt=i.DEPTH24_STENCIL8);for(let Dt=0;Dt<6;Dt++)i.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,0,Lt,T.width,T.height,0,Ot,Ft,null)}}else $(T.depthTexture,0);const wt=Et.__webglTexture,Pt=an(T),ft=_t?i.TEXTURE_CUBE_MAP_POSITIVE_X+J:i.TEXTURE_2D,ht=T.depthTexture.format===lr?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;if(T.depthTexture.format===ka)pe(T)?d.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,ht,ft,wt,0,Pt):i.framebufferTexture2D(i.FRAMEBUFFER,ht,ft,wt,0);else if(T.depthTexture.format===lr)pe(T)?d.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,ht,ft,wt,0,Pt):i.framebufferTexture2D(i.FRAMEBUFFER,ht,ft,wt,0);else throw new Error("Unknown depthTexture format")}function xe(P){const T=s.get(P),J=P.isWebGLCubeRenderTarget===!0;if(T.__boundDepthTexture!==P.depthTexture){const _t=P.depthTexture;if(T.__depthDisposeCallback&&T.__depthDisposeCallback(),_t){const Et=()=>{delete T.__boundDepthTexture,delete T.__depthDisposeCallback,_t.removeEventListener("dispose",Et)};_t.addEventListener("dispose",Et),T.__depthDisposeCallback=Et}T.__boundDepthTexture=_t}if(P.depthTexture&&!T.__autoAllocateDepthBuffer)if(J)for(let _t=0;_t<6;_t++)he(T.__webglFramebuffer[_t],P,_t);else{const _t=P.texture.mipmaps;_t&&_t.length>0?he(T.__webglFramebuffer[0],P,0):he(T.__webglFramebuffer,P,0)}else if(J){T.__webglDepthbuffer=[];for(let _t=0;_t<6;_t++)if(n.bindFramebuffer(i.FRAMEBUFFER,T.__webglFramebuffer[_t]),T.__webglDepthbuffer[_t]===void 0)T.__webglDepthbuffer[_t]=i.createRenderbuffer(),Xe(T.__webglDepthbuffer[_t],P,!1);else{const Et=P.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,wt=T.__webglDepthbuffer[_t];i.bindRenderbuffer(i.RENDERBUFFER,wt),i.framebufferRenderbuffer(i.FRAMEBUFFER,Et,i.RENDERBUFFER,wt)}}else{const _t=P.texture.mipmaps;if(_t&&_t.length>0?n.bindFramebuffer(i.FRAMEBUFFER,T.__webglFramebuffer[0]):n.bindFramebuffer(i.FRAMEBUFFER,T.__webglFramebuffer),T.__webglDepthbuffer===void 0)T.__webglDepthbuffer=i.createRenderbuffer(),Xe(T.__webglDepthbuffer,P,!1);else{const Et=P.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,wt=T.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,wt),i.framebufferRenderbuffer(i.FRAMEBUFFER,Et,i.RENDERBUFFER,wt)}}n.bindFramebuffer(i.FRAMEBUFFER,null)}function Ue(P,T,J){const _t=s.get(P);T!==void 0&&$t(_t.__webglFramebuffer,P,P.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),J!==void 0&&xe(P)}function ue(P){const T=P.texture,J=s.get(P),_t=s.get(T);P.addEventListener("dispose",E);const Et=P.textures,wt=P.isWebGLCubeRenderTarget===!0,Pt=Et.length>1;if(Pt||(_t.__webglTexture===void 0&&(_t.__webglTexture=i.createTexture()),_t.__version=T.version,u.memory.textures++),wt){J.__webglFramebuffer=[];for(let ft=0;ft<6;ft++)if(T.mipmaps&&T.mipmaps.length>0){J.__webglFramebuffer[ft]=[];for(let ht=0;ht<T.mipmaps.length;ht++)J.__webglFramebuffer[ft][ht]=i.createFramebuffer()}else J.__webglFramebuffer[ft]=i.createFramebuffer()}else{if(T.mipmaps&&T.mipmaps.length>0){J.__webglFramebuffer=[];for(let ft=0;ft<T.mipmaps.length;ft++)J.__webglFramebuffer[ft]=i.createFramebuffer()}else J.__webglFramebuffer=i.createFramebuffer();if(Pt)for(let ft=0,ht=Et.length;ft<ht;ft++){const Ot=s.get(Et[ft]);Ot.__webglTexture===void 0&&(Ot.__webglTexture=i.createTexture(),u.memory.textures++)}if(P.samples>0&&pe(P)===!1){J.__webglMultisampledFramebuffer=i.createFramebuffer(),J.__webglColorRenderbuffer=[],n.bindFramebuffer(i.FRAMEBUFFER,J.__webglMultisampledFramebuffer);for(let ft=0;ft<Et.length;ft++){const ht=Et[ft];J.__webglColorRenderbuffer[ft]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,J.__webglColorRenderbuffer[ft]);const Ot=c.convert(ht.format,ht.colorSpace),Ft=c.convert(ht.type),Lt=L(ht.internalFormat,Ot,Ft,ht.normalized,ht.colorSpace,P.isXRRenderTarget===!0),Dt=an(P);i.renderbufferStorageMultisample(i.RENDERBUFFER,Dt,Lt,P.width,P.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ft,i.RENDERBUFFER,J.__webglColorRenderbuffer[ft])}i.bindRenderbuffer(i.RENDERBUFFER,null),P.depthBuffer&&(J.__webglDepthRenderbuffer=i.createRenderbuffer(),Xe(J.__webglDepthRenderbuffer,P,!0)),n.bindFramebuffer(i.FRAMEBUFFER,null)}}if(wt){n.bindTexture(i.TEXTURE_CUBE_MAP,_t.__webglTexture),Nt(i.TEXTURE_CUBE_MAP,T);for(let ft=0;ft<6;ft++)if(T.mipmaps&&T.mipmaps.length>0)for(let ht=0;ht<T.mipmaps.length;ht++)$t(J.__webglFramebuffer[ft][ht],P,T,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ft,ht);else $t(J.__webglFramebuffer[ft],P,T,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ft,0);x(T)&&A(i.TEXTURE_CUBE_MAP),n.unbindTexture()}else if(Pt){for(let ft=0,ht=Et.length;ft<ht;ft++){const Ot=Et[ft],Ft=s.get(Ot);let Lt=i.TEXTURE_2D;(P.isWebGL3DRenderTarget||P.isWebGLArrayRenderTarget)&&(Lt=P.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),n.bindTexture(Lt,Ft.__webglTexture),Nt(Lt,Ot),$t(J.__webglFramebuffer,P,Ot,i.COLOR_ATTACHMENT0+ft,Lt,0),x(Ot)&&A(Lt)}n.unbindTexture()}else{let ft=i.TEXTURE_2D;if((P.isWebGL3DRenderTarget||P.isWebGLArrayRenderTarget)&&(ft=P.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),n.bindTexture(ft,_t.__webglTexture),Nt(ft,T),T.mipmaps&&T.mipmaps.length>0)for(let ht=0;ht<T.mipmaps.length;ht++)$t(J.__webglFramebuffer[ht],P,T,i.COLOR_ATTACHMENT0,ft,ht);else $t(J.__webglFramebuffer,P,T,i.COLOR_ATTACHMENT0,ft,0);x(T)&&A(ft),n.unbindTexture()}P.depthBuffer&&xe(P)}function cn(P){const T=P.textures;for(let J=0,_t=T.length;J<_t;J++){const Et=T[J];if(x(Et)){const wt=N(P),Pt=s.get(Et).__webglTexture;n.bindTexture(wt,Pt),A(wt),n.unbindTexture()}}}const Ze=[],Dn=[];function Y(P){if(P.samples>0){if(pe(P)===!1){const T=P.textures,J=P.width,_t=P.height;let Et=i.COLOR_BUFFER_BIT;const wt=P.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Pt=s.get(P),ft=T.length>1;if(ft)for(let Ot=0;Ot<T.length;Ot++)n.bindFramebuffer(i.FRAMEBUFFER,Pt.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ot,i.RENDERBUFFER,null),n.bindFramebuffer(i.FRAMEBUFFER,Pt.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ot,i.TEXTURE_2D,null,0);n.bindFramebuffer(i.READ_FRAMEBUFFER,Pt.__webglMultisampledFramebuffer);const ht=P.texture.mipmaps;ht&&ht.length>0?n.bindFramebuffer(i.DRAW_FRAMEBUFFER,Pt.__webglFramebuffer[0]):n.bindFramebuffer(i.DRAW_FRAMEBUFFER,Pt.__webglFramebuffer);for(let Ot=0;Ot<T.length;Ot++){if(P.resolveDepthBuffer&&(P.depthBuffer&&(Et|=i.DEPTH_BUFFER_BIT),P.stencilBuffer&&P.resolveStencilBuffer&&(Et|=i.STENCIL_BUFFER_BIT)),ft){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Pt.__webglColorRenderbuffer[Ot]);const Ft=s.get(T[Ot]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ft,0)}i.blitFramebuffer(0,0,J,_t,0,0,J,_t,Et,i.NEAREST),p===!0&&(Ze.length=0,Dn.length=0,Ze.push(i.COLOR_ATTACHMENT0+Ot),P.depthBuffer&&P.resolveDepthBuffer===!1&&(Ze.push(wt),Dn.push(wt),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,Dn)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,Ze))}if(n.bindFramebuffer(i.READ_FRAMEBUFFER,null),n.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ft)for(let Ot=0;Ot<T.length;Ot++){n.bindFramebuffer(i.FRAMEBUFFER,Pt.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ot,i.RENDERBUFFER,Pt.__webglColorRenderbuffer[Ot]);const Ft=s.get(T[Ot]).__webglTexture;n.bindFramebuffer(i.FRAMEBUFFER,Pt.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ot,i.TEXTURE_2D,Ft,0)}n.bindFramebuffer(i.DRAW_FRAMEBUFFER,Pt.__webglMultisampledFramebuffer)}else if(P.depthBuffer&&P.resolveDepthBuffer===!1&&p){const T=P.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[T])}}}function an(P){return Math.min(o.maxSamples,P.samples)}function pe(P){const T=s.get(P);return P.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&T.__useRenderToTexture!==!1}function Ve(P){const T=u.render.frame;g.get(P)!==T&&(g.set(P,T),P.update())}function Ct(P,T){const J=P.colorSpace,_t=P.format,Et=P.type;return P.isCompressedTexture===!0||P.isVideoTexture===!0||J!==ef&&J!==As&&(be.getTransfer(J)===ze?(_t!==Xi||Et!==Ni)&&ie("WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):Te("WebGLTextures: Unsupported texture color space:",J)),T}function $e(P){return typeof HTMLImageElement<"u"&&P instanceof HTMLImageElement?(h.width=P.naturalWidth||P.width,h.height=P.naturalHeight||P.height):typeof VideoFrame<"u"&&P instanceof VideoFrame?(h.width=P.displayWidth,h.height=P.displayHeight):(h.width=P.width,h.height=P.height),h}this.allocateTextureUnit=I,this.resetTextureUnits=lt,this.getTextureUnits=ct,this.setTextureUnits=q,this.setTexture2D=$,this.setTexture2DArray=dt,this.setTexture3D=xt,this.setTextureCube=z,this.rebindTextures=Ue,this.setupRenderTarget=ue,this.updateRenderTargetMipmap=cn,this.updateMultisampleRenderTarget=Y,this.setupDepthRenderbuffer=xe,this.setupFrameBufferTexture=$t,this.useMultisampledRTT=pe,this.isReversedDepthBuffer=function(){return n.buffers.depth.getReversed()}}function k3(i,t){function n(s,o=As){let c;const u=be.getTransfer(o);if(s===Ni)return i.UNSIGNED_BYTE;if(s===Jm)return i.UNSIGNED_SHORT_4_4_4_4;if(s===$m)return i.UNSIGNED_SHORT_5_5_5_1;if(s===lM)return i.UNSIGNED_INT_5_9_9_9_REV;if(s===cM)return i.UNSIGNED_INT_10F_11F_11F_REV;if(s===rM)return i.BYTE;if(s===oM)return i.SHORT;if(s===zl)return i.UNSIGNED_SHORT;if(s===Qm)return i.INT;if(s===fa)return i.UNSIGNED_INT;if(s===sa)return i.FLOAT;if(s===Ga)return i.HALF_FLOAT;if(s===uM)return i.ALPHA;if(s===fM)return i.RGB;if(s===Xi)return i.RGBA;if(s===ka)return i.DEPTH_COMPONENT;if(s===lr)return i.DEPTH_STENCIL;if(s===dM)return i.RED;if(s===tg)return i.RED_INTEGER;if(s===pr)return i.RG;if(s===eg)return i.RG_INTEGER;if(s===ng)return i.RGBA_INTEGER;if(s===Vu||s===Hu||s===Gu||s===ku)if(u===ze)if(c=t.get("WEBGL_compressed_texture_s3tc_srgb"),c!==null){if(s===Vu)return c.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===Hu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===Gu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===ku)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(c=t.get("WEBGL_compressed_texture_s3tc"),c!==null){if(s===Vu)return c.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===Hu)return c.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===Gu)return c.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===ku)return c.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===kp||s===jp||s===Xp||s===Wp)if(c=t.get("WEBGL_compressed_texture_pvrtc"),c!==null){if(s===kp)return c.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===jp)return c.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===Xp)return c.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===Wp)return c.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===qp||s===Yp||s===Kp||s===Zp||s===Qp||s===$u||s===Jp)if(c=t.get("WEBGL_compressed_texture_etc"),c!==null){if(s===qp||s===Yp)return u===ze?c.COMPRESSED_SRGB8_ETC2:c.COMPRESSED_RGB8_ETC2;if(s===Kp)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:c.COMPRESSED_RGBA8_ETC2_EAC;if(s===Zp)return c.COMPRESSED_R11_EAC;if(s===Qp)return c.COMPRESSED_SIGNED_R11_EAC;if(s===$u)return c.COMPRESSED_RG11_EAC;if(s===Jp)return c.COMPRESSED_SIGNED_RG11_EAC}else return null;if(s===$p||s===tm||s===em||s===nm||s===im||s===am||s===sm||s===rm||s===om||s===lm||s===cm||s===um||s===fm||s===dm)if(c=t.get("WEBGL_compressed_texture_astc"),c!==null){if(s===$p)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:c.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===tm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:c.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===em)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:c.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===nm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:c.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===im)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:c.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===am)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:c.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===sm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:c.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===rm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:c.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===om)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:c.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===lm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:c.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===cm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:c.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===um)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:c.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===fm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:c.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===dm)return u===ze?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:c.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===hm||s===pm||s===mm)if(c=t.get("EXT_texture_compression_bptc"),c!==null){if(s===hm)return u===ze?c.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:c.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(s===pm)return c.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(s===mm)return c.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(s===gm||s===_m||s===tf||s===vm)if(c=t.get("EXT_texture_compression_rgtc"),c!==null){if(s===gm)return c.COMPRESSED_RED_RGTC1_EXT;if(s===_m)return c.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===tf)return c.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===vm)return c.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===Vl?i.UNSIGNED_INT_24_8:i[s]!==void 0?i[s]:null}return{convert:n}}const j3=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,X3=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class W3{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,n){if(this.texture===null){const s=new EM(t.texture);(t.depthNear!==n.depthNear||t.depthFar!==n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(t){if(this.texture!==null&&this.mesh===null){const n=t.cameras[0].viewport,s=new da({vertexShader:j3,fragmentShader:X3,uniforms:{depthColor:{value:this.texture},depthWidth:{value:n.z},depthHeight:{value:n.w}}});this.mesh=new ja(new xf(20,20),s)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class q3 extends vr{constructor(t,n){super();const s=this;let o=null,c=1,u=null,d="local-floor",p=1,h=null,g=null,_=null,v=null,y=null,b=null;const R=typeof XRWebGLBinding<"u",S=new W3,x={},A=n.getContextAttributes();let N=null,L=null;const H=[],B=[],O=new je;let E=null;const U=new Di;U.viewport=new hn;const V=new Di;V.viewport=new hn;const F=[U,V],j=new iR;let lt=null,ct=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ot){let Mt=H[ot];return Mt===void 0&&(Mt=new Wh,H[ot]=Mt),Mt.getTargetRaySpace()},this.getControllerGrip=function(ot){let Mt=H[ot];return Mt===void 0&&(Mt=new Wh,H[ot]=Mt),Mt.getGripSpace()},this.getHand=function(ot){let Mt=H[ot];return Mt===void 0&&(Mt=new Wh,H[ot]=Mt),Mt.getHandSpace()};function q(ot){const Mt=B.indexOf(ot.inputSource);if(Mt===-1)return;const Tt=H[Mt];Tt!==void 0&&(Tt.update(ot.inputSource,ot.frame,h||u),Tt.dispatchEvent({type:ot.type,data:ot.inputSource}))}function I(){o.removeEventListener("select",q),o.removeEventListener("selectstart",q),o.removeEventListener("selectend",q),o.removeEventListener("squeeze",q),o.removeEventListener("squeezestart",q),o.removeEventListener("squeezeend",q),o.removeEventListener("end",I),o.removeEventListener("inputsourceschange",G);for(let ot=0;ot<H.length;ot++){const Mt=B[ot];Mt!==null&&(B[ot]=null,H[ot].disconnect(Mt))}lt=null,ct=null,S.reset();for(const ot in x)delete x[ot];t.setRenderTarget(N),y=null,v=null,_=null,o=null,L=null,Nt.stop(),s.isPresenting=!1,t.setPixelRatio(E),t.setSize(O.width,O.height,!1),s.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ot){c=ot,s.isPresenting===!0&&ie("WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ot){d=ot,s.isPresenting===!0&&ie("WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||u},this.setReferenceSpace=function(ot){h=ot},this.getBaseLayer=function(){return v!==null?v:y},this.getBinding=function(){return _===null&&R&&(_=new XRWebGLBinding(o,n)),_},this.getFrame=function(){return b},this.getSession=function(){return o},this.setSession=async function(ot){if(o=ot,o!==null){if(N=t.getRenderTarget(),o.addEventListener("select",q),o.addEventListener("selectstart",q),o.addEventListener("selectend",q),o.addEventListener("squeeze",q),o.addEventListener("squeezestart",q),o.addEventListener("squeezeend",q),o.addEventListener("end",I),o.addEventListener("inputsourceschange",G),A.xrCompatible!==!0&&await n.makeXRCompatible(),E=t.getPixelRatio(),t.getSize(O),R&&"createProjectionLayer"in XRWebGLBinding.prototype){let Tt=null,Ht=null,ee=null;A.depth&&(ee=A.stencil?n.DEPTH24_STENCIL8:n.DEPTH_COMPONENT24,Tt=A.stencil?lr:ka,Ht=A.stencil?Vl:fa);const $t={colorFormat:n.RGBA8,depthFormat:ee,scaleFactor:c};_=this.getBinding(),v=_.createProjectionLayer($t),o.updateRenderState({layers:[v]}),t.setPixelRatio(1),t.setSize(v.textureWidth,v.textureHeight,!1),L=new la(v.textureWidth,v.textureHeight,{format:Xi,type:Ni,depthTexture:new So(v.textureWidth,v.textureHeight,Ht,void 0,void 0,void 0,void 0,void 0,void 0,Tt),stencilBuffer:A.stencil,colorSpace:t.outputColorSpace,samples:A.antialias?4:0,resolveDepthBuffer:v.ignoreDepthValues===!1,resolveStencilBuffer:v.ignoreDepthValues===!1})}else{const Tt={antialias:A.antialias,alpha:!0,depth:A.depth,stencil:A.stencil,framebufferScaleFactor:c};y=new XRWebGLLayer(o,n,Tt),o.updateRenderState({baseLayer:y}),t.setPixelRatio(1),t.setSize(y.framebufferWidth,y.framebufferHeight,!1),L=new la(y.framebufferWidth,y.framebufferHeight,{format:Xi,type:Ni,colorSpace:t.outputColorSpace,stencilBuffer:A.stencil,resolveDepthBuffer:y.ignoreDepthValues===!1,resolveStencilBuffer:y.ignoreDepthValues===!1})}L.isXRRenderTarget=!0,this.setFoveation(p),h=null,u=await o.requestReferenceSpace(d),Nt.setContext(o),Nt.start(),s.isPresenting=!0,s.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(o!==null)return o.environmentBlendMode},this.getDepthTexture=function(){return S.getDepthTexture()};function G(ot){for(let Mt=0;Mt<ot.removed.length;Mt++){const Tt=ot.removed[Mt],Ht=B.indexOf(Tt);Ht>=0&&(B[Ht]=null,H[Ht].disconnect(Tt))}for(let Mt=0;Mt<ot.added.length;Mt++){const Tt=ot.added[Mt];let Ht=B.indexOf(Tt);if(Ht===-1){for(let $t=0;$t<H.length;$t++)if($t>=B.length){B.push(Tt),Ht=$t;break}else if(B[$t]===null){B[$t]=Tt,Ht=$t;break}if(Ht===-1)break}const ee=H[Ht];ee&&ee.connect(Tt)}}const $=new rt,dt=new rt;function xt(ot,Mt,Tt){$.setFromMatrixPosition(Mt.matrixWorld),dt.setFromMatrixPosition(Tt.matrixWorld);const Ht=$.distanceTo(dt),ee=Mt.projectionMatrix.elements,$t=Tt.projectionMatrix.elements,Xe=ee[14]/(ee[10]-1),he=ee[14]/(ee[10]+1),xe=(ee[9]+1)/ee[5],Ue=(ee[9]-1)/ee[5],ue=(ee[8]-1)/ee[0],cn=($t[8]+1)/$t[0],Ze=Xe*ue,Dn=Xe*cn,Y=Ht/(-ue+cn),an=Y*-ue;if(Mt.matrixWorld.decompose(ot.position,ot.quaternion,ot.scale),ot.translateX(an),ot.translateZ(Y),ot.matrixWorld.compose(ot.position,ot.quaternion,ot.scale),ot.matrixWorldInverse.copy(ot.matrixWorld).invert(),ee[10]===-1)ot.projectionMatrix.copy(Mt.projectionMatrix),ot.projectionMatrixInverse.copy(Mt.projectionMatrixInverse);else{const pe=Xe+Y,Ve=he+Y,Ct=Ze-an,$e=Dn+(Ht-an),P=xe*he/Ve*pe,T=Ue*he/Ve*pe;ot.projectionMatrix.makePerspective(Ct,$e,P,T,pe,Ve),ot.projectionMatrixInverse.copy(ot.projectionMatrix).invert()}}function z(ot,Mt){Mt===null?ot.matrixWorld.copy(ot.matrix):ot.matrixWorld.multiplyMatrices(Mt.matrixWorld,ot.matrix),ot.matrixWorldInverse.copy(ot.matrixWorld).invert()}this.updateCamera=function(ot){if(o===null)return;let Mt=ot.near,Tt=ot.far;S.texture!==null&&(S.depthNear>0&&(Mt=S.depthNear),S.depthFar>0&&(Tt=S.depthFar)),j.near=V.near=U.near=Mt,j.far=V.far=U.far=Tt,(lt!==j.near||ct!==j.far)&&(o.updateRenderState({depthNear:j.near,depthFar:j.far}),lt=j.near,ct=j.far),j.layers.mask=ot.layers.mask|6,U.layers.mask=j.layers.mask&-5,V.layers.mask=j.layers.mask&-3;const Ht=ot.parent,ee=j.cameras;z(j,Ht);for(let $t=0;$t<ee.length;$t++)z(ee[$t],Ht);ee.length===2?xt(j,U,V):j.projectionMatrix.copy(U.projectionMatrix),Q(ot,j,Ht)};function Q(ot,Mt,Tt){Tt===null?ot.matrix.copy(Mt.matrixWorld):(ot.matrix.copy(Tt.matrixWorld),ot.matrix.invert(),ot.matrix.multiply(Mt.matrixWorld)),ot.matrix.decompose(ot.position,ot.quaternion,ot.scale),ot.updateMatrixWorld(!0),ot.projectionMatrix.copy(Mt.projectionMatrix),ot.projectionMatrixInverse.copy(Mt.projectionMatrixInverse),ot.isPerspectiveCamera&&(ot.fov=ym*2*Math.atan(1/ot.projectionMatrix.elements[5]),ot.zoom=1)}this.getCamera=function(){return j},this.getFoveation=function(){if(!(v===null&&y===null))return p},this.setFoveation=function(ot){p=ot,v!==null&&(v.fixedFoveation=ot),y!==null&&y.fixedFoveation!==void 0&&(y.fixedFoveation=ot)},this.hasDepthSensing=function(){return S.texture!==null},this.getDepthSensingMesh=function(){return S.getMesh(j)},this.getCameraTexture=function(ot){return x[ot]};let St=null;function Rt(ot,Mt){if(g=Mt.getViewerPose(h||u),b=Mt,g!==null){const Tt=g.views;y!==null&&(t.setRenderTargetFramebuffer(L,y.framebuffer),t.setRenderTarget(L));let Ht=!1;Tt.length!==j.cameras.length&&(j.cameras.length=0,Ht=!0);for(let he=0;he<Tt.length;he++){const xe=Tt[he];let Ue=null;if(y!==null)Ue=y.getViewport(xe);else{const cn=_.getViewSubImage(v,xe);Ue=cn.viewport,he===0&&(t.setRenderTargetTextures(L,cn.colorTexture,cn.depthStencilTexture),t.setRenderTarget(L))}let ue=F[he];ue===void 0&&(ue=new Di,ue.layers.enable(he),ue.viewport=new hn,F[he]=ue),ue.matrix.fromArray(xe.transform.matrix),ue.matrix.decompose(ue.position,ue.quaternion,ue.scale),ue.projectionMatrix.fromArray(xe.projectionMatrix),ue.projectionMatrixInverse.copy(ue.projectionMatrix).invert(),ue.viewport.set(Ue.x,Ue.y,Ue.width,Ue.height),he===0&&(j.matrix.copy(ue.matrix),j.matrix.decompose(j.position,j.quaternion,j.scale)),Ht===!0&&j.cameras.push(ue)}const ee=o.enabledFeatures;if(ee&&ee.includes("depth-sensing")&&o.depthUsage=="gpu-optimized"&&R){_=s.getBinding();const he=_.getDepthInformation(Tt[0]);he&&he.isValid&&he.texture&&S.init(he,o.renderState)}if(ee&&ee.includes("camera-access")&&R){t.state.unbindTexture(),_=s.getBinding();for(let he=0;he<Tt.length;he++){const xe=Tt[he].camera;if(xe){let Ue=x[xe];Ue||(Ue=new EM,x[xe]=Ue);const ue=_.getCameraImage(xe);Ue.sourceTexture=ue}}}}for(let Tt=0;Tt<H.length;Tt++){const Ht=B[Tt],ee=H[Tt];Ht!==null&&ee!==void 0&&ee.update(Ht,Mt,h||u)}St&&St(ot,Mt),Mt.detectedPlanes&&s.dispatchEvent({type:"planesdetected",data:Mt}),b=null}const Nt=new CM;Nt.setAnimationLoop(Rt),this.setAnimationLoop=function(ot){St=ot},this.dispose=function(){}}}const Y3=new Sn,OM=new oe;OM.set(-1,0,0,0,1,0,0,0,1);function K3(i,t){function n(S,x){S.matrixAutoUpdate===!0&&S.updateMatrix(),x.value.copy(S.matrix)}function s(S,x){x.color.getRGB(S.fogColor.value,TM(i)),x.isFog?(S.fogNear.value=x.near,S.fogFar.value=x.far):x.isFogExp2&&(S.fogDensity.value=x.density)}function o(S,x,A,N,L){x.isNodeMaterial?x.uniformsNeedUpdate=!1:x.isMeshBasicMaterial?c(S,x):x.isMeshLambertMaterial?(c(S,x),x.envMap&&(S.envMapIntensity.value=x.envMapIntensity)):x.isMeshToonMaterial?(c(S,x),_(S,x)):x.isMeshPhongMaterial?(c(S,x),g(S,x),x.envMap&&(S.envMapIntensity.value=x.envMapIntensity)):x.isMeshStandardMaterial?(c(S,x),v(S,x),x.isMeshPhysicalMaterial&&y(S,x,L)):x.isMeshMatcapMaterial?(c(S,x),b(S,x)):x.isMeshDepthMaterial?c(S,x):x.isMeshDistanceMaterial?(c(S,x),R(S,x)):x.isMeshNormalMaterial?c(S,x):x.isLineBasicMaterial?(u(S,x),x.isLineDashedMaterial&&d(S,x)):x.isPointsMaterial?p(S,x,A,N):x.isSpriteMaterial?h(S,x):x.isShadowMaterial?(S.color.value.copy(x.color),S.opacity.value=x.opacity):x.isShaderMaterial&&(x.uniformsNeedUpdate=!1)}function c(S,x){S.opacity.value=x.opacity,x.color&&S.diffuse.value.copy(x.color),x.emissive&&S.emissive.value.copy(x.emissive).multiplyScalar(x.emissiveIntensity),x.map&&(S.map.value=x.map,n(x.map,S.mapTransform)),x.alphaMap&&(S.alphaMap.value=x.alphaMap,n(x.alphaMap,S.alphaMapTransform)),x.bumpMap&&(S.bumpMap.value=x.bumpMap,n(x.bumpMap,S.bumpMapTransform),S.bumpScale.value=x.bumpScale,x.side===ii&&(S.bumpScale.value*=-1)),x.normalMap&&(S.normalMap.value=x.normalMap,n(x.normalMap,S.normalMapTransform),S.normalScale.value.copy(x.normalScale),x.side===ii&&S.normalScale.value.negate()),x.displacementMap&&(S.displacementMap.value=x.displacementMap,n(x.displacementMap,S.displacementMapTransform),S.displacementScale.value=x.displacementScale,S.displacementBias.value=x.displacementBias),x.emissiveMap&&(S.emissiveMap.value=x.emissiveMap,n(x.emissiveMap,S.emissiveMapTransform)),x.specularMap&&(S.specularMap.value=x.specularMap,n(x.specularMap,S.specularMapTransform)),x.alphaTest>0&&(S.alphaTest.value=x.alphaTest);const A=t.get(x),N=A.envMap,L=A.envMapRotation;N&&(S.envMap.value=N,S.envMapRotation.value.setFromMatrix4(Y3.makeRotationFromEuler(L)).transpose(),N.isCubeTexture&&N.isRenderTargetTexture===!1&&S.envMapRotation.value.premultiply(OM),S.reflectivity.value=x.reflectivity,S.ior.value=x.ior,S.refractionRatio.value=x.refractionRatio),x.lightMap&&(S.lightMap.value=x.lightMap,S.lightMapIntensity.value=x.lightMapIntensity,n(x.lightMap,S.lightMapTransform)),x.aoMap&&(S.aoMap.value=x.aoMap,S.aoMapIntensity.value=x.aoMapIntensity,n(x.aoMap,S.aoMapTransform))}function u(S,x){S.diffuse.value.copy(x.color),S.opacity.value=x.opacity,x.map&&(S.map.value=x.map,n(x.map,S.mapTransform))}function d(S,x){S.dashSize.value=x.dashSize,S.totalSize.value=x.dashSize+x.gapSize,S.scale.value=x.scale}function p(S,x,A,N){S.diffuse.value.copy(x.color),S.opacity.value=x.opacity,S.size.value=x.size*A,S.scale.value=N*.5,x.map&&(S.map.value=x.map,n(x.map,S.uvTransform)),x.alphaMap&&(S.alphaMap.value=x.alphaMap,n(x.alphaMap,S.alphaMapTransform)),x.alphaTest>0&&(S.alphaTest.value=x.alphaTest)}function h(S,x){S.diffuse.value.copy(x.color),S.opacity.value=x.opacity,S.rotation.value=x.rotation,x.map&&(S.map.value=x.map,n(x.map,S.mapTransform)),x.alphaMap&&(S.alphaMap.value=x.alphaMap,n(x.alphaMap,S.alphaMapTransform)),x.alphaTest>0&&(S.alphaTest.value=x.alphaTest)}function g(S,x){S.specular.value.copy(x.specular),S.shininess.value=Math.max(x.shininess,1e-4)}function _(S,x){x.gradientMap&&(S.gradientMap.value=x.gradientMap)}function v(S,x){S.metalness.value=x.metalness,x.metalnessMap&&(S.metalnessMap.value=x.metalnessMap,n(x.metalnessMap,S.metalnessMapTransform)),S.roughness.value=x.roughness,x.roughnessMap&&(S.roughnessMap.value=x.roughnessMap,n(x.roughnessMap,S.roughnessMapTransform)),x.envMap&&(S.envMapIntensity.value=x.envMapIntensity)}function y(S,x,A){S.ior.value=x.ior,x.sheen>0&&(S.sheenColor.value.copy(x.sheenColor).multiplyScalar(x.sheen),S.sheenRoughness.value=x.sheenRoughness,x.sheenColorMap&&(S.sheenColorMap.value=x.sheenColorMap,n(x.sheenColorMap,S.sheenColorMapTransform)),x.sheenRoughnessMap&&(S.sheenRoughnessMap.value=x.sheenRoughnessMap,n(x.sheenRoughnessMap,S.sheenRoughnessMapTransform))),x.clearcoat>0&&(S.clearcoat.value=x.clearcoat,S.clearcoatRoughness.value=x.clearcoatRoughness,x.clearcoatMap&&(S.clearcoatMap.value=x.clearcoatMap,n(x.clearcoatMap,S.clearcoatMapTransform)),x.clearcoatRoughnessMap&&(S.clearcoatRoughnessMap.value=x.clearcoatRoughnessMap,n(x.clearcoatRoughnessMap,S.clearcoatRoughnessMapTransform)),x.clearcoatNormalMap&&(S.clearcoatNormalMap.value=x.clearcoatNormalMap,n(x.clearcoatNormalMap,S.clearcoatNormalMapTransform),S.clearcoatNormalScale.value.copy(x.clearcoatNormalScale),x.side===ii&&S.clearcoatNormalScale.value.negate())),x.dispersion>0&&(S.dispersion.value=x.dispersion),x.iridescence>0&&(S.iridescence.value=x.iridescence,S.iridescenceIOR.value=x.iridescenceIOR,S.iridescenceThicknessMinimum.value=x.iridescenceThicknessRange[0],S.iridescenceThicknessMaximum.value=x.iridescenceThicknessRange[1],x.iridescenceMap&&(S.iridescenceMap.value=x.iridescenceMap,n(x.iridescenceMap,S.iridescenceMapTransform)),x.iridescenceThicknessMap&&(S.iridescenceThicknessMap.value=x.iridescenceThicknessMap,n(x.iridescenceThicknessMap,S.iridescenceThicknessMapTransform))),x.transmission>0&&(S.transmission.value=x.transmission,S.transmissionSamplerMap.value=A.texture,S.transmissionSamplerSize.value.set(A.width,A.height),x.transmissionMap&&(S.transmissionMap.value=x.transmissionMap,n(x.transmissionMap,S.transmissionMapTransform)),S.thickness.value=x.thickness,x.thicknessMap&&(S.thicknessMap.value=x.thicknessMap,n(x.thicknessMap,S.thicknessMapTransform)),S.attenuationDistance.value=x.attenuationDistance,S.attenuationColor.value.copy(x.attenuationColor)),x.anisotropy>0&&(S.anisotropyVector.value.set(x.anisotropy*Math.cos(x.anisotropyRotation),x.anisotropy*Math.sin(x.anisotropyRotation)),x.anisotropyMap&&(S.anisotropyMap.value=x.anisotropyMap,n(x.anisotropyMap,S.anisotropyMapTransform))),S.specularIntensity.value=x.specularIntensity,S.specularColor.value.copy(x.specularColor),x.specularColorMap&&(S.specularColorMap.value=x.specularColorMap,n(x.specularColorMap,S.specularColorMapTransform)),x.specularIntensityMap&&(S.specularIntensityMap.value=x.specularIntensityMap,n(x.specularIntensityMap,S.specularIntensityMapTransform))}function b(S,x){x.matcap&&(S.matcap.value=x.matcap)}function R(S,x){const A=t.get(x).light;S.referencePosition.value.setFromMatrixPosition(A.matrixWorld),S.nearDistance.value=A.shadow.camera.near,S.farDistance.value=A.shadow.camera.far}return{refreshFogUniforms:s,refreshMaterialUniforms:o}}function Z3(i,t,n,s){let o={},c={},u=[];const d=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function p(A,N){const L=N.program;s.uniformBlockBinding(A,L)}function h(A,N){let L=o[A.id];L===void 0&&(b(A),L=g(A),o[A.id]=L,A.addEventListener("dispose",S));const H=N.program;s.updateUBOMapping(A,H);const B=t.render.frame;c[A.id]!==B&&(v(A),c[A.id]=B)}function g(A){const N=_();A.__bindingPointIndex=N;const L=i.createBuffer(),H=A.__size,B=A.usage;return i.bindBuffer(i.UNIFORM_BUFFER,L),i.bufferData(i.UNIFORM_BUFFER,H,B),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,N,L),L}function _(){for(let A=0;A<d;A++)if(u.indexOf(A)===-1)return u.push(A),A;return Te("WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function v(A){const N=o[A.id],L=A.uniforms,H=A.__cache;i.bindBuffer(i.UNIFORM_BUFFER,N);for(let B=0,O=L.length;B<O;B++){const E=Array.isArray(L[B])?L[B]:[L[B]];for(let U=0,V=E.length;U<V;U++){const F=E[U];if(y(F,B,U,H)===!0){const j=F.__offset,lt=Array.isArray(F.value)?F.value:[F.value];let ct=0;for(let q=0;q<lt.length;q++){const I=lt[q],G=R(I);typeof I=="number"||typeof I=="boolean"?(F.__data[0]=I,i.bufferSubData(i.UNIFORM_BUFFER,j+ct,F.__data)):I.isMatrix3?(F.__data[0]=I.elements[0],F.__data[1]=I.elements[1],F.__data[2]=I.elements[2],F.__data[3]=0,F.__data[4]=I.elements[3],F.__data[5]=I.elements[4],F.__data[6]=I.elements[5],F.__data[7]=0,F.__data[8]=I.elements[6],F.__data[9]=I.elements[7],F.__data[10]=I.elements[8],F.__data[11]=0):ArrayBuffer.isView(I)?F.__data.set(new I.constructor(I.buffer,I.byteOffset,F.__data.length)):(I.toArray(F.__data,ct),ct+=G.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,j,F.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function y(A,N,L,H){const B=A.value,O=N+"_"+L;if(H[O]===void 0)return typeof B=="number"||typeof B=="boolean"?H[O]=B:ArrayBuffer.isView(B)?H[O]=B.slice():H[O]=B.clone(),!0;{const E=H[O];if(typeof B=="number"||typeof B=="boolean"){if(E!==B)return H[O]=B,!0}else{if(ArrayBuffer.isView(B))return!0;if(E.equals(B)===!1)return E.copy(B),!0}}return!1}function b(A){const N=A.uniforms;let L=0;const H=16;for(let O=0,E=N.length;O<E;O++){const U=Array.isArray(N[O])?N[O]:[N[O]];for(let V=0,F=U.length;V<F;V++){const j=U[V],lt=Array.isArray(j.value)?j.value:[j.value];for(let ct=0,q=lt.length;ct<q;ct++){const I=lt[ct],G=R(I),$=L%H,dt=$%G.boundary,xt=$+dt;L+=dt,xt!==0&&H-xt<G.storage&&(L+=H-xt),j.__data=new Float32Array(G.storage/Float32Array.BYTES_PER_ELEMENT),j.__offset=L,L+=G.storage}}}const B=L%H;return B>0&&(L+=H-B),A.__size=L,A.__cache={},this}function R(A){const N={boundary:0,storage:0};return typeof A=="number"||typeof A=="boolean"?(N.boundary=4,N.storage=4):A.isVector2?(N.boundary=8,N.storage=8):A.isVector3||A.isColor?(N.boundary=16,N.storage=12):A.isVector4?(N.boundary=16,N.storage=16):A.isMatrix3?(N.boundary=48,N.storage=48):A.isMatrix4?(N.boundary=64,N.storage=64):A.isTexture?ie("WebGLRenderer: Texture samplers can not be part of an uniforms group."):ArrayBuffer.isView(A)?(N.boundary=16,N.storage=A.byteLength):ie("WebGLRenderer: Unsupported uniform value type.",A),N}function S(A){const N=A.target;N.removeEventListener("dispose",S);const L=u.indexOf(N.__bindingPointIndex);u.splice(L,1),i.deleteBuffer(o[N.id]),delete o[N.id],delete c[N.id]}function x(){for(const A in o)i.deleteBuffer(o[A]);u=[],o={},c={}}return{bind:p,update:h,dispose:x}}const Q3=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]);let ea=null;function J3(){return ea===null&&(ea=new kA(Q3,16,16,pr,Ga),ea.name="DFG_LUT",ea.minFilter=jn,ea.magFilter=jn,ea.wrapS=za,ea.wrapT=za,ea.generateMipmaps=!1,ea.needsUpdate=!0),ea}class $3{constructor(t={}){const{canvas:n=yA(),context:s=null,depth:o=!0,stencil:c=!1,alpha:u=!1,antialias:d=!1,premultipliedAlpha:p=!0,preserveDrawingBuffer:h=!1,powerPreference:g="default",failIfMajorPerformanceCaveat:_=!1,reversedDepthBuffer:v=!1,outputBufferType:y=Ni}=t;this.isWebGLRenderer=!0;let b;if(s!==null){if(typeof WebGLRenderingContext<"u"&&s instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");b=s.getContextAttributes().alpha}else b=u;const R=y,S=new Set([ng,eg,tg]),x=new Set([Ni,fa,zl,Vl,Jm,$m]),A=new Uint32Array(4),N=new Int32Array(4),L=new rt;let H=null,B=null;const O=[],E=[];let U=null;this.domElement=n,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=oa,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const V=this;let F=!1,j=null;this._outputColorSpace=wi;let lt=0,ct=0,q=null,I=-1,G=null;const $=new hn,dt=new hn;let xt=null;const z=new Le(0);let Q=0,St=n.width,Rt=n.height,Nt=1,ot=null,Mt=null;const Tt=new hn(0,0,St,Rt),Ht=new hn(0,0,St,Rt);let ee=!1;const $t=new SM;let Xe=!1,he=!1;const xe=new Sn,Ue=new rt,ue=new hn,cn={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ze=!1;function Dn(){return q===null?Nt:1}let Y=s;function an(C,K){return n.getContext(C,K)}try{const C={alpha:!0,depth:o,stencil:c,antialias:d,premultipliedAlpha:p,preserveDrawingBuffer:h,powerPreference:g,failIfMajorPerformanceCaveat:_};if("setAttribute"in n&&n.setAttribute("data-engine",`three.js r${Zm}`),n.addEventListener("webglcontextlost",bt,!1),n.addEventListener("webglcontextrestored",Yt,!1),n.addEventListener("webglcontextcreationerror",ne,!1),Y===null){const K="webgl2";if(Y=an(K,C),Y===null)throw an(K)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(C){throw Te("WebGLRenderer: "+C.message),C}let pe,Ve,Ct,$e,P,T,J,_t,Et,wt,Pt,ft,ht,Ot,Ft,Lt,Dt,ae,se,me,X,At,mt;function zt(){pe=new Jw(Y),pe.init(),X=new k3(Y,pe),Ve=new jw(Y,pe,t,X),Ct=new H3(Y,pe),Ve.reversedDepthBuffer&&v&&Ct.buffers.depth.setReversed(!0),$e=new e2(Y),P=new R3,T=new G3(Y,pe,Ct,P,Ve,X,$e),J=new Qw(V),_t=new sR(Y),At=new Gw(Y,_t),Et=new $w(Y,_t,$e,At),wt=new i2(Y,Et,_t,At,$e),ae=new n2(Y,Ve,T),Ft=new Xw(P),Pt=new A3(V,J,pe,Ve,At,Ft),ft=new K3(V,P),ht=new w3,Ot=new O3(pe),Dt=new Hw(V,J,Ct,wt,b,p),Lt=new V3(V,wt,Ve),mt=new Z3(Y,$e,Ve,Ct),se=new kw(Y,pe,$e),me=new t2(Y,pe,$e),$e.programs=Pt.programs,V.capabilities=Ve,V.extensions=pe,V.properties=P,V.renderLists=ht,V.shadowMap=Lt,V.state=Ct,V.info=$e}zt(),R!==Ni&&(U=new s2(R,n.width,n.height,o,c));const Ut=new q3(V,Y);this.xr=Ut,this.getContext=function(){return Y},this.getContextAttributes=function(){return Y.getContextAttributes()},this.forceContextLoss=function(){const C=pe.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=pe.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return Nt},this.setPixelRatio=function(C){C!==void 0&&(Nt=C,this.setSize(St,Rt,!1))},this.getSize=function(C){return C.set(St,Rt)},this.setSize=function(C,K,at=!0){if(Ut.isPresenting){ie("WebGLRenderer: Can't change size while VR device is presenting.");return}St=C,Rt=K,n.width=Math.floor(C*Nt),n.height=Math.floor(K*Nt),at===!0&&(n.style.width=C+"px",n.style.height=K+"px"),U!==null&&U.setSize(n.width,n.height),this.setViewport(0,0,C,K)},this.getDrawingBufferSize=function(C){return C.set(St*Nt,Rt*Nt).floor()},this.setDrawingBufferSize=function(C,K,at){St=C,Rt=K,Nt=at,n.width=Math.floor(C*at),n.height=Math.floor(K*at),this.setViewport(0,0,C,K)},this.setEffects=function(C){if(R===Ni){Te("THREE.WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.");return}if(C){for(let K=0;K<C.length;K++)if(C[K].isOutputPass===!0){ie("THREE.WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.");break}}U.setEffects(C||[])},this.getCurrentViewport=function(C){return C.copy($)},this.getViewport=function(C){return C.copy(Tt)},this.setViewport=function(C,K,at,nt){C.isVector4?Tt.set(C.x,C.y,C.z,C.w):Tt.set(C,K,at,nt),Ct.viewport($.copy(Tt).multiplyScalar(Nt).round())},this.getScissor=function(C){return C.copy(Ht)},this.setScissor=function(C,K,at,nt){C.isVector4?Ht.set(C.x,C.y,C.z,C.w):Ht.set(C,K,at,nt),Ct.scissor(dt.copy(Ht).multiplyScalar(Nt).round())},this.getScissorTest=function(){return ee},this.setScissorTest=function(C){Ct.setScissorTest(ee=C)},this.setOpaqueSort=function(C){ot=C},this.setTransparentSort=function(C){Mt=C},this.getClearColor=function(C){return C.copy(Dt.getClearColor())},this.setClearColor=function(){Dt.setClearColor(...arguments)},this.getClearAlpha=function(){return Dt.getClearAlpha()},this.setClearAlpha=function(){Dt.setClearAlpha(...arguments)},this.clear=function(C=!0,K=!0,at=!0){let nt=0;if(C){let it=!1;if(q!==null){const It=q.texture.format;it=S.has(It)}if(it){const It=q.texture.type,kt=x.has(It),Bt=Dt.getClearColor(),Xt=Dt.getClearAlpha(),jt=Bt.r,Qt=Bt.g,le=Bt.b;kt?(A[0]=jt,A[1]=Qt,A[2]=le,A[3]=Xt,Y.clearBufferuiv(Y.COLOR,0,A)):(N[0]=jt,N[1]=Qt,N[2]=le,N[3]=Xt,Y.clearBufferiv(Y.COLOR,0,N))}else nt|=Y.COLOR_BUFFER_BIT}K&&(nt|=Y.DEPTH_BUFFER_BIT,this.state.buffers.depth.setMask(!0)),at&&(nt|=Y.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),nt!==0&&Y.clear(nt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.setNodesHandler=function(C){C.setRenderer(this),j=C},this.dispose=function(){n.removeEventListener("webglcontextlost",bt,!1),n.removeEventListener("webglcontextrestored",Yt,!1),n.removeEventListener("webglcontextcreationerror",ne,!1),Dt.dispose(),ht.dispose(),Ot.dispose(),P.dispose(),J.dispose(),wt.dispose(),At.dispose(),mt.dispose(),Pt.dispose(),Ut.dispose(),Ut.removeEventListener("sessionstart",No),Ut.removeEventListener("sessionend",Lo),zn.stop()};function bt(C){C.preventDefault(),Fx("WebGLRenderer: Context Lost."),F=!0}function Yt(){Fx("WebGLRenderer: Context Restored."),F=!1;const C=$e.autoReset,K=Lt.enabled,at=Lt.autoUpdate,nt=Lt.needsUpdate,it=Lt.type;zt(),$e.autoReset=C,Lt.enabled=K,Lt.autoUpdate=at,Lt.needsUpdate=nt,Lt.type=it}function ne(C){Te("WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function sn(C){const K=C.target;K.removeEventListener("dispose",sn),we(K)}function we(C){xi(C),P.remove(C)}function xi(C){const K=P.get(C).programs;K!==void 0&&(K.forEach(function(at){Pt.releaseProgram(at)}),C.isShaderMaterial&&Pt.releaseShaderCache(C))}this.renderBufferDirect=function(C,K,at,nt,it,It){K===null&&(K=cn);const kt=it.isMesh&&it.matrixWorld.determinant()<0,Bt=qa(C,K,at,nt,it);Ct.setMaterial(nt,kt);let Xt=at.index,jt=1;if(nt.wireframe===!0){if(Xt=Et.getWireframeAttribute(at),Xt===void 0)return;jt=2}const Qt=at.drawRange,le=at.attributes.position;let Zt=Qt.start*jt,Ae=(Qt.start+Qt.count)*jt;It!==null&&(Zt=Math.max(Zt,It.start*jt),Ae=Math.min(Ae,(It.start+It.count)*jt)),Xt!==null?(Zt=Math.max(Zt,0),Ae=Math.min(Ae,Xt.count)):le!=null&&(Zt=Math.max(Zt,0),Ae=Math.min(Ae,le.count));const tn=Ae-Zt;if(tn<0||tn===1/0)return;At.setup(it,nt,Bt,at,Xt);let We,Pe=se;if(Xt!==null&&(We=_t.get(Xt),Pe=me,Pe.setIndex(We)),it.isMesh)nt.wireframe===!0?(Ct.setLineWidth(nt.wireframeLinewidth*Dn()),Pe.setMode(Y.LINES)):Pe.setMode(Y.TRIANGLES);else if(it.isLine){let Oe=nt.linewidth;Oe===void 0&&(Oe=1),Ct.setLineWidth(Oe*Dn()),it.isLineSegments?Pe.setMode(Y.LINES):it.isLineLoop?Pe.setMode(Y.LINE_LOOP):Pe.setMode(Y.LINE_STRIP)}else it.isPoints?Pe.setMode(Y.POINTS):it.isSprite&&Pe.setMode(Y.TRIANGLES);if(it.isBatchedMesh)if(pe.get("WEBGL_multi_draw"))Pe.renderMultiDraw(it._multiDrawStarts,it._multiDrawCounts,it._multiDrawCount);else{const Oe=it._multiDrawStarts,Gt=it._multiDrawCounts,Vn=it._multiDrawCount,ge=Xt?_t.get(Xt).bytesPerElement:1,bn=P.get(nt).currentProgram.getUniforms();for(let ri=0;ri<Vn;ri++)bn.setValue(Y,"_gl_DrawID",ri),Pe.render(Oe[ri]/ge,Gt[ri])}else if(it.isInstancedMesh)Pe.renderInstances(Zt,tn,it.count);else if(at.isInstancedBufferGeometry){const Oe=at._maxInstanceCount!==void 0?at._maxInstanceCount:1/0,Gt=Math.min(at.instanceCount,Oe);Pe.renderInstances(Zt,tn,Gt)}else Pe.render(Zt,tn)};function si(C,K,at){C.transparent===!0&&C.side===Ia&&C.forceSinglePass===!1?(C.side=ii,C.needsUpdate=!0,xr(C,K,at),C.side=ws,C.needsUpdate=!0,xr(C,K,at),C.side=Ia):xr(C,K,at)}this.compile=function(C,K,at=null){at===null&&(at=C),B=Ot.get(at),B.init(K),E.push(B),at.traverseVisible(function(it){it.isLight&&it.layers.test(K.layers)&&(B.pushLight(it),it.castShadow&&B.pushShadow(it))}),C!==at&&C.traverseVisible(function(it){it.isLight&&it.layers.test(K.layers)&&(B.pushLight(it),it.castShadow&&B.pushShadow(it))}),B.setupLights();const nt=new Set;return C.traverse(function(it){if(!(it.isMesh||it.isPoints||it.isLine||it.isSprite))return;const It=it.material;if(It)if(Array.isArray(It))for(let kt=0;kt<It.length;kt++){const Bt=It[kt];si(Bt,at,it),nt.add(Bt)}else si(It,at,it),nt.add(It)}),B=E.pop(),nt},this.compileAsync=function(C,K,at=null){const nt=this.compile(C,K,at);return new Promise(it=>{function It(){if(nt.forEach(function(kt){P.get(kt).currentProgram.isReady()&&nt.delete(kt)}),nt.size===0){it(C);return}setTimeout(It,10)}pe.get("KHR_parallel_shader_compile")!==null?It():setTimeout(It,10)})};let Us=null;function Do(C){Us&&Us(C)}function No(){zn.stop()}function Lo(){zn.start()}const zn=new CM;zn.setAnimationLoop(Do),typeof self<"u"&&zn.setContext(self),this.setAnimationLoop=function(C){Us=C,Ut.setAnimationLoop(C),C===null?zn.stop():zn.start()},Ut.addEventListener("sessionstart",No),Ut.addEventListener("sessionend",Lo),this.render=function(C,K){if(K!==void 0&&K.isCamera!==!0){Te("WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(F===!0)return;j!==null&&j.renderStart(C,K);const at=Ut.enabled===!0&&Ut.isPresenting===!0,nt=U!==null&&(q===null||at)&&U.begin(V,q);if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),K.parent===null&&K.matrixWorldAutoUpdate===!0&&K.updateMatrixWorld(),Ut.enabled===!0&&Ut.isPresenting===!0&&(U===null||U.isCompositing()===!1)&&(Ut.cameraAutoUpdate===!0&&Ut.updateCamera(K),K=Ut.getCamera()),C.isScene===!0&&C.onBeforeRender(V,C,K,q),B=Ot.get(C,E.length),B.init(K),B.state.textureUnits=T.getTextureUnits(),E.push(B),xe.multiplyMatrices(K.projectionMatrix,K.matrixWorldInverse),$t.setFromProjectionMatrix(xe,ra,K.reversedDepth),he=this.localClippingEnabled,Xe=Ft.init(this.clippingPlanes,he),H=ht.get(C,O.length),H.init(),O.push(H),Ut.enabled===!0&&Ut.isPresenting===!0){const kt=V.xr.getDepthSensingMesh();kt!==null&&un(kt,K,-1/0,V.sortObjects)}un(C,K,0,V.sortObjects),H.finish(),V.sortObjects===!0&&H.sort(ot,Mt),Ze=Ut.enabled===!1||Ut.isPresenting===!1||Ut.hasDepthSensing()===!1,Ze&&Dt.addToRenderList(H,C),this.info.render.frame++,Xe===!0&&Ft.beginShadows();const it=B.state.shadowsArray;if(Lt.render(it,C,K),Xe===!0&&Ft.endShadows(),this.info.autoReset===!0&&this.info.reset(),(nt&&U.hasRenderPass())===!1){const kt=H.opaque,Bt=H.transmissive;if(B.setupLights(),K.isArrayCamera){const Xt=K.cameras;if(Bt.length>0)for(let jt=0,Qt=Xt.length;jt<Qt;jt++){const le=Xt[jt];pa(kt,Bt,C,le)}Ze&&Dt.render(C);for(let jt=0,Qt=Xt.length;jt<Qt;jt++){const le=Xt[jt];Nn(H,C,le,le.viewport)}}else Bt.length>0&&pa(kt,Bt,C,K),Ze&&Dt.render(C),Nn(H,C,K)}q!==null&&ct===0&&(T.updateMultisampleRenderTarget(q),T.updateRenderTargetMipmap(q)),nt&&U.end(V),C.isScene===!0&&C.onAfterRender(V,C,K),At.resetDefaultState(),I=-1,G=null,E.pop(),E.length>0?(B=E[E.length-1],T.setTextureUnits(B.state.textureUnits),Xe===!0&&Ft.setGlobalState(V.clippingPlanes,B.state.camera)):B=null,O.pop(),O.length>0?H=O[O.length-1]:H=null,j!==null&&j.renderEnd()};function un(C,K,at,nt){if(C.visible===!1)return;if(C.layers.test(K.layers)){if(C.isGroup)at=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(K);else if(C.isLightProbeGrid)B.pushLightProbeGrid(C);else if(C.isLight)B.pushLight(C),C.castShadow&&B.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||$t.intersectsSprite(C)){nt&&ue.setFromMatrixPosition(C.matrixWorld).applyMatrix4(xe);const kt=wt.update(C),Bt=C.material;Bt.visible&&H.push(C,kt,Bt,at,ue.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||$t.intersectsObject(C))){const kt=wt.update(C),Bt=C.material;if(nt&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),ue.copy(C.boundingSphere.center)):(kt.boundingSphere===null&&kt.computeBoundingSphere(),ue.copy(kt.boundingSphere.center)),ue.applyMatrix4(C.matrixWorld).applyMatrix4(xe)),Array.isArray(Bt)){const Xt=kt.groups;for(let jt=0,Qt=Xt.length;jt<Qt;jt++){const le=Xt[jt],Zt=Bt[le.materialIndex];Zt&&Zt.visible&&H.push(C,kt,Zt,at,ue.z,le)}}else Bt.visible&&H.push(C,kt,Bt,at,ue.z,null)}}const It=C.children;for(let kt=0,Bt=It.length;kt<Bt;kt++)un(It[kt],K,at,nt)}function Nn(C,K,at,nt){const{opaque:it,transmissive:It,transparent:kt}=C;B.setupLightsView(at),Xe===!0&&Ft.setGlobalState(V.clippingPlanes,at),nt&&Ct.viewport($.copy(nt)),it.length>0&&Xa(it,K,at),It.length>0&&Xa(It,K,at),kt.length>0&&Xa(kt,K,at),Ct.buffers.depth.setTest(!0),Ct.buffers.depth.setMask(!0),Ct.buffers.color.setMask(!0),Ct.setPolygonOffset(!1)}function pa(C,K,at,nt){if((at.isScene===!0?at.overrideMaterial:null)!==null)return;if(B.state.transmissionRenderTarget[nt.id]===void 0){const Zt=pe.has("EXT_color_buffer_half_float")||pe.has("EXT_color_buffer_float");B.state.transmissionRenderTarget[nt.id]=new la(1,1,{generateMipmaps:!0,type:Zt?Ga:Ni,minFilter:or,samples:Math.max(4,Ve.samples),stencilBuffer:c,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:be.workingColorSpace})}const It=B.state.transmissionRenderTarget[nt.id],kt=nt.viewport||$;It.setSize(kt.z*V.transmissionResolutionScale,kt.w*V.transmissionResolutionScale);const Bt=V.getRenderTarget(),Xt=V.getActiveCubeFace(),jt=V.getActiveMipmapLevel();V.setRenderTarget(It),V.getClearColor(z),Q=V.getClearAlpha(),Q<1&&V.setClearColor(16777215,.5),V.clear(),Ze&&Dt.render(at);const Qt=V.toneMapping;V.toneMapping=oa;const le=nt.viewport;if(nt.viewport!==void 0&&(nt.viewport=void 0),B.setupLightsView(nt),Xe===!0&&Ft.setGlobalState(V.clippingPlanes,nt),Xa(C,at,nt),T.updateMultisampleRenderTarget(It),T.updateRenderTargetMipmap(It),pe.has("WEBGL_multisampled_render_to_texture")===!1){let Zt=!1;for(let Ae=0,tn=K.length;Ae<tn;Ae++){const We=K[Ae],{object:Pe,geometry:Oe,material:Gt,group:Vn}=We;if(Gt.side===Ia&&Pe.layers.test(nt.layers)){const ge=Gt.side;Gt.side=ii,Gt.needsUpdate=!0,tc(Pe,at,nt,Oe,Gt,Vn),Gt.side=ge,Gt.needsUpdate=!0,Zt=!0}}Zt===!0&&(T.updateMultisampleRenderTarget(It),T.updateRenderTargetMipmap(It))}V.setRenderTarget(Bt,Xt,jt),V.setClearColor(z,Q),le!==void 0&&(nt.viewport=le),V.toneMapping=Qt}function Xa(C,K,at){const nt=K.isScene===!0?K.overrideMaterial:null;for(let it=0,It=C.length;it<It;it++){const kt=C[it],{object:Bt,geometry:Xt,group:jt}=kt;let Qt=kt.material;Qt.allowOverride===!0&&nt!==null&&(Qt=nt),Bt.layers.test(at.layers)&&tc(Bt,K,at,Xt,Qt,jt)}}function tc(C,K,at,nt,it,It){C.onBeforeRender(V,K,at,nt,it,It),C.modelViewMatrix.multiplyMatrices(at.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),it.onBeforeRender(V,K,at,nt,C,It),it.transparent===!0&&it.side===Ia&&it.forceSinglePass===!1?(it.side=ii,it.needsUpdate=!0,V.renderBufferDirect(at,K,nt,it,C,It),it.side=ws,it.needsUpdate=!0,V.renderBufferDirect(at,K,nt,it,C,It),it.side=Ia):V.renderBufferDirect(at,K,nt,it,C,It),C.onAfterRender(V,K,at,nt,it,It)}function xr(C,K,at){K.isScene!==!0&&(K=cn);const nt=P.get(C),it=B.state.lights,It=B.state.shadowsArray,kt=it.state.version,Bt=Pt.getParameters(C,it.state,It,K,at,B.state.lightProbeGridArray),Xt=Pt.getProgramCacheKey(Bt);let jt=nt.programs;nt.environment=C.isMeshStandardMaterial||C.isMeshLambertMaterial||C.isMeshPhongMaterial?K.environment:null,nt.fog=K.fog;const Qt=C.isMeshStandardMaterial||C.isMeshLambertMaterial&&!C.envMap||C.isMeshPhongMaterial&&!C.envMap;nt.envMap=J.get(C.envMap||nt.environment,Qt),nt.envMapRotation=nt.environment!==null&&C.envMap===null?K.environmentRotation:C.envMapRotation,jt===void 0&&(C.addEventListener("dispose",sn),jt=new Map,nt.programs=jt);let le=jt.get(Xt);if(le!==void 0){if(nt.currentProgram===le&&nt.lightsStateVersion===kt)return Wa(C,Bt),le}else Bt.uniforms=Pt.getUniforms(C),j!==null&&C.isNodeMaterial&&j.build(C,at,Bt),C.onBeforeCompile(Bt,V),le=Pt.acquireProgram(Bt,Xt),jt.set(Xt,le),nt.uniforms=Bt.uniforms;const Zt=nt.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Zt.clippingPlanes=Ft.uniform),Wa(C,Bt),nt.needsLights=Ps(C),nt.lightsStateVersion=kt,nt.needsLights&&(Zt.ambientLightColor.value=it.state.ambient,Zt.lightProbe.value=it.state.probe,Zt.directionalLights.value=it.state.directional,Zt.directionalLightShadows.value=it.state.directionalShadow,Zt.spotLights.value=it.state.spot,Zt.spotLightShadows.value=it.state.spotShadow,Zt.rectAreaLights.value=it.state.rectArea,Zt.ltc_1.value=it.state.rectAreaLTC1,Zt.ltc_2.value=it.state.rectAreaLTC2,Zt.pointLights.value=it.state.point,Zt.pointLightShadows.value=it.state.pointShadow,Zt.hemisphereLights.value=it.state.hemi,Zt.directionalShadowMatrix.value=it.state.directionalShadowMatrix,Zt.spotLightMatrix.value=it.state.spotLightMatrix,Zt.spotLightMap.value=it.state.spotLightMap,Zt.pointShadowMatrix.value=it.state.pointShadowMatrix),nt.lightProbeGrid=B.state.lightProbeGridArray.length>0,nt.currentProgram=le,nt.uniformsList=null,le}function Uo(C){if(C.uniformsList===null){const K=C.currentProgram.getUniforms();C.uniformsList=ju.seqWithValue(K.seq,C.uniforms)}return C.uniformsList}function Wa(C,K){const at=P.get(C);at.outputColorSpace=K.outputColorSpace,at.batching=K.batching,at.batchingColor=K.batchingColor,at.instancing=K.instancing,at.instancingColor=K.instancingColor,at.instancingMorph=K.instancingMorph,at.skinning=K.skinning,at.morphTargets=K.morphTargets,at.morphNormals=K.morphNormals,at.morphColors=K.morphColors,at.morphTargetsCount=K.morphTargetsCount,at.numClippingPlanes=K.numClippingPlanes,at.numIntersection=K.numClipIntersection,at.vertexAlphas=K.vertexAlphas,at.vertexTangents=K.vertexTangents,at.toneMapping=K.toneMapping}function Po(C,K){if(C.length===0)return null;if(C.length===1)return C[0].texture!==null?C[0]:null;L.setFromMatrixPosition(K.matrixWorld);for(let at=0,nt=C.length;at<nt;at++){const it=C[at];if(it.texture!==null&&it.boundingBox.containsPoint(L))return it}return null}function qa(C,K,at,nt,it){K.isScene!==!0&&(K=cn),T.resetTextureUnits();const It=K.fog,kt=nt.isMeshStandardMaterial||nt.isMeshLambertMaterial||nt.isMeshPhongMaterial?K.environment:null,Bt=q===null?V.outputColorSpace:q.isXRRenderTarget===!0?q.texture.colorSpace:be.workingColorSpace,Xt=nt.isMeshStandardMaterial||nt.isMeshLambertMaterial&&!nt.envMap||nt.isMeshPhongMaterial&&!nt.envMap,jt=J.get(nt.envMap||kt,Xt),Qt=nt.vertexColors===!0&&!!at.attributes.color&&at.attributes.color.itemSize===4,le=!!at.attributes.tangent&&(!!nt.normalMap||nt.anisotropy>0),Zt=!!at.morphAttributes.position,Ae=!!at.morphAttributes.normal,tn=!!at.morphAttributes.color;let We=oa;nt.toneMapped&&(q===null||q.isXRRenderTarget===!0)&&(We=V.toneMapping);const Pe=at.morphAttributes.position||at.morphAttributes.normal||at.morphAttributes.color,Oe=Pe!==void 0?Pe.length:0,Gt=P.get(nt),Vn=B.state.lights;if(Xe===!0&&(he===!0||C!==G)){const Ne=C===G&&nt.id===I;Ft.setState(nt,C,Ne)}let ge=!1;nt.version===Gt.__version?(Gt.needsLights&&Gt.lightsStateVersion!==Vn.state.version||Gt.outputColorSpace!==Bt||it.isBatchedMesh&&Gt.batching===!1||!it.isBatchedMesh&&Gt.batching===!0||it.isBatchedMesh&&Gt.batchingColor===!0&&it.colorTexture===null||it.isBatchedMesh&&Gt.batchingColor===!1&&it.colorTexture!==null||it.isInstancedMesh&&Gt.instancing===!1||!it.isInstancedMesh&&Gt.instancing===!0||it.isSkinnedMesh&&Gt.skinning===!1||!it.isSkinnedMesh&&Gt.skinning===!0||it.isInstancedMesh&&Gt.instancingColor===!0&&it.instanceColor===null||it.isInstancedMesh&&Gt.instancingColor===!1&&it.instanceColor!==null||it.isInstancedMesh&&Gt.instancingMorph===!0&&it.morphTexture===null||it.isInstancedMesh&&Gt.instancingMorph===!1&&it.morphTexture!==null||Gt.envMap!==jt||nt.fog===!0&&Gt.fog!==It||Gt.numClippingPlanes!==void 0&&(Gt.numClippingPlanes!==Ft.numPlanes||Gt.numIntersection!==Ft.numIntersection)||Gt.vertexAlphas!==Qt||Gt.vertexTangents!==le||Gt.morphTargets!==Zt||Gt.morphNormals!==Ae||Gt.morphColors!==tn||Gt.toneMapping!==We||Gt.morphTargetsCount!==Oe||!!Gt.lightProbeGrid!=B.state.lightProbeGridArray.length>0)&&(ge=!0):(ge=!0,Gt.__version=nt.version);let bn=Gt.currentProgram;ge===!0&&(bn=xr(nt,K,it),j&&nt.isNodeMaterial&&j.onUpdateProgram(nt,bn,Gt));let ri=!1,Pi=!1,oi=!1;const Fe=bn.getUniforms(),en=Gt.uniforms;if(Ct.useProgram(bn.program)&&(ri=!0,Pi=!0,oi=!0),nt.id!==I&&(I=nt.id,Pi=!0),Gt.needsLights){const Ne=Po(B.state.lightProbeGridArray,it);Gt.lightProbeGrid!==Ne&&(Gt.lightProbeGrid=Ne,Pi=!0)}if(ri||G!==C){Ct.buffers.depth.getReversed()&&C.reversedDepth!==!0&&(C._reversedDepth=!0,C.updateProjectionMatrix()),Fe.setValue(Y,"projectionMatrix",C.projectionMatrix),Fe.setValue(Y,"viewMatrix",C.matrixWorldInverse);const Ki=Fe.map.cameraPosition;Ki!==void 0&&Ki.setValue(Y,Ue.setFromMatrixPosition(C.matrixWorld)),Ve.logarithmicDepthBuffer&&Fe.setValue(Y,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(nt.isMeshPhongMaterial||nt.isMeshToonMaterial||nt.isMeshLambertMaterial||nt.isMeshBasicMaterial||nt.isMeshStandardMaterial||nt.isShaderMaterial)&&Fe.setValue(Y,"isOrthographic",C.isOrthographicCamera===!0),G!==C&&(G=C,Pi=!0,oi=!0)}if(Gt.needsLights&&(Vn.state.directionalShadowMap.length>0&&Fe.setValue(Y,"directionalShadowMap",Vn.state.directionalShadowMap,T),Vn.state.spotShadowMap.length>0&&Fe.setValue(Y,"spotShadowMap",Vn.state.spotShadowMap,T),Vn.state.pointShadowMap.length>0&&Fe.setValue(Y,"pointShadowMap",Vn.state.pointShadowMap,T)),it.isSkinnedMesh){Fe.setOptional(Y,it,"bindMatrix"),Fe.setOptional(Y,it,"bindMatrixInverse");const Ne=it.skeleton;Ne&&(Ne.boneTexture===null&&Ne.computeBoneTexture(),Fe.setValue(Y,"boneTexture",Ne.boneTexture,T))}it.isBatchedMesh&&(Fe.setOptional(Y,it,"batchingTexture"),Fe.setValue(Y,"batchingTexture",it._matricesTexture,T),Fe.setOptional(Y,it,"batchingIdTexture"),Fe.setValue(Y,"batchingIdTexture",it._indirectTexture,T),Fe.setOptional(Y,it,"batchingColorTexture"),it._colorsTexture!==null&&Fe.setValue(Y,"batchingColorTexture",it._colorsTexture,T));const Oi=at.morphAttributes;if((Oi.position!==void 0||Oi.normal!==void 0||Oi.color!==void 0)&&ae.update(it,at,bn),(Pi||Gt.receiveShadow!==it.receiveShadow)&&(Gt.receiveShadow=it.receiveShadow,Fe.setValue(Y,"receiveShadow",it.receiveShadow)),(nt.isMeshStandardMaterial||nt.isMeshLambertMaterial||nt.isMeshPhongMaterial)&&nt.envMap===null&&K.environment!==null&&(en.envMapIntensity.value=K.environmentIntensity),en.dfgLUT!==void 0&&(en.dfgLUT.value=J3()),Pi){if(Fe.setValue(Y,"toneMappingExposure",V.toneMappingExposure),Gt.needsLights&&Ya(en,oi),It&&nt.fog===!0&&ft.refreshFogUniforms(en,It),ft.refreshMaterialUniforms(en,nt,Nt,Rt,B.state.transmissionRenderTarget[C.id]),Gt.needsLights&&Gt.lightProbeGrid){const Ne=Gt.lightProbeGrid;en.probesSH.value=Ne.texture,en.probesMin.value.copy(Ne.boundingBox.min),en.probesMax.value.copy(Ne.boundingBox.max),en.probesResolution.value.copy(Ne.resolution)}ju.upload(Y,Uo(Gt),en,T)}if(nt.isShaderMaterial&&nt.uniformsNeedUpdate===!0&&(ju.upload(Y,Uo(Gt),en,T),nt.uniformsNeedUpdate=!1),nt.isSpriteMaterial&&Fe.setValue(Y,"center",it.center),Fe.setValue(Y,"modelViewMatrix",it.modelViewMatrix),Fe.setValue(Y,"normalMatrix",it.normalMatrix),Fe.setValue(Y,"modelMatrix",it.matrixWorld),nt.uniformsGroups!==void 0){const Ne=nt.uniformsGroups;for(let Ki=0,Za=Ne.length;Ki<Za;Ki++){const Os=Ne[Ki];mt.update(Os,bn),mt.bind(Os,bn)}}return bn}function Ya(C,K){C.ambientLightColor.needsUpdate=K,C.lightProbe.needsUpdate=K,C.directionalLights.needsUpdate=K,C.directionalLightShadows.needsUpdate=K,C.pointLights.needsUpdate=K,C.pointLightShadows.needsUpdate=K,C.spotLights.needsUpdate=K,C.spotLightShadows.needsUpdate=K,C.rectAreaLights.needsUpdate=K,C.hemisphereLights.needsUpdate=K}function Ps(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return lt},this.getActiveMipmapLevel=function(){return ct},this.getRenderTarget=function(){return q},this.setRenderTargetTextures=function(C,K,at){const nt=P.get(C);nt.__autoAllocateDepthBuffer=C.resolveDepthBuffer===!1,nt.__autoAllocateDepthBuffer===!1&&(nt.__useRenderToTexture=!1),P.get(C.texture).__webglTexture=K,P.get(C.depthTexture).__webglTexture=nt.__autoAllocateDepthBuffer?void 0:at,nt.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(C,K){const at=P.get(C);at.__webglFramebuffer=K,at.__useDefaultFramebuffer=K===void 0};const Ka=Y.createFramebuffer();this.setRenderTarget=function(C,K=0,at=0){q=C,lt=K,ct=at;let nt=null,it=!1,It=!1;if(C){const Bt=P.get(C);if(Bt.__useDefaultFramebuffer!==void 0){Ct.bindFramebuffer(Y.FRAMEBUFFER,Bt.__webglFramebuffer),$.copy(C.viewport),dt.copy(C.scissor),xt=C.scissorTest,Ct.viewport($),Ct.scissor(dt),Ct.setScissorTest(xt),I=-1;return}else if(Bt.__webglFramebuffer===void 0)T.setupRenderTarget(C);else if(Bt.__hasExternalTextures)T.rebindTextures(C,P.get(C.texture).__webglTexture,P.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const Qt=C.depthTexture;if(Bt.__boundDepthTexture!==Qt){if(Qt!==null&&P.has(Qt)&&(C.width!==Qt.image.width||C.height!==Qt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");T.setupDepthRenderbuffer(C)}}const Xt=C.texture;(Xt.isData3DTexture||Xt.isDataArrayTexture||Xt.isCompressedArrayTexture)&&(It=!0);const jt=P.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(jt[K])?nt=jt[K][at]:nt=jt[K],it=!0):C.samples>0&&T.useMultisampledRTT(C)===!1?nt=P.get(C).__webglMultisampledFramebuffer:Array.isArray(jt)?nt=jt[at]:nt=jt,$.copy(C.viewport),dt.copy(C.scissor),xt=C.scissorTest}else $.copy(Tt).multiplyScalar(Nt).floor(),dt.copy(Ht).multiplyScalar(Nt).floor(),xt=ee;if(at!==0&&(nt=Ka),Ct.bindFramebuffer(Y.FRAMEBUFFER,nt)&&Ct.drawBuffers(C,nt),Ct.viewport($),Ct.scissor(dt),Ct.setScissorTest(xt),it){const Bt=P.get(C.texture);Y.framebufferTexture2D(Y.FRAMEBUFFER,Y.COLOR_ATTACHMENT0,Y.TEXTURE_CUBE_MAP_POSITIVE_X+K,Bt.__webglTexture,at)}else if(It){const Bt=K;for(let Xt=0;Xt<C.textures.length;Xt++){const jt=P.get(C.textures[Xt]);Y.framebufferTextureLayer(Y.FRAMEBUFFER,Y.COLOR_ATTACHMENT0+Xt,jt.__webglTexture,at,Bt)}}else if(C!==null&&at!==0){const Bt=P.get(C.texture);Y.framebufferTexture2D(Y.FRAMEBUFFER,Y.COLOR_ATTACHMENT0,Y.TEXTURE_2D,Bt.__webglTexture,at)}I=-1},this.readRenderTargetPixels=function(C,K,at,nt,it,It,kt,Bt=0){if(!(C&&C.isWebGLRenderTarget)){Te("WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Xt=P.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&kt!==void 0&&(Xt=Xt[kt]),Xt){Ct.bindFramebuffer(Y.FRAMEBUFFER,Xt);try{const jt=C.textures[Bt],Qt=jt.format,le=jt.type;if(C.textures.length>1&&Y.readBuffer(Y.COLOR_ATTACHMENT0+Bt),!Ve.textureFormatReadable(Qt)){Te("WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Ve.textureTypeReadable(le)){Te("WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}K>=0&&K<=C.width-nt&&at>=0&&at<=C.height-it&&Y.readPixels(K,at,nt,it,X.convert(Qt),X.convert(le),It)}finally{const jt=q!==null?P.get(q).__webglFramebuffer:null;Ct.bindFramebuffer(Y.FRAMEBUFFER,jt)}}},this.readRenderTargetPixelsAsync=async function(C,K,at,nt,it,It,kt,Bt=0){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Xt=P.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&kt!==void 0&&(Xt=Xt[kt]),Xt)if(K>=0&&K<=C.width-nt&&at>=0&&at<=C.height-it){Ct.bindFramebuffer(Y.FRAMEBUFFER,Xt);const jt=C.textures[Bt],Qt=jt.format,le=jt.type;if(C.textures.length>1&&Y.readBuffer(Y.COLOR_ATTACHMENT0+Bt),!Ve.textureFormatReadable(Qt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Ve.textureTypeReadable(le))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const Zt=Y.createBuffer();Y.bindBuffer(Y.PIXEL_PACK_BUFFER,Zt),Y.bufferData(Y.PIXEL_PACK_BUFFER,It.byteLength,Y.STREAM_READ),Y.readPixels(K,at,nt,it,X.convert(Qt),X.convert(le),0);const Ae=q!==null?P.get(q).__webglFramebuffer:null;Ct.bindFramebuffer(Y.FRAMEBUFFER,Ae);const tn=Y.fenceSync(Y.SYNC_GPU_COMMANDS_COMPLETE,0);return Y.flush(),await SA(Y,tn,4),Y.bindBuffer(Y.PIXEL_PACK_BUFFER,Zt),Y.getBufferSubData(Y.PIXEL_PACK_BUFFER,0,It),Y.deleteBuffer(Zt),Y.deleteSync(tn),It}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(C,K=null,at=0){const nt=Math.pow(2,-at),it=Math.floor(C.image.width*nt),It=Math.floor(C.image.height*nt),kt=K!==null?K.x:0,Bt=K!==null?K.y:0;T.setTexture2D(C,0),Y.copyTexSubImage2D(Y.TEXTURE_2D,at,0,0,kt,Bt,it,It),Ct.unbindTexture()};const pn=Y.createFramebuffer(),ec=Y.createFramebuffer();this.copyTextureToTexture=function(C,K,at=null,nt=null,it=0,It=0){let kt,Bt,Xt,jt,Qt,le,Zt,Ae,tn;const We=C.isCompressedTexture?C.mipmaps[It]:C.image;if(at!==null)kt=at.max.x-at.min.x,Bt=at.max.y-at.min.y,Xt=at.isBox3?at.max.z-at.min.z:1,jt=at.min.x,Qt=at.min.y,le=at.isBox3?at.min.z:0;else{const en=Math.pow(2,-it);kt=Math.floor(We.width*en),Bt=Math.floor(We.height*en),C.isDataArrayTexture?Xt=We.depth:C.isData3DTexture?Xt=Math.floor(We.depth*en):Xt=1,jt=0,Qt=0,le=0}nt!==null?(Zt=nt.x,Ae=nt.y,tn=nt.z):(Zt=0,Ae=0,tn=0);const Pe=X.convert(K.format),Oe=X.convert(K.type);let Gt;K.isData3DTexture?(T.setTexture3D(K,0),Gt=Y.TEXTURE_3D):K.isDataArrayTexture||K.isCompressedArrayTexture?(T.setTexture2DArray(K,0),Gt=Y.TEXTURE_2D_ARRAY):(T.setTexture2D(K,0),Gt=Y.TEXTURE_2D),Ct.activeTexture(Y.TEXTURE0),Ct.pixelStorei(Y.UNPACK_FLIP_Y_WEBGL,K.flipY),Ct.pixelStorei(Y.UNPACK_PREMULTIPLY_ALPHA_WEBGL,K.premultiplyAlpha),Ct.pixelStorei(Y.UNPACK_ALIGNMENT,K.unpackAlignment);const Vn=Ct.getParameter(Y.UNPACK_ROW_LENGTH),ge=Ct.getParameter(Y.UNPACK_IMAGE_HEIGHT),bn=Ct.getParameter(Y.UNPACK_SKIP_PIXELS),ri=Ct.getParameter(Y.UNPACK_SKIP_ROWS),Pi=Ct.getParameter(Y.UNPACK_SKIP_IMAGES);Ct.pixelStorei(Y.UNPACK_ROW_LENGTH,We.width),Ct.pixelStorei(Y.UNPACK_IMAGE_HEIGHT,We.height),Ct.pixelStorei(Y.UNPACK_SKIP_PIXELS,jt),Ct.pixelStorei(Y.UNPACK_SKIP_ROWS,Qt),Ct.pixelStorei(Y.UNPACK_SKIP_IMAGES,le);const oi=C.isDataArrayTexture||C.isData3DTexture,Fe=K.isDataArrayTexture||K.isData3DTexture;if(C.isDepthTexture){const en=P.get(C),Oi=P.get(K),Ne=P.get(en.__renderTarget),Ki=P.get(Oi.__renderTarget);Ct.bindFramebuffer(Y.READ_FRAMEBUFFER,Ne.__webglFramebuffer),Ct.bindFramebuffer(Y.DRAW_FRAMEBUFFER,Ki.__webglFramebuffer);for(let Za=0;Za<Xt;Za++)oi&&(Y.framebufferTextureLayer(Y.READ_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,P.get(C).__webglTexture,it,le+Za),Y.framebufferTextureLayer(Y.DRAW_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,P.get(K).__webglTexture,It,tn+Za)),Y.blitFramebuffer(jt,Qt,kt,Bt,Zt,Ae,kt,Bt,Y.DEPTH_BUFFER_BIT,Y.NEAREST);Ct.bindFramebuffer(Y.READ_FRAMEBUFFER,null),Ct.bindFramebuffer(Y.DRAW_FRAMEBUFFER,null)}else if(it!==0||C.isRenderTargetTexture||P.has(C)){const en=P.get(C),Oi=P.get(K);Ct.bindFramebuffer(Y.READ_FRAMEBUFFER,pn),Ct.bindFramebuffer(Y.DRAW_FRAMEBUFFER,ec);for(let Ne=0;Ne<Xt;Ne++)oi?Y.framebufferTextureLayer(Y.READ_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,en.__webglTexture,it,le+Ne):Y.framebufferTexture2D(Y.READ_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,Y.TEXTURE_2D,en.__webglTexture,it),Fe?Y.framebufferTextureLayer(Y.DRAW_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,Oi.__webglTexture,It,tn+Ne):Y.framebufferTexture2D(Y.DRAW_FRAMEBUFFER,Y.COLOR_ATTACHMENT0,Y.TEXTURE_2D,Oi.__webglTexture,It),it!==0?Y.blitFramebuffer(jt,Qt,kt,Bt,Zt,Ae,kt,Bt,Y.COLOR_BUFFER_BIT,Y.NEAREST):Fe?Y.copyTexSubImage3D(Gt,It,Zt,Ae,tn+Ne,jt,Qt,kt,Bt):Y.copyTexSubImage2D(Gt,It,Zt,Ae,jt,Qt,kt,Bt);Ct.bindFramebuffer(Y.READ_FRAMEBUFFER,null),Ct.bindFramebuffer(Y.DRAW_FRAMEBUFFER,null)}else Fe?C.isDataTexture||C.isData3DTexture?Y.texSubImage3D(Gt,It,Zt,Ae,tn,kt,Bt,Xt,Pe,Oe,We.data):K.isCompressedArrayTexture?Y.compressedTexSubImage3D(Gt,It,Zt,Ae,tn,kt,Bt,Xt,Pe,We.data):Y.texSubImage3D(Gt,It,Zt,Ae,tn,kt,Bt,Xt,Pe,Oe,We):C.isDataTexture?Y.texSubImage2D(Y.TEXTURE_2D,It,Zt,Ae,kt,Bt,Pe,Oe,We.data):C.isCompressedTexture?Y.compressedTexSubImage2D(Y.TEXTURE_2D,It,Zt,Ae,We.width,We.height,Pe,We.data):Y.texSubImage2D(Y.TEXTURE_2D,It,Zt,Ae,kt,Bt,Pe,Oe,We);Ct.pixelStorei(Y.UNPACK_ROW_LENGTH,Vn),Ct.pixelStorei(Y.UNPACK_IMAGE_HEIGHT,ge),Ct.pixelStorei(Y.UNPACK_SKIP_PIXELS,bn),Ct.pixelStorei(Y.UNPACK_SKIP_ROWS,ri),Ct.pixelStorei(Y.UNPACK_SKIP_IMAGES,Pi),It===0&&K.generateMipmaps&&Y.generateMipmap(Gt),Ct.unbindTexture()},this.initRenderTarget=function(C){P.get(C).__webglFramebuffer===void 0&&T.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?T.setTextureCube(C,0):C.isData3DTexture?T.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?T.setTexture2DArray(C,0):T.setTexture2D(C,0),Ct.unbindTexture()},this.resetState=function(){lt=0,ct=0,q=null,Ct.reset(),At.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return ra}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const n=this.getContext();n.drawingBufferColorSpace=be._getDrawingBufferColorSpace(t),n.unpackColorSpace=be._getUnpackColorSpace()}}function _i(...i){return i.filter(Boolean).join(" ")}function Ry({className:i}){const t=yt.useRef(null);return yt.useEffect(()=>{const n=t.current;if(!n)return;const s=new BA;s.fog=new rg(1118481,1400,6600);const o=new Di(60,1,1,8e3);o.position.set(0,330,1180);const c=new $3({alpha:!0,antialias:!0,powerPreference:"high-performance"});c.setPixelRatio(Math.min(window.devicePixelRatio,2)),c.setClearColor(1118481,0),n.appendChild(c.domElement);const u=150,d=42,p=54,h=[],g=[],_=new Yi;for(let N=0;N<d;N+=1)for(let L=0;L<p;L+=1)h.push(N*u-d*u/2,0,L*u-p*u/2),g.push(.58,.58,.58);_.setAttribute("position",new Wi(h,3)),_.setAttribute("color",new Wi(g,3));const v=new MM({size:7,vertexColors:!0,transparent:!0,opacity:.26,sizeAttenuation:!0}),y=new qA(_,v);s.add(y);let b=0,R=0;const S=window.matchMedia("(prefers-reduced-motion: reduce)").matches,x=()=>{const N=n.clientWidth||window.innerWidth,L=n.clientHeight||window.innerHeight;o.aspect=N/L,o.updateProjectionMatrix(),c.setSize(N,L,!1)},A=()=>{R=requestAnimationFrame(A);const N=_.attributes.position,L=N.array;let H=0;for(let B=0;B<d;B+=1)for(let O=0;O<p;O+=1){const E=H*3;L[E+1]=Math.sin((B+b)*.28)*38+Math.sin((O+b)*.44)*34,H+=1}N.needsUpdate=!0,y.rotation.x=-.08,c.render(s,o),b+=S?0:.045};return x(),A(),window.addEventListener("resize",x),()=>{window.removeEventListener("resize",x),cancelAnimationFrame(R),_.dispose(),v.dispose(),c.dispose(),c.domElement.remove()}},[]),D.jsx("div",{ref:t,className:_i("dotted-surface",i),"aria-hidden":"true"})}const tD=i=>i.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),eD=i=>i.replace(/^([A-Z])|[\s-_]+(\w)/g,(t,n,s)=>s?s.toUpperCase():n.toLowerCase()),Cy=i=>{const t=eD(i);return t.charAt(0).toUpperCase()+t.slice(1)},FM=(...i)=>i.filter((t,n,s)=>!!t&&t.trim()!==""&&s.indexOf(t)===n).join(" ").trim(),nD=i=>{for(const t in i)if(t.startsWith("aria-")||t==="role"||t==="title")return!0};var iD={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};const aD=yt.forwardRef(({color:i="currentColor",size:t=24,strokeWidth:n=2,absoluteStrokeWidth:s,className:o="",children:c,iconNode:u,...d},p)=>yt.createElement("svg",{ref:p,...iD,width:t,height:t,stroke:i,strokeWidth:s?Number(n)*24/Number(t):n,className:FM("lucide",o),...!c&&!nD(d)&&{"aria-hidden":"true"},...d},[...u.map(([h,g])=>yt.createElement(h,g)),...Array.isArray(c)?c:[c]]));const Mn=(i,t)=>{const n=yt.forwardRef(({className:s,...o},c)=>yt.createElement(aD,{ref:c,iconNode:t,className:FM(`lucide-${tD(Cy(i))}`,`lucide-${i}`,s),...o}));return n.displayName=Cy(i),n};const sD=[["path",{d:"m5 12 7-7 7 7",key:"hav0vg"}],["path",{d:"M12 19V5",key:"x0mq9r"}]],rD=Mn("arrow-up",sD);const oD=[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]],BM=Mn("check",oD);const lD=[["path",{d:"m6 9 6 6 6-6",key:"qrunsl"}]],IM=Mn("chevron-down",lD);const cD=[["path",{d:"m9 18 6-6-6-6",key:"mthhwq"}]],uD=Mn("chevron-right",cD);const fD=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]],gr=Mn("circle-alert",fD);const dD=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]],Hl=Mn("circle-check",dD);const hD=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m15 9-6 6",key:"1uzhvr"}],["path",{d:"m9 9 6 6",key:"z0biqf"}]],wy=Mn("circle-x",hD);const pD=[["path",{d:"m18 16 4-4-4-4",key:"1inbqp"}],["path",{d:"m6 8-4 4 4 4",key:"15zrgr"}],["path",{d:"m14.5 4-5 16",key:"e7oirm"}]],mD=Mn("code-xml",pD);const gD=[["rect",{width:"14",height:"14",x:"8",y:"8",rx:"2",ry:"2",key:"17jyea"}],["path",{d:"M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2",key:"zix9uf"}]],_D=Mn("copy",gD);const vD=[["ellipse",{cx:"12",cy:"5",rx:"9",ry:"3",key:"msslwz"}],["path",{d:"M3 5V19A9 3 0 0 0 21 19V5",key:"1wlel7"}],["path",{d:"M3 12A9 3 0 0 0 21 12",key:"mv7ke4"}]],xD=Mn("database",vD);const yD=[["path",{d:"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z",key:"1oefj6"}],["path",{d:"M14 2v5a1 1 0 0 0 1 1h5",key:"wfsgrz"}],["path",{d:"M10 9H8",key:"b1mrlr"}],["path",{d:"M16 13H8",key:"t4e002"}],["path",{d:"M16 17H8",key:"z1uh3a"}]],Mf=Mn("file-text",yD);const SD=[["path",{d:"M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2",key:"18mbvz"}],["path",{d:"M6.453 15h11.094",key:"3shlmq"}],["path",{d:"M8.5 2h7",key:"csnxdl"}]],MD=Mn("flask-conical",SD);const bD=[["path",{d:"M21 12a9 9 0 1 1-6.219-8.56",key:"13zald"}]],_r=Mn("loader-circle",bD);const ED=[["rect",{width:"18",height:"11",x:"3",y:"11",rx:"2",ry:"2",key:"1w4ew1"}],["path",{d:"M7 11V7a5 5 0 0 1 10 0v4",key:"fwvmzm"}]],TD=Mn("lock",ED);const AD=[["path",{d:"M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z",key:"10ikf1"}]],RD=Mn("play",AD);const CD=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]],wD=Mn("plus",CD);const DD=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],ND=Mn("search",DD);const LD=[["path",{d:"M10 5H3",key:"1qgfaw"}],["path",{d:"M12 19H3",key:"yhmn1j"}],["path",{d:"M14 3v4",key:"1sua03"}],["path",{d:"M16 17v4",key:"1q0r14"}],["path",{d:"M21 12h-9",key:"1o4lsq"}],["path",{d:"M21 19h-5",key:"1rlt1p"}],["path",{d:"M21 5h-7",key:"1oszz2"}],["path",{d:"M8 10v4",key:"tgpxqk"}],["path",{d:"M8 12H3",key:"a7s4jb"}]],UD=Mn("sliders-horizontal",LD);const PD=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],zM=Mn("sparkles",PD);const OD=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],og=Mn("x",OD),FD=[{id:"codex-supervisor",name:"本地 Codex Supervisor",description:"先生成研究计划、风险和证据要求",badge:"默认"},{id:"auto-research",name:"Auto Research",description:"自动推进到导出预检，结果保持草案层"},{id:"human-review",name:"半自动审阅",description:"每一步等待人工确认后再继续"}],BD=10,ID=50*1024*1024,Dy=200;function Ny(i){return typeof crypto<"u"&&"randomUUID"in crypto?`${i}_${crypto.randomUUID()}`:`${i}_${Date.now()}_${Math.floor(Math.random()*1e5)}`}function zD(i){if(i===0)return"0 B";const t=["B","KB","MB","GB"],n=Math.min(Math.floor(Math.log(i)/Math.log(1024)),t.length-1);return`${Number.parseFloat((i/1024**n).toFixed(1))} ${t[n]}`}function Ly(i){const t=i.split(".").pop()?.toUpperCase()||"FILE";return t.length>8?`${t.slice(0,8)}...`:t}function VM(i){const t=i.name.split(".").pop()?.toLowerCase()||"",n=new Set(["csv","json","md","txt","py","r","do","sql","yaml","yml","toml","log","tex"]);return i.type.startsWith("text/")||n.has(t)}function VD(i){return new Promise((t,n)=>{const s=new FileReader;s.onload=o=>t(o.target?.result||""),s.onerror=n,s.readAsText(i)})}function vo({children:i,label:t,disabled:n,onClick:s,className:o}){return D.jsx("button",{"aria-label":t,className:_i("icon-button",o),disabled:n,title:t,type:"button",onClick:s,children:i})}function HM({label:i,title:t,content:n,onRemove:s}){return D.jsxs("article",{className:"preview-card text-preview-card",children:[D.jsx("div",{className:"preview-card__text",children:n.slice(0,280)}),D.jsxs("div",{className:"preview-card__veil",children:[D.jsx("span",{className:"preview-card__type",children:i}),D.jsx("strong",{title:t,children:t}),D.jsxs("div",{className:"preview-card__actions",children:[D.jsx(vo,{label:"复制内容",onClick:()=>{navigator.clipboard.writeText(n)},children:D.jsx(_D,{size:14})}),D.jsx(vo,{label:"移除内容",onClick:s,children:D.jsx(og,{size:14})})]})]})]})}function HD({file:i,onRemove:t}){return VM(i.file)&&i.textContent?D.jsx(HM,{label:Ly(i.file.name),title:i.file.name,content:i.textContent,onRemove:t}):D.jsxs("article",{className:"preview-card file-preview-card",children:[D.jsx(Mf,{size:28}),D.jsxs("div",{className:"preview-card__meta",children:[D.jsx("strong",{title:i.file.name,children:i.file.name}),D.jsx("span",{children:zD(i.file.size)})]}),D.jsx("span",{className:"preview-card__type",children:Ly(i.file.name)}),D.jsxs("div",{className:"preview-card__actions",children:[i.uploadStatus==="uploading"?D.jsx(_r,{className:"spin",size:15}):null,i.uploadStatus==="error"?D.jsx(gr,{size:15}):null,D.jsx(vo,{label:"移除文件",onClick:t,children:D.jsx(og,{size:14})})]})]})}function GD({modes:i,selectedMode:t,onModeChange:n}){const[s,o]=yt.useState(!1),c=yt.useRef(null),u=i.find(d=>d.id===t)||i[0];return yt.useEffect(()=>{function d(p){c.current&&!c.current.contains(p.target)&&o(!1)}return document.addEventListener("mousedown",d),()=>document.removeEventListener("mousedown",d)},[]),D.jsxs("div",{className:"mode-selector",ref:c,children:[D.jsxs("button",{"aria-expanded":s,className:"mode-selector__trigger",type:"button",onClick:()=>o(d=>!d),children:[D.jsx("span",{children:u.name}),D.jsx(IM,{size:16})]}),s?D.jsx("div",{className:"mode-selector__menu",role:"listbox",children:i.map(d=>D.jsxs("button",{"aria-selected":d.id===t,className:"mode-selector__item",role:"option",type:"button",onClick:()=>{n(d.id),o(!1)},children:[D.jsxs("span",{children:[D.jsx("strong",{children:d.name}),D.jsx("small",{children:d.description})]}),d.badge?D.jsx("em",{children:d.badge}):null,d.id===t?D.jsx(BM,{size:16}):null]},d.id))}):null]})}function kD({onSubmit:i,onDraftChange:t,disabled:n=!1,placeholder:s="输入研究题目、数据线索或下一步任务...",maxFiles:o=BD,maxFileSize:c=ID,modes:u=FD}){const[d,p]=yt.useState(""),[h,g]=yt.useState([]),[_,v]=yt.useState([]),[y,b]=yt.useState(!1),[R,S]=yt.useState(u[0]?.id||""),x=yt.useRef(null),A=yt.useRef(null);yt.useEffect(()=>{x.current&&(x.current.style.height="auto",x.current.style.height=`${Math.min(x.current.scrollHeight,180)}px`)},[d]),yt.useEffect(()=>{t?.({message:d,fileCount:h.length,pastedCount:_.length,mode:R,hasMaterial:d.trim().length>0||h.length>0||_.length>0})},[h.length,d,t,_.length,R]);const N=yt.useCallback(U=>{if(!U||U.length===0)return;const V=Math.max(o-h.length,0),F=Array.from(U).slice(0,V).filter(j=>j.size<=c).map(j=>({id:Ny("file"),file:j,type:j.type||"application/octet-stream",uploadStatus:"uploading",uploadProgress:1}));g(j=>[...j,...F]),F.forEach(j=>{VM(j.file)?VD(j.file).then(lt=>{g(ct=>ct.map(q=>q.id===j.id?{...q,textContent:lt,uploadStatus:"complete",uploadProgress:100}:q))}).catch(()=>{g(lt=>lt.map(ct=>ct.id===j.id?{...ct,uploadStatus:"error",uploadProgress:0}:ct))}):setTimeout(()=>{g(lt=>lt.map(ct=>ct.id===j.id?{...ct,uploadStatus:"complete",uploadProgress:100}:ct))},180)})},[h.length,o,c]),L=yt.useCallback(U=>{const V=Array.from(U.clipboardData.items).filter(j=>j.kind==="file");if(V.length>0){U.preventDefault();const j=new DataTransfer;V.forEach(lt=>{const ct=lt.getAsFile();ct&&j.items.add(ct)}),N(j.files);return}const F=U.clipboardData.getData("text");F.length>Dy&&(U.preventDefault(),p(j=>`${j}${j?`
`:""}${F.slice(0,Dy)}...`),v(j=>[...j,{id:Ny("paste"),content:F,timestamp:new Date,wordCount:F.split(/\s+/).filter(Boolean).length}]))},[N]),H=yt.useCallback(U=>{U.preventDefault(),b(!1),N(U.dataTransfer.files)},[N]),B=yt.useCallback(U=>{g(V=>V.filter(F=>F.id!==U))},[]),O=!n&&(d.trim().length>0||h.length>0||_.length>0)&&h.every(U=>U.uploadStatus!=="uploading");function E(){O&&(i?.({message:d,files:h,pastedContent:_,mode:R}),p(""),g([]),v([]))}return D.jsxs("section",{"aria-label":"研究输入器",className:_i("research-input",y&&"research-input--dragging"),onDragLeave:U=>{U.preventDefault(),b(!1)},onDragOver:U=>{U.preventDefault(),b(!0)},onDrop:H,children:[y?D.jsx("div",{className:"research-input__drop",children:"松开后添加到本次研究任务"}):null,D.jsx("textarea",{"aria-label":"输入研究题目",className:"research-input__textarea",disabled:n,onChange:U=>p(U.target.value),onKeyDown:U=>{U.key==="Enter"&&!U.shiftKey&&!U.nativeEvent.isComposing&&(U.preventDefault(),E())},onPaste:L,placeholder:s,ref:x,rows:3,value:d}),(h.length>0||_.length>0)&&D.jsxs("div",{className:"research-input__previews",children:[_.map(U=>D.jsx(HM,{content:U.content,label:"PASTE",title:`${U.wordCount} 词 · ${U.timestamp.toLocaleTimeString("zh-CN",{hour:"2-digit",minute:"2-digit"})}`,onRemove:()=>v(V=>V.filter(F=>F.id!==U.id))},U.id)),h.map(U=>D.jsx(HD,{file:U,onRemove:()=>B(U.id)},U.id))]}),D.jsxs("div",{className:"research-input__footer",children:[D.jsxs("div",{className:"research-input__tools",children:[D.jsx(vo,{disabled:n||h.length>=o,label:"添加文件",onClick:()=>A.current?.click(),children:D.jsx(wD,{size:19})}),D.jsx(vo,{disabled:n,label:"任务参数",children:D.jsx(UD,{size:18})})]}),D.jsxs("div",{className:"research-input__run",children:[D.jsx(GD,{modes:u,selectedMode:R,onModeChange:S}),D.jsx(vo,{className:"send-button",disabled:!O,label:"开始研究",onClick:E,children:D.jsx(rD,{size:20})})]})]}),D.jsx("input",{className:"visually-hidden",multiple:!0,onChange:U=>{N(U.target.files),U.currentTarget.value=""},ref:A,type:"file"})]})}const GM=yt.createContext({});function jD(i){const t=yt.useRef(null);return t.current===null&&(t.current=i()),t.current}const XD=typeof window<"u",WD=XD?yt.useLayoutEffect:yt.useEffect,lg=yt.createContext(null);function cg(i,t){i.indexOf(t)===-1&&i.push(t)}function rf(i,t){const n=i.indexOf(t);n>-1&&i.splice(n,1)}const ha=(i,t,n)=>n>t?t:n<i?i:n;let ug=()=>{};const Ds={},kM=i=>/^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(i),jM=i=>typeof i=="object"&&i!==null,XM=i=>/^0[^.\s]+$/u.test(i);function WM(i){let t;return()=>(t===void 0&&(t=i()),t)}const Ui=i=>i,Zl=(...i)=>i.reduce((t,n)=>s=>n(t(s))),Gl=(i,t,n)=>{const s=t-i;return s?(n-i)/s:1};class fg{constructor(){this.subscriptions=[]}add(t){return cg(this.subscriptions,t),()=>rf(this.subscriptions,t)}notify(t,n,s){const o=this.subscriptions.length;if(o)if(o===1)this.subscriptions[0](t,n,s);else for(let c=0;c<o;c++){const u=this.subscriptions[c];u&&u(t,n,s)}}getSize(){return this.subscriptions.length}clear(){this.subscriptions.length=0}}const vi=i=>i*1e3,Li=i=>i/1e3,qM=(i,t)=>t?i*(1e3/t):0,YM=(i,t,n)=>(((1-3*n+3*t)*i+(3*n-6*t))*i+3*t)*i,qD=1e-7,YD=12;function KD(i,t,n,s,o){let c,u,d=0;do u=t+(n-t)/2,c=YM(u,s,o)-i,c>0?n=u:t=u;while(Math.abs(c)>qD&&++d<YD);return u}function Ql(i,t,n,s){if(i===t&&n===s)return Ui;const o=c=>KD(c,0,1,i,n);return c=>c===0||c===1?c:YM(o(c),t,s)}const KM=i=>t=>t<=.5?i(2*t)/2:(2-i(2*(1-t)))/2,ZM=i=>t=>1-i(1-t),QM=Ql(.33,1.53,.69,.99),dg=ZM(QM),JM=KM(dg),$M=i=>i>=1?1:(i*=2)<1?.5*dg(i):.5*(2-Math.pow(2,-10*(i-1))),hg=i=>1-Math.sin(Math.acos(i)),tb=ZM(hg),eb=KM(hg),ZD=Ql(.42,0,1,1),QD=Ql(0,0,.58,1),nb=Ql(.42,0,.58,1),JD=i=>Array.isArray(i)&&typeof i[0]!="number",ib=i=>Array.isArray(i)&&typeof i[0]=="number",$D={linear:Ui,easeIn:ZD,easeInOut:nb,easeOut:QD,circIn:hg,circInOut:eb,circOut:tb,backIn:dg,backInOut:JM,backOut:QM,anticipate:$M},tN=i=>typeof i=="string",Uy=i=>{if(ib(i)){ug(i.length===4);const[t,n,s,o]=i;return Ql(t,n,s,o)}else if(tN(i))return $D[i];return i},Ou=["setup","read","resolveKeyframes","preUpdate","update","preRender","render","postRender"];function eN(i,t){let n=new Set,s=new Set,o=!1,c=!1;const u=new WeakSet;let d={delta:0,timestamp:0,isProcessing:!1};function p(g){u.has(g)&&(h.schedule(g),i()),g(d)}const h={schedule:(g,_=!1,v=!1)=>{const b=v&&o?n:s;return _&&u.add(g),b.add(g),g},cancel:g=>{s.delete(g),u.delete(g)},process:g=>{if(d=g,o){c=!0;return}o=!0;const _=n;n=s,s=_,n.forEach(p),n.clear(),o=!1,c&&(c=!1,h.process(g))}};return h}const nN=40;function ab(i,t){let n=!1,s=!0;const o={delta:0,timestamp:0,isProcessing:!1},c=()=>n=!0,u=Ou.reduce((N,L)=>(N[L]=eN(c),N),{}),{setup:d,read:p,resolveKeyframes:h,preUpdate:g,update:_,preRender:v,render:y,postRender:b}=u,R=()=>{const N=Ds.useManualTiming,L=N?o.timestamp:performance.now();n=!1,N||(o.delta=s?1e3/60:Math.max(Math.min(L-o.timestamp,nN),1)),o.timestamp=L,o.isProcessing=!0,d.process(o),p.process(o),h.process(o),g.process(o),_.process(o),v.process(o),y.process(o),b.process(o),o.isProcessing=!1,n&&t&&(s=!1,i(R))},S=()=>{n=!0,s=!0,o.isProcessing||i(R)};return{schedule:Ou.reduce((N,L)=>{const H=u[L];return N[L]=(B,O=!1,E=!1)=>(n||S(),H.schedule(B,O,E)),N},{}),cancel:N=>{for(let L=0;L<Ou.length;L++)u[Ou[L]].cancel(N)},state:o,steps:u}}const{schedule:Ke,cancel:Ns,state:Fn,steps:mp}=ab(typeof requestAnimationFrame<"u"?requestAnimationFrame:Ui,!0);let Xu;function iN(){Xu=void 0}const qn={now:()=>(Xu===void 0&&qn.set(Fn.isProcessing||Ds.useManualTiming?Fn.timestamp:performance.now()),Xu),set:i=>{Xu=i,queueMicrotask(iN)}},sb=i=>t=>typeof t=="string"&&t.startsWith(i),rb=sb("--"),aN=sb("var(--"),pg=i=>aN(i)?sN.test(i.split("/*")[0].trim()):!1,sN=/var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;function Py(i){return typeof i!="string"?!1:i.split("/*")[0].includes("var(--")}const Ro={test:i=>typeof i=="number",parse:parseFloat,transform:i=>i},kl={...Ro,transform:i=>ha(0,1,i)},Fu={...Ro,default:1},Ol=i=>Math.round(i*1e5)/1e5,mg=/-?(?:\d+(?:\.\d+)?|\.\d+)/gu;function rN(i){return i==null}const oN=/^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu,gg=(i,t)=>n=>!!(typeof n=="string"&&oN.test(n)&&n.startsWith(i)||t&&!rN(n)&&Object.prototype.hasOwnProperty.call(n,t)),ob=(i,t,n)=>s=>{if(typeof s!="string")return s;const[o,c,u,d]=s.match(mg);return{[i]:parseFloat(o),[t]:parseFloat(c),[n]:parseFloat(u),alpha:d!==void 0?parseFloat(d):1}},lN=i=>ha(0,255,i),gp={...Ro,transform:i=>Math.round(lN(i))},cr={test:gg("rgb","red"),parse:ob("red","green","blue"),transform:({red:i,green:t,blue:n,alpha:s=1})=>"rgba("+gp.transform(i)+", "+gp.transform(t)+", "+gp.transform(n)+", "+Ol(kl.transform(s))+")"};function cN(i){let t="",n="",s="",o="";return i.length>5?(t=i.substring(1,3),n=i.substring(3,5),s=i.substring(5,7),o=i.substring(7,9)):(t=i.substring(1,2),n=i.substring(2,3),s=i.substring(3,4),o=i.substring(4,5),t+=t,n+=n,s+=s,o+=o),{red:parseInt(t,16),green:parseInt(n,16),blue:parseInt(s,16),alpha:o?parseInt(o,16)/255:1}}const Em={test:gg("#"),parse:cN,transform:cr.transform},Jl=i=>({test:t=>typeof t=="string"&&t.endsWith(i)&&t.split(" ").length===1,parse:parseFloat,transform:t=>`${t}${i}`}),Ba=Jl("deg"),ua=Jl("%"),qt=Jl("px"),uN=Jl("vh"),fN=Jl("vw"),Oy={...ua,parse:i=>ua.parse(i)/100,transform:i=>ua.transform(i*100)},ho={test:gg("hsl","hue"),parse:ob("hue","saturation","lightness"),transform:({hue:i,saturation:t,lightness:n,alpha:s=1})=>"hsla("+Math.round(i)+", "+ua.transform(Ol(t))+", "+ua.transform(Ol(n))+", "+Ol(kl.transform(s))+")"},yn={test:i=>cr.test(i)||Em.test(i)||ho.test(i),parse:i=>cr.test(i)?cr.parse(i):ho.test(i)?ho.parse(i):Em.parse(i),transform:i=>typeof i=="string"?i:i.hasOwnProperty("red")?cr.transform(i):ho.transform(i),getAnimatableNone:i=>{const t=yn.parse(i);return t.alpha=0,yn.transform(t)}},dN=/(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu;function hN(i){return isNaN(i)&&typeof i=="string"&&(i.match(mg)?.length||0)+(i.match(dN)?.length||0)>0}const lb="number",cb="color",pN="var",mN="var(",Fy="${}",gN=/var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;function bo(i){const t=i.toString(),n=[],s={color:[],number:[],var:[]},o=[];let c=0;const d=t.replace(gN,p=>(yn.test(p)?(s.color.push(c),o.push(cb),n.push(yn.parse(p))):p.startsWith(mN)?(s.var.push(c),o.push(pN),n.push(p)):(s.number.push(c),o.push(lb),n.push(parseFloat(p))),++c,Fy)).split(Fy);return{values:n,split:d,indexes:s,types:o}}function _N(i){return bo(i).values}function ub({split:i,types:t}){const n=i.length;return s=>{let o="";for(let c=0;c<n;c++)if(o+=i[c],s[c]!==void 0){const u=t[c];u===lb?o+=Ol(s[c]):u===cb?o+=yn.transform(s[c]):o+=s[c]}return o}}function vN(i){return ub(bo(i))}const xN=i=>typeof i=="number"?0:yn.test(i)?yn.getAnimatableNone(i):i,yN=(i,t)=>typeof i=="number"?t?.trim().endsWith("/")?i:0:xN(i);function SN(i){const t=bo(i);return ub(t)(t.values.map((s,o)=>yN(s,t.split[o])))}const qi={test:hN,parse:_N,createTransformer:vN,getAnimatableNone:SN};function _p(i,t,n){return n<0&&(n+=1),n>1&&(n-=1),n<1/6?i+(t-i)*6*n:n<1/2?t:n<2/3?i+(t-i)*(2/3-n)*6:i}function MN({hue:i,saturation:t,lightness:n,alpha:s}){i/=360,t/=100,n/=100;let o=0,c=0,u=0;if(!t)o=c=u=n;else{const d=n<.5?n*(1+t):n+t-n*t,p=2*n-d;o=_p(p,d,i+1/3),c=_p(p,d,i),u=_p(p,d,i-1/3)}return{red:Math.round(o*255),green:Math.round(c*255),blue:Math.round(u*255),alpha:s}}function of(i,t){return n=>n>0?t:i}const Ye=(i,t,n)=>i+(t-i)*n,vp=(i,t,n)=>{const s=i*i,o=n*(t*t-s)+s;return o<0?0:Math.sqrt(o)},bN=[Em,cr,ho],EN=i=>bN.find(t=>t.test(i));function By(i){const t=EN(i);if(!t)return!1;let n=t.parse(i);return t===ho&&(n=MN(n)),n}const Iy=(i,t)=>{const n=By(i),s=By(t);if(!n||!s)return of(i,t);const o={...n};return c=>(o.red=vp(n.red,s.red,c),o.green=vp(n.green,s.green,c),o.blue=vp(n.blue,s.blue,c),o.alpha=Ye(n.alpha,s.alpha,c),cr.transform(o))},Tm=new Set(["none","hidden"]);function TN(i,t){return Tm.has(i)?n=>n<=0?i:t:n=>n>=1?t:i}function AN(i,t){return n=>Ye(i,t,n)}function _g(i){return typeof i=="number"?AN:typeof i=="string"?pg(i)?of:yn.test(i)?Iy:wN:Array.isArray(i)?fb:typeof i=="object"?yn.test(i)?Iy:RN:of}function fb(i,t){const n=[...i],s=n.length,o=i.map((c,u)=>_g(c)(c,t[u]));return c=>{for(let u=0;u<s;u++)n[u]=o[u](c);return n}}function RN(i,t){const n={...i,...t},s={};for(const o in n)i[o]!==void 0&&t[o]!==void 0&&(s[o]=_g(i[o])(i[o],t[o]));return o=>{for(const c in s)n[c]=s[c](o);return n}}function CN(i,t){const n=[],s={color:0,var:0,number:0};for(let o=0;o<t.values.length;o++){const c=t.types[o],u=i.indexes[c][s[c]],d=i.values[u]??0;n[o]=d,s[c]++}return n}const wN=(i,t)=>{const n=qi.createTransformer(t),s=bo(i),o=bo(t);return s.indexes.var.length===o.indexes.var.length&&s.indexes.color.length===o.indexes.color.length&&s.indexes.number.length>=o.indexes.number.length?Tm.has(i)&&!o.values.length||Tm.has(t)&&!s.values.length?TN(i,t):Zl(fb(CN(s,o),o.values),n):of(i,t)};function db(i,t,n){return typeof i=="number"&&typeof t=="number"&&typeof n=="number"?Ye(i,t,n):_g(i)(i,t)}const DN=i=>{const t=({timestamp:n})=>i(n);return{start:(n=!0)=>Ke.update(t,n),stop:()=>Ns(t),now:()=>Fn.isProcessing?Fn.timestamp:qn.now()}},hb=(i,t,n=10)=>{let s="";const o=Math.max(Math.round(t/n),2);for(let c=0;c<o;c++)s+=Math.round(i(c/(o-1))*1e4)/1e4+", ";return`linear(${s.substring(0,s.length-2)})`},lf=2e4;function vg(i){let t=0;const n=50;let s=i.next(t);for(;!s.done&&t<lf;)t+=n,s=i.next(t);return t>=lf?1/0:t}function NN(i,t=100,n){const s=n({...i,keyframes:[0,t]}),o=Math.min(vg(s),lf);return{type:"keyframes",ease:c=>s.next(o*c).value/t,duration:Li(o)}}const ln={stiffness:100,damping:10,mass:1,velocity:0,duration:800,bounce:.3,visualDuration:.3,restSpeed:{granular:.01,default:2},restDelta:{granular:.005,default:.5},minDuration:.01,maxDuration:10,minDamping:.05,maxDamping:1};function Am(i,t){return i*Math.sqrt(1-t*t)}const LN=12;function UN(i,t,n){let s=n;for(let o=1;o<LN;o++)s=s-i(s)/t(s);return s}const xp=.001;function PN({duration:i=ln.duration,bounce:t=ln.bounce,velocity:n=ln.velocity,mass:s=ln.mass}){let o,c,u=1-t;u=ha(ln.minDamping,ln.maxDamping,u),i=ha(ln.minDuration,ln.maxDuration,Li(i)),u<1?(o=h=>{const g=h*u,_=g*i,v=g-n,y=Am(h,u),b=Math.exp(-_);return xp-v/y*b},c=h=>{const _=h*u*i,v=_*n+n,y=Math.pow(u,2)*Math.pow(h,2)*i,b=Math.exp(-_),R=Am(Math.pow(h,2),u);return(-o(h)+xp>0?-1:1)*((v-y)*b)/R}):(o=h=>{const g=Math.exp(-h*i),_=(h-n)*i+1;return-xp+g*_},c=h=>{const g=Math.exp(-h*i),_=(n-h)*(i*i);return g*_});const d=5/i,p=UN(o,c,d);if(i=vi(i),isNaN(p))return{stiffness:ln.stiffness,damping:ln.damping,duration:i};{const h=Math.pow(p,2)*s;return{stiffness:h,damping:u*2*Math.sqrt(s*h),duration:i}}}const ON=["duration","bounce"],FN=["stiffness","damping","mass"];function zy(i,t){return t.some(n=>i[n]!==void 0)}function BN(i){let t={velocity:ln.velocity,stiffness:ln.stiffness,damping:ln.damping,mass:ln.mass,isResolvedFromDuration:!1,...i};if(!zy(i,FN)&&zy(i,ON))if(t.velocity=0,i.visualDuration){const n=i.visualDuration,s=2*Math.PI/(n*1.2),o=s*s,c=2*ha(.05,1,1-(i.bounce||0))*Math.sqrt(o);t={...t,mass:ln.mass,stiffness:o,damping:c}}else{const n=PN({...i,velocity:0});t={...t,...n,mass:ln.mass},t.isResolvedFromDuration=!0}return t}function cf(i=ln.visualDuration,t=ln.bounce){const n=typeof i!="object"?{visualDuration:i,keyframes:[0,1],bounce:t}:i;let{restSpeed:s,restDelta:o}=n;const c=n.keyframes[0],u=n.keyframes[n.keyframes.length-1],d={done:!1,value:c},{stiffness:p,damping:h,mass:g,duration:_,velocity:v,isResolvedFromDuration:y}=BN({...n,velocity:-Li(n.velocity||0)}),b=v||0,R=h/(2*Math.sqrt(p*g)),S=u-c,x=Li(Math.sqrt(p/g)),A=Math.abs(S)<5;s||(s=A?ln.restSpeed.granular:ln.restSpeed.default),o||(o=A?ln.restDelta.granular:ln.restDelta.default);let N,L,H,B,O,E;if(R<1)H=Am(x,R),B=(b+R*x*S)/H,N=V=>{const F=Math.exp(-R*x*V);return u-F*(B*Math.sin(H*V)+S*Math.cos(H*V))},O=R*x*B+S*H,E=R*x*S-B*H,L=V=>Math.exp(-R*x*V)*(O*Math.sin(H*V)+E*Math.cos(H*V));else if(R===1){N=F=>u-Math.exp(-x*F)*(S+(b+x*S)*F);const V=b+x*S;L=F=>Math.exp(-x*F)*(x*V*F-b)}else{const V=x*Math.sqrt(R*R-1);N=ct=>{const q=Math.exp(-R*x*ct),I=Math.min(V*ct,300);return u-q*((b+R*x*S)*Math.sinh(I)+V*S*Math.cosh(I))/V};const F=(b+R*x*S)/V,j=R*x*F-S*V,lt=R*x*S-F*V;L=ct=>{const q=Math.exp(-R*x*ct),I=Math.min(V*ct,300);return q*(j*Math.sinh(I)+lt*Math.cosh(I))}}const U={calculatedDuration:y&&_||null,velocity:V=>vi(L(V)),next:V=>{if(!y&&R<1){const j=Math.exp(-R*x*V),lt=Math.sin(H*V),ct=Math.cos(H*V),q=u-j*(B*lt+S*ct),I=vi(j*(O*lt+E*ct));return d.done=Math.abs(I)<=s&&Math.abs(u-q)<=o,d.value=d.done?u:q,d}const F=N(V);if(y)d.done=V>=_;else{const j=vi(L(V));d.done=Math.abs(j)<=s&&Math.abs(u-F)<=o}return d.value=d.done?u:F,d},toString:()=>{const V=Math.min(vg(U),lf),F=hb(j=>U.next(V*j).value,V,30);return V+"ms "+F},toTransition:()=>{}};return U}cf.applyToOptions=i=>{const t=NN(i,100,cf);return i.ease=t.ease,i.duration=vi(t.duration),i.type="keyframes",i};const IN=5;function pb(i,t,n){const s=Math.max(t-IN,0);return qM(n-i(s),t-s)}function Rm({keyframes:i,velocity:t=0,power:n=.8,timeConstant:s=325,bounceDamping:o=10,bounceStiffness:c=500,modifyTarget:u,min:d,max:p,restDelta:h=.5,restSpeed:g}){const _=i[0],v={done:!1,value:_},y=E=>d!==void 0&&E<d||p!==void 0&&E>p,b=E=>d===void 0?p:p===void 0||Math.abs(d-E)<Math.abs(p-E)?d:p;let R=n*t;const S=_+R,x=u===void 0?S:u(S);x!==S&&(R=x-_);const A=E=>-R*Math.exp(-E/s),N=E=>x+A(E),L=E=>{const U=A(E),V=N(E);v.done=Math.abs(U)<=h,v.value=v.done?x:V};let H,B;const O=E=>{y(v.value)&&(H=E,B=cf({keyframes:[v.value,b(v.value)],velocity:pb(N,E,v.value),damping:o,stiffness:c,restDelta:h,restSpeed:g}))};return O(0),{calculatedDuration:null,next:E=>{let U=!1;return!B&&H===void 0&&(U=!0,L(E),O(E)),H!==void 0&&E>=H?B.next(E-H):(!U&&L(E),v)}}}function zN(i,t,n){const s=[],o=n||Ds.mix||db,c=i.length-1;for(let u=0;u<c;u++){let d=o(i[u],i[u+1]);if(t){const p=Array.isArray(t)?t[u]||Ui:t;d=Zl(p,d)}s.push(d)}return s}function VN(i,t,{clamp:n=!0,ease:s,mixer:o}={}){const c=i.length;if(ug(c===t.length),c===1)return()=>t[0];if(c===2&&t[0]===t[1])return()=>t[1];const u=i[0]===i[1];i[0]>i[c-1]&&(i=[...i].reverse(),t=[...t].reverse());const d=zN(t,s,o),p=d.length,h=g=>{if(u&&g<i[0])return t[0];let _=0;if(p>1)for(;_<i.length-2&&!(g<i[_+1]);_++);const v=Gl(i[_],i[_+1],g);return d[_](v)};return n?g=>h(ha(i[0],i[c-1],g)):h}function HN(i,t){const n=i[i.length-1];for(let s=1;s<=t;s++){const o=Gl(0,t,s);i.push(Ye(n,1,o))}}function GN(i){const t=[0];return HN(t,i.length-1),t}function kN(i,t){return i.map(n=>n*t)}function jN(i,t){return i.map(()=>t||nb).splice(0,i.length-1)}function Fl({duration:i=300,keyframes:t,times:n,ease:s="easeInOut"}){const o=JD(s)?s.map(Uy):Uy(s),c={done:!1,value:t[0]},u=kN(n&&n.length===t.length?n:GN(t),i),d=VN(u,t,{ease:Array.isArray(o)?o:jN(t,o)});return{calculatedDuration:i,next:p=>(c.value=d(p),c.done=p>=i,c)}}const XN=i=>i!==null;function bf(i,{repeat:t,repeatType:n="loop"},s,o=1){const c=i.filter(XN),d=o<0||t&&n!=="loop"&&t%2===1?0:c.length-1;return!d||s===void 0?c[d]:s}const WN={decay:Rm,inertia:Rm,tween:Fl,keyframes:Fl,spring:cf};function mb(i){typeof i.type=="string"&&(i.type=WN[i.type])}class xg{constructor(){this.updateFinished()}get finished(){return this._finished}updateFinished(){this._finished=new Promise(t=>{this.resolve=t})}notifyFinished(){this.resolve()}then(t,n){return this.finished.then(t,n)}}const qN=i=>i/100;class uf extends xg{constructor(t){super(),this.state="idle",this.startTime=null,this.isStopped=!1,this.currentTime=0,this.holdTime=null,this.playbackSpeed=1,this.delayState={done:!1,value:void 0},this.stop=()=>{const{motionValue:n}=this.options;n&&n.updatedAt!==qn.now()&&this.tick(qn.now()),this.isStopped=!0,this.state!=="idle"&&(this.teardown(),this.options.onStop?.())},this.options=t,this.initAnimation(),this.play(),t.autoplay===!1&&this.pause()}initAnimation(){const{options:t}=this;mb(t);const{type:n=Fl,repeat:s=0,repeatDelay:o=0,repeatType:c,velocity:u=0}=t;let{keyframes:d}=t;const p=n||Fl;p!==Fl&&typeof d[0]!="number"&&(this.mixKeyframes=Zl(qN,db(d[0],d[1])),d=[0,100]);const h=p({...t,keyframes:d});c==="mirror"&&(this.mirroredGenerator=p({...t,keyframes:[...d].reverse(),velocity:-u})),h.calculatedDuration===null&&(h.calculatedDuration=vg(h));const{calculatedDuration:g}=h;this.calculatedDuration=g,this.resolvedDuration=g+o,this.totalDuration=this.resolvedDuration*(s+1)-o,this.generator=h}updateTime(t){const n=Math.round(t-this.startTime)*this.playbackSpeed;this.holdTime!==null?this.currentTime=this.holdTime:this.currentTime=n}tick(t,n=!1){const{generator:s,totalDuration:o,mixKeyframes:c,mirroredGenerator:u,resolvedDuration:d,calculatedDuration:p}=this;if(this.startTime===null)return s.next(0);const{delay:h=0,keyframes:g,repeat:_,repeatType:v,repeatDelay:y,type:b,onUpdate:R,finalKeyframe:S}=this.options;this.speed>0?this.startTime=Math.min(this.startTime,t):this.speed<0&&(this.startTime=Math.min(t-o/this.speed,this.startTime)),n?this.currentTime=t:this.updateTime(t);const x=this.currentTime-h*(this.playbackSpeed>=0?1:-1),A=this.playbackSpeed>=0?x<0:x>o;this.currentTime=Math.max(x,0),this.state==="finished"&&this.holdTime===null&&(this.currentTime=o);let N=this.currentTime,L=s;if(_){const E=Math.min(this.currentTime,o)/d;let U=Math.floor(E),V=E%1;!V&&E>=1&&(V=1),V===1&&U--,U=Math.min(U,_+1),U%2&&(v==="reverse"?(V=1-V,y&&(V-=y/d)):v==="mirror"&&(L=u)),N=ha(0,1,V)*d}let H;A?(this.delayState.value=g[0],H=this.delayState):H=L.next(N),c&&!A&&(H.value=c(H.value));let{done:B}=H;!A&&p!==null&&(B=this.playbackSpeed>=0?this.currentTime>=o:this.currentTime<=0);const O=this.holdTime===null&&(this.state==="finished"||this.state==="running"&&B);return O&&b!==Rm&&(H.value=bf(g,this.options,S,this.speed)),R&&R(H.value),O&&this.finish(),H}then(t,n){return this.finished.then(t,n)}get duration(){return Li(this.calculatedDuration)}get iterationDuration(){const{delay:t=0}=this.options||{};return this.duration+Li(t)}get time(){return Li(this.currentTime)}set time(t){t=vi(t),this.currentTime=t,this.startTime===null||this.holdTime!==null||this.playbackSpeed===0?this.holdTime=t:this.driver&&(this.startTime=this.driver.now()-t/this.playbackSpeed),this.driver?this.driver.start(!1):(this.startTime=0,this.state="paused",this.holdTime=t,this.tick(t))}getGeneratorVelocity(){const t=this.currentTime;if(t<=0)return this.options.velocity||0;if(this.generator.velocity)return this.generator.velocity(t);const n=this.generator.next(t).value;return pb(s=>this.generator.next(s).value,t,n)}get speed(){return this.playbackSpeed}set speed(t){const n=this.playbackSpeed!==t;n&&this.driver&&this.updateTime(qn.now()),this.playbackSpeed=t,n&&this.driver&&(this.time=Li(this.currentTime))}play(){if(this.isStopped)return;const{driver:t=DN,startTime:n}=this.options;this.driver||(this.driver=t(o=>this.tick(o))),this.options.onPlay?.();const s=this.driver.now();this.state==="finished"?(this.updateFinished(),this.startTime=s):this.holdTime!==null?this.startTime=s-this.holdTime:this.startTime||(this.startTime=n??s),this.state==="finished"&&this.speed<0&&(this.startTime+=this.calculatedDuration),this.holdTime=null,this.state="running",this.driver.start()}pause(){this.state="paused",this.updateTime(qn.now()),this.holdTime=this.currentTime}complete(){this.state!=="running"&&this.play(),this.state="finished",this.holdTime=null}finish(){this.notifyFinished(),this.teardown(),this.state="finished",this.options.onComplete?.()}cancel(){this.holdTime=null,this.startTime=0,this.tick(0),this.teardown(),this.options.onCancel?.()}teardown(){this.state="idle",this.stopDriver(),this.startTime=this.holdTime=null}stopDriver(){this.driver&&(this.driver.stop(),this.driver=void 0)}sample(t){return this.startTime=0,this.tick(t,!0)}attachTimeline(t){return this.options.allowFlatten&&(this.options.type="keyframes",this.options.ease="linear",this.initAnimation()),this.driver?.stop(),t.observe(this)}}function YN(i){for(let t=1;t<i.length;t++)i[t]??(i[t]=i[t-1])}const ur=i=>i*180/Math.PI,Cm=i=>{const t=ur(Math.atan2(i[1],i[0]));return wm(t)},KN={x:4,y:5,translateX:4,translateY:5,scaleX:0,scaleY:3,scale:i=>(Math.abs(i[0])+Math.abs(i[3]))/2,rotate:Cm,rotateZ:Cm,skewX:i=>ur(Math.atan(i[1])),skewY:i=>ur(Math.atan(i[2])),skew:i=>(Math.abs(i[1])+Math.abs(i[2]))/2},wm=i=>(i=i%360,i<0&&(i+=360),i),Vy=Cm,Hy=i=>Math.sqrt(i[0]*i[0]+i[1]*i[1]),Gy=i=>Math.sqrt(i[4]*i[4]+i[5]*i[5]),ZN={x:12,y:13,z:14,translateX:12,translateY:13,translateZ:14,scaleX:Hy,scaleY:Gy,scale:i=>(Hy(i)+Gy(i))/2,rotateX:i=>wm(ur(Math.atan2(i[6],i[5]))),rotateY:i=>wm(ur(Math.atan2(-i[2],i[0]))),rotateZ:Vy,rotate:Vy,skewX:i=>ur(Math.atan(i[4])),skewY:i=>ur(Math.atan(i[1])),skew:i=>(Math.abs(i[1])+Math.abs(i[4]))/2};function Dm(i){return i.includes("scale")?1:0}function Nm(i,t){if(!i||i==="none")return Dm(t);const n=i.match(/^matrix3d\(([-\d.e\s,]+)\)$/u);let s,o;if(n)s=ZN,o=n;else{const d=i.match(/^matrix\(([-\d.e\s,]+)\)$/u);s=KN,o=d}if(!o)return Dm(t);const c=s[t],u=o[1].split(",").map(JN);return typeof c=="function"?c(u):u[c]}const QN=(i,t)=>{const{transform:n="none"}=getComputedStyle(i);return Nm(n,t)};function JN(i){return parseFloat(i.trim())}const Co=["transformPerspective","x","y","z","translateX","translateY","translateZ","scale","scaleX","scaleY","rotate","rotateX","rotateY","rotateZ","skew","skewX","skewY"],wo=new Set([...Co,"pathRotation"]),ky=i=>i===Ro||i===qt,$N=new Set(["x","y","z"]),tL=Co.filter(i=>!$N.has(i));function eL(i){const t=[];return tL.forEach(n=>{const s=i.getValue(n);s!==void 0&&(t.push([n,s.get()]),s.set(n.startsWith("scale")?1:0))}),t}const Cs={width:({x:i},{paddingLeft:t="0",paddingRight:n="0",boxSizing:s})=>{const o=i.max-i.min;return s==="border-box"?o:o-parseFloat(t)-parseFloat(n)},height:({y:i},{paddingTop:t="0",paddingBottom:n="0",boxSizing:s})=>{const o=i.max-i.min;return s==="border-box"?o:o-parseFloat(t)-parseFloat(n)},top:(i,{top:t})=>parseFloat(t),left:(i,{left:t})=>parseFloat(t),bottom:({y:i},{top:t})=>parseFloat(t)+(i.max-i.min),right:({x:i},{left:t})=>parseFloat(t)+(i.max-i.min),x:(i,{transform:t})=>Nm(t,"x"),y:(i,{transform:t})=>Nm(t,"y")};Cs.translateX=Cs.x;Cs.translateY=Cs.y;const fr=new Set;let Lm=!1,Um=!1,Pm=!1;function gb(){if(Um){const i=Array.from(fr).filter(s=>s.needsMeasurement),t=new Set(i.map(s=>s.element)),n=new Map;t.forEach(s=>{const o=eL(s);o.length&&(n.set(s,o),s.render())}),i.forEach(s=>s.measureInitialState()),t.forEach(s=>{s.render();const o=n.get(s);o&&o.forEach(([c,u])=>{s.getValue(c)?.set(u)})}),i.forEach(s=>s.measureEndState()),i.forEach(s=>{s.suspendedScrollY!==void 0&&window.scrollTo(0,s.suspendedScrollY)})}Um=!1,Lm=!1,fr.forEach(i=>i.complete(Pm)),fr.clear()}function _b(){fr.forEach(i=>{i.readKeyframes(),i.needsMeasurement&&(Um=!0)})}function nL(){Pm=!0,_b(),gb(),Pm=!1}class yg{constructor(t,n,s,o,c,u=!1){this.state="pending",this.isAsync=!1,this.needsMeasurement=!1,this.unresolvedKeyframes=[...t],this.onComplete=n,this.name=s,this.motionValue=o,this.element=c,this.isAsync=u}scheduleResolve(){this.state="scheduled",this.isAsync?(fr.add(this),Lm||(Lm=!0,Ke.read(_b),Ke.resolveKeyframes(gb))):(this.readKeyframes(),this.complete())}readKeyframes(){const{unresolvedKeyframes:t,name:n,element:s,motionValue:o}=this;if(t[0]===null){const c=o?.get(),u=t[t.length-1];if(c!==void 0)t[0]=c;else if(s&&n){const d=s.readValue(n,u);d!=null&&(t[0]=d)}t[0]===void 0&&(t[0]=u),o&&c===void 0&&o.set(t[0])}YN(t)}setFinalKeyframe(){}measureInitialState(){}renderEndStyles(){}measureEndState(){}complete(t=!1){this.state="complete",this.onComplete(this.unresolvedKeyframes,this.finalKeyframe,t),fr.delete(this)}cancel(){this.state==="scheduled"&&(fr.delete(this),this.state="pending")}resume(){this.state==="pending"&&this.scheduleResolve()}}const iL=i=>i.startsWith("--");function vb(i,t,n){iL(t)?i.style.setProperty(t,n):i.style[t]=n}const aL={};function xb(i,t){const n=WM(i);return()=>aL[t]??n()}const sL=xb(()=>window.ScrollTimeline!==void 0,"scrollTimeline"),yb=xb(()=>{try{document.createElement("div").animate({opacity:0},{easing:"linear(0, 1)"})}catch{return!1}return!0},"linearEasing"),Pl=([i,t,n,s])=>`cubic-bezier(${i}, ${t}, ${n}, ${s})`,jy={linear:"linear",ease:"ease",easeIn:"ease-in",easeOut:"ease-out",easeInOut:"ease-in-out",circIn:Pl([0,.65,.55,1]),circOut:Pl([.55,0,1,.45]),backIn:Pl([.31,.01,.66,-.59]),backOut:Pl([.33,1.53,.69,.99])};function Sb(i,t){if(i)return typeof i=="function"?yb()?hb(i,t):"ease-out":ib(i)?Pl(i):Array.isArray(i)?i.map(n=>Sb(n,t)||jy.easeOut):jy[i]}function rL(i,t,n,{delay:s=0,duration:o=300,repeat:c=0,repeatType:u="loop",ease:d="easeOut",times:p}={},h=void 0){const g={[t]:n};p&&(g.offset=p);const _=Sb(d,o);Array.isArray(_)&&(g.easing=_);const v={delay:s,duration:o,easing:Array.isArray(_)?"linear":_,fill:"both",iterations:c+1,direction:u==="reverse"?"alternate":"normal"};return h&&(v.pseudoElement=h),i.animate(g,v)}function Mb(i){return typeof i=="function"&&"applyToOptions"in i}function oL({type:i,...t}){return Mb(i)&&yb()?i.applyToOptions(t):(t.duration??(t.duration=300),t.ease??(t.ease="easeOut"),t)}class bb extends xg{constructor(t){if(super(),this.finishedTime=null,this.isStopped=!1,this.manualStartTime=null,!t)return;const{element:n,name:s,keyframes:o,pseudoElement:c,allowFlatten:u=!1,finalKeyframe:d,onComplete:p}=t;this.isPseudoElement=!!c,this.allowFlatten=u,this.options=t,ug(typeof t.type!="string");const h=oL(t);this.animation=rL(n,s,o,h,c),h.autoplay===!1&&this.animation.pause(),this.animation.onfinish=()=>{if(this.finishedTime=this.time,!c){const g=bf(o,this.options,d,this.speed);this.updateMotionValue&&this.updateMotionValue(g),vb(n,s,g),this.animation.cancel()}p?.(),this.notifyFinished()}}play(){this.isStopped||(this.manualStartTime=null,this.animation.play(),this.state==="finished"&&this.updateFinished())}pause(){this.animation.pause()}complete(){this.animation.finish?.()}cancel(){try{this.animation.cancel()}catch{}}stop(){if(this.isStopped)return;this.isStopped=!0;const{state:t}=this;t==="idle"||t==="finished"||(this.updateMotionValue?this.updateMotionValue():this.commitStyles(),this.isPseudoElement||this.cancel())}commitStyles(){const t=this.options?.element;!this.isPseudoElement&&t?.isConnected&&this.animation.commitStyles?.()}get duration(){const t=this.animation.effect?.getComputedTiming?.().duration||0;return Li(Number(t))}get iterationDuration(){const{delay:t=0}=this.options||{};return this.duration+Li(t)}get time(){return Li(Number(this.animation.currentTime)||0)}set time(t){const n=this.finishedTime!==null;this.manualStartTime=null,this.finishedTime=null,this.animation.currentTime=vi(t),n&&this.animation.pause()}get speed(){return this.animation.playbackRate}set speed(t){t<0&&(this.finishedTime=null),this.animation.playbackRate=t}get state(){return this.finishedTime!==null?"finished":this.animation.playState}get startTime(){return this.manualStartTime??Number(this.animation.startTime)}set startTime(t){this.manualStartTime=this.animation.startTime=t}attachTimeline({timeline:t,rangeStart:n,rangeEnd:s,observe:o}){return this.allowFlatten&&this.animation.effect?.updateTiming({easing:"linear"}),this.animation.onfinish=null,t&&sL()?(this.animation.timeline=t,n&&(this.animation.rangeStart=n),s&&(this.animation.rangeEnd=s),Ui):o(this)}}const Eb={anticipate:$M,backInOut:JM,circInOut:eb};function lL(i){return i in Eb}function cL(i){typeof i.ease=="string"&&lL(i.ease)&&(i.ease=Eb[i.ease])}const yp=10;class uL extends bb{constructor(t){cL(t),mb(t),super(t),t.startTime!==void 0&&t.autoplay!==!1&&(this.startTime=t.startTime),this.options=t}updateMotionValue(t){const{motionValue:n,onUpdate:s,onComplete:o,element:c,...u}=this.options;if(!n)return;if(t!==void 0){n.set(t);return}const d=new uf({...u,autoplay:!1}),p=Math.max(yp,qn.now()-this.startTime),h=ha(0,yp,p-yp),g=d.sample(p).value,{name:_}=this.options;c&&_&&vb(c,_,g),n.setWithVelocity(d.sample(Math.max(0,p-h)).value,g,h),d.stop()}}const Xy=(i,t)=>t==="zIndex"?!1:!!(typeof i=="number"||Array.isArray(i)||typeof i=="string"&&(qi.test(i)||i==="0")&&!i.startsWith("url("));function fL(i){const t=i[0];if(i.length===1)return!0;for(let n=0;n<i.length;n++)if(i[n]!==t)return!0}function dL(i,t,n,s){const o=i[0];if(o===null)return!1;if(t==="display"||t==="visibility")return!0;const c=i[i.length-1],u=Xy(o,t),d=Xy(c,t);return!u||!d?!1:fL(i)||(n==="spring"||Mb(n))&&s}function Om(i){i.duration=0,i.type="keyframes"}const Tb=new Set(["opacity","clipPath","filter","transform"]),hL=/^(?:oklch|oklab|lab|lch|color|color-mix|light-dark)\(/;function pL(i){for(let t=0;t<i.length;t++)if(typeof i[t]=="string"&&hL.test(i[t]))return!0;return!1}const mL=new Set(["color","backgroundColor","outlineColor","fill","stroke","borderColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"]),gL=WM(()=>Object.hasOwnProperty.call(Element.prototype,"animate"));function _L(i){const{motionValue:t,name:n,repeatDelay:s,repeatType:o,damping:c,type:u,keyframes:d}=i;if(!(t?.owner?.current instanceof HTMLElement))return!1;const{onUpdate:h,transformTemplate:g}=t.owner.getProps();return gL()&&n&&(Tb.has(n)||mL.has(n)&&pL(d))&&(n!=="transform"||!g)&&!h&&!s&&o!=="mirror"&&c!==0&&u!=="inertia"}const vL=40;class xL extends xg{constructor({autoplay:t=!0,delay:n=0,type:s="keyframes",repeat:o=0,repeatDelay:c=0,repeatType:u="loop",keyframes:d,name:p,motionValue:h,element:g,..._}){super(),this.stop=()=>{this._animation&&(this._animation.stop(),this.stopTimeline?.()),this.keyframeResolver?.cancel()},this.createdAt=qn.now();const v={autoplay:t,delay:n,type:s,repeat:o,repeatDelay:c,repeatType:u,name:p,motionValue:h,element:g,..._},y=g?.KeyframeResolver||yg;this.keyframeResolver=new y(d,(b,R,S)=>this.onKeyframesResolved(b,R,v,!S),p,h,g),this.keyframeResolver?.scheduleResolve()}onKeyframesResolved(t,n,s,o){this.keyframeResolver=void 0;const{name:c,type:u,velocity:d,delay:p,isHandoff:h,onUpdate:g}=s;this.resolvedAt=qn.now();let _=!0;dL(t,c,u,d)||(_=!1,(Ds.instantAnimations||!p)&&g?.(bf(t,s,n)),t[0]=t[t.length-1],Om(s),s.repeat=0);const y={startTime:o?this.resolvedAt?this.resolvedAt-this.createdAt>vL?this.resolvedAt:this.createdAt:this.createdAt:void 0,finalKeyframe:n,...s,keyframes:t},b=_&&!h&&_L(y),R=y.motionValue?.owner?.current;let S;if(b)try{S=new uL({...y,element:R})}catch{S=new uf(y)}else S=new uf(y);S.finished.then(()=>{this.notifyFinished()}).catch(Ui),this.pendingTimeline&&(this.stopTimeline=S.attachTimeline(this.pendingTimeline),this.pendingTimeline=void 0),this._animation=S}get finished(){return this._animation?this.animation.finished:this._finished}then(t,n){return this.finished.finally(t).then(()=>{})}get animation(){return this._animation||(this.keyframeResolver?.resume(),nL()),this._animation}get duration(){return this.animation.duration}get iterationDuration(){return this.animation.iterationDuration}get time(){return this.animation.time}set time(t){this.animation.time=t}get speed(){return this.animation.speed}get state(){return this.animation.state}set speed(t){this.animation.speed=t}get startTime(){return this.animation.startTime}attachTimeline(t){return this._animation?this.stopTimeline=this.animation.attachTimeline(t):this.pendingTimeline=t,()=>this.stop()}play(){this.animation.play()}pause(){this.animation.pause()}complete(){this.animation.complete()}cancel(){this._animation&&this.animation.cancel(),this.keyframeResolver?.cancel()}}function Ab(i,t,n,s=0,o=1){const c=Array.from(i).sort((h,g)=>h.sortNodePosition(g)).indexOf(t),u=i.size,d=(u-1)*s;return typeof n=="function"?n(c,u):o===1?c*s:d-c*s}const Wy=30,yL=i=>!isNaN(parseFloat(i));class SL{constructor(t,n={}){this.canTrackVelocity=null,this.events={},this.updateAndNotify=s=>{const o=qn.now();if(this.updatedAt!==o&&this.setPrevFrameValue(),this.prev=this.current,this.setCurrent(s),this.current!==this.prev&&(this.events.change?.notify(this.current),this.dependents))for(const c of this.dependents)c.dirty()},this.hasAnimated=!1,this.setCurrent(t),this.owner=n.owner}setCurrent(t){this.current=t,this.updatedAt=qn.now(),this.canTrackVelocity===null&&t!==void 0&&(this.canTrackVelocity=yL(this.current))}setPrevFrameValue(t=this.current){this.prevFrameValue=t,this.prevUpdatedAt=this.updatedAt}onChange(t){return this.on("change",t)}on(t,n){this.events[t]||(this.events[t]=new fg);const s=this.events[t].add(n);return t==="change"?()=>{s(),Ke.read(()=>{this.events.change.getSize()||this.stop()})}:s}clearListeners(){for(const t in this.events)this.events[t].clear()}attach(t,n){this.passiveEffect=t,this.stopPassiveEffect=n}set(t){this.passiveEffect?this.passiveEffect(t,this.updateAndNotify):this.updateAndNotify(t)}setWithVelocity(t,n,s){this.set(n),this.prev=void 0,this.prevFrameValue=t,this.prevUpdatedAt=this.updatedAt-s}jump(t,n=!0){this.updateAndNotify(t),this.prev=t,this.prevUpdatedAt=this.prevFrameValue=void 0,n&&this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}dirty(){this.events.change?.notify(this.current)}addDependent(t){this.dependents||(this.dependents=new Set),this.dependents.add(t)}removeDependent(t){this.dependents&&this.dependents.delete(t)}get(){return this.current}getPrevious(){return this.prev}getVelocity(){const t=qn.now();if(!this.canTrackVelocity||this.prevFrameValue===void 0||t-this.updatedAt>Wy)return 0;const n=Math.min(this.updatedAt-this.prevUpdatedAt,Wy);return qM(parseFloat(this.current)-parseFloat(this.prevFrameValue),n)}start(t){return this.stop(),new Promise(n=>{this.hasAnimated=!0,this.animation=t(n),this.events.animationStart&&this.events.animationStart.notify()}).then(()=>{this.events.animationComplete&&this.events.animationComplete.notify(),this.clearAnimation()})}stop(){this.animation&&(this.animation.stop(),this.events.animationCancel&&this.events.animationCancel.notify()),this.clearAnimation()}isAnimating(){return!!this.animation}clearAnimation(){delete this.animation}destroy(){this.dependents?.clear(),this.events.destroy?.notify(),this.clearListeners(),this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}}function Eo(i,t){return new SL(i,t)}function Rb(i,t){if(i?.inherit&&t){const{inherit:n,...s}=i;return{...t,...s}}return i}function Sg(i,t){const n=i?.[t]??i?.default??i;return n!==i?Rb(n,i):n}const ML={type:"spring",stiffness:500,damping:25,restSpeed:10},bL=i=>({type:"spring",stiffness:550,damping:i===0?2*Math.sqrt(550):30,restSpeed:10}),EL={type:"keyframes",duration:.8},TL={type:"keyframes",ease:[.25,.1,.35,1],duration:.3},AL=(i,{keyframes:t})=>t.length>2?EL:wo.has(i)?i.startsWith("scale")?bL(t[1]):ML:TL,RL=new Set(["when","delay","delayChildren","staggerChildren","staggerDirection","repeat","repeatType","repeatDelay","from","elapsed"]);function CL(i){for(const t in i)if(!RL.has(t))return!0;return!1}const Mg=(i,t,n,s={},o,c)=>u=>{const d=Sg(s,i)||{},p=d.delay||s.delay||0;let{elapsed:h=0}=s;h=h-vi(p);const g={keyframes:Array.isArray(n)?n:[null,n],ease:"easeOut",velocity:t.getVelocity(),...d,delay:-h,onUpdate:v=>{t.set(v),d.onUpdate&&d.onUpdate(v)},onComplete:()=>{u(),d.onComplete&&d.onComplete()},name:i,motionValue:t,element:c?void 0:o};CL(d)||Object.assign(g,AL(i,g)),g.duration&&(g.duration=vi(g.duration)),g.repeatDelay&&(g.repeatDelay=vi(g.repeatDelay)),g.from!==void 0&&(g.keyframes[0]=g.from);let _=!1;if((g.type===!1||g.duration===0&&!g.repeatDelay)&&(Om(g),g.delay===0&&(_=!0)),(Ds.instantAnimations||Ds.skipAnimations||o?.shouldSkipAnimations||d.skipAnimations)&&(_=!0,Om(g),g.delay=0),g.allowFlatten=!d.type&&!d.ease,_&&!c&&t.get()!==void 0){const v=bf(g.keyframes,d);if(v!==void 0){Ke.update(()=>{g.onUpdate(v),g.onComplete()});return}}return d.isSync?new uf(g):new xL(g)},wL=/^var\(--(?:([\w-]+)|([\w-]+), ?([a-zA-Z\d ()%#.,-]+))\)/u;function DL(i){const t=wL.exec(i);if(!t)return[,];const[,n,s,o]=t;return[`--${n??s}`,o]}function Cb(i,t,n=1){const[s,o]=DL(i);if(!s)return;const c=window.getComputedStyle(t).getPropertyValue(s);if(c){const u=c.trim();return kM(u)?parseFloat(u):u}return pg(o)?Cb(o,t,n+1):o}function qy(i){const t=[{},{}];return i?.values.forEach((n,s)=>{t[0][s]=n.get(),t[1][s]=n.getVelocity()}),t}function bg(i,t,n,s){if(typeof t=="function"){const[o,c]=qy(s);t=t(n!==void 0?n:i.custom,o,c)}if(typeof t=="string"&&(t=i.variants&&i.variants[t]),typeof t=="function"){const[o,c]=qy(s);t=t(n!==void 0?n:i.custom,o,c)}return t}function dr(i,t,n){const s=i.getProps();return bg(s,t,n!==void 0?n:s.custom,i)}const wb=new Set(["width","height","top","left","right","bottom",...Co]),Fm=i=>Array.isArray(i);function NL(i,t,n){i.hasValue(t)?i.getValue(t).set(n):i.addValue(t,Eo(n))}function LL(i){return Fm(i)?i[i.length-1]||0:i}function UL(i,t){const n=dr(i,t);let{transitionEnd:s={},transition:o={},...c}=n||{};c={...c,...s};for(const u in c){const d=LL(c[u]);NL(i,u,d)}}const In=i=>!!(i&&i.getVelocity);function PL(i){return!!(In(i)&&i.add)}function Bm(i,t){const n=i.getValue("willChange");if(PL(n))return n.add(t);if(!n&&Ds.WillChange){const s=new Ds.WillChange("auto");i.addValue("willChange",s),s.add(t)}}function Eg(i){return i.replace(/([A-Z])/g,t=>`-${t.toLowerCase()}`)}const OL="framerAppearId",Db="data-"+Eg(OL);function Nb(i){return i.props[Db]}function FL({protectedKeys:i,needsAnimating:t},n){const s=i.hasOwnProperty(n)&&t[n]!==!0;return t[n]=!1,s}function Lb(i,t,{delay:n=0,transitionOverride:s,type:o}={}){let{transition:c,transitionEnd:u,...d}=t;const p=i.getDefaultTransition();c=c?Rb(c,p):p;const h=c?.reduceMotion,g=c?.skipAnimations;s&&(c=s);const _=[],v=o&&i.animationState&&i.animationState.getState()[o],y=c?.path;y&&y.animateVisualElement(i,d,c,n,_);for(const b in d){const R=i.getValue(b,i.latestValues[b]??null),S=d[b];if(S===void 0||v&&FL(v,b))continue;const x={delay:n,...Sg(c||{},b)};g&&(x.skipAnimations=!0);const A=R.get();if(A!==void 0&&!R.isAnimating()&&!Array.isArray(S)&&S===A&&!x.velocity){Ke.update(()=>R.set(S));continue}let N=!1;if(window.MotionHandoffAnimation){const B=Nb(i);if(B){const O=window.MotionHandoffAnimation(B,b,Ke);O!==null&&(x.startTime=O,N=!0)}}Bm(i,b);const L=h??i.shouldReduceMotion;R.start(Mg(b,R,S,L&&wb.has(b)?{type:!1}:x,i,N));const H=R.animation;H&&_.push(H)}if(u){const b=()=>Ke.update(()=>{u&&UL(i,u)});_.length?Promise.all(_).then(b):b()}return _}function Im(i,t,n={}){const s=dr(i,t,n.type==="exit"?i.presenceContext?.custom:void 0);let{transition:o=i.getDefaultTransition()||{}}=s||{};n.transitionOverride&&(o=n.transitionOverride);const c=s?()=>Promise.all(Lb(i,s,n)):()=>Promise.resolve(),u=i.variantChildren&&i.variantChildren.size?(p=0)=>{const{delayChildren:h=0,staggerChildren:g,staggerDirection:_}=o;return BL(i,t,p,h,g,_,n)}:()=>Promise.resolve(),{when:d}=o;if(d){const[p,h]=d==="beforeChildren"?[c,u]:[u,c];return p().then(()=>h())}else return Promise.all([c(),u(n.delay)])}function BL(i,t,n=0,s=0,o=0,c=1,u){const d=[];for(const p of i.variantChildren)p.notify("AnimationStart",t),d.push(Im(p,t,{...u,delay:n+(typeof s=="function"?0:s)+Ab(i.variantChildren,p,s,o,c)}).then(()=>p.notify("AnimationComplete",t)));return Promise.all(d)}function IL(i,t,n={}){i.notify("AnimationStart",t);let s;if(Array.isArray(t)){const o=t.map(c=>Im(i,c,n));s=Promise.all(o)}else if(typeof t=="string")s=Im(i,t,n);else{const o=typeof t=="function"?dr(i,t,n.custom):t;s=Promise.all(Lb(i,o,n))}return s.then(()=>{i.notify("AnimationComplete",t)})}const zL={test:i=>i==="auto",parse:i=>i},Ub=i=>t=>t.test(i),Pb=[Ro,qt,ua,Ba,fN,uN,zL],Yy=i=>Pb.find(Ub(i));function VL(i){return typeof i=="number"?i===0:i!==null?i==="none"||i==="0"||XM(i):!0}const HL=new Set(["brightness","contrast","saturate","opacity"]);function GL(i){const[t,n]=i.slice(0,-1).split("(");if(t==="drop-shadow")return i;const[s]=n.match(mg)||[];if(!s)return i;const o=n.replace(s,"");let c=HL.has(t)?1:0;return s!==n&&(c*=100),t+"("+c+o+")"}const kL=/\b([a-z-]*)\(.*?\)/gu,zm={...qi,getAnimatableNone:i=>{const t=i.match(kL);return t?t.map(GL).join(" "):i}},Vm={...qi,getAnimatableNone:i=>{const t=qi.parse(i);return qi.createTransformer(i)(t.map(s=>typeof s=="number"?0:typeof s=="object"?{...s,alpha:1}:s))}},Ky={...Ro,transform:Math.round},jL={rotate:Ba,pathRotation:Ba,rotateX:Ba,rotateY:Ba,rotateZ:Ba,scale:Fu,scaleX:Fu,scaleY:Fu,scaleZ:Fu,skew:Ba,skewX:Ba,skewY:Ba,distance:qt,translateX:qt,translateY:qt,translateZ:qt,x:qt,y:qt,z:qt,perspective:qt,transformPerspective:qt,opacity:kl,originX:Oy,originY:Oy,originZ:qt},ff={borderWidth:qt,borderTopWidth:qt,borderRightWidth:qt,borderBottomWidth:qt,borderLeftWidth:qt,borderRadius:qt,borderTopLeftRadius:qt,borderTopRightRadius:qt,borderBottomRightRadius:qt,borderBottomLeftRadius:qt,width:qt,maxWidth:qt,height:qt,maxHeight:qt,top:qt,right:qt,bottom:qt,left:qt,inset:qt,insetBlock:qt,insetBlockStart:qt,insetBlockEnd:qt,insetInline:qt,insetInlineStart:qt,insetInlineEnd:qt,padding:qt,paddingTop:qt,paddingRight:qt,paddingBottom:qt,paddingLeft:qt,paddingBlock:qt,paddingBlockStart:qt,paddingBlockEnd:qt,paddingInline:qt,paddingInlineStart:qt,paddingInlineEnd:qt,margin:qt,marginTop:qt,marginRight:qt,marginBottom:qt,marginLeft:qt,marginBlock:qt,marginBlockStart:qt,marginBlockEnd:qt,marginInline:qt,marginInlineStart:qt,marginInlineEnd:qt,fontSize:qt,backgroundPositionX:qt,backgroundPositionY:qt,...jL,zIndex:Ky,fillOpacity:kl,strokeOpacity:kl,numOctaves:Ky},XL={...ff,color:yn,backgroundColor:yn,outlineColor:yn,fill:yn,stroke:yn,borderColor:yn,borderTopColor:yn,borderRightColor:yn,borderBottomColor:yn,borderLeftColor:yn,filter:zm,WebkitFilter:zm,mask:Vm,WebkitMask:Vm},Ob=i=>XL[i],WL=new Set([zm,Vm]);function Fb(i,t){let n=Ob(i);return WL.has(n)||(n=qi),n.getAnimatableNone?n.getAnimatableNone(t):void 0}const qL=new Set(["auto","none","0"]);function YL(i,t,n){let s=0,o;for(;s<i.length&&!o;){const c=i[s];typeof c=="string"&&!qL.has(c)&&bo(c).values.length&&(o=i[s]),s++}if(o&&n)for(const c of t)i[c]=Fb(n,o)}class KL extends yg{constructor(t,n,s,o,c){super(t,n,s,o,c,!0)}readKeyframes(){const{unresolvedKeyframes:t,element:n,name:s}=this;if(!n||!n.current)return;super.readKeyframes();for(let g=0;g<t.length;g++){let _=t[g];if(typeof _=="string"&&(_=_.trim(),pg(_))){const v=Cb(_,n.current);v!==void 0&&(t[g]=v),g===t.length-1&&(this.finalKeyframe=_)}}if(this.resolveNoneKeyframes(),!wb.has(s)||t.length!==2)return;const[o,c]=t,u=Yy(o),d=Yy(c),p=Py(o),h=Py(c);if(p!==h&&Cs[s]){this.needsMeasurement=!0;return}if(u!==d)if(ky(u)&&ky(d))for(let g=0;g<t.length;g++){const _=t[g];typeof _=="string"&&(t[g]=parseFloat(_))}else Cs[s]&&(this.needsMeasurement=!0)}resolveNoneKeyframes(){const{unresolvedKeyframes:t,name:n}=this,s=[];for(let o=0;o<t.length;o++)(t[o]===null||VL(t[o]))&&s.push(o);s.length&&YL(t,s,n)}measureInitialState(){const{element:t,unresolvedKeyframes:n,name:s}=this;if(!t||!t.current)return;s==="height"&&(this.suspendedScrollY=window.pageYOffset),this.measuredOrigin=Cs[s](t.measureViewportBox(),window.getComputedStyle(t.current)),n[0]=this.measuredOrigin;const o=n[n.length-1];o!==void 0&&t.getValue(s,o).jump(o,!1)}measureEndState(){const{element:t,name:n,unresolvedKeyframes:s}=this;if(!t||!t.current)return;const o=t.getValue(n);o&&o.jump(this.measuredOrigin,!1);const c=s.length-1,u=s[c];s[c]=Cs[n](t.measureViewportBox(),window.getComputedStyle(t.current)),u!==null&&this.finalKeyframe===void 0&&(this.finalKeyframe=u),this.removedTransforms?.length&&this.removedTransforms.forEach(([d,p])=>{t.getValue(d).set(p)}),this.resolveNoneKeyframes()}}function Bb(i,t,n){if(i==null)return[];if(i instanceof EventTarget)return[i];if(typeof i=="string"){let s=document;const o=n?.[i]??s.querySelectorAll(i);return o?Array.from(o):[]}return Array.from(i).filter(s=>s!=null)}const Hm=(i,t)=>t&&typeof i=="number"?t.transform(i):i;function ZL(i){return jM(i)&&"offsetHeight"in i&&!("ownerSVGElement"in i)}const{schedule:Tg}=ab(queueMicrotask,!1),ki={x:!1,y:!1};function Ib(){return ki.x||ki.y}function QL(i){return i==="x"||i==="y"?ki[i]?null:(ki[i]=!0,()=>{ki[i]=!1}):ki.x||ki.y?null:(ki.x=ki.y=!0,()=>{ki.x=ki.y=!1})}function zb(i,t){const n=Bb(i),s=new AbortController,o={passive:!0,...t,signal:s.signal};return[n,o,()=>s.abort()]}function JL(i){return!(i.pointerType==="touch"||Ib())}function $L(i,t,n={}){const[s,o,c]=zb(i,n);return s.forEach(u=>{let d=!1,p=!1,h;const g=()=>{u.removeEventListener("pointerleave",b)},_=S=>{h&&(h(S),h=void 0),g()},v=S=>{d=!1,window.removeEventListener("pointerup",v),window.removeEventListener("pointercancel",v),p&&(p=!1,_(S))},y=()=>{d=!0,window.addEventListener("pointerup",v,o),window.addEventListener("pointercancel",v,o)},b=S=>{if(S.pointerType!=="touch"){if(d){p=!0;return}_(S)}},R=S=>{if(!JL(S))return;p=!1;const x=t(u,S);typeof x=="function"&&(h=x,u.addEventListener("pointerleave",b,o))};u.addEventListener("pointerenter",R,o),u.addEventListener("pointerdown",y,o)}),c}const Vb=(i,t)=>t?i===t?!0:Vb(i,t.parentElement):!1,Ag=i=>i.pointerType==="mouse"?typeof i.button!="number"||i.button<=0:i.isPrimary!==!1,tU=new Set(["BUTTON","INPUT","SELECT","TEXTAREA","A"]);function eU(i){return tU.has(i.tagName)||i.isContentEditable===!0}const nU=new Set(["INPUT","SELECT","TEXTAREA"]);function iU(i){return nU.has(i.tagName)||i.isContentEditable===!0}const Wu=new WeakSet;function Zy(i){return t=>{t.key==="Enter"&&i(t)}}function Sp(i,t){i.dispatchEvent(new PointerEvent("pointer"+t,{isPrimary:!0,bubbles:!0}))}const aU=(i,t)=>{const n=i.currentTarget;if(!n)return;const s=Zy(()=>{if(Wu.has(n))return;Sp(n,"down");const o=Zy(()=>{Sp(n,"up")}),c=()=>Sp(n,"cancel");n.addEventListener("keyup",o,t),n.addEventListener("blur",c,t)});n.addEventListener("keydown",s,t),n.addEventListener("blur",()=>n.removeEventListener("keydown",s),t)};function Qy(i){return Ag(i)&&!Ib()}const Jy=new WeakSet;function sU(i,t,n={}){const[s,o,c]=zb(i,n),u=d=>{const p=d.currentTarget;if(!Qy(d)||Jy.has(d))return;Wu.add(p),n.stopPropagation&&Jy.add(d);const h=t(p,d),g=(y,b)=>{window.removeEventListener("pointerup",_),window.removeEventListener("pointercancel",v),Wu.has(p)&&Wu.delete(p),Qy(y)&&typeof h=="function"&&h(y,{success:b})},_=y=>{g(y,p===window||p===document||n.useGlobalTarget||Vb(p,y.target))},v=y=>{g(y,!1)};window.addEventListener("pointerup",_,o),window.addEventListener("pointercancel",v,o)};return s.forEach(d=>{(n.useGlobalTarget?window:d).addEventListener("pointerdown",u,o),ZL(d)&&(d.addEventListener("focus",h=>aU(h,o)),!eU(d)&&!d.hasAttribute("tabindex")&&(d.tabIndex=0))}),c}function Rg(i){return jM(i)&&"ownerSVGElement"in i}const qu=new WeakMap;let Yu;const Hb=(i,t,n)=>(s,o)=>o&&o[0]?o[0][i+"Size"]:Rg(s)&&"getBBox"in s?s.getBBox()[t]:s[n],rU=Hb("inline","width","offsetWidth"),oU=Hb("block","height","offsetHeight");function lU({target:i,borderBoxSize:t}){qu.get(i)?.forEach(n=>{n(i,{get width(){return rU(i,t)},get height(){return oU(i,t)}})})}function cU(i){i.forEach(lU)}function uU(){typeof ResizeObserver>"u"||(Yu=new ResizeObserver(cU))}function fU(i,t){Yu||uU();const n=Bb(i);return n.forEach(s=>{let o=qu.get(s);o||(o=new Set,qu.set(s,o)),o.add(t),Yu?.observe(s)}),()=>{n.forEach(s=>{const o=qu.get(s);o?.delete(t),o?.size||Yu?.unobserve(s)})}}const Ku=new Set;let po;function dU(){po=()=>{const i={get width(){return window.innerWidth},get height(){return window.innerHeight}};Ku.forEach(t=>t(i))},window.addEventListener("resize",po)}function hU(i){return Ku.add(i),po||dU(),()=>{Ku.delete(i),!Ku.size&&typeof po=="function"&&(window.removeEventListener("resize",po),po=void 0)}}function $y(i,t){return typeof i=="function"?hU(i):fU(i,t)}function pU(i){return Rg(i)&&i.tagName==="svg"}const mU=[...Pb,yn,qi],gU=i=>mU.find(Ub(i)),tS=()=>({translate:0,scale:1,origin:0,originPoint:0}),mo=()=>({x:tS(),y:tS()}),eS=()=>({min:0,max:0}),Tn=()=>({x:eS(),y:eS()}),_U=new WeakMap;function Ef(i){return i!==null&&typeof i=="object"&&typeof i.start=="function"}function jl(i){return typeof i=="string"||Array.isArray(i)}const Cg=["animate","whileInView","whileFocus","whileHover","whileTap","whileDrag","exit"],wg=["initial",...Cg];function Tf(i){return Ef(i.animate)||wg.some(t=>jl(i[t]))}function Gb(i){return!!(Tf(i)||i.variants)}function vU(i,t,n){for(const s in t){const o=t[s],c=n[s];if(In(o))i.addValue(s,o);else if(In(c))i.addValue(s,Eo(o,{owner:i}));else if(c!==o)if(i.hasValue(s)){const u=i.getValue(s);u.liveStyle===!0?u.jump(o):u.hasAnimated||u.set(o)}else{const u=i.getStaticValue(s);i.addValue(s,Eo(u!==void 0?u:o,{owner:i}))}}for(const s in n)t[s]===void 0&&i.removeValue(s);return t}const Gm={current:null},kb={current:!1},xU=typeof window<"u";function yU(){if(kb.current=!0,!!xU)if(window.matchMedia){const i=window.matchMedia("(prefers-reduced-motion)"),t=()=>Gm.current=i.matches;i.addEventListener("change",t),t()}else Gm.current=!1}const nS=["AnimationStart","AnimationComplete","Update","BeforeLayoutMeasure","LayoutMeasure","LayoutAnimationStart","LayoutAnimationComplete"];let df={};function jb(i){df=i}function SU(){return df}class MU{scrapeMotionValuesFromProps(t,n,s){return{}}constructor({parent:t,props:n,presenceContext:s,reducedMotionConfig:o,skipAnimations:c,blockInitialAnimation:u,visualState:d},p={}){this.current=null,this.children=new Set,this.isVariantNode=!1,this.isControllingVariants=!1,this.shouldReduceMotion=null,this.shouldSkipAnimations=!1,this.values=new Map,this.KeyframeResolver=yg,this.features={},this.valueSubscriptions=new Map,this.prevMotionValues={},this.hasBeenMounted=!1,this.events={},this.propEventSubscriptions={},this.notifyUpdate=()=>this.notify("Update",this.latestValues),this.render=()=>{this.current&&(this.triggerBuild(),this.renderInstance(this.current,this.renderState,this.props.style,this.projection))},this.renderScheduledAt=0,this.scheduleRender=()=>{const y=qn.now();this.renderScheduledAt<y&&(this.renderScheduledAt=y,Ke.render(this.render,!1,!0))};const{latestValues:h,renderState:g}=d;this.latestValues=h,this.baseTarget={...h},this.initialValues=n.initial?{...h}:{},this.renderState=g,this.parent=t,this.props=n,this.presenceContext=s,this.depth=t?t.depth+1:0,this.reducedMotionConfig=o,this.skipAnimationsConfig=c,this.options=p,this.blockInitialAnimation=!!u,this.isControllingVariants=Tf(n),this.isVariantNode=Gb(n),this.isVariantNode&&(this.variantChildren=new Set),this.manuallyAnimateOnMount=!!(t&&t.current);const{willChange:_,...v}=this.scrapeMotionValuesFromProps(n,{},this);for(const y in v){const b=v[y];h[y]!==void 0&&In(b)&&b.set(h[y])}}mount(t){if(this.hasBeenMounted)for(const n in this.initialValues)this.values.get(n)?.jump(this.initialValues[n]),this.latestValues[n]=this.initialValues[n];this.current=t,_U.set(t,this),this.projection&&!this.projection.instance&&this.projection.mount(t),this.parent&&this.isVariantNode&&!this.isControllingVariants&&(this.removeFromVariantTree=this.parent.addVariantChild(this)),this.values.forEach((n,s)=>this.bindToMotionValue(s,n)),this.reducedMotionConfig==="never"?this.shouldReduceMotion=!1:this.reducedMotionConfig==="always"?this.shouldReduceMotion=!0:(kb.current||yU(),this.shouldReduceMotion=Gm.current),this.shouldSkipAnimations=this.skipAnimationsConfig??!1,this.parent?.addChild(this),this.update(this.props,this.presenceContext),this.hasBeenMounted=!0}unmount(){this.projection&&this.projection.unmount(),Ns(this.notifyUpdate),Ns(this.render),this.valueSubscriptions.forEach(t=>t()),this.valueSubscriptions.clear(),this.removeFromVariantTree&&this.removeFromVariantTree(),this.parent?.removeChild(this);for(const t in this.events)this.events[t].clear();for(const t in this.features){const n=this.features[t];n&&(n.unmount(),n.isMounted=!1)}this.current=null}addChild(t){this.children.add(t),this.enteringChildren??(this.enteringChildren=new Set),this.enteringChildren.add(t)}removeChild(t){this.children.delete(t),this.enteringChildren&&this.enteringChildren.delete(t)}bindToMotionValue(t,n){if(this.valueSubscriptions.has(t)&&this.valueSubscriptions.get(t)(),n.accelerate&&Tb.has(t)&&this.current instanceof HTMLElement){const{factory:u,keyframes:d,times:p,ease:h,duration:g}=n.accelerate,_=new bb({element:this.current,name:t,keyframes:d,times:p,ease:h,duration:vi(g)}),v=u(_);this.valueSubscriptions.set(t,()=>{v(),_.cancel()});return}const s=wo.has(t);s&&this.onBindTransform&&this.onBindTransform();const o=n.on("change",u=>{this.latestValues[t]=u,this.props.onUpdate&&Ke.preRender(this.notifyUpdate),s&&this.projection&&(this.projection.isTransformDirty=!0),this.scheduleRender()});let c;typeof window<"u"&&window.MotionCheckAppearSync&&(c=window.MotionCheckAppearSync(this,t,n)),this.valueSubscriptions.set(t,()=>{o(),c&&c()})}sortNodePosition(t){return!this.current||!this.sortInstanceNodePosition||this.type!==t.type?0:this.sortInstanceNodePosition(this.current,t.current)}updateFeatures(){let t="animation";for(t in df){const n=df[t];if(!n)continue;const{isEnabled:s,Feature:o}=n;if(!this.features[t]&&o&&s(this.props)&&(this.features[t]=new o(this)),this.features[t]){const c=this.features[t];c.isMounted?c.update():(c.mount(),c.isMounted=!0)}}}triggerBuild(){this.build(this.renderState,this.latestValues,this.props)}measureViewportBox(){return this.current?this.measureInstanceViewportBox(this.current,this.props):Tn()}getStaticValue(t){return this.latestValues[t]}setStaticValue(t,n){this.latestValues[t]=n}update(t,n){(t.transformTemplate||this.props.transformTemplate)&&this.scheduleRender(),this.prevProps=this.props,this.props=t,this.prevPresenceContext=this.presenceContext,this.presenceContext=n;for(let s=0;s<nS.length;s++){const o=nS[s];this.propEventSubscriptions[o]&&(this.propEventSubscriptions[o](),delete this.propEventSubscriptions[o]);const c="on"+o,u=t[c];u&&(this.propEventSubscriptions[o]=this.on(o,u))}this.prevMotionValues=vU(this,this.scrapeMotionValuesFromProps(t,this.prevProps||{},this),this.prevMotionValues),this.handleChildMotionValue&&this.handleChildMotionValue()}getProps(){return this.props}getVariant(t){return this.props.variants?this.props.variants[t]:void 0}getDefaultTransition(){return this.props.transition}getTransformPagePoint(){return this.props.transformPagePoint}getClosestVariantNode(){return this.isVariantNode?this:this.parent?this.parent.getClosestVariantNode():void 0}addVariantChild(t){const n=this.getClosestVariantNode();if(n)return n.variantChildren&&n.variantChildren.add(t),()=>n.variantChildren.delete(t)}addValue(t,n){const s=this.values.get(t);n!==s&&(s&&this.removeValue(t),this.bindToMotionValue(t,n),this.values.set(t,n),this.latestValues[t]=n.get())}removeValue(t){this.values.delete(t);const n=this.valueSubscriptions.get(t);n&&(n(),this.valueSubscriptions.delete(t)),delete this.latestValues[t],this.removeValueFromRenderState(t,this.renderState)}hasValue(t){return this.values.has(t)}getValue(t,n){if(this.props.values&&this.props.values[t])return this.props.values[t];let s=this.values.get(t);return s===void 0&&n!==void 0&&(s=Eo(n===null?void 0:n,{owner:this}),this.addValue(t,s)),s}readValue(t,n){let s=this.latestValues[t]!==void 0||!this.current?this.latestValues[t]:this.getBaseTargetFromProps(this.props,t)??this.readValueFromInstance(this.current,t,this.options);return s!=null&&(typeof s=="string"&&(kM(s)||XM(s))?s=parseFloat(s):!gU(s)&&qi.test(n)&&(s=Fb(t,n)),this.setBaseTarget(t,In(s)?s.get():s)),In(s)?s.get():s}setBaseTarget(t,n){this.baseTarget[t]=n}getBaseTarget(t){const{initial:n}=this.props;let s;if(typeof n=="string"||typeof n=="object"){const c=bg(this.props,n,this.presenceContext?.custom);c&&(s=c[t])}if(n&&s!==void 0)return s;const o=this.getBaseTargetFromProps(this.props,t);return o!==void 0&&!In(o)?o:this.initialValues[t]!==void 0&&s===void 0?void 0:this.baseTarget[t]}on(t,n){return this.events[t]||(this.events[t]=new fg),this.events[t].add(n)}notify(t,...n){this.events[t]&&this.events[t].notify(...n)}scheduleRenderMicrotask(){Tg.render(this.render)}}class Xb extends MU{constructor(){super(...arguments),this.KeyframeResolver=KL}sortInstanceNodePosition(t,n){return t.compareDocumentPosition(n)&2?1:-1}getBaseTargetFromProps(t,n){const s=t.style;return s?s[n]:void 0}removeValueFromRenderState(t,{vars:n,style:s}){delete n[t],delete s[t]}handleChildMotionValue(){this.childSubscription&&(this.childSubscription(),delete this.childSubscription);const{children:t}=this.props;In(t)&&(this.childSubscription=t.on("change",n=>{this.current&&(this.current.textContent=`${n}`)}))}}class Ls{constructor(t){this.isMounted=!1,this.node=t}update(){}}function Wb({top:i,left:t,right:n,bottom:s}){return{x:{min:t,max:n},y:{min:i,max:s}}}function bU({x:i,y:t}){return{top:t.min,right:i.max,bottom:t.max,left:i.min}}function EU(i,t){if(!t)return i;const n=t({x:i.left,y:i.top}),s=t({x:i.right,y:i.bottom});return{top:n.y,left:n.x,bottom:s.y,right:s.x}}function Mp(i){return i===void 0||i===1}function km({scale:i,scaleX:t,scaleY:n}){return!Mp(i)||!Mp(t)||!Mp(n)}function ar(i){return km(i)||qb(i)||i.z||i.rotate||i.rotateX||i.rotateY||i.skewX||i.skewY}function qb(i){return iS(i.x)||iS(i.y)}function iS(i){return i&&i!=="0%"}function hf(i,t,n){const s=i-n,o=t*s;return n+o}function aS(i,t,n,s,o){return o!==void 0&&(i=hf(i,o,s)),hf(i,n,s)+t}function jm(i,t=0,n=1,s,o){i.min=aS(i.min,t,n,s,o),i.max=aS(i.max,t,n,s,o)}function Yb(i,{x:t,y:n}){jm(i.x,t.translate,t.scale,t.originPoint),jm(i.y,n.translate,n.scale,n.originPoint)}const sS=.999999999999,rS=1.0000000000001;function TU(i,t,n,s=!1){const o=n.length;if(!o)return;t.x=t.y=1;let c,u;for(let d=0;d<o;d++){c=n[d],u=c.projectionDelta;const{visualElement:p}=c.options;p&&p.props.style&&p.props.style.display==="contents"||(s&&c.options.layoutScroll&&c.scroll&&c!==c.root&&(aa(i.x,-c.scroll.offset.x),aa(i.y,-c.scroll.offset.y)),u&&(t.x*=u.x.scale,t.y*=u.y.scale,Yb(i,u)),s&&ar(c.latestValues)&&Zu(i,c.latestValues,c.layout?.layoutBox))}t.x<rS&&t.x>sS&&(t.x=1),t.y<rS&&t.y>sS&&(t.y=1)}function aa(i,t){i.min+=t,i.max+=t}function oS(i,t,n,s,o=.5){const c=Ye(i.min,i.max,o);jm(i,t,n,c,s)}function lS(i,t){return typeof i=="string"?parseFloat(i)/100*(t.max-t.min):i}function Zu(i,t,n){const s=n??i;oS(i.x,lS(t.x,s.x),t.scaleX,t.scale,t.originX),oS(i.y,lS(t.y,s.y),t.scaleY,t.scale,t.originY)}function Kb(i,t){return Wb(EU(i.getBoundingClientRect(),t))}function AU(i,t,n){const s=Kb(i,n),{scroll:o}=t;return o&&(aa(s.x,o.offset.x),aa(s.y,o.offset.y)),s}const RU={x:"translateX",y:"translateY",z:"translateZ",transformPerspective:"perspective"},CU=Co.length;function wU(i,t,n){let s="",o=!0;for(let u=0;u<CU;u++){const d=Co[u],p=i[d];if(p===void 0)continue;let h=!0;if(typeof p=="number")h=p===(d.startsWith("scale")?1:0);else{const g=parseFloat(p);h=d.startsWith("scale")?g===1:g===0}if(!h||n){const g=Hm(p,ff[d]);if(!h){o=!1;const _=RU[d]||d;s+=`${_}(${g}) `}n&&(t[d]=g)}}const c=i.pathRotation;return c&&(o=!1,s+=`rotate(${Hm(c,ff.pathRotation)}) `),s=s.trim(),n?s=n(t,o?"":s):o&&(s="none"),s}function Dg(i,t,n){const{style:s,vars:o,transformOrigin:c}=i;let u=!1,d=!1;for(const p in t){const h=t[p];if(wo.has(p)){u=!0;continue}else if(rb(p)){o[p]=h;continue}else{const g=Hm(h,ff[p]);p.startsWith("origin")?(d=!0,c[p]=g):s[p]=g}}if(t.transform||(u||n?s.transform=wU(t,i.transform,n):s.transform&&(s.transform="none")),d){const{originX:p="50%",originY:h="50%",originZ:g=0}=c;s.transformOrigin=`${p} ${h} ${g}`}}function Zb(i,{style:t,vars:n},s,o){const c=i.style;let u;for(u in t)c[u]=t[u];o?.applyProjectionStyles(c,s);for(u in n)c.setProperty(u,n[u])}function cS(i,t){return t.max===t.min?0:i/(t.max-t.min)*100}const Nl={correct:(i,t)=>{if(!t.target)return i;if(typeof i=="string")if(qt.test(i))i=parseFloat(i);else return i;const n=cS(i,t.target.x),s=cS(i,t.target.y);return`${n}% ${s}%`}},DU={correct:(i,{treeScale:t,projectionDelta:n})=>{const s=i,o=qi.parse(i);if(o.length>5)return s;const c=qi.createTransformer(i),u=typeof o[0]!="number"?1:0,d=n.x.scale*t.x,p=n.y.scale*t.y;o[0+u]/=d,o[1+u]/=p;const h=Ye(d,p,.5);return typeof o[2+u]=="number"&&(o[2+u]/=h),typeof o[3+u]=="number"&&(o[3+u]/=h),c(o)}},Xm={borderRadius:{...Nl,applyTo:["borderTopLeftRadius","borderTopRightRadius","borderBottomLeftRadius","borderBottomRightRadius"]},borderTopLeftRadius:Nl,borderTopRightRadius:Nl,borderBottomLeftRadius:Nl,borderBottomRightRadius:Nl,boxShadow:DU};function Qb(i,{layout:t,layoutId:n}){return wo.has(i)||i.startsWith("origin")||(t||n!==void 0)&&(!!Xm[i]||i==="opacity")}function Ng(i,t,n){const s=i.style,o=t?.style,c={};if(!s)return c;for(const u in s)(In(s[u])||o&&In(o[u])||Qb(u,i)||n?.getValue(u)?.liveStyle!==void 0)&&(c[u]=s[u]);return c}function NU(i){return window.getComputedStyle(i)}class LU extends Xb{constructor(){super(...arguments),this.type="html",this.renderInstance=Zb}readValueFromInstance(t,n){if(wo.has(n))return this.projection?.isProjecting?Dm(n):QN(t,n);{const s=NU(t),o=(rb(n)?s.getPropertyValue(n):s[n])||0;return typeof o=="string"?o.trim():o}}measureInstanceViewportBox(t,{transformPagePoint:n}){return Kb(t,n)}build(t,n,s){Dg(t,n,s.transformTemplate)}scrapeMotionValuesFromProps(t,n,s){return Ng(t,n,s)}}const UU={offset:"stroke-dashoffset",array:"stroke-dasharray"},PU={offset:"strokeDashoffset",array:"strokeDasharray"};function OU(i,t,n=1,s=0,o=!0){i.pathLength=1;const c=o?UU:PU;i[c.offset]=`${-s}`,i[c.array]=`${t} ${n}`}const FU=["offsetDistance","offsetPath","offsetRotate","offsetAnchor"];function Jb(i,{attrX:t,attrY:n,attrScale:s,pathLength:o,pathSpacing:c=1,pathOffset:u=0,...d},p,h,g){if(Dg(i,d,h),p){i.style.viewBox&&(i.attrs.viewBox=i.style.viewBox);return}i.attrs=i.style,i.style={};const{attrs:_,style:v}=i;_.transform&&(v.transform=_.transform,delete _.transform),(v.transform||_.transformOrigin)&&(v.transformOrigin=_.transformOrigin??"50% 50%",delete _.transformOrigin),v.transform&&(v.transformBox=g?.transformBox??"fill-box",delete _.transformBox);for(const y of FU)_[y]!==void 0&&(v[y]=_[y],delete _[y]);t!==void 0&&(_.x=t),n!==void 0&&(_.y=n),s!==void 0&&(_.scale=s),o!==void 0&&OU(_,o,c,u,!1)}const $b=new Set(["baseFrequency","diffuseConstant","kernelMatrix","kernelUnitLength","keySplines","keyTimes","limitingConeAngle","markerHeight","markerWidth","numOctaves","targetX","targetY","surfaceScale","specularConstant","specularExponent","stdDeviation","tableValues","viewBox","gradientTransform","pathLength","startOffset","textLength","lengthAdjust"]),tE=i=>typeof i=="string"&&i.toLowerCase()==="svg";function BU(i,t,n,s){Zb(i,t,void 0,s);for(const o in t.attrs)i.setAttribute($b.has(o)?o:Eg(o),t.attrs[o])}function eE(i,t,n){const s=Ng(i,t,n);for(const o in i)if(In(i[o])||In(t[o])){const c=Co.indexOf(o)!==-1?"attr"+o.charAt(0).toUpperCase()+o.substring(1):o;s[c]=i[o]}return s}class IU extends Xb{constructor(){super(...arguments),this.type="svg",this.isSVGTag=!1,this.measureInstanceViewportBox=Tn}getBaseTargetFromProps(t,n){return t[n]}readValueFromInstance(t,n){if(wo.has(n)){const s=Ob(n);return s&&s.default||0}return n=$b.has(n)?n:Eg(n),t.getAttribute(n)}scrapeMotionValuesFromProps(t,n,s){return eE(t,n,s)}build(t,n,s){Jb(t,n,this.isSVGTag,s.transformTemplate,s.style)}renderInstance(t,n,s,o){BU(t,n,s,o)}mount(t){this.isSVGTag=tE(t.tagName),super.mount(t)}}const zU=wg.length;function nE(i){if(!i)return;if(!i.isControllingVariants){const n=i.parent?nE(i.parent)||{}:{};return i.props.initial!==void 0&&(n.initial=i.props.initial),n}const t={};for(let n=0;n<zU;n++){const s=wg[n],o=i.props[s];(jl(o)||o===!1)&&(t[s]=o)}return t}function iE(i,t){if(!Array.isArray(t))return!1;const n=t.length;if(n!==i.length)return!1;for(let s=0;s<n;s++)if(t[s]!==i[s])return!1;return!0}const VU=[...Cg].reverse(),HU=Cg.length;function GU(i){return t=>Promise.all(t.map(({animation:n,options:s})=>IL(i,n,s)))}function kU(i){let t=GU(i),n=uS(),s=!0,o=!1;const c=h=>(g,_)=>{const v=dr(i,_,h==="exit"?i.presenceContext?.custom:void 0);if(v){const{transition:y,transitionEnd:b,...R}=v;g={...g,...R,...b}}return g};function u(h){t=h(i)}function d(h){const{props:g}=i,_=nE(i.parent)||{},v=[],y=new Set;let b={},R=1/0;for(let x=0;x<HU;x++){const A=VU[x],N=n[A],L=g[A]!==void 0?g[A]:_[A],H=jl(L),B=A===h?N.isActive:null;B===!1&&(R=x);let O=L===_[A]&&L!==g[A]&&H;if(O&&(s||o)&&i.manuallyAnimateOnMount&&(O=!1),N.protectedKeys={...b},!N.isActive&&B===null||!L&&!N.prevProp||Ef(L)||typeof L=="boolean")continue;if(A==="exit"&&N.isActive&&B!==!0){N.prevResolvedValues&&(b={...b,...N.prevResolvedValues});continue}const E=jU(N.prevProp,L);let U=E||A===h&&N.isActive&&!O&&H||x>R&&H,V=!1;const F=Array.isArray(L)?L:[L];let j=F.reduce(c(A),{});B===!1&&(j={});const{prevResolvedValues:lt={}}=N,ct={...lt,...j},q=$=>{U=!0,y.has($)&&(V=!0,y.delete($)),N.needsAnimating[$]=!0;const dt=i.getValue($);dt&&(dt.liveStyle=!1)};for(const $ in ct){const dt=j[$],xt=lt[$];if(b.hasOwnProperty($))continue;let z=!1;Fm(dt)&&Fm(xt)?z=!iE(dt,xt)||E:z=dt!==xt,z?dt!=null?q($):y.add($):dt!==void 0&&y.has($)?q($):N.protectedKeys[$]=!0}N.prevProp=L,N.prevResolvedValues=j,N.isActive&&(b={...b,...j}),(s||o)&&i.blockInitialAnimation&&(U=!1);const I=O&&E;U&&(!I||V)&&v.push(...F.map($=>{const dt={type:A};if(typeof $=="string"&&(s||o)&&!I&&i.manuallyAnimateOnMount&&i.parent){const{parent:xt}=i,z=dr(xt,$);if(xt.enteringChildren&&z){const{delayChildren:Q}=z.transition||{};dt.delay=Ab(xt.enteringChildren,i,Q)}}return{animation:$,options:dt}}))}if(y.size){const x={};if(typeof g.initial!="boolean"){const A=dr(i,Array.isArray(g.initial)?g.initial[0]:g.initial);A&&A.transition&&(x.transition=A.transition)}y.forEach(A=>{const N=i.getBaseTarget(A),L=i.getValue(A);L&&(L.liveStyle=!0),x[A]=N??null}),v.push({animation:x})}let S=!!v.length;return s&&(g.initial===!1||g.initial===g.animate)&&!i.manuallyAnimateOnMount&&(S=!1),s=!1,o=!1,S?t(v):Promise.resolve()}function p(h,g){if(n[h].isActive===g)return Promise.resolve();i.variantChildren?.forEach(v=>v.animationState?.setActive(h,g)),n[h].isActive=g;const _=d(h);for(const v in n)n[v].protectedKeys={};return _}return{animateChanges:d,setActive:p,setAnimateFunction:u,getState:()=>n,reset:()=>{n=uS(),o=!0}}}function jU(i,t){return typeof t=="string"?t!==i:Array.isArray(t)?!iE(t,i):!1}function nr(i=!1){return{isActive:i,protectedKeys:{},needsAnimating:{},prevResolvedValues:{}}}function uS(){return{animate:nr(!0),whileInView:nr(),whileHover:nr(),whileTap:nr(),whileDrag:nr(),whileFocus:nr(),exit:nr()}}function Wm(i,t){i.min=t.min,i.max=t.max}function Gi(i,t){Wm(i.x,t.x),Wm(i.y,t.y)}function fS(i,t){i.translate=t.translate,i.scale=t.scale,i.originPoint=t.originPoint,i.origin=t.origin}const aE=1e-4,XU=1-aE,WU=1+aE,sE=.01,qU=0-sE,YU=0+sE;function Yn(i){return i.max-i.min}function KU(i,t,n){return Math.abs(i-t)<=n}function dS(i,t,n,s=.5){i.origin=s,i.originPoint=Ye(t.min,t.max,i.origin),i.scale=Yn(n)/Yn(t),i.translate=Ye(n.min,n.max,i.origin)-i.originPoint,(i.scale>=XU&&i.scale<=WU||isNaN(i.scale))&&(i.scale=1),(i.translate>=qU&&i.translate<=YU||isNaN(i.translate))&&(i.translate=0)}function Bl(i,t,n,s){dS(i.x,t.x,n.x,s?s.originX:void 0),dS(i.y,t.y,n.y,s?s.originY:void 0)}function hS(i,t,n,s=0){const o=s?Ye(n.min,n.max,s):n.min;i.min=o+t.min,i.max=i.min+Yn(t)}function ZU(i,t,n,s){hS(i.x,t.x,n.x,s?.x),hS(i.y,t.y,n.y,s?.y)}function pS(i,t,n,s=0){const o=s?Ye(n.min,n.max,s):n.min;i.min=t.min-o,i.max=i.min+Yn(t)}function pf(i,t,n,s){pS(i.x,t.x,n.x,s?.x),pS(i.y,t.y,n.y,s?.y)}function mS(i,t,n,s,o){return i-=t,i=hf(i,1/n,s),o!==void 0&&(i=hf(i,1/o,s)),i}function QU(i,t=0,n=1,s=.5,o,c=i,u=i){if(ua.test(t)&&(t=parseFloat(t),t=Ye(u.min,u.max,t/100)-u.min),typeof t!="number")return;let d=Ye(c.min,c.max,s);i===c&&(d-=t),i.min=mS(i.min,t,n,d,o),i.max=mS(i.max,t,n,d,o)}function gS(i,t,[n,s,o],c,u){QU(i,t[n],t[s],t[o],t.scale,c,u)}const JU=["x","scaleX","originX"],$U=["y","scaleY","originY"];function _S(i,t,n,s){gS(i.x,t,JU,n?n.x:void 0,s?s.x:void 0),gS(i.y,t,$U,n?n.y:void 0,s?s.y:void 0)}function vS(i){return i.translate===0&&i.scale===1}function rE(i){return vS(i.x)&&vS(i.y)}function xS(i,t){return i.min===t.min&&i.max===t.max}function tP(i,t){return xS(i.x,t.x)&&xS(i.y,t.y)}function yS(i,t){return Math.round(i.min)===Math.round(t.min)&&Math.round(i.max)===Math.round(t.max)}function oE(i,t){return yS(i.x,t.x)&&yS(i.y,t.y)}function SS(i){return Yn(i.x)/Yn(i.y)}function MS(i,t){return i.translate===t.translate&&i.scale===t.scale&&i.originPoint===t.originPoint}function na(i){return[i("x"),i("y")]}function eP(i,t,n){let s="";const o=i.x.translate/t.x,c=i.y.translate/t.y,u=n?.z||0;if((o||c||u)&&(s=`translate3d(${o}px, ${c}px, ${u}px) `),(t.x!==1||t.y!==1)&&(s+=`scale(${1/t.x}, ${1/t.y}) `),n){const{transformPerspective:h,rotate:g,pathRotation:_,rotateX:v,rotateY:y,skewX:b,skewY:R}=n;h&&(s=`perspective(${h}px) ${s}`),g&&(s+=`rotate(${g}deg) `),_&&(s+=`rotate(${_}deg) `),v&&(s+=`rotateX(${v}deg) `),y&&(s+=`rotateY(${y}deg) `),b&&(s+=`skewX(${b}deg) `),R&&(s+=`skewY(${R}deg) `)}const d=i.x.scale*t.x,p=i.y.scale*t.y;return(d!==1||p!==1)&&(s+=`scale(${d}, ${p})`),s||"none"}const lE=["borderTopLeftRadius","borderTopRightRadius","borderBottomLeftRadius","borderBottomRightRadius"],nP=lE.length,bS=i=>typeof i=="string"?parseFloat(i):i,ES=i=>typeof i=="number"||qt.test(i);function iP(i,t,n,s,o,c){o?(i.opacity=Ye(0,n.opacity??1,aP(s)),i.opacityExit=Ye(t.opacity??1,0,sP(s))):c&&(i.opacity=Ye(t.opacity??1,n.opacity??1,s));for(let u=0;u<nP;u++){const d=lE[u];let p=TS(t,d),h=TS(n,d);if(p===void 0&&h===void 0)continue;p||(p=0),h||(h=0),p===0||h===0||ES(p)===ES(h)?(i[d]=Math.max(Ye(bS(p),bS(h),s),0),(ua.test(h)||ua.test(p))&&(i[d]+="%")):i[d]=h}(t.rotate||n.rotate)&&(i.rotate=Ye(t.rotate||0,n.rotate||0,s))}function TS(i,t){return i[t]!==void 0?i[t]:i.borderRadius}const aP=cE(0,.5,tb),sP=cE(.5,.95,Ui);function cE(i,t,n){return s=>s<i?0:s>t?1:n(Gl(i,t,s))}function rP(i,t,n){const s=In(i)?i:Eo(i);return s.start(Mg("",s,t,n)),s.animation}function Xl(i,t,n,s={passive:!0}){return i.addEventListener(t,n,s),()=>i.removeEventListener(t,n)}const oP=(i,t)=>i.depth-t.depth;class lP{constructor(){this.children=[],this.isDirty=!1}add(t){cg(this.children,t),this.isDirty=!0}remove(t){rf(this.children,t),this.isDirty=!0}forEach(t){this.isDirty&&this.children.sort(oP),this.isDirty=!1,this.children.forEach(t)}}function cP(i,t){const n=qn.now(),s=({timestamp:o})=>{const c=o-n;c>=t&&(Ns(s),i(c-t))};return Ke.setup(s,!0),()=>Ns(s)}function Qu(i){return In(i)?i.get():i}class uP{constructor(){this.members=[]}add(t){cg(this.members,t);for(let n=this.members.length-1;n>=0;n--){const s=this.members[n];if(s===t||s===this.lead||s===this.prevLead)continue;const o=s.instance;(!o||o.isConnected===!1)&&!s.snapshot&&(rf(this.members,s),s.unmount())}t.scheduleRender()}remove(t){if(rf(this.members,t),t===this.prevLead&&(this.prevLead=void 0),t===this.lead){const n=this.members[this.members.length-1];n&&this.promote(n)}}relegate(t){for(let n=this.members.indexOf(t)-1;n>=0;n--){const s=this.members[n];if(s.isPresent!==!1&&s.instance?.isConnected!==!1)return this.promote(s),!0}return!1}promote(t,n){const s=this.lead;if(t!==s&&(this.prevLead=s,this.lead=t,t.show(),s)){s.updateSnapshot(),t.scheduleRender();const{layoutDependency:o}=s.options,{layoutDependency:c}=t.options;(o===void 0||o!==c)&&(t.resumeFrom=s,n&&(s.preserveOpacity=!0),s.snapshot&&(t.snapshot=s.snapshot,t.snapshot.latestValues=s.animationValues||s.latestValues),t.root?.isUpdating&&(t.isLayoutDirty=!0)),t.options.crossfade===!1&&s.hide()}}exitAnimationComplete(){this.members.forEach(t=>{t.options.onExitComplete?.(),t.resumingFrom?.options.onExitComplete?.()})}scheduleRender(){this.members.forEach(t=>t.instance&&t.scheduleRender(!1))}removeLeadSnapshot(){this.lead?.snapshot&&(this.lead.snapshot=void 0)}}const Ju={hasAnimatedSinceResize:!0,hasEverUpdated:!1},bp=["","X","Y","Z"],fP=1e3;let dP=0;function Ep(i,t,n,s){const{latestValues:o}=t;o[i]&&(n[i]=o[i],t.setStaticValue(i,0),s&&(s[i]=0))}function uE(i){if(i.hasCheckedOptimisedAppear=!0,i.root===i)return;const{visualElement:t}=i.options;if(!t)return;const n=Nb(t);if(window.MotionHasOptimisedAnimation(n,"transform")){const{layout:o,layoutId:c}=i.options;window.MotionCancelOptimisedAnimation(n,"transform",Ke,!(o||c))}const{parent:s}=i;s&&!s.hasCheckedOptimisedAppear&&uE(s)}function fE({attachResizeListener:i,defaultParent:t,measureScroll:n,checkIsScrollRoot:s,resetTransform:o}){return class{constructor(u={},d=t?.()){this.id=dP++,this.animationId=0,this.animationCommitId=0,this.children=new Set,this.options={},this.isTreeAnimating=!1,this.isAnimationBlocked=!1,this.isLayoutDirty=!1,this.isProjectionDirty=!1,this.isSharedProjectionDirty=!1,this.isTransformDirty=!1,this.updateManuallyBlocked=!1,this.updateBlockedByResize=!1,this.isUpdating=!1,this.isSVG=!1,this.needsReset=!1,this.shouldResetTransform=!1,this.hasCheckedOptimisedAppear=!1,this.treeScale={x:1,y:1},this.eventHandlers=new Map,this.hasTreeAnimated=!1,this.layoutVersion=0,this.updateScheduled=!1,this.scheduleUpdate=()=>this.update(),this.projectionUpdateScheduled=!1,this.checkUpdateFailed=()=>{this.isUpdating&&(this.isUpdating=!1,this.clearAllSnapshots())},this.updateProjection=()=>{this.projectionUpdateScheduled=!1,this.nodes.forEach(mP),this.nodes.forEach(SP),this.nodes.forEach(MP),this.nodes.forEach(gP)},this.resolvedRelativeTargetAt=0,this.linkedParentVersion=0,this.hasProjected=!1,this.isVisible=!0,this.animationProgress=0,this.sharedNodes=new Map,this.latestValues=u,this.root=d?d.root||d:this,this.path=d?[...d.path,d]:[],this.parent=d,this.depth=d?d.depth+1:0;for(let p=0;p<this.path.length;p++)this.path[p].shouldResetTransform=!0;this.root===this&&(this.nodes=new lP)}addEventListener(u,d){return this.eventHandlers.has(u)||this.eventHandlers.set(u,new fg),this.eventHandlers.get(u).add(d)}notifyListeners(u,...d){const p=this.eventHandlers.get(u);p&&p.notify(...d)}hasListeners(u){return this.eventHandlers.has(u)}mount(u){if(this.instance)return;this.isSVG=Rg(u)&&!pU(u),this.instance=u;const{layoutId:d,layout:p,visualElement:h}=this.options;if(h&&!h.current&&h.mount(u),this.root.nodes.add(this),this.parent&&this.parent.children.add(this),this.root.hasTreeAnimated&&(p||d)&&(this.isLayoutDirty=!0),i){let g,_=0;const v=()=>this.root.updateBlockedByResize=!1;Ke.read(()=>{_=window.innerWidth}),i(u,()=>{const y=window.innerWidth;y!==_&&(_=y,this.root.updateBlockedByResize=!0,g&&g(),g=cP(v,250),Ju.hasAnimatedSinceResize&&(Ju.hasAnimatedSinceResize=!1,this.nodes.forEach(CS)))})}d&&this.root.registerSharedNode(d,this),this.options.animate!==!1&&h&&(d||p)&&this.addEventListener("didUpdate",({delta:g,hasLayoutChanged:_,hasRelativeLayoutChanged:v,layout:y})=>{if(this.isTreeAnimationBlocked()){this.target=void 0,this.relativeTarget=void 0;return}const b=this.options.transition||h.getDefaultTransition()||RP,{onLayoutAnimationStart:R,onLayoutAnimationComplete:S}=h.getProps(),x=!this.targetLayout||!oE(this.targetLayout,y),A=!_&&v;if(this.options.layoutRoot||this.resumeFrom||A||_&&(x||!this.currentAnimation)){this.resumeFrom&&(this.resumingFrom=this.resumeFrom,this.resumingFrom.resumingFrom=void 0);const N={...Sg(b,"layout"),onPlay:R,onComplete:S};(h.shouldReduceMotion||this.options.layoutRoot)&&(N.delay=0,N.type=!1),this.startAnimation(N),this.setAnimationOrigin(g,A,N.path)}else _||CS(this),this.isLead()&&this.options.onExitComplete&&this.options.onExitComplete();this.targetLayout=y})}unmount(){this.options.layoutId&&this.willUpdate(),this.root.nodes.remove(this);const u=this.getStack();u&&u.remove(this),this.parent&&this.parent.children.delete(this),this.instance=void 0,this.eventHandlers.clear(),Ns(this.updateProjection)}blockUpdate(){this.updateManuallyBlocked=!0}unblockUpdate(){this.updateManuallyBlocked=!1}isUpdateBlocked(){return this.updateManuallyBlocked||this.updateBlockedByResize}isTreeAnimationBlocked(){return this.isAnimationBlocked||this.parent&&this.parent.isTreeAnimationBlocked()||!1}startUpdate(){this.isUpdateBlocked()||(this.isUpdating=!0,this.nodes&&this.nodes.forEach(bP),this.animationId++)}getTransformTemplate(){const{visualElement:u}=this.options;return u&&u.getProps().transformTemplate}willUpdate(u=!0){if(this.root.hasTreeAnimated=!0,this.root.isUpdateBlocked()){this.options.onExitComplete&&this.options.onExitComplete();return}if(window.MotionCancelOptimisedAnimation&&!this.hasCheckedOptimisedAppear&&uE(this),!this.root.isUpdating&&this.root.startUpdate(),this.isLayoutDirty)return;this.isLayoutDirty=!0;for(let g=0;g<this.path.length;g++){const _=this.path[g];_.shouldResetTransform=!0,(typeof _.latestValues.x=="string"||typeof _.latestValues.y=="string")&&(_.isLayoutDirty=!0),_.updateScroll("snapshot"),_.options.layoutRoot&&_.willUpdate(!1)}const{layoutId:d,layout:p}=this.options;if(d===void 0&&!p)return;const h=this.getTransformTemplate();this.prevTransformTemplateValue=h?h(this.latestValues,""):void 0,this.updateSnapshot(),u&&this.notifyListeners("willUpdate")}update(){if(this.updateScheduled=!1,this.isUpdateBlocked()){const p=this.updateBlockedByResize;this.unblockUpdate(),this.updateBlockedByResize=!1,this.clearAllSnapshots(),p&&this.nodes.forEach(vP),this.nodes.forEach(AS);return}if(this.animationId<=this.animationCommitId){this.nodes.forEach(RS);return}this.animationCommitId=this.animationId,this.isUpdating?(this.isUpdating=!1,this.nodes.forEach(xP),this.nodes.forEach(yP),this.nodes.forEach(hP),this.nodes.forEach(pP)):this.nodes.forEach(RS),this.clearAllSnapshots();const d=qn.now();Fn.delta=ha(0,1e3/60,d-Fn.timestamp),Fn.timestamp=d,Fn.isProcessing=!0,mp.update.process(Fn),mp.preRender.process(Fn),mp.render.process(Fn),Fn.isProcessing=!1}didUpdate(){this.updateScheduled||(this.updateScheduled=!0,Tg.read(this.scheduleUpdate))}clearAllSnapshots(){this.nodes.forEach(_P),this.sharedNodes.forEach(EP)}scheduleUpdateProjection(){this.projectionUpdateScheduled||(this.projectionUpdateScheduled=!0,Ke.preRender(this.updateProjection,!1,!0))}scheduleCheckAfterUnmount(){Ke.postRender(()=>{this.isLayoutDirty?this.root.didUpdate():this.root.checkUpdateFailed()})}updateSnapshot(){this.snapshot||!this.instance||(this.snapshot=this.measure(),this.snapshot&&!Yn(this.snapshot.measuredBox.x)&&!Yn(this.snapshot.measuredBox.y)&&(this.snapshot=void 0))}updateLayout(){if(!this.instance||(this.updateScroll(),!(this.options.alwaysMeasureLayout&&this.isLead())&&!this.isLayoutDirty))return;if(this.resumeFrom&&!this.resumeFrom.instance)for(let p=0;p<this.path.length;p++)this.path[p].updateScroll();const u=this.layout;this.layout=this.measure(!1),this.layoutVersion++,this.layoutCorrected||(this.layoutCorrected=Tn()),this.isLayoutDirty=!1,this.projectionDelta=void 0,this.notifyListeners("measure",this.layout.layoutBox);const{visualElement:d}=this.options;d&&d.notify("LayoutMeasure",this.layout.layoutBox,u?u.layoutBox:void 0)}updateScroll(u="measure"){let d=!!(this.options.layoutScroll&&this.instance);if(this.scroll&&this.scroll.animationId===this.root.animationId&&this.scroll.phase===u&&(d=!1),d&&this.instance){const p=s(this.instance);this.scroll={animationId:this.root.animationId,phase:u,isRoot:p,offset:n(this.instance),wasRoot:this.scroll?this.scroll.isRoot:p}}}resetTransform(){if(!o)return;const u=this.isLayoutDirty||this.shouldResetTransform||this.options.alwaysMeasureLayout,d=this.projectionDelta&&!rE(this.projectionDelta),p=this.getTransformTemplate(),h=p?p(this.latestValues,""):void 0,g=h!==this.prevTransformTemplateValue;u&&this.instance&&(d||ar(this.latestValues)||g)&&(o(this.instance,h),this.shouldResetTransform=!1,this.scheduleRender())}measure(u=!0){const d=this.measurePageBox();let p=this.removeElementScroll(d);return u&&(p=this.removeTransform(p)),CP(p),{animationId:this.root.animationId,measuredBox:d,layoutBox:p,latestValues:{},source:this.id}}measurePageBox(){const{visualElement:u}=this.options;if(!u)return Tn();const d=u.measureViewportBox();if(!(this.scroll?.wasRoot||this.path.some(wP))){const{scroll:h}=this.root;h&&(aa(d.x,h.offset.x),aa(d.y,h.offset.y))}return d}removeElementScroll(u){const d=Tn();if(Gi(d,u),this.scroll?.wasRoot)return d;for(let p=0;p<this.path.length;p++){const h=this.path[p],{scroll:g,options:_}=h;h!==this.root&&g&&_.layoutScroll&&(g.wasRoot&&Gi(d,u),aa(d.x,g.offset.x),aa(d.y,g.offset.y))}return d}applyTransform(u,d=!1,p){const h=p||Tn();Gi(h,u);for(let g=0;g<this.path.length;g++){const _=this.path[g];!d&&_.options.layoutScroll&&_.scroll&&_!==_.root&&(aa(h.x,-_.scroll.offset.x),aa(h.y,-_.scroll.offset.y)),ar(_.latestValues)&&Zu(h,_.latestValues,_.layout?.layoutBox)}return ar(this.latestValues)&&Zu(h,this.latestValues,this.layout?.layoutBox),h}removeTransform(u){const d=Tn();Gi(d,u);for(let p=0;p<this.path.length;p++){const h=this.path[p];if(!ar(h.latestValues))continue;let g;h.instance&&(km(h.latestValues)&&h.updateSnapshot(),g=Tn(),Gi(g,h.measurePageBox())),_S(d,h.latestValues,h.snapshot?.layoutBox,g)}return ar(this.latestValues)&&_S(d,this.latestValues),d}setTargetDelta(u){this.targetDelta=u,this.root.scheduleUpdateProjection(),this.isProjectionDirty=!0}setOptions(u){this.options={...this.options,...u,crossfade:u.crossfade!==void 0?u.crossfade:!0}}clearMeasurements(){this.scroll=void 0,this.layout=void 0,this.snapshot=void 0,this.prevTransformTemplateValue=void 0,this.targetDelta=void 0,this.target=void 0,this.isLayoutDirty=!1}forceRelativeParentToResolveTarget(){this.relativeParent&&this.relativeParent.resolvedRelativeTargetAt!==Fn.timestamp&&this.relativeParent.resolveTargetDelta(!0)}resolveTargetDelta(u=!1){const d=this.getLead();this.isProjectionDirty||(this.isProjectionDirty=d.isProjectionDirty),this.isTransformDirty||(this.isTransformDirty=d.isTransformDirty),this.isSharedProjectionDirty||(this.isSharedProjectionDirty=d.isSharedProjectionDirty);const p=!!this.resumingFrom||this!==d;if(!(u||p&&this.isSharedProjectionDirty||this.isProjectionDirty||this.parent?.isProjectionDirty||this.attemptToResolveRelativeTarget||this.root.updateBlockedByResize))return;const{layout:g,layoutId:_}=this.options;if(!this.layout||!(g||_))return;this.resolvedRelativeTargetAt=Fn.timestamp;const v=this.getClosestProjectingParent();v&&this.linkedParentVersion!==v.layoutVersion&&!v.options.layoutRoot&&this.removeRelativeTarget(),!this.targetDelta&&!this.relativeTarget&&(this.options.layoutAnchor!==!1&&v&&v.layout?this.createRelativeTarget(v,this.layout.layoutBox,v.layout.layoutBox):this.removeRelativeTarget()),!(!this.relativeTarget&&!this.targetDelta)&&(this.target||(this.target=Tn(),this.targetWithTransforms=Tn()),this.relativeTarget&&this.relativeTargetOrigin&&this.relativeParent&&this.relativeParent.target?(this.forceRelativeParentToResolveTarget(),ZU(this.target,this.relativeTarget,this.relativeParent.target,this.options.layoutAnchor||void 0)):this.targetDelta?(this.resumingFrom?this.applyTransform(this.layout.layoutBox,!1,this.target):Gi(this.target,this.layout.layoutBox),Yb(this.target,this.targetDelta)):Gi(this.target,this.layout.layoutBox),this.attemptToResolveRelativeTarget&&(this.attemptToResolveRelativeTarget=!1,this.options.layoutAnchor!==!1&&v&&!!v.resumingFrom==!!this.resumingFrom&&!v.options.layoutScroll&&v.target&&this.animationProgress!==1?this.createRelativeTarget(v,this.target,v.target):this.relativeParent=this.relativeTarget=void 0))}getClosestProjectingParent(){if(!(!this.parent||km(this.parent.latestValues)||qb(this.parent.latestValues)))return this.parent.isProjecting()?this.parent:this.parent.getClosestProjectingParent()}isProjecting(){return!!((this.relativeTarget||this.targetDelta||this.options.layoutRoot)&&this.layout)}createRelativeTarget(u,d,p){this.relativeParent=u,this.linkedParentVersion=u.layoutVersion,this.forceRelativeParentToResolveTarget(),this.relativeTarget=Tn(),this.relativeTargetOrigin=Tn(),pf(this.relativeTargetOrigin,d,p,this.options.layoutAnchor||void 0),Gi(this.relativeTarget,this.relativeTargetOrigin)}removeRelativeTarget(){this.relativeParent=this.relativeTarget=void 0}calcProjection(){const u=this.getLead(),d=!!this.resumingFrom||this!==u;let p=!0;if((this.isProjectionDirty||this.parent?.isProjectionDirty)&&(p=!1),d&&(this.isSharedProjectionDirty||this.isTransformDirty)&&(p=!1),this.resolvedRelativeTargetAt===Fn.timestamp&&(p=!1),p)return;const{layout:h,layoutId:g}=this.options;if(this.isTreeAnimating=!!(this.parent&&this.parent.isTreeAnimating||this.currentAnimation||this.pendingAnimation),this.isTreeAnimating||(this.targetDelta=this.relativeTarget=void 0),!this.layout||!(h||g))return;Gi(this.layoutCorrected,this.layout.layoutBox);const _=this.treeScale.x,v=this.treeScale.y;TU(this.layoutCorrected,this.treeScale,this.path,d),u.layout&&!u.target&&(this.treeScale.x!==1||this.treeScale.y!==1)&&(u.target=u.layout.layoutBox,u.targetWithTransforms=Tn());const{target:y}=u;if(!y){this.prevProjectionDelta&&(this.createProjectionDeltas(),this.scheduleRender());return}!this.projectionDelta||!this.prevProjectionDelta?this.createProjectionDeltas():(fS(this.prevProjectionDelta.x,this.projectionDelta.x),fS(this.prevProjectionDelta.y,this.projectionDelta.y)),Bl(this.projectionDelta,this.layoutCorrected,y,this.latestValues),(this.treeScale.x!==_||this.treeScale.y!==v||!MS(this.projectionDelta.x,this.prevProjectionDelta.x)||!MS(this.projectionDelta.y,this.prevProjectionDelta.y))&&(this.hasProjected=!0,this.scheduleRender(),this.notifyListeners("projectionUpdate",y))}hide(){this.isVisible=!1}show(){this.isVisible=!0}scheduleRender(u=!0){if(this.options.visualElement?.scheduleRender(),u){const d=this.getStack();d&&d.scheduleRender()}this.resumingFrom&&!this.resumingFrom.instance&&(this.resumingFrom=void 0)}createProjectionDeltas(){this.prevProjectionDelta=mo(),this.projectionDelta=mo(),this.projectionDeltaWithTransform=mo()}setAnimationOrigin(u,d=!1,p){const h=this.snapshot,g=h?h.latestValues:{},_={...this.latestValues},v=mo();(!this.relativeParent||!this.relativeParent.options.layoutRoot)&&(this.relativeTarget=this.relativeTargetOrigin=void 0),this.attemptToResolveRelativeTarget=!d;const y=Tn(),b=h?h.source:void 0,R=this.layout?this.layout.source:void 0,S=b!==R,x=this.getStack(),A=!x||x.members.length<=1,N=!!(S&&!A&&this.options.crossfade===!0&&!this.path.some(AP));this.animationProgress=0;let L;const H=p?.interpolateProjection(u);this.mixTargetDelta=B=>{const O=B/1e3,E=H?.(O);E?(v.x.translate=E.x,v.x.scale=Ye(u.x.scale,1,O),v.x.origin=u.x.origin,v.x.originPoint=u.x.originPoint,v.y.translate=E.y,v.y.scale=Ye(u.y.scale,1,O),v.y.origin=u.y.origin,v.y.originPoint=u.y.originPoint):(wS(v.x,u.x,O),wS(v.y,u.y,O)),this.setTargetDelta(v),this.relativeTarget&&this.relativeTargetOrigin&&this.layout&&this.relativeParent&&this.relativeParent.layout&&(pf(y,this.layout.layoutBox,this.relativeParent.layout.layoutBox,this.options.layoutAnchor||void 0),TP(this.relativeTarget,this.relativeTargetOrigin,y,O),L&&tP(this.relativeTarget,L)&&(this.isProjectionDirty=!1),L||(L=Tn()),Gi(L,this.relativeTarget)),S&&(this.animationValues=_,iP(_,g,this.latestValues,O,N,A)),E&&E.rotate!==void 0&&(this.animationValues||(this.animationValues=_),this.animationValues.pathRotation=E.rotate),this.root.scheduleUpdateProjection(),this.scheduleRender(),this.animationProgress=O},this.mixTargetDelta(this.options.layoutRoot?1e3:0)}startAnimation(u){this.notifyListeners("animationStart"),this.currentAnimation?.stop(),this.resumingFrom?.currentAnimation?.stop(),this.pendingAnimation&&(Ns(this.pendingAnimation),this.pendingAnimation=void 0),this.pendingAnimation=Ke.update(()=>{Ju.hasAnimatedSinceResize=!0,this.motionValue||(this.motionValue=Eo(0)),this.motionValue.jump(0,!1),this.currentAnimation=rP(this.motionValue,[0,1e3],{...u,velocity:0,isSync:!0,onUpdate:d=>{this.mixTargetDelta(d),u.onUpdate&&u.onUpdate(d)},onStop:()=>{},onComplete:()=>{u.onComplete&&u.onComplete(),this.completeAnimation()}}),this.resumingFrom&&(this.resumingFrom.currentAnimation=this.currentAnimation),this.pendingAnimation=void 0})}completeAnimation(){this.resumingFrom&&(this.resumingFrom.currentAnimation=void 0,this.resumingFrom.preserveOpacity=void 0);const u=this.getStack();u&&u.exitAnimationComplete(),this.resumingFrom=this.currentAnimation=this.animationValues=void 0,this.notifyListeners("animationComplete")}finishAnimation(){this.currentAnimation&&(this.mixTargetDelta&&this.mixTargetDelta(fP),this.currentAnimation.stop()),this.completeAnimation()}applyTransformsToTarget(){const u=this.getLead();let{targetWithTransforms:d,target:p,layout:h,latestValues:g}=u;if(!(!d||!p||!h)){if(this!==u&&this.layout&&h&&dE(this.options.animationType,this.layout.layoutBox,h.layoutBox)){p=this.target||Tn();const _=Yn(this.layout.layoutBox.x);p.x.min=u.target.x.min,p.x.max=p.x.min+_;const v=Yn(this.layout.layoutBox.y);p.y.min=u.target.y.min,p.y.max=p.y.min+v}Gi(d,p),Zu(d,g),Bl(this.projectionDeltaWithTransform,this.layoutCorrected,d,g)}}registerSharedNode(u,d){this.sharedNodes.has(u)||this.sharedNodes.set(u,new uP),this.sharedNodes.get(u).add(d);const h=d.options.initialPromotionConfig;d.promote({transition:h?h.transition:void 0,preserveFollowOpacity:h&&h.shouldPreserveFollowOpacity?h.shouldPreserveFollowOpacity(d):void 0})}isLead(){const u=this.getStack();return u?u.lead===this:!0}getLead(){const{layoutId:u}=this.options;return u?this.getStack()?.lead||this:this}getPrevLead(){const{layoutId:u}=this.options;return u?this.getStack()?.prevLead:void 0}getStack(){const{layoutId:u}=this.options;if(u)return this.root.sharedNodes.get(u)}promote({needsReset:u,transition:d,preserveFollowOpacity:p}={}){const h=this.getStack();h&&h.promote(this,p),u&&(this.projectionDelta=void 0,this.needsReset=!0),d&&this.setOptions({transition:d})}relegate(){const u=this.getStack();return u?u.relegate(this):!1}resetSkewAndRotation(){const{visualElement:u}=this.options;if(!u)return;let d=!1;const{latestValues:p}=u;if((p.z||p.rotate||p.rotateX||p.rotateY||p.rotateZ||p.skewX||p.skewY)&&(d=!0),!d)return;const h={};p.z&&Ep("z",u,h,this.animationValues);for(let g=0;g<bp.length;g++)Ep(`rotate${bp[g]}`,u,h,this.animationValues),Ep(`skew${bp[g]}`,u,h,this.animationValues);u.render();for(const g in h)u.setStaticValue(g,h[g]),this.animationValues&&(this.animationValues[g]=h[g]);u.scheduleRender()}applyProjectionStyles(u,d){if(!this.instance||this.isSVG)return;if(!this.isVisible){u.visibility="hidden";return}const p=this.getTransformTemplate();if(this.needsReset){this.needsReset=!1,u.visibility="",u.opacity="",u.pointerEvents=Qu(d?.pointerEvents)||"",u.transform=p?p(this.latestValues,""):"none";return}const h=this.getLead();if(!this.projectionDelta||!this.layout||!h.target){this.options.layoutId&&(u.opacity=this.latestValues.opacity!==void 0?this.latestValues.opacity:1,u.pointerEvents=Qu(d?.pointerEvents)||""),this.hasProjected&&!ar(this.latestValues)&&(u.transform=p?p({},""):"none",this.hasProjected=!1);return}u.visibility="";const g=h.animationValues||h.latestValues;this.applyTransformsToTarget();let _=eP(this.projectionDeltaWithTransform,this.treeScale,g);p&&(_=p(g,_)),u.transform=_;const{x:v,y}=this.projectionDelta;u.transformOrigin=`${v.origin*100}% ${y.origin*100}% 0`,h.animationValues?u.opacity=h===this?g.opacity??this.latestValues.opacity??1:this.preserveOpacity?this.latestValues.opacity:g.opacityExit:u.opacity=h===this?g.opacity!==void 0?g.opacity:"":g.opacityExit!==void 0?g.opacityExit:0;for(const b in Xm){if(g[b]===void 0)continue;const{correct:R,applyTo:S,isCSSVariable:x}=Xm[b],A=_==="none"?g[b]:R(g[b],h);if(S){const N=S.length;for(let L=0;L<N;L++)u[S[L]]=A}else x?this.options.visualElement.renderState.vars[b]=A:u[b]=A}this.options.layoutId&&(u.pointerEvents=h===this?Qu(d?.pointerEvents)||"":"none")}clearSnapshot(){this.resumeFrom=this.snapshot=void 0}resetTree(){this.root.nodes.forEach(u=>u.currentAnimation?.stop()),this.root.nodes.forEach(AS),this.root.sharedNodes.clear()}}}function hP(i){i.updateLayout()}function pP(i){const t=i.resumeFrom?.snapshot||i.snapshot;if(i.isLead()&&i.layout&&t&&i.hasListeners("didUpdate")){const{layoutBox:n,measuredBox:s}=i.layout,{animationType:o}=i.options,c=t.source!==i.layout.source;if(o==="size")na(g=>{const _=c?t.measuredBox[g]:t.layoutBox[g],v=Yn(_);_.min=n[g].min,_.max=_.min+v});else if(o==="x"||o==="y"){const g=o==="x"?"y":"x";Wm(c?t.measuredBox[g]:t.layoutBox[g],n[g])}else dE(o,t.layoutBox,n)&&na(g=>{const _=c?t.measuredBox[g]:t.layoutBox[g],v=Yn(n[g]);_.max=_.min+v,i.relativeTarget&&!i.currentAnimation&&(i.isProjectionDirty=!0,i.relativeTarget[g].max=i.relativeTarget[g].min+v)});const u=mo();Bl(u,n,t.layoutBox);const d=mo();c?Bl(d,i.applyTransform(s,!0),t.measuredBox):Bl(d,n,t.layoutBox);const p=!rE(u);let h=!1;if(!i.resumeFrom){const g=i.getClosestProjectingParent();if(g&&!g.resumeFrom){const{snapshot:_,layout:v}=g;if(_&&v){const y=i.options.layoutAnchor||void 0,b=Tn();pf(b,t.layoutBox,_.layoutBox,y);const R=Tn();pf(R,n,v.layoutBox,y),oE(b,R)||(h=!0),g.options.layoutRoot&&(i.relativeTarget=R,i.relativeTargetOrigin=b,i.relativeParent=g)}}}i.notifyListeners("didUpdate",{layout:n,snapshot:t,delta:d,layoutDelta:u,hasLayoutChanged:p,hasRelativeLayoutChanged:h})}else if(i.isLead()){const{onExitComplete:n}=i.options;n&&n()}i.options.transition=void 0}function mP(i){i.parent&&(i.isProjecting()||(i.isProjectionDirty=i.parent.isProjectionDirty),i.isSharedProjectionDirty||(i.isSharedProjectionDirty=!!(i.isProjectionDirty||i.parent.isProjectionDirty||i.parent.isSharedProjectionDirty)),i.isTransformDirty||(i.isTransformDirty=i.parent.isTransformDirty))}function gP(i){i.isProjectionDirty=i.isSharedProjectionDirty=i.isTransformDirty=!1}function _P(i){i.clearSnapshot()}function AS(i){i.clearMeasurements()}function vP(i){i.isLayoutDirty=!0,i.updateLayout()}function RS(i){i.isLayoutDirty=!1}function xP(i){i.isAnimationBlocked&&i.layout&&!i.isLayoutDirty&&(i.snapshot=i.layout,i.isLayoutDirty=!0)}function yP(i){const{visualElement:t}=i.options;t&&t.getProps().onBeforeLayoutMeasure&&t.notify("BeforeLayoutMeasure"),i.resetTransform()}function CS(i){i.finishAnimation(),i.targetDelta=i.relativeTarget=i.target=void 0,i.isProjectionDirty=!0}function SP(i){i.resolveTargetDelta()}function MP(i){i.calcProjection()}function bP(i){i.resetSkewAndRotation()}function EP(i){i.removeLeadSnapshot()}function wS(i,t,n){i.translate=Ye(t.translate,0,n),i.scale=Ye(t.scale,1,n),i.origin=t.origin,i.originPoint=t.originPoint}function DS(i,t,n,s){i.min=Ye(t.min,n.min,s),i.max=Ye(t.max,n.max,s)}function TP(i,t,n,s){DS(i.x,t.x,n.x,s),DS(i.y,t.y,n.y,s)}function AP(i){return i.animationValues&&i.animationValues.opacityExit!==void 0}const RP={duration:.45,ease:[.4,0,.1,1]},NS=i=>typeof navigator<"u"&&navigator.userAgent&&navigator.userAgent.toLowerCase().includes(i),LS=NS("applewebkit/")&&!NS("chrome/")?Math.round:Ui;function US(i){i.min=LS(i.min),i.max=LS(i.max)}function CP(i){US(i.x),US(i.y)}function dE(i,t,n){return i==="position"||i==="preserve-aspect"&&!KU(SS(t),SS(n),.2)}function wP(i){return i!==i.root&&i.scroll?.wasRoot}const DP=fE({attachResizeListener:(i,t)=>Xl(i,"resize",t),measureScroll:()=>({x:document.documentElement.scrollLeft||document.body?.scrollLeft||0,y:document.documentElement.scrollTop||document.body?.scrollTop||0}),checkIsScrollRoot:()=>!0}),Tp={current:void 0},hE=fE({measureScroll:i=>({x:i.scrollLeft,y:i.scrollTop}),defaultParent:()=>{if(!Tp.current){const i=new DP({});i.mount(window),i.setOptions({layoutScroll:!0}),Tp.current=i}return Tp.current},resetTransform:(i,t)=>{i.style.transform=t!==void 0?t:"none"},checkIsScrollRoot:i=>window.getComputedStyle(i).position==="fixed"}),pE=yt.createContext({transformPagePoint:i=>i,isStatic:!1,reducedMotion:"never"});function NP(i=!0){const t=yt.useContext(lg);if(t===null)return[!0,null];const{isPresent:n,onExitComplete:s,register:o}=t,c=yt.useId();yt.useEffect(()=>{if(i)return o(c)},[i]);const u=yt.useCallback(()=>i&&s&&s(c),[c,s,i]);return!n&&s?[!1,u]:[!0]}const mE=yt.createContext({strict:!1}),PS={animation:["animate","variants","whileHover","whileTap","exit","whileInView","whileFocus","whileDrag"],exit:["exit"],drag:["drag","dragControls"],focus:["whileFocus"],hover:["whileHover","onHoverStart","onHoverEnd"],tap:["whileTap","onTap","onTapStart","onTapCancel"],pan:["onPan","onPanStart","onPanSessionStart","onPanEnd"],inView:["whileInView","onViewportEnter","onViewportLeave"],layout:["layout","layoutId"]};let OS=!1;function LP(){if(OS)return;const i={};for(const t in PS)i[t]={isEnabled:n=>PS[t].some(s=>!!n[s])};jb(i),OS=!0}function gE(){return LP(),SU()}function UP(i){const t=gE();for(const n in i)t[n]={...t[n],...i[n]};jb(t)}const PP=new Set(["animate","exit","variants","initial","style","values","variants","transition","transformTemplate","custom","inherit","onBeforeLayoutMeasure","onAnimationStart","onAnimationComplete","onUpdate","onDragStart","onDrag","onDragEnd","onMeasureDragConstraints","onDirectionLock","onDragTransitionEnd","_dragX","_dragY","onHoverStart","onHoverEnd","onViewportEnter","onViewportLeave","globalTapTarget","propagate","ignoreStrict","viewport"]);function mf(i){return i.startsWith("while")||i.startsWith("drag")&&i!=="draggable"||i.startsWith("layout")||i.startsWith("onTap")||i.startsWith("onPan")||i.startsWith("onLayout")||PP.has(i)}let _E=i=>!mf(i);function OP(i){typeof i=="function"&&(_E=t=>t.startsWith("on")?!mf(t):i(t))}try{OP(require("@emotion/is-prop-valid").default)}catch{}function FP(i,t,n){const s={};for(const o in i)o==="values"&&typeof i.values=="object"||In(i[o])||(_E(o)||n===!0&&mf(o)||!t&&!mf(o)||i.draggable&&o.startsWith("onDrag"))&&(s[o]=i[o]);return s}const Af=yt.createContext({});function BP(i,t){if(Tf(i)){const{initial:n,animate:s}=i;return{initial:n===!1||jl(n)?n:void 0,animate:jl(s)?s:void 0}}return i.inherit!==!1?t:{}}function IP(i){const{initial:t,animate:n}=BP(i,yt.useContext(Af));return yt.useMemo(()=>({initial:t,animate:n}),[FS(t),FS(n)])}function FS(i){return Array.isArray(i)?i.join(" "):i}const Lg=()=>({style:{},transform:{},transformOrigin:{},vars:{}});function vE(i,t,n){for(const s in t)!In(t[s])&&!Qb(s,n)&&(i[s]=t[s])}function zP({transformTemplate:i},t){return yt.useMemo(()=>{const n=Lg();return Dg(n,t,i),Object.assign({},n.vars,n.style)},[t])}function VP(i,t){const n=i.style||{},s={};return vE(s,n,i),Object.assign(s,zP(i,t)),s}function HP(i,t){const n={},s=VP(i,t);return i.drag&&i.dragListener!==!1&&(n.draggable=!1,s.userSelect=s.WebkitUserSelect=s.WebkitTouchCallout="none",s.touchAction=i.drag===!0?"none":`pan-${i.drag==="x"?"y":"x"}`),i.tabIndex===void 0&&(i.onTap||i.onTapStart||i.whileTap)&&(n.tabIndex=0),n.style=s,n}const xE=()=>({...Lg(),attrs:{}});function GP(i,t,n,s){const o=yt.useMemo(()=>{const c=xE();return Jb(c,t,tE(s),i.transformTemplate,i.style),{...c.attrs,style:{...c.style}}},[t]);if(i.style){const c={};vE(c,i.style,i),o.style={...c,...o.style}}return o}const kP=["animate","circle","defs","desc","ellipse","g","image","line","filter","marker","mask","metadata","path","pattern","polygon","polyline","rect","stop","switch","symbol","svg","text","tspan","use","view"];function Ug(i){return typeof i!="string"||i.includes("-")?!1:!!(kP.indexOf(i)>-1||/[A-Z]/u.test(i))}function jP(i,t,n,{latestValues:s},o,c=!1,u){const p=(u??Ug(i)?GP:HP)(t,s,o,i),h=FP(t,typeof i=="string",c),g=i!==yt.Fragment?{...h,...p,ref:n}:{},{children:_}=t,v=yt.useMemo(()=>In(_)?_.get():_,[_]);return yt.createElement(i,{...g,children:v})}function XP({scrapeMotionValuesFromProps:i,createRenderState:t},n,s,o){return{latestValues:WP(n,s,o,i),renderState:t()}}function WP(i,t,n,s){const o={},c=s(i,{});for(const v in c)o[v]=Qu(c[v]);let{initial:u,animate:d}=i;const p=Tf(i),h=Gb(i);t&&h&&!p&&i.inherit!==!1&&(u===void 0&&(u=t.initial),d===void 0&&(d=t.animate));let g=n?n.initial===!1:!1;g=g||u===!1;const _=g?d:u;if(_&&typeof _!="boolean"&&!Ef(_)){const v=Array.isArray(_)?_:[_];for(let y=0;y<v.length;y++){const b=bg(i,v[y]);if(b){const{transitionEnd:R,transition:S,...x}=b;for(const A in x){let N=x[A];if(Array.isArray(N)){const L=g?N.length-1:0;N=N[L]}N!==null&&(o[A]=N)}for(const A in R)o[A]=R[A]}}}return o}const yE=i=>(t,n)=>{const s=yt.useContext(Af),o=yt.useContext(lg),c=()=>XP(i,t,s,o);return n?c():jD(c)},qP=yE({scrapeMotionValuesFromProps:Ng,createRenderState:Lg}),YP=yE({scrapeMotionValuesFromProps:eE,createRenderState:xE}),KP=Symbol.for("motionComponentSymbol");function ZP(i,t,n){const s=yt.useRef(n);yt.useInsertionEffect(()=>{s.current=n});const o=yt.useRef(null);return yt.useCallback(c=>{c&&i.onMount?.(c),t&&(c?t.mount(c):t.unmount());const u=s.current;if(typeof u=="function")if(c){const d=u(c);typeof d=="function"&&(o.current=d)}else o.current?(o.current(),o.current=null):u(c);else u&&(u.current=c)},[t])}const SE=yt.createContext({});function fo(i){return i&&typeof i=="object"&&Object.prototype.hasOwnProperty.call(i,"current")}function QP(i,t,n,s,o,c){const{visualElement:u}=yt.useContext(Af),d=yt.useContext(mE),p=yt.useContext(lg),h=yt.useContext(pE),g=h.reducedMotion,_=h.skipAnimations,v=yt.useRef(null),y=yt.useRef(!1);s=s||d.renderer,!v.current&&s&&(v.current=s(i,{visualState:t,parent:u,props:n,presenceContext:p,blockInitialAnimation:p?p.initial===!1:!1,reducedMotionConfig:g,skipAnimations:_,isSVG:c}),y.current&&v.current&&(v.current.manuallyAnimateOnMount=!0));const b=v.current,R=yt.useContext(SE);b&&!b.projection&&o&&(b.type==="html"||b.type==="svg")&&JP(v.current,n,o,R);const S=yt.useRef(!1);yt.useInsertionEffect(()=>{b&&S.current&&b.update(n,p)});const x=n[Db],A=yt.useRef(!!x&&typeof window<"u"&&!window.MotionHandoffIsComplete?.(x)&&window.MotionHasOptimisedAnimation?.(x));return WD(()=>{y.current=!0,b&&(S.current=!0,window.MotionIsMounted=!0,b.updateFeatures(),b.scheduleRenderMicrotask(),A.current&&b.animationState&&b.animationState.animateChanges())}),yt.useEffect(()=>{b&&(!A.current&&b.animationState&&b.animationState.animateChanges(),A.current&&(queueMicrotask(()=>{window.MotionHandoffMarkAsComplete?.(x)}),A.current=!1),b.enteringChildren=void 0)}),b}function JP(i,t,n,s){const{layoutId:o,layout:c,drag:u,dragConstraints:d,layoutScroll:p,layoutRoot:h,layoutAnchor:g,layoutCrossfade:_}=t;i.projection=new n(i.latestValues,t["data-framer-portal-id"]?void 0:ME(i.parent)),i.projection.setOptions({layoutId:o,layout:c,alwaysMeasureLayout:!!u||d&&fo(d),visualElement:i,animationType:typeof c=="string"?c:"both",initialPromotionConfig:s,crossfade:_,layoutScroll:p,layoutRoot:h,layoutAnchor:g})}function ME(i){if(i)return i.options.allowProjection!==!1?i.projection:ME(i.parent)}function Ap(i,{forwardMotionProps:t=!1,type:n}={},s,o){s&&UP(s);const c=n?n==="svg":Ug(i),u=c?YP:qP;function d(h,g){let _;const v={...yt.useContext(pE),...h,layoutId:$P(h)},{isStatic:y}=v,b=IP(h),R=u(h,y);if(!y&&typeof window<"u"){tO();const S=eO(v);_=S.MeasureLayout,b.visualElement=QP(i,R,v,o,S.ProjectionNode,c)}return D.jsxs(Af.Provider,{value:b,children:[_&&b.visualElement?D.jsx(_,{visualElement:b.visualElement,...v}):null,jP(i,h,ZP(R,b.visualElement,g),R,y,t,c)]})}d.displayName=`motion.${typeof i=="string"?i:`create(${i.displayName??i.name??""})`}`;const p=yt.forwardRef(d);return p[KP]=i,p}function $P({layoutId:i}){const t=yt.useContext(GM).id;return t&&i!==void 0?t+"-"+i:i}function tO(i,t){yt.useContext(mE).strict}function eO(i){const t=gE(),{drag:n,layout:s}=t;if(!n&&!s)return{};const o={...n,...s};return{MeasureLayout:n?.isEnabled(i)||s?.isEnabled(i)?o.MeasureLayout:void 0,ProjectionNode:o.ProjectionNode}}function nO(i,t){if(typeof Proxy>"u")return Ap;const n=new Map,s=(c,u)=>Ap(c,u,i,t),o=(c,u)=>s(c,u);return new Proxy(o,{get:(c,u)=>u==="create"?s:(n.has(u)||n.set(u,Ap(u,void 0,i,t)),n.get(u))})}const iO=(i,t)=>t.isSVG??Ug(i)?new IU(t):new LU(t,{allowProjection:i!==yt.Fragment});class aO extends Ls{constructor(t){super(t),t.animationState||(t.animationState=kU(t))}updateAnimationControlsSubscription(){const{animate:t}=this.node.getProps();Ef(t)&&(this.unmountControls=t.subscribe(this.node))}mount(){this.updateAnimationControlsSubscription()}update(){const{animate:t}=this.node.getProps(),{animate:n}=this.node.prevProps||{};t!==n&&this.updateAnimationControlsSubscription()}unmount(){this.node.animationState.reset(),this.unmountControls?.()}}let sO=0;class rO extends Ls{constructor(){super(...arguments),this.id=sO++,this.isExitComplete=!1}update(){if(!this.node.presenceContext)return;const{isPresent:t,onExitComplete:n}=this.node.presenceContext,{isPresent:s}=this.node.prevPresenceContext||{};if(!this.node.animationState||t===s)return;if(t&&s===!1){if(this.isExitComplete){const{initial:c,custom:u}=this.node.getProps();if(typeof c=="string"||typeof c=="object"&&c!==null&&!Array.isArray(c)){const d=dr(this.node,c,u);if(d){const{transition:p,transitionEnd:h,...g}=d;for(const _ in g)this.node.getValue(_)?.jump(g[_])}}this.node.animationState.reset(),this.node.animationState.animateChanges()}else this.node.animationState.setActive("exit",!1);this.isExitComplete=!1;return}const o=this.node.animationState.setActive("exit",!t);n&&!t&&o.then(()=>{this.isExitComplete=!0,n(this.id)})}mount(){const{register:t,onExitComplete:n}=this.node.presenceContext||{};n&&n(this.id),t&&(this.unmount=t(this.id))}unmount(){}}const oO={animation:{Feature:aO},exit:{Feature:rO}};function $l(i){return{point:{x:i.pageX,y:i.pageY}}}const lO=i=>t=>Ag(t)&&i(t,$l(t));function Il(i,t,n,s){return Xl(i,t,lO(n),s)}const bE=({current:i})=>i?i.ownerDocument.defaultView:null,BS=(i,t)=>Math.abs(i-t);function cO(i,t){const n=BS(i.x,t.x),s=BS(i.y,t.y);return Math.sqrt(n**2+s**2)}const IS=new Set(["auto","scroll"]);class EE{constructor(t,n,{transformPagePoint:s,contextWindow:o=window,dragSnapToOrigin:c=!1,distanceThreshold:u=3,element:d}={}){if(this.startEvent=null,this.lastMoveEvent=null,this.lastMoveEventInfo=null,this.lastRawMoveEventInfo=null,this.handlers={},this.contextWindow=window,this.scrollPositions=new Map,this.removeScrollListeners=null,this.onElementScroll=y=>{this.handleScroll(y.target)},this.onWindowScroll=()=>{this.handleScroll(window)},this.updatePoint=()=>{if(!(this.lastMoveEvent&&this.lastMoveEventInfo))return;this.lastRawMoveEventInfo&&(this.lastMoveEventInfo=Bu(this.lastRawMoveEventInfo,this.transformPagePoint));const y=Rp(this.lastMoveEventInfo,this.history),b=this.startEvent!==null,R=cO(y.offset,{x:0,y:0})>=this.distanceThreshold;if(!b&&!R)return;const{point:S}=y,{timestamp:x}=Fn;this.history.push({...S,timestamp:x});const{onStart:A,onMove:N}=this.handlers;b||(A&&A(this.lastMoveEvent,y),this.startEvent=this.lastMoveEvent),N&&N(this.lastMoveEvent,y)},this.handlePointerMove=(y,b)=>{this.lastMoveEvent=y,this.lastRawMoveEventInfo=b,this.lastMoveEventInfo=Bu(b,this.transformPagePoint),Ke.update(this.updatePoint,!0)},this.handlePointerUp=(y,b)=>{this.end();const{onEnd:R,onSessionEnd:S,resumeAnimation:x}=this.handlers;if((this.dragSnapToOrigin||!this.startEvent)&&x&&x(),!(this.lastMoveEvent&&this.lastMoveEventInfo))return;const A=Rp(y.type==="pointercancel"?this.lastMoveEventInfo:Bu(b,this.transformPagePoint),this.history);this.startEvent&&R&&R(y,A),S&&S(y,A)},!Ag(t))return;this.dragSnapToOrigin=c,this.handlers=n,this.transformPagePoint=s,this.distanceThreshold=u,this.contextWindow=o||window;const p=$l(t),h=Bu(p,this.transformPagePoint),{point:g}=h,{timestamp:_}=Fn;this.history=[{...g,timestamp:_}];const{onSessionStart:v}=n;v&&v(t,Rp(h,this.history)),this.removeListeners=Zl(Il(this.contextWindow,"pointermove",this.handlePointerMove),Il(this.contextWindow,"pointerup",this.handlePointerUp),Il(this.contextWindow,"pointercancel",this.handlePointerUp)),d&&this.startScrollTracking(d)}startScrollTracking(t){let n=t.parentElement;for(;n;){const s=getComputedStyle(n);(IS.has(s.overflowX)||IS.has(s.overflowY))&&this.scrollPositions.set(n,{x:n.scrollLeft,y:n.scrollTop}),n=n.parentElement}this.scrollPositions.set(window,{x:window.scrollX,y:window.scrollY}),window.addEventListener("scroll",this.onElementScroll,{capture:!0}),window.addEventListener("scroll",this.onWindowScroll),this.removeScrollListeners=()=>{window.removeEventListener("scroll",this.onElementScroll,{capture:!0}),window.removeEventListener("scroll",this.onWindowScroll)}}handleScroll(t){const n=this.scrollPositions.get(t);if(!n)return;const s=t===window,o=s?{x:window.scrollX,y:window.scrollY}:{x:t.scrollLeft,y:t.scrollTop},c={x:o.x-n.x,y:o.y-n.y};c.x===0&&c.y===0||(s?this.lastMoveEventInfo&&(this.lastMoveEventInfo.point.x+=c.x,this.lastMoveEventInfo.point.y+=c.y):this.history.length>0&&(this.history[0].x-=c.x,this.history[0].y-=c.y),this.scrollPositions.set(t,o),Ke.update(this.updatePoint,!0))}updateHandlers(t){this.handlers=t}end(){this.removeListeners&&this.removeListeners(),this.removeScrollListeners&&this.removeScrollListeners(),this.scrollPositions.clear(),Ns(this.updatePoint)}}function Bu(i,t){return t?{point:t(i.point)}:i}function zS(i,t){return{x:i.x-t.x,y:i.y-t.y}}function Rp({point:i},t){return{point:i,delta:zS(i,TE(t)),offset:zS(i,uO(t)),velocity:fO(t,.1)}}function uO(i){return i[0]}function TE(i){return i[i.length-1]}function fO(i,t){if(i.length<2)return{x:0,y:0};let n=i.length-1,s=null;const o=TE(i);for(;n>=0&&(s=i[n],!(o.timestamp-s.timestamp>vi(t)));)n--;if(!s)return{x:0,y:0};s===i[0]&&i.length>2&&o.timestamp-s.timestamp>vi(t)*2&&(s=i[1]);const c=Li(o.timestamp-s.timestamp);if(c===0)return{x:0,y:0};const u={x:(o.x-s.x)/c,y:(o.y-s.y)/c};return u.x===1/0&&(u.x=0),u.y===1/0&&(u.y=0),u}function dO(i,{min:t,max:n},s){return t!==void 0&&i<t?i=s?Ye(t,i,s.min):Math.max(i,t):n!==void 0&&i>n&&(i=s?Ye(n,i,s.max):Math.min(i,n)),i}function VS(i,t,n){return{min:t!==void 0?i.min+t:void 0,max:n!==void 0?i.max+n-(i.max-i.min):void 0}}function hO(i,{top:t,left:n,bottom:s,right:o}){return{x:VS(i.x,n,o),y:VS(i.y,t,s)}}function HS(i,t){let n=t.min-i.min,s=t.max-i.max;return t.max-t.min<i.max-i.min&&([n,s]=[s,n]),{min:n,max:s}}function pO(i,t){return{x:HS(i.x,t.x),y:HS(i.y,t.y)}}function mO(i,t){let n=.5;const s=Yn(i),o=Yn(t);return o>s?n=Gl(t.min,t.max-s,i.min):s>o&&(n=Gl(i.min,i.max-o,t.min)),ha(0,1,n)}function gO(i,t){const n={};return t.min!==void 0&&(n.min=t.min-i.min),t.max!==void 0&&(n.max=t.max-i.min),n}const qm=.35;function _O(i=qm){return i===!1?i=0:i===!0&&(i=qm),{x:GS(i,"left","right"),y:GS(i,"top","bottom")}}function GS(i,t,n){return{min:kS(i,t),max:kS(i,n)}}function kS(i,t){return typeof i=="number"?i:i[t]||0}const vO=new WeakMap;class xO{constructor(t){this.openDragLock=null,this.isDragging=!1,this.currentDirection=null,this.originPoint={x:0,y:0},this.constraints=!1,this.hasMutatedConstraints=!1,this.elastic=Tn(),this.latestPointerEvent=null,this.latestPanInfo=null,this.visualElement=t}start(t,{snapToCursor:n=!1,distanceThreshold:s}={}){const{presenceContext:o}=this.visualElement;if(o&&o.isPresent===!1)return;const c=_=>{n&&this.snapToCursor($l(_).point),this.stopAnimation()},u=(_,v)=>{const{drag:y,dragPropagation:b,onDragStart:R}=this.getProps();if(y&&!b&&(this.openDragLock&&this.openDragLock(),this.openDragLock=QL(y),!this.openDragLock))return;this.latestPointerEvent=_,this.latestPanInfo=v,this.isDragging=!0,this.currentDirection=null,this.resolveConstraints(),this.visualElement.projection&&(this.visualElement.projection.isAnimationBlocked=!0,this.visualElement.projection.target=void 0),na(x=>{let A=this.getAxisMotionValue(x).get()||0;if(ua.test(A)){const{projection:N}=this.visualElement;if(N&&N.layout){const L=N.layout.layoutBox[x];L&&(A=Yn(L)*(parseFloat(A)/100))}}this.originPoint[x]=A}),R&&Ke.update(()=>R(_,v),!1,!0),Bm(this.visualElement,"transform");const{animationState:S}=this.visualElement;S&&S.setActive("whileDrag",!0)},d=(_,v)=>{this.latestPointerEvent=_,this.latestPanInfo=v;const{dragPropagation:y,dragDirectionLock:b,onDirectionLock:R,onDrag:S}=this.getProps();if(!y&&!this.openDragLock)return;const{offset:x}=v;if(b&&this.currentDirection===null){this.currentDirection=SO(x),this.currentDirection!==null&&R&&R(this.currentDirection);return}this.updateAxis("x",v.point,x),this.updateAxis("y",v.point,x),this.visualElement.render(),S&&Ke.update(()=>S(_,v),!1,!0)},p=(_,v)=>{this.latestPointerEvent=_,this.latestPanInfo=v,this.stop(_,v),this.latestPointerEvent=null,this.latestPanInfo=null},h=()=>{const{dragSnapToOrigin:_}=this.getProps();(_||this.constraints)&&this.startAnimation({x:0,y:0})},{dragSnapToOrigin:g}=this.getProps();this.panSession=new EE(t,{onSessionStart:c,onStart:u,onMove:d,onSessionEnd:p,resumeAnimation:h},{transformPagePoint:this.visualElement.getTransformPagePoint(),dragSnapToOrigin:g,distanceThreshold:s,contextWindow:bE(this.visualElement),element:this.visualElement.current})}stop(t,n){const s=t||this.latestPointerEvent,o=n||this.latestPanInfo,c=this.isDragging;if(this.cancel(),!c||!o||!s)return;const{velocity:u}=o;this.startAnimation(u);const{onDragEnd:d}=this.getProps();d&&Ke.postRender(()=>d(s,o))}cancel(){this.isDragging=!1;const{projection:t,animationState:n}=this.visualElement;t&&(t.isAnimationBlocked=!1),this.endPanSession();const{dragPropagation:s}=this.getProps();!s&&this.openDragLock&&(this.openDragLock(),this.openDragLock=null),n&&n.setActive("whileDrag",!1)}endPanSession(){this.panSession&&this.panSession.end(),this.panSession=void 0}updateAxis(t,n,s){const{drag:o}=this.getProps();if(!s||!Iu(t,o,this.currentDirection))return;const c=this.getAxisMotionValue(t);let u=this.originPoint[t]+s[t];this.constraints&&this.constraints[t]&&(u=dO(u,this.constraints[t],this.elastic[t])),c.set(u)}resolveConstraints(){const{dragConstraints:t,dragElastic:n}=this.getProps(),s=this.visualElement.projection&&!this.visualElement.projection.layout?this.visualElement.projection.measure(!1):this.visualElement.projection?.layout,o=this.constraints;t&&fo(t)?this.constraints||(this.constraints=this.resolveRefConstraints()):t&&s?this.constraints=hO(s.layoutBox,t):this.constraints=!1,this.elastic=_O(n),o!==this.constraints&&!fo(t)&&s&&this.constraints&&!this.hasMutatedConstraints&&na(c=>{this.constraints!==!1&&this.getAxisMotionValue(c)&&(this.constraints[c]=gO(s.layoutBox[c],this.constraints[c]))})}resolveRefConstraints(){const{dragConstraints:t,onMeasureDragConstraints:n}=this.getProps();if(!t||!fo(t))return!1;const s=t.current,{projection:o}=this.visualElement;if(!o||!o.layout)return!1;o.root&&(o.root.scroll=void 0,o.root.updateScroll());const c=AU(s,o.root,this.visualElement.getTransformPagePoint());let u=pO(o.layout.layoutBox,c);if(n){const d=n(bU(u));this.hasMutatedConstraints=!!d,d&&(u=Wb(d))}return u}startAnimation(t){const{drag:n,dragMomentum:s,dragElastic:o,dragTransition:c,dragSnapToOrigin:u,onDragTransitionEnd:d}=this.getProps(),p=this.constraints||{},h=na(g=>{if(!Iu(g,n,this.currentDirection))return;let _=p&&p[g]||{};(u===!0||u===g)&&(_={min:0,max:0});const v=o?200:1e6,y=o?40:1e7,b={type:"inertia",velocity:s?t[g]:0,bounceStiffness:v,bounceDamping:y,timeConstant:750,restDelta:1,restSpeed:10,...c,..._};return this.startAxisValueAnimation(g,b)});return Promise.all(h).then(d)}startAxisValueAnimation(t,n){const s=this.getAxisMotionValue(t);return Bm(this.visualElement,t),s.start(Mg(t,s,0,n,this.visualElement,!1))}stopAnimation(){na(t=>this.getAxisMotionValue(t).stop())}getAxisMotionValue(t){const n=`_drag${t.toUpperCase()}`,o=this.visualElement.getProps()[n];return o||this.visualElement.getValue(t,this.visualElement.latestValues[t]??0)}snapToCursor(t){na(n=>{const{drag:s}=this.getProps();if(!Iu(n,s,this.currentDirection))return;const{projection:o}=this.visualElement,c=this.getAxisMotionValue(n);if(o&&o.layout){const{min:u,max:d}=o.layout.layoutBox[n],p=c.get()||0;c.set(t[n]-Ye(u,d,.5)+p)}})}scalePositionWithinConstraints(){if(!this.visualElement.current)return;const{drag:t,dragConstraints:n}=this.getProps(),{projection:s}=this.visualElement;if(!fo(n)||!s||!this.constraints)return;this.stopAnimation();const o={x:0,y:0};na(u=>{const d=this.getAxisMotionValue(u);if(d&&this.constraints!==!1){const p=d.get();o[u]=mO({min:p,max:p},this.constraints[u])}});const{transformTemplate:c}=this.visualElement.getProps();this.visualElement.current.style.transform=c?c({},""):"none",s.root&&s.root.updateScroll(),s.updateLayout(),this.constraints=!1,this.resolveConstraints(),na(u=>{if(!Iu(u,t,null))return;const d=this.getAxisMotionValue(u),{min:p,max:h}=this.constraints[u];d.set(Ye(p,h,o[u]))}),this.visualElement.render()}addListeners(){if(!this.visualElement.current)return;vO.set(this.visualElement,this);const t=this.visualElement.current,n=Il(t,"pointerdown",h=>{const{drag:g,dragListener:_=!0}=this.getProps(),v=h.target,y=v!==t&&iU(v);g&&_&&!y&&this.start(h)});let s;const o=()=>{const{dragConstraints:h}=this.getProps();fo(h)&&h.current&&(this.constraints=this.resolveRefConstraints(),s||(s=yO(t,h.current,()=>this.scalePositionWithinConstraints())))},{projection:c}=this.visualElement,u=c.addEventListener("measure",o);c&&!c.layout&&(c.root&&c.root.updateScroll(),c.updateLayout()),Ke.read(o);const d=Xl(window,"resize",()=>this.scalePositionWithinConstraints()),p=c.addEventListener("didUpdate",(({delta:h,hasLayoutChanged:g})=>{this.isDragging&&g&&(na(_=>{const v=this.getAxisMotionValue(_);v&&(this.originPoint[_]+=h[_].translate,v.set(v.get()+h[_].translate))}),this.visualElement.render())}));return()=>{d(),n(),u(),p&&p(),s&&s()}}getProps(){const t=this.visualElement.getProps(),{drag:n=!1,dragDirectionLock:s=!1,dragPropagation:o=!1,dragConstraints:c=!1,dragElastic:u=qm,dragMomentum:d=!0}=t;return{...t,drag:n,dragDirectionLock:s,dragPropagation:o,dragConstraints:c,dragElastic:u,dragMomentum:d}}}function jS(i){let t=!0;return()=>{if(t){t=!1;return}i()}}function yO(i,t,n){const s=$y(i,jS(n)),o=$y(t,jS(n));return()=>{s(),o()}}function Iu(i,t,n){return(t===!0||t===i)&&(n===null||n===i)}function SO(i,t=10){let n=null;return Math.abs(i.y)>t?n="y":Math.abs(i.x)>t&&(n="x"),n}class MO extends Ls{constructor(t){super(t),this.removeGroupControls=Ui,this.removeListeners=Ui,this.controls=new xO(t)}mount(){const{dragControls:t}=this.node.getProps();t&&(this.removeGroupControls=t.subscribe(this.controls)),this.removeListeners=this.controls.addListeners()||Ui}update(){const{dragControls:t}=this.node.getProps(),{dragControls:n}=this.node.prevProps||{};t!==n&&(this.removeGroupControls(),t&&(this.removeGroupControls=t.subscribe(this.controls)))}unmount(){this.removeGroupControls(),this.removeListeners(),this.controls.isDragging||this.controls.endPanSession()}}const Cp=i=>(t,n)=>{i&&Ke.update(()=>i(t,n),!1,!0)};class bO extends Ls{constructor(){super(...arguments),this.removePointerDownListener=Ui}onPointerDown(t){this.session=new EE(t,this.createPanHandlers(),{transformPagePoint:this.node.getTransformPagePoint(),contextWindow:bE(this.node)})}createPanHandlers(){const{onPanSessionStart:t,onPanStart:n,onPan:s,onPanEnd:o}=this.node.getProps();return{onSessionStart:Cp(t),onStart:Cp(n),onMove:Cp(s),onEnd:(c,u)=>{delete this.session,o&&Ke.postRender(()=>o(c,u))}}}mount(){this.removePointerDownListener=Il(this.node.current,"pointerdown",t=>this.onPointerDown(t))}update(){this.session&&this.session.updateHandlers(this.createPanHandlers())}unmount(){this.removePointerDownListener(),this.session&&this.session.end()}}let wp=!1;class EO extends yt.Component{componentDidMount(){const{visualElement:t,layoutGroup:n,switchLayoutGroup:s,layoutId:o}=this.props,{projection:c}=t;c&&(n.group&&n.group.add(c),s&&s.register&&o&&s.register(c),wp&&c.root.didUpdate(),c.addEventListener("animationComplete",()=>{this.safeToRemove()}),c.setOptions({...c.options,layoutDependency:this.props.layoutDependency,onExitComplete:()=>this.safeToRemove()})),Ju.hasEverUpdated=!0}getSnapshotBeforeUpdate(t){const{layoutDependency:n,visualElement:s,drag:o,isPresent:c}=this.props,{projection:u}=s;return u&&(u.isPresent=c,t.layoutDependency!==n&&u.setOptions({...u.options,layoutDependency:n}),wp=!0,o||t.layoutDependency!==n||n===void 0||t.isPresent!==c?u.willUpdate():this.safeToRemove(),t.isPresent!==c&&(c?u.promote():u.relegate()||Ke.postRender(()=>{const d=u.getStack();(!d||!d.members.length)&&this.safeToRemove()}))),null}componentDidUpdate(){const{visualElement:t,layoutAnchor:n}=this.props,{projection:s}=t;s&&(s.options.layoutAnchor=n,s.root.didUpdate(),Tg.postRender(()=>{!s.currentAnimation&&s.isLead()&&this.safeToRemove()}))}componentWillUnmount(){const{visualElement:t,layoutGroup:n,switchLayoutGroup:s}=this.props,{projection:o}=t;wp=!0,o&&(o.scheduleCheckAfterUnmount(),n&&n.group&&n.group.remove(o),s&&s.deregister&&s.deregister(o))}safeToRemove(){const{safeToRemove:t}=this.props;t&&t()}render(){return null}}function AE(i){const[t,n]=NP(),s=yt.useContext(GM);return D.jsx(EO,{...i,layoutGroup:s,switchLayoutGroup:yt.useContext(SE),isPresent:t,safeToRemove:n})}const TO={pan:{Feature:bO},drag:{Feature:MO,ProjectionNode:hE,MeasureLayout:AE}};function XS(i,t,n){const{props:s}=i;i.animationState&&s.whileHover&&i.animationState.setActive("whileHover",n==="Start");const o="onHover"+n,c=s[o];c&&Ke.postRender(()=>c(t,$l(t)))}class AO extends Ls{mount(){const{current:t}=this.node;t&&(this.unmount=$L(t,(n,s)=>(XS(this.node,s,"Start"),o=>XS(this.node,o,"End"))))}unmount(){}}class RO extends Ls{constructor(){super(...arguments),this.isActive=!1}onFocus(){let t=!1;try{t=this.node.current.matches(":focus-visible")}catch{t=!0}!t||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!0),this.isActive=!0)}onBlur(){!this.isActive||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!1),this.isActive=!1)}mount(){this.unmount=Zl(Xl(this.node.current,"focus",()=>this.onFocus()),Xl(this.node.current,"blur",()=>this.onBlur()))}unmount(){}}function WS(i,t,n){const{props:s}=i;if(i.current instanceof HTMLButtonElement&&i.current.disabled)return;i.animationState&&s.whileTap&&i.animationState.setActive("whileTap",n==="Start");const o="onTap"+(n==="End"?"":n),c=s[o];c&&Ke.postRender(()=>c(t,$l(t)))}class CO extends Ls{mount(){const{current:t}=this.node;if(!t)return;const{globalTapTarget:n,propagate:s}=this.node.props;this.unmount=sU(t,(o,c)=>(WS(this.node,c,"Start"),(u,{success:d})=>WS(this.node,u,d?"End":"Cancel")),{useGlobalTarget:n,stopPropagation:s?.tap===!1})}unmount(){}}const Ym=new WeakMap,Dp=new WeakMap,wO=i=>{const t=Ym.get(i.target);t&&t(i)},DO=i=>{i.forEach(wO)};function NO({root:i,...t}){const n=i||document;Dp.has(n)||Dp.set(n,{});const s=Dp.get(n),o=JSON.stringify(t);return s[o]||(s[o]=new IntersectionObserver(DO,{root:i,...t})),s[o]}function LO(i,t,n){const s=NO(t);return Ym.set(i,n),s.observe(i),()=>{Ym.delete(i),s.unobserve(i)}}const UO={some:0,all:1};class PO extends Ls{constructor(){super(...arguments),this.hasEnteredView=!1,this.isInView=!1}startObserver(){this.stopObserver?.();const{viewport:t={}}=this.node.getProps(),{root:n,margin:s,amount:o="some",once:c}=t,u={root:n?n.current:void 0,rootMargin:s,threshold:typeof o=="number"?o:UO[o]},d=p=>{const{isIntersecting:h}=p;if(this.isInView===h||(this.isInView=h,c&&!h&&this.hasEnteredView))return;h&&(this.hasEnteredView=!0),this.node.animationState&&this.node.animationState.setActive("whileInView",h);const{onViewportEnter:g,onViewportLeave:_}=this.node.getProps(),v=h?g:_;v&&v(p)};this.stopObserver=LO(this.node.current,u,d)}mount(){this.startObserver()}update(){if(typeof IntersectionObserver>"u")return;const{props:t,prevProps:n}=this.node;["amount","margin","root"].some(OO(t,n))&&this.startObserver()}unmount(){this.stopObserver?.(),this.hasEnteredView=!1,this.isInView=!1}}function OO({viewport:i={}},{viewport:t={}}={}){return n=>i[n]!==t[n]}const FO={inView:{Feature:PO},tap:{Feature:CO},focus:{Feature:RO},hover:{Feature:AO}},BO={layout:{ProjectionNode:hE,MeasureLayout:AE}},IO={...oO,...FO,...TO,...BO},zO=nO(IO,iO),VO=[{id:"brief",label:"任务书",hint:"确认研究题目和边界"},{id:"recursive-search",label:"递归搜索",hint:"题目、变量、数据、文献互相追问"},{id:"variables",label:"数据变量",hint:"字段画像和变量角色候选"},{id:"design",label:"方法设计",hint:"识别策略和模型设定"},{id:"execution",label:"执行实验",hint:"运行、诊断、预检和草案"}];function HO({tabs:i=VO,value:t,onChange:n}){const[s,o]=yt.useState(t||i[0]?.id||""),[c,u]=yt.useState({left:0,width:0,opacity:0}),d=yt.useRef({}),p=i.find(_=>_.id===s)||i[0];yt.useEffect(()=>{t&&o(t)},[t]);function h(_){o(_),n?.(_);const v=d.current[_];v&&u({left:v.offsetLeft,width:v.offsetWidth,opacity:1})}function g(_,v){if(_.key!=="ArrowRight"&&_.key!=="ArrowLeft")return;_.preventDefault();const y=_.key==="ArrowRight"?1:-1,b=(v+y+i.length)%i.length,R=i[b];h(R.id),d.current[R.id]?.focus()}return D.jsxs("nav",{"aria-label":"研究阶段",className:"slide-tabs-wrap",children:[D.jsxs("div",{className:"slide-tabs",onMouseLeave:()=>{const _=d.current[s];u(_?{left:_.offsetLeft,width:_.offsetWidth,opacity:1}:c)},role:"tablist",children:[i.map((_,v)=>D.jsx("button",{"aria-selected":_.id===s,className:_i("slide-tabs__tab",_.id===s&&"slide-tabs__tab--active"),onClick:()=>h(_.id),onFocus:()=>h(_.id),onKeyDown:y=>g(y,v),onMouseEnter:y=>{u({left:y.currentTarget.offsetLeft,width:y.currentTarget.offsetWidth,opacity:1})},ref:y=>{d.current[_.id]=y},role:"tab",type:"button",children:_.label},_.id)),D.jsx(zO.span,{animate:c,className:"slide-tabs__cursor",transition:{type:"spring",stiffness:420,damping:34}})]}),D.jsx("p",{className:"slide-tabs__hint",children:p?.hint})]})}function GO({topic:i,onComplete:t}){const[n,s]=yt.useState("idle"),[o,c]=yt.useState(null),[u,d]=yt.useState(null),p=yt.useCallback(async()=>{s("loading"),c(null),d(null);try{const h=await fetch("/api/brief",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic:i})});if(!h.ok){const _=await h.text();throw new Error(`HTTP ${h.status}: ${_}`)}const g=await h.json();d(g),s("success"),g.verdict_passed&&t&&t({markdown:g.brief_markdown,path:g.brief_path})}catch(h){const g=h instanceof Error?h.message:String(h);c(g),s("error")}},[i,t]);return D.jsx("section",{"aria-label":"任务书扩写",className:"task-brief",children:D.jsxs("div",{className:"task-brief__main",children:[D.jsxs("div",{className:"task-brief__lead",children:[D.jsx("span",{className:"eyebrow",children:"第 1 阶段：研究简报"}),D.jsx("h2",{children:"生成研究简报"}),D.jsxs("p",{children:["研究题目：",i||"（未填）"]})]}),D.jsx("div",{className:"task-brief__confirm-actions",children:D.jsx("button",{type:"button",className:"btn btn--primary",onClick:p,disabled:n==="loading"||!i.trim(),children:n==="loading"?"生成中…":"生成研究简报"})}),n==="error"&&o&&D.jsxs("div",{className:"task-brief__error",role:"alert",children:[D.jsx("strong",{children:"错误："})," ",o]}),n==="success"&&u&&D.jsxs("div",{className:"task-brief__result",children:[D.jsxs("div",{className:"task-brief__verdict",children:[D.jsx("span",{className:u.verdict_passed?"checklist-status-badge checklist-status-badge--ready":"checklist-status-badge checklist-status-badge--pending","data-testid":"brief-verdict",children:u.verdict_passed?"verdict passed":"verdict failed"}),D.jsxs("span",{className:"task-brief__path",children:["文件：",u.brief_path]})]}),D.jsx("pre",{className:"task-brief__markdown","data-testid":"brief-markdown",children:u.brief_markdown})]})]})})}const kO=i=>i>=.8?"search-score search-score--high":i>=.5?"search-score search-score--mid":"search-score search-score--low";function jO({briefPath:i,topicSlug:t,onComplete:n}){const[s,o]=yt.useState({loading:!1,error:null,response:null,excluded:new Set}),c=async()=>{o({loading:!0,error:null,response:null,excluded:new Set});try{const d=await fetch("/api/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic_slug:t,brief_path:i})});if(!d.ok){const h=await d.text();throw new Error(`HTTP ${d.status}: ${h}`)}const p=await d.json();o(h=>({...h,loading:!1,response:p})),p.verdict_passed&&n&&n(p.papers,p.literature_path)}catch(d){o(p=>({...p,loading:!1,error:d instanceof Error?d.message:String(d)}))}},u=d=>{o(p=>{const h=new Set(p.excluded);return h.has(d)?h.delete(d):h.add(d),{...p,excluded:h}})};return D.jsxs("section",{"aria-label":"递归搜索",className:"search-panel","data-testid":"search-panel",children:[D.jsxs("header",{className:"search-panel__header",children:[D.jsx("span",{className:"eyebrow",children:"第 2 阶段：递归搜索 arxiv + LLM 重排"}),D.jsx("h2",{children:"从 arxiv 召回 8-12 篇相关论文"}),D.jsxs("p",{children:["任务书已确认：",D.jsx("code",{"data-testid":"search-brief-path",children:i})]})]}),!s.response&&!s.loading&&!s.error&&D.jsxs("div",{className:"search-panel__cta",children:[D.jsx("p",{className:"search-panel__hint",children:"LLM 将基于研究简报生成 3-5 个英文 arxiv 检索词，命中 arxiv 后再由 LLM 重排打分。"}),D.jsxs("button",{className:"btn btn--primary btn--large",type:"button",onClick:c,"data-testid":"search-trigger",disabled:!i,children:[D.jsx(ND,{size:16}),D.jsx("span",{children:"开始搜索"})]})]}),s.loading&&D.jsxs("div",{className:"search-panel__loading","data-testid":"search-loading",children:[D.jsx(_r,{size:20,className:"spin"}),D.jsx("span",{children:"arxiv 检索 + LLM 重排中..."})]}),s.error&&D.jsxs("div",{className:"search-panel__error","data-testid":"search-error",role:"alert",children:[D.jsx(gr,{size:16}),D.jsxs("span",{children:["搜索失败：",s.error]}),D.jsx("button",{className:"btn btn--ghost",type:"button",onClick:c,children:"重试"})]}),s.response&&D.jsxs(D.Fragment,{children:[D.jsxs("div",{className:"search-panel__verdict",children:[D.jsx("span",{className:_i("verdict-badge",s.response.verdict_passed?"verdict-badge--pass":"verdict-badge--fail"),"data-testid":"search-verdict",children:s.response.verdict_passed?"verdict pass":"verdict fail"}),D.jsxs("span",{className:"search-panel__count",children:[s.response.papers.length," 篇候选 / 已排除 ",s.excluded.size," 篇"]}),D.jsx("button",{className:"btn btn--ghost",type:"button",onClick:c,"data-testid":"search-retrigger",children:"重新搜索"})]}),D.jsx("ol",{className:"search-panel__list","data-testid":"search-paper-list",children:s.response.papers.map(d=>{const p=s.excluded.has(d.arxiv_id);return D.jsxs("li",{className:_i("search-paper",p&&"search-paper--excluded"),"data-testid":"search-paper",children:[D.jsxs("div",{className:"search-paper__header",children:[D.jsx("h3",{className:"search-paper__title",children:d.title}),D.jsx("span",{className:kO(d.relevance_score),children:d.relevance_score.toFixed(2)})]}),D.jsxs("div",{className:"search-paper__meta",children:[D.jsx("span",{children:d.authors.join(", ")||"未知作者"}),D.jsxs("span",{children:["· ",d.year]}),D.jsxs("span",{children:["· arXiv:",d.arxiv_id]})]}),D.jsx("p",{className:"search-paper__abstract",children:d.abstract}),D.jsx("div",{className:"search-paper__actions",children:D.jsx("button",{className:_i("btn","btn--small",p?"btn--ghost":"btn--primary"),type:"button",onClick:()=>u(d.arxiv_id),"data-testid":"search-toggle-exclude",children:p?D.jsxs(D.Fragment,{children:[D.jsx(og,{size:12}),D.jsx("span",{children:"已排除 · 恢复"})]}):D.jsxs(D.Fragment,{children:[D.jsx(BM,{size:12}),D.jsx("span",{children:"采纳"})]})})})]},d.arxiv_id)})}),s.response.literature_markdown&&D.jsxs("details",{className:"search-panel__markdown","data-testid":"search-markdown",children:[D.jsxs("summary",{children:[D.jsx(Mf,{size:14}),D.jsxs("span",{children:["查看 literature.md 预览（已写入 ",s.response.literature_path,"）"]})]}),D.jsx("pre",{children:s.response.literature_markdown.slice(0,4e3)})]})]})]})}const qS=[{value:"CFPS",label:"CFPS (中国家庭追踪调查)",hint:"工业机器人/就业/工资研究主流"},{value:"CHIP",label:"CHIP (中国家庭收入调查)",hint:"收入不平等主题"},{value:"CHARLS",label:"CHARLS (中国健康与养老追踪调查)",hint:"中老年劳动参与"},{value:"custom",label:"自定义数据集",hint:"需在 data/{name}/schema.yaml 准备"}],XO={X:{color:"var(--variables-x, #c1440e)",label:"X 解释变量"},Y:{color:"var(--variables-y, #1f6feb)",label:"Y 被解释变量"},control:{color:"var(--variables-control, #6e7681)",label:"控制变量"},mediator:{color:"var(--variables-mediator, #8b5cf6)",label:"中介变量"},moderator:{color:"var(--variables-moderator, #0e8a86)",label:"调节变量"}};function WO({briefPath:i,topicSlug:t,defaultDataset:n="CFPS",onComplete:s}){const[o,c]=yt.useState(n),[u,d]=yt.useState(!1),[p,h]=yt.useState(null),[g,_]=yt.useState(null),[v,y]=yt.useState(!1);yt.useEffect(()=>{v||!i||!t||(y(!0),b())},[i,t]);async function b(){if(!u){d(!0),h(null);try{const A=await fetch("/api/variables",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic_slug:t,brief_path:i,dataset_name:o})});if(!A.ok){const L=await A.text();throw new Error(`HTTP ${A.status}: ${L||A.statusText}`)}const N=await A.json();_(N),N.verdict_passed&&s?.(N.variables,N.variables_path)}catch(A){h(A.message)}finally{d(!1)}}}function R(A){c(A),_(null),h(null)}const S=g?.variables??[],x=new Set(S.map(A=>A.role));return D.jsxs("div",{className:"variables-panel","data-testid":"variables-panel",children:[D.jsxs("div",{className:"variables-panel__header",children:[D.jsxs("div",{className:"variables-panel__heading",children:[D.jsx(xD,{className:"variables-panel__icon","aria-hidden":!0}),D.jsxs("div",{children:[D.jsx("h2",{children:"识别研究变量"}),D.jsx("p",{className:"variables-panel__hint",children:"基于数据集 schema + 研究简报，由 LLM 把列名映射到研究变量。"})]})]}),D.jsxs("div",{className:"variables-panel__controls",children:[D.jsxs("label",{className:"variables-panel__dataset-label",children:[D.jsx("span",{children:"数据集"}),D.jsx("select",{className:"variables-panel__select",value:o,onChange:A=>R(A.target.value),disabled:u,"data-testid":"variables-dataset-select",children:qS.map(A=>D.jsx("option",{value:A.value,children:A.label},A.value))})]}),D.jsx("button",{type:"button",className:"variables-panel__button",onClick:()=>{b()},disabled:u,"data-testid":"variables-run-button",children:u?D.jsxs(D.Fragment,{children:[D.jsx(_r,{className:"variables-panel__spinner","aria-hidden":!0}),"识别中…"]}):D.jsxs(D.Fragment,{children:[D.jsx(zM,{"aria-hidden":!0}),g?"重新识别变量":"识别变量"]})})]}),D.jsx("p",{className:"variables-panel__dataset-hint",children:qS.find(A=>A.value===o)?.hint})]}),p?D.jsxs("div",{className:"variables-panel__error",role:"alert","data-testid":"variables-error",children:[D.jsx(gr,{"aria-hidden":!0}),D.jsx("span",{children:p})]}):null,u?D.jsxs("div",{className:"variables-panel__loading","data-testid":"variables-loading",children:[D.jsx(_r,{className:"variables-panel__spinner","aria-hidden":!0}),D.jsx("span",{children:"LLM 解析 schema 中…"})]}):null,g?D.jsxs("div",{className:"variables-panel__verdict","data-testid":"variables-verdict",children:[g.verdict_passed?D.jsxs("span",{className:"variables-panel__verdict-passed",children:[D.jsx(Hl,{"aria-hidden":!0})," verdict 通过"]}):D.jsxs("span",{className:"variables-panel__verdict-failed",children:[D.jsx(wy,{"aria-hidden":!0})," verdict 未通过（变量数不足或 role 非法）"]}),D.jsxs("span",{className:"variables-panel__verdict-path",title:g.variables_path,children:[D.jsx(Mf,{"aria-hidden":!0})," ",g.variables_path]})]}):null,S.length>0?D.jsx("div",{className:"variables-panel__grid","data-testid":"variables-grid",children:S.map((A,N)=>{const L=XO[A.role];return D.jsxs("article",{className:"variables-card","data-testid":`variables-card-${A.role}`,style:{borderLeftColor:L.color},children:[D.jsxs("header",{className:"variables-card__header",children:[D.jsx("span",{className:"variables-card__role",style:{backgroundColor:L.color},title:L.label,children:A.role}),D.jsx("h3",{className:"variables-card__label",children:A.semantic_label})]}),D.jsxs("dl",{className:"variables-card__meta",children:[D.jsx("dt",{children:"列名"}),D.jsx("dd",{children:D.jsx("code",{children:A.dataset_column})})]}),D.jsx("p",{className:"variables-card__description",children:A.description}),A.reference_papers.length>0?D.jsxs("div",{className:"variables-card__papers",children:[D.jsx("span",{className:"variables-card__papers-title",children:"引用文献"}),D.jsx("ul",{children:A.reference_papers.map((H,B)=>D.jsx("li",{children:H},B))})]}):null]},`${A.dataset_column}-${N}`)})}):null,S.length>0?D.jsxs("footer",{className:"variables-panel__footer","data-testid":"variables-footer",children:[D.jsx("span",{children:"已覆盖 role: "}),["X","Y","control","mediator","moderator"].map(A=>{const N=x.has(A);return D.jsxs("span",{className:_i("variables-panel__role-chip",N&&"variables-panel__role-chip--present"),children:[N?D.jsx(Hl,{"aria-hidden":!0}):D.jsx(wy,{"aria-hidden":!0}),A]},A)})]}):null]})}const qO={DID:"双重差分 (DID)",IV:"工具变量 (IV)",RDD:"断点回归 (RDD)",PSM:"倾向得分匹配 (PSM)",DML:"双重机器学习 (DML)"};function YO({topicSlug:i,briefPath:t,variablesPath:n,onComplete:s}){const[o,c]=yt.useState(!1),[u,d]=yt.useState(null),[p,h]=yt.useState(null);async function g(){if(!o){c(!0),d(null),h(null);try{const _=await fetch("/api/design",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic_slug:i,brief_path:t,variables_path:n})});if(!_.ok)throw new Error(`HTTP ${_.status}: ${_.statusText}`);const v=await _.json();h(v),v.verdict_passed&&s&&s(v.recommended,v.design_path)}catch(_){d(_ instanceof Error?_.message:String(_))}finally{c(!1)}}}return D.jsxs("section",{className:"design-panel","aria-label":"方法设计",children:[D.jsxs("header",{className:"design-panel__header",children:[D.jsx(MD,{size:18}),D.jsxs("div",{children:[D.jsx("h2",{children:"方法设计"}),D.jsx("p",{children:"基于研究变量 + StatsPAI 估算候选方法，由 LLM 解释 + 推荐。"})]})]}),!p&&D.jsx("button",{type:"button",className:"design-panel__cta",onClick:g,disabled:o,"data-testid":"design-trigger",children:o?D.jsxs(D.Fragment,{children:[D.jsx(_r,{size:16,className:"design-panel__spin"}),"正在调 StatsPAI + LLM 评估..."]}):D.jsxs(D.Fragment,{children:[D.jsx(zM,{size:16}),"设计方法"]})}),u&&D.jsxs("div",{className:"design-panel__error",role:"alert",children:[D.jsx(gr,{size:16}),D.jsx("span",{children:u})]}),p&&D.jsxs("div",{className:"design-panel__results",children:[D.jsx("div",{className:"design-panel__verdict",children:p.verdict_passed?D.jsxs(D.Fragment,{children:[D.jsx(Hl,{size:16}),D.jsxs("span",{children:["verdict gate 通过（",p.candidates.length," 个候选 + 推荐 ",p.recommended,"）"]})]}):D.jsxs(D.Fragment,{children:[D.jsx(gr,{size:16}),D.jsx("span",{children:"verdict gate 未通过"})]})}),D.jsx("ul",{className:"design-panel__candidates",children:p.candidates.map(_=>{const v=_.method===p.recommended;return D.jsxs("li",{className:_i("design-panel__candidate",v&&"design-panel__candidate--recommended",!_.fits_data&&"design-panel__candidate--warn"),"data-testid":"design-candidate","data-method":_.method,children:[D.jsxs("div",{className:"design-panel__candidate-head",children:[D.jsxs("h3",{children:[qO[_.method]||_.method,v&&D.jsx("span",{className:"design-panel__badge","data-testid":"design-recommended",children:"推荐"})]}),D.jsx("span",{className:_i("design-panel__fits",_.fits_data?"is-fit":"is-misfit"),children:_.fits_data?"fits data":"weak fit"})]}),D.jsx("p",{className:"design-panel__rationale",children:_.rationale}),D.jsxs("details",{className:"design-panel__sp",children:[D.jsx("summary",{children:"StatsPAI sp_output"}),D.jsx("pre",{children:JSON.stringify(_.sp_output,null,2)})]})]},_.method)})}),D.jsxs("div",{className:"design-panel__code",children:[D.jsxs("div",{className:"design-panel__code-head",children:[D.jsx(mD,{size:14}),D.jsxs("span",{children:["code_stub（",p.recommended,"）"]})]}),D.jsx("pre",{"data-testid":"design-code-stub",children:p.code_stub})]}),D.jsx("footer",{className:"design-panel__footer",children:D.jsxs("span",{className:"design-panel__path",title:p.design_path,children:["已落盘：",p.design_path]})})]})]})}const YS=800;function KO(i,t){return i.length<=t?i:i.slice(0,t)+"..."}function ZO({prompt:i,rawOutput:t,parsedOutput:n,sectionIndex:s}){const[o,c]=yt.useState(null),u=p=>{c(h=>h===p?null:p)},d=[{key:"prompt",title:"1. 提示词",body:i,truncated:!1},{key:"raw",title:"2. 原始输出",body:KO(t,YS),truncated:t.length>YS},{key:"parsed",title:"3. 解析后",body:n,truncated:!1}];return D.jsxs("div",{className:"reasoning-chain","data-testid":`reasoning-chain-${s}`,children:[D.jsx("div",{className:"reasoning-chain__header",children:"推理链"}),d.map(p=>{const h=o===p.key;return D.jsxs("details",{className:"reasoning-chain__item","data-testid":`reasoning-chain-${s}-${p.key}`,open:h,children:[D.jsxs("summary",{onClick:g=>{g.preventDefault(),u(p.key)},className:"reasoning-chain__summary",children:[h?D.jsx(IM,{size:14}):D.jsx(uD,{size:14}),D.jsx("span",{children:p.title}),p.truncated?D.jsx("span",{className:"reasoning-chain__truncated-tag",children:"(截断)"}):null]}),D.jsx("pre",{className:_i("reasoning-chain__body",p.key==="prompt"&&"reasoning-chain__body--prompt"),children:p.body})]},p.key)}),D.jsx("style",{children:`
        .reasoning-chain {
          margin-top: 0.5rem;
          padding: 0.5rem 0.75rem;
          background: #f9fafb;
          border-radius: 6px;
          font-size: 0.8rem;
        }
        .reasoning-chain__header {
          font-weight: 600;
          color: #4b5563;
          margin-bottom: 0.4rem;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .reasoning-chain__item {
          margin-bottom: 0.3rem;
        }
        .reasoning-chain__summary {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          cursor: pointer;
          list-style: none;
          color: #1f2937;
          padding: 0.2rem 0;
        }
        .reasoning-chain__summary::-webkit-details-marker {
          display: none;
        }
        .reasoning-chain__truncated-tag {
          font-size: 0.7rem;
          color: #9ca3af;
          margin-left: 0.3rem;
        }
        .reasoning-chain__body {
          margin: 0.3rem 0 0.3rem 1.4rem;
          padding: 0.5rem;
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 4px;
          white-space: pre-wrap;
          word-break: break-word;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          font-size: 0.75rem;
          max-height: 320px;
          overflow-y: auto;
          color: #1f2937;
        }
        .reasoning-chain__body--prompt {
          color: #4b5563;
        }
      `})]})}const KS={1:"1. 引言",2:"2. 文献综述",3:"3. 制度背景",4:"4. 数据",5:"5. 实证策略",6:"6. 主结果",7:"7. 稳健性检验",8:"8. 结论",9:"9. 参考文献"};async function QO(i,t){if(!i.body)throw new Error("response.body is null — SSE not supported");const n=i.body.getReader(),s=new TextDecoder;let o="";for(;;){const{done:c,value:u}=await n.read();if(c)break;o+=s.decode(u,{stream:!0});const d=o.split(`

`);o=d.pop()||"";for(const p of d){const h=p.trim();if(h.startsWith("data: ")){const g=h.slice(6);try{t(JSON.parse(g))}catch{}}}}}function JO({briefPath:i,variablesPath:t,designPath:n,topicSlug:s,onComplete:o}){const[c,u]=yt.useState(!1),[d,p]=yt.useState(null),[h,g]=yt.useState({}),[_,v]=yt.useState("点击「开始跑」以流式生成 9 节论文 + paper.pdf + results.json"),[y,b]=yt.useState("idle"),[R,S]=yt.useState(null),[x,A]=yt.useState(null),[N,L]=yt.useState({}),H=yt.useRef(!1),B=yt.useRef(null);async function O(){if(!c){u(!0),p(null),g({}),L({}),S(null),A(null),H.current=!1,v("正在打开 SSE 流..."),b("connecting");try{const V=await fetch("/api/execute",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic_slug:s,brief_path:i,variables_path:t,design_path:n})});if(!V.ok)throw new Error(`HTTP ${V.status}: ${V.statusText}`);await QO(V,F=>{v(F.message),b(F.stage),F.event==="section_done"&&F.section_index!=null?(g(j=>({...j,[F.section_index]:F})),(F.prompt||F.raw_output||F.parsed_output)&&L(j=>({...j,[F.section_index]:{prompt:F.prompt??"",rawOutput:F.raw_output??"",parsedOutput:F.parsed_output??""}}))):F.event==="paper_ready"&&F.paper_pdf_path?(S(F.paper_pdf_path),B.current=F.paper_pdf_path):F.event==="done"&&F.results_json_path?(A(F.results_json_path),!H.current&&B.current&&F.results_json_path&&(H.current=!0,o?.(B.current,F.results_json_path))):F.event==="error"&&p(F.message)})}catch(V){const F=V instanceof Error?V.message:String(V);p(F)}finally{u(!1)}}}const U=Object.keys(h).map(V=>Number(V)).sort((V,F)=>V-F).length===9;return D.jsxs("div",{className:"execution-panel",children:[D.jsxs("header",{className:"execution-panel__header",children:[D.jsx("h2",{children:"执行实验"}),D.jsx("p",{className:"execution-panel__subtitle",children:"按 9 节顺序写作、引言 → 参考文献，最终拼成 paper.pdf 并落盘 results.json"})]}),D.jsxs("div",{className:"execution-panel__controls",children:[D.jsx("button",{type:"button",onClick:O,disabled:c,className:_i("execution-panel__button",c&&"is-running"),"data-testid":"execute-start",children:c?D.jsxs(D.Fragment,{children:[D.jsx(_r,{size:16,className:"spin"})," 正在跑..."]}):D.jsxs(D.Fragment,{children:[D.jsx(RD,{size:16})," 开始跑"]})}),D.jsxs("div",{className:"execution-panel__status",children:[D.jsx("span",{className:"execution-panel__status-label",children:"状态："}),D.jsx("code",{children:y}),D.jsx("span",{className:"execution-panel__status-message",children:_})]})]}),d&&D.jsxs("div",{className:"execution-panel__error","data-testid":"execute-error",children:[D.jsx(gr,{size:16})," ",d]}),D.jsx("ol",{className:"execution-panel__sections","data-testid":"execute-sections",children:Array.from({length:9},(V,F)=>F+1).map(V=>{const F=h[V];return D.jsxs("li",{className:_i("execution-panel__section",F&&"is-done",c&&!F&&"is-pending"),"data-testid":`execute-section-${V}`,children:[D.jsx("span",{className:"execution-panel__section-title",children:KS[V]??`Section ${V}`}),D.jsx("span",{className:"execution-panel__section-state",children:F?D.jsxs(D.Fragment,{children:[D.jsx(Hl,{size:14})," done"]}):c?D.jsxs(D.Fragment,{children:[D.jsx(_r,{size:14,className:"spin"})," writing"]}):"—"})]},V)})}),Object.keys(N).length>0?D.jsx("div",{className:"execution-panel__chains","data-testid":"execute-reasoning-chains",children:Object.entries(N).sort(([V],[F])=>Number(V)-Number(F)).map(([V,F])=>{const j=Number(V),lt=KS[j]??`Section ${j}`;return D.jsxs("details",{className:"execution-panel__chain-block","data-testid":`execute-chain-block-${j}`,children:[D.jsxs("summary",{className:"execution-panel__chain-summary",children:[lt," · 推理链"]}),D.jsx(ZO,{sectionIndex:j,prompt:F.prompt,rawOutput:F.rawOutput,parsedOutput:F.parsedOutput})]},j)})}):null,U&&R&&D.jsxs("div",{className:"execution-panel__result","data-testid":"execute-paper-ready",children:[D.jsx(Mf,{size:16}),D.jsx("span",{children:"Paper ready: "}),D.jsx("code",{children:R})]}),x&&D.jsxs("div",{className:"execution-panel__result","data-testid":"execute-done",children:[D.jsx(Hl,{size:16}),D.jsx("span",{children:"Results: "}),D.jsx("code",{children:x})]}),D.jsx("style",{children:`
        .execution-panel {
          padding: 1.25rem 1.5rem;
          background: #fafafa;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .execution-panel__chains {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .execution-panel__chain-block {
          background: #f3f4f6;
          border-radius: 6px;
          padding: 0.4rem 0.6rem;
        }
        .execution-panel__chain-summary {
          cursor: pointer;
          font-size: 0.85rem;
          color: #1f2937;
          font-weight: 500;
          list-style: none;
        }
        .execution-panel__chain-summary::-webkit-details-marker {
          display: none;
        }
        .execution-panel__header h2 {
          margin: 0;
          font-size: 1.15rem;
        }
        .execution-panel__subtitle {
          margin: 0.25rem 0 0;
          font-size: 0.85rem;
          color: #666;
        }
        .execution-panel__controls {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .execution-panel__button {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          background: #1f2937;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 0.5rem 0.9rem;
          cursor: pointer;
          font-size: 0.9rem;
        }
        .execution-panel__button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .execution-panel__button.is-running {
          background: #374151;
        }
        .execution-panel__status {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #555;
        }
        .execution-panel__status code {
          background: #e5e7eb;
          padding: 0 0.3rem;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        .execution-panel__status-message {
          color: #444;
        }
        .execution-panel__error {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #b91c1c;
          background: #fee2e2;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          font-size: 0.9rem;
        }
        .execution-panel__sections {
          list-style: none;
          margin: 0;
          padding: 0;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 0.5rem;
        }
        .execution-panel__section {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          background: #f3f4f6;
          font-size: 0.85rem;
        }
        .execution-panel__section.is-done {
          background: #ecfdf5;
          color: #047857;
        }
        .execution-panel__section.is-pending {
          background: #fef3c7;
        }
        .execution-panel__section-state {
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          font-size: 0.75rem;
        }
        .execution-panel__result {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #ecfdf5;
          color: #065f46;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          font-size: 0.85rem;
        }
        .execution-panel__result code {
          font-size: 0.75rem;
          word-break: break-all;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `})]})}function $O(){return D.jsxs("div",{className:"identification-audit","data-testid":"identification-audit-panel",children:[D.jsxs("header",{className:"identification-audit__header",children:[D.jsx(TD,{size:16}),D.jsx("h2",{children:"识别策略审计 (待解锁)"}),D.jsx("p",{className:"identification-audit__subtitle",children:"Pre-trend 检验 + 弱 IV 诊断 + DAG 可视化（pre-registration 占位）"})]}),D.jsxs("div",{className:"identification-audit__cards",children:[D.jsxs("section",{className:"identification-audit__card","data-testid":"audit-card-pretrend",children:[D.jsx("h3",{children:"Pre-trend test"}),D.jsx("p",{className:"identification-audit__hint",children:"事件研究法：处理前各期系数应不显著"}),D.jsx("div",{className:"identification-audit__chart-placeholder","data-testid":"audit-pretrend-plot-placeholder",children:"[图: pre-trend coefficient plot — 后续接入]"}),D.jsx("fieldset",{disabled:!0,className:"identification-audit__fieldset",children:D.jsxs("label",{children:["Pre-trend 检验 p 值（联合）",D.jsx("input",{type:"number",step:"0.01",defaultValue:.42,readOnly:!0})]})})]}),D.jsxs("section",{className:"identification-audit__card","data-testid":"audit-card-weakiv",children:[D.jsx("h3",{children:"Weak-IV diagnostics"}),D.jsx("p",{className:"identification-audit__hint",children:"第一阶段 F + Partial R² + Anderson-Rubin p"}),D.jsxs("fieldset",{disabled:!0,className:"identification-audit__fieldset",children:[D.jsxs("label",{children:["Partial R²",D.jsx("input",{type:"number",step:"0.01",defaultValue:.47,readOnly:!0,"data-testid":"audit-weakiv-partial-r2"})]}),D.jsxs("label",{children:["AR p-value",D.jsx("input",{type:"number",step:"0.0001",defaultValue:3e-6,readOnly:!0,"data-testid":"audit-weakiv-ar-pvalue"})]})]})]}),D.jsxs("section",{className:"identification-audit__card","data-testid":"audit-card-dag",children:[D.jsx("h3",{children:"DAG visualization"}),D.jsx("p",{className:"identification-audit__hint",children:"因果图：X → Y + 控制变量 + 工具变量"}),D.jsx("pre",{className:"identification-audit__dag","data-testid":"audit-dag-placeholder",children:`      [Y]
       ↑
       | β
       |
      [X] ← γ ← [Z: Bartik IV]
       ↑  ↘
       |    ↘
   [控制变量]  [ε]

占位：未来用 graphviz/d3 渲染。`})]})]}),D.jsxs("footer",{className:"identification-audit__footer",children:[D.jsx(gr,{size:14}),D.jsx("span",{children:"此 tab 当前为脚手架 (scaffold)，所有字段为只读占位。未来接入 pre-registration 工作流时解锁。"})]}),D.jsx("style",{children:`
        .identification-audit {
          padding: 1.25rem 1.5rem;
          background: #fafafa;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          opacity: 0.85;
        }
        .identification-audit__header {
          display: flex;
          align-items: baseline;
          gap: 0.6rem;
        }
        .identification-audit__header h2 {
          margin: 0;
          font-size: 1.1rem;
          color: #4b5563;
        }
        .identification-audit__subtitle {
          margin: 0 0 0 auto;
          font-size: 0.8rem;
          color: #6b7280;
        }
        .identification-audit__cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1rem;
        }
        .identification-audit__card {
          background: #f3f4f6;
          border-radius: 8px;
          padding: 0.9rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .identification-audit__card h3 {
          margin: 0;
          font-size: 0.95rem;
          color: #1f2937;
        }
        .identification-audit__hint {
          margin: 0;
          font-size: 0.8rem;
          color: #6b7280;
        }
        .identification-audit__chart-placeholder {
          background: #ffffff;
          border: 1px dashed #9ca3af;
          border-radius: 4px;
          padding: 1.5rem;
          text-align: center;
          color: #9ca3af;
          font-size: 0.8rem;
        }
        .identification-audit__dag {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 4px;
          padding: 0.8rem;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          font-size: 0.75rem;
          color: #374151;
          margin: 0;
          white-space: pre-wrap;
        }
        .identification-audit__fieldset {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          border: none;
          padding: 0;
          margin: 0;
        }
        .identification-audit__fieldset label {
          display: flex;
          flex-direction: column;
          font-size: 0.8rem;
          color: #4b5563;
          gap: 0.2rem;
        }
        .identification-audit__fieldset input {
          padding: 0.3rem 0.5rem;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          font-size: 0.85rem;
          background: #ffffff;
        }
        .identification-audit__footer {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: #6b7280;
          background: #fef3c7;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
        }
      `})]})}const ZS=["brief","search","variables","design","execution","identification-audit"],Np={brief:{label:"任务书",hint:"生成 4 段式研究简报（研究问题 / 边际贡献 / 研究边界 / 成功标准）"},search:{label:"递归搜索",hint:"arxiv 召回 + LLM 重排，提炼 8-12 篇相关文献"},variables:{label:"数据变量",hint:"基于数据集 schema + 简报识别 X / Y / control 候选变量"},design:{label:"方法设计",hint:"StatsPAI 估算候选识别策略，LLM 解释并推荐"},execution:{label:"执行实验",hint:"流式生成 9 节论文 + paper.pdf + results.json"},"identification-audit":{label:"识别审计",hint:"Pre-trend + 弱 IV 诊断 + DAG（pre-registration 占位）"}};function tF(i){return i.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,50)||"untitled"}function eF(){const[i,t]=yt.useState(null),[n,s]=yt.useState(""),[o,c]=yt.useState("brief"),[u,d]=yt.useState(null),[p,h]=yt.useState(null),[g,_]=yt.useState(null),[v,y]=yt.useState(null),[b,R]=yt.useState(null),[S,x]=yt.useState(null),A=yt.useCallback(O=>{switch(O){case"brief":return!0;case"search":return u!==null;case"variables":return u!==null&&p!==null;case"design":return u!==null&&p!==null&&g!==null;case"execution":return u!==null&&g!==null&&v!==null;case"identification-audit":return b!==null;default:return!1}},[u,p,g,v,b]),N=yt.useCallback(O=>{x(O),window.setTimeout(()=>x(null),3e3)},[]),L=O=>{if(!ZS.includes(O))return;const E=O;if(!A(E)){N("请按顺序完成前一阶段后再进入。");return}c(E)},H=()=>{t(null),s(""),c("brief"),d(null),h(null),_(null),y(null),R(null)};if(i===null)return D.jsxs("main",{className:"app-shell app-shell--intake",children:[D.jsx(Ry,{}),D.jsxs("section",{className:"start-panel",children:[D.jsxs("div",{className:"start-panel__heading",children:[D.jsx("span",{className:"eyebrow",children:"本地实证研究 OS"}),D.jsx("h1",{children:"今天要推进什么研究？"})]}),D.jsx(kD,{onSubmit:({message:O,files:E,pastedContent:U,mode:V})=>{t({message:O,mode:V,fileCount:E.length,pastedCount:U.length}),s(tF(O)),c("brief")}})]})]});const B=ZS.map(O=>{const E=Np[O],U=A(O);return{id:O,label:U?E.label:`${E.label} (待解锁)`,hint:U?E.hint:"请按顺序完成前一阶段后再进入。"}});return D.jsxs("main",{className:"app-shell analysis-workspace",children:[D.jsx(Ry,{}),D.jsxs("section",{className:"analysis-workspace__header",children:[D.jsx("button",{className:"analysis-workspace__back",type:"button",onClick:H,children:"新任务"}),D.jsxs("div",{children:[D.jsx("span",{className:"eyebrow",children:"分析工作台"}),D.jsx("h1",{children:i.message||"附件驱动任务"}),D.jsxs("p",{children:["模式：",i.mode==="codex-supervisor"?"智能规划模式":i.mode==="auto-research"?"自动探索模式":"人工审阅模式"," · ","文件 ",i.fileCount," · 长文本 ",i.pastedCount," · slug:"," ",D.jsx("code",{"data-testid":"topic-slug",children:n})]})]})]}),D.jsxs("section",{className:"stage-panel","aria-label":"研究路径",children:[S?D.jsxs("div",{className:"inline-toast",role:"alert","data-testid":"stage-locked-toast",children:[D.jsx("span",{className:"toast-icon",children:"🔒"}),D.jsx("span",{children:S})]}):null,D.jsx(HO,{tabs:B,value:o,onChange:L}),o==="brief"?D.jsx(GO,{topic:i.message,onComplete:O=>{d(O),c("search")}}):null,o==="search"&&u?D.jsx(jO,{briefPath:u.path,topicSlug:n,onComplete:(O,E)=>{h({papers:O,literaturePath:E}),c("variables")}}):null,o==="variables"&&u?D.jsx(WO,{briefPath:u.path,topicSlug:n,onComplete:(O,E)=>{_({variables:O,variablesPath:E}),c("design")}}):null,o==="design"&&u&&g?D.jsx(YO,{topicSlug:n,briefPath:u.path,variablesPath:g.variablesPath,onComplete:(O,E)=>{y({recommended:O,designPath:E}),c("execution")}}):null,o==="execution"&&u&&g&&v?D.jsx(JO,{briefPath:u.path,variablesPath:g.variablesPath,topicSlug:n,designPath:v.designPath,onComplete:(O,E)=>{R({paperPath:O,resultsPath:E})}}):null,o==="identification-audit"&&b?D.jsx($O,{}):null,b?D.jsxs("div",{className:"stage-panel__completion","data-testid":"final-complete",role:"status",children:[D.jsx("h2",{children:"研究链路完成"}),D.jsxs("p",{children:["paper.pdf:"," ",D.jsx("code",{"data-testid":"final-paper-path",children:b.paperPath})]}),D.jsxs("p",{children:["results.json:"," ",D.jsx("code",{"data-testid":"final-results-path",children:b.resultsPath})]}),D.jsx("p",{className:"stage-panel__completion-hint",children:"5 tab 走通完成，产物已落盘到项目目录，可以入库。"})]}):null,D.jsxs("div",{className:"stage-panel__summary",children:[D.jsx("span",{children:"当前阶段"}),D.jsx("strong",{children:Np[o].label}),D.jsx("p",{children:Np[o].hint})]})]})]})}V1.createRoot(document.getElementById("root")).render(D.jsx(U1.StrictMode,{children:D.jsx(eF,{})}));
