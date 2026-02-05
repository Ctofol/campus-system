"use weex:vue";

if (typeof Promise !== 'undefined' && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor
    return this.then(
      value => promise.resolve(callback()).then(() => value),
      reason => promise.resolve(callback()).then(() => {
        throw reason
      })
    )
  }
};

if (typeof uni !== 'undefined' && uni && uni.requireGlobal) {
  const global = uni.requireGlobal()
  ArrayBuffer = global.ArrayBuffer
  Int8Array = global.Int8Array
  Uint8Array = global.Uint8Array
  Uint8ClampedArray = global.Uint8ClampedArray
  Int16Array = global.Int16Array
  Uint16Array = global.Uint16Array
  Int32Array = global.Int32Array
  Uint32Array = global.Uint32Array
  Float32Array = global.Float32Array
  Float64Array = global.Float64Array
  BigInt64Array = global.BigInt64Array
  BigUint64Array = global.BigUint64Array
};


(()=>{var b=Object.create;var p=Object.defineProperty;var x=Object.getOwnPropertyDescriptor;var y=Object.getOwnPropertyNames;var C=Object.getPrototypeOf,k=Object.prototype.hasOwnProperty;var v=(e,o)=>()=>(o||e((o={exports:{}}).exports,o),o.exports);var S=(e,o,a,n)=>{if(o&&typeof o=="object"||typeof o=="function")for(let r of y(o))!k.call(e,r)&&r!==a&&p(e,r,{get:()=>o[r],enumerable:!(n=x(o,r))||n.enumerable});return e};var f=(e,o,a)=>(a=e!=null?b(C(e)):{},S(o||!e||!e.__esModule?p(a,"default",{value:e,enumerable:!0}):a,e));var c=v((L,g)=>{g.exports=Vue});var l=f(c());function m(e,o,...a){uni.__log__?uni.__log__(e,o,...a):console[e].apply(console,[...a,o])}var h=(e,o)=>{let a=e.__vccOpts||e;for(let[n,r]of o)a[n]=r;return a};var t=f(c()),w={"camera-min-page":{"":{flex:1,backgroundColor:"#f5f5f5",flexDirection:"column"}},"status-bar":{"":{backgroundColor:"#ffffff"}},header:{"":{paddingTop:20,paddingRight:20,paddingBottom:20,paddingLeft:20,backgroundColor:"#ffffff",borderBottomWidth:1,borderBottomColor:"#eeeeee"}},title:{"":{fontSize:18,fontWeight:"bold",color:"#333333"}},subtitle:{"":{fontSize:12,color:"#999999",marginTop:5}},"camera-container":{"":{width:"750rpx",height:"500rpx",backgroundColor:"#000000",marginTop:20,position:"relative"}},"live-camera":{"":{width:"750rpx",height:"500rpx"}},"camera-overlay":{"":{position:"absolute",bottom:"20rpx",left:"20rpx",backgroundColor:"rgba(0,0,0,0.5)",paddingTop:5,paddingRight:10,paddingBottom:5,paddingLeft:10,borderRadius:4}},"overlay-text":{"":{color:"#ffffff",fontSize:12}},"debug-info":{"":{paddingTop:20,paddingRight:20,paddingBottom:20,paddingLeft:20,marginTop:10,backgroundColor:"#ffffff"}},"info-item":{"":{fontSize:14,color:"#666666",marginBottom:5}},"action-btn":{"":{marginTop:10,marginRight:20,marginBottom:10,marginLeft:20,backgroundColor:"#20C997",borderRadius:8,height:44,justifyContent:"center",alignItems:"center"}},secondary:{"":{backgroundColor:"#dddddd"}}},A={data(){return{statusBarHeight:20,statusMsg:"\u521D\u59CB\u5316...",authStatus:"\u672A\u77E5"}},onLoad(){let e=uni.getSystemInfoSync();this.statusBarHeight=e.statusBarHeight||20,this.statusMsg="\u9875\u9762\u5DF2\u52A0\u8F7D",this.checkAuth()},methods:{handleCameraError(e){m("error","at pages/test/camera-min.nvue:62","Camera Error:",e),this.statusMsg="\u6444\u50CF\u5934\u9519\u8BEF: "+(e.detail.errMsg||"\u672A\u77E5"),uni.showToast({title:"\u6444\u50CF\u5934\u542F\u52A8\u5931\u8D25",icon:"none"})},checkAuth(){let e=uni.getAppAuthorizeSetting();this.authStatus=e.cameraAuthorized||"\u672A\u68C0\u6D4B\u5230",e.cameraAuthorized==="denied"?(this.statusMsg="\u6743\u9650\u88AB\u62D2\u7EDD",uni.showModal({title:"\u6743\u9650\u63D0\u793A",content:"\u6444\u50CF\u5934\u6743\u9650\u5DF2\u88AB\u62D2\u7EDD\uFF0C\u8BF7\u524D\u5F80\u7CFB\u7EDF\u8BBE\u7F6E\u5F00\u542F",confirmText:"\u53BB\u8BBE\u7F6E",success:o=>{o.confirm&&uni.openAppAuthorizeSetting()}})):this.statusMsg="\u6743\u9650\u6B63\u5E38"},back(){uni.navigateBack()}}};function B(e,o,a,n,r,s){let d=(0,t.resolveComponent)("button");return(0,t.openBlock)(),(0,t.createElementBlock)("scroll-view",{scrollY:!0,showScrollbar:!0,enableBackToTop:!0,bubble:"true",style:{flexDirection:"column"}},[(0,t.createElementVNode)("view",{class:"camera-min-page"},[(0,t.createElementVNode)("view",{class:"status-bar",style:(0,t.normalizeStyle)({height:r.statusBarHeight+"px"})},null,4),(0,t.createElementVNode)("view",{class:"header"},[(0,t.createElementVNode)("u-text",{class:"title"},"\u6444\u50CF\u5934\u6700\u5C0F\u53EF\u7528\u6D4B\u8BD5"),(0,t.createElementVNode)("u-text",{class:"subtitle"},"\u4EC5\u7528\u4E8E\u68C0\u6D4B App \u7AEF\u6444\u50CF\u5934\u753B\u9762\u662F\u5426\u6B63\u5E38")]),(0,t.createElementVNode)("view",{class:"camera-container"},[(0,t.createElementVNode)("camera",{class:"live-camera",devicePosition:"back",flash:"off",onError:o[0]||(o[0]=(..._)=>s.handleCameraError&&s.handleCameraError(..._))},[(0,t.createElementVNode)("cover-view",{class:"camera-overlay"},[(0,t.createElementVNode)("u-text",{class:"overlay-text"},"\u539F\u751F\u7EC4\u4EF6\u8FD0\u884C\u4E2D")])],32)]),(0,t.createElementVNode)("view",{class:"debug-info"},[(0,t.createElementVNode)("u-text",{class:"info-item"},"\u72B6\u6001\uFF1A"+(0,t.toDisplayString)(r.statusMsg),1),(0,t.createElementVNode)("u-text",{class:"info-item"},"\u6743\u9650\uFF1A"+(0,t.toDisplayString)(r.authStatus),1)]),(0,t.createVNode)(d,{class:"action-btn",onClick:s.checkAuth},{default:(0,t.withCtx)(()=>[(0,t.createTextVNode)("\u68C0\u67E5\u6743\u9650")]),_:1},8,["onClick"]),(0,t.createVNode)(d,{class:"action-btn secondary",onClick:s.back},{default:(0,t.withCtx)(()=>[(0,t.createTextVNode)("\u8FD4\u56DE")]),_:1},8,["onClick"])])])}var i=h(A,[["render",B],["styles",[w]]]);var u=plus.webview.currentWebview();if(u){let e=parseInt(u.id),o="pages/test/camera-min",a={};try{a=JSON.parse(u.__query__)}catch(r){}i.mpType="page";let n=Vue.createPageApp(i,{$store:getApp({allowDefault:!0}).$store,__pageId:e,__pagePath:o,__pageQuery:a});n.provide("__globalStyles",Vue.useCssStyles([...__uniConfig.styles,...i.styles||[]])),n.mount("#root")}})();
