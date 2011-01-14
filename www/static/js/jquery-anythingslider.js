/*
 AnythingSlider v1.5.6.2 minified using Google Closure Compiler
 By Chris Coyier: http://css-tricks.com
 with major improvements by Doug Neiner: http://pixelgraphics.us/
 based on work by Remy Sharp: http://jqueryfordesigners.com/
*/

(function(c){c.anythingSlider=function(g,h){var a=this;a.$el=c(g).addClass("anythingBase").wrap('<div class="anythingSlider"><div class="anythingWindow" /></div>');a.$el.data("AnythingSlider",a);a.init=function(){a.options=c.extend({},c.anythingSlider.defaults,h);c.isFunction(a.options.onBeforeInitialize)&&a.$el.bind("before_initialize",a.options.onBeforeInitialize);a.$el.trigger("before_initialize",a);a.$wrapper=a.$el.parent().closest("div.anythingSlider").addClass("anythingSlider-"+a.options.theme); a.$window=a.$el.closest("div.anythingWindow");a.$controls=c('<div class="anythingControls"></div>').appendTo(c(a.options.appendControlsTo).length?c(a.options.appendControlsTo):a.$wrapper);a.$nav=c('<ul class="thumbNav" />').appendTo(a.$controls);a.timer=null;a.flag=false;a.playing=false;a.hovered=false;a.panelSize=[];a.currentPage=a.options.startPanel;a.options.playRtl&&a.$wrapper.addClass("rtl");a.original=[a.options.autoPlay,a.options.buildNavigation,a.options.buildArrows];a.updateSlider();a.$currentPage= a.$items.eq(a.currentPage);a.$lastPage=a.$currentPage;a.runTimes=c("div.anythingSlider").index(a.$wrapper)+1;a.regex=RegExp("panel"+a.runTimes+"-(\\d+)","i");if(!c.isFunction(c.easing[a.options.easing]))a.options.easing="swing";a.options.theme!="default"&&!c("link[href*="+a.options.theme+"]").length&&c("body").append('<link rel="stylesheet" href="'+a.options.themeDirectory.replace(/\{themeName\}/g,a.options.theme)+'" type="text/css" />');a.options.pauseOnHover&&a.$wrapper.hover(function(){if(a.playing){a.$el.trigger("slideshow_paused", a);a.clearTimer(true)}},function(){if(a.playing){a.$el.trigger("slideshow_unpaused",a);a.startStop(a.playing,true)}});var b=a.options.hashTags?a.gotoHash()||a.options.startPanel:a.options.startPanel;a.setCurrentPage(b,false);a.slideControls(false);a.$wrapper.hover(function(d){a.hovered=d.type=="mouseenter"?true:false;a.slideControls(a.hovered,false)});a.options.enableKeyboard&&c(document).keyup(function(d){if(a.$wrapper.is(".activeSlider"))switch(d.which){case 39:a.goForward();break;case 37:a.goBack()}}); c.isFunction(a.options.onShowPause)&&a.$el.bind("slideshow_paused",a.options.onShowPause);c.isFunction(a.options.onShowUnpause)&&a.$el.bind("slideshow_unpaused",a.options.onShowUnpause);c.isFunction(a.options.onSlideInit)&&a.$el.bind("slide_init",a.options.onSlideInit);c.isFunction(a.options.onSlideBegin)&&a.$el.bind("slide_begin",a.options.onSlideBegin);c.isFunction(a.options.onShowStop)&&a.$el.bind("slideshow_stop",a.options.onShowStop);c.isFunction(a.options.onShowStart)&&a.$el.bind("slideshow_start", a.options.onShowStart);c.isFunction(a.options.onInitialized)&&a.$el.bind("initialized",a.options.onInitialized);c.isFunction(a.options.onSlideComplete)&&a.$el.bind("slide_complete",function(){setTimeout(function(){a.options.onSlideComplete(a)},0)});a.$el.trigger("initialized",a)};a.updateSlider=function(){a.$el.find("li.cloned").remove();a.$nav.empty();a.$items=a.$el.find("> li");a.pages=a.$items.length;if(a.options.resizeContents){a.options.width&&a.$wrapper.add(a.$items).css("width",a.options.width); a.options.height&&a.$wrapper.add(a.$items).css("height",a.options.height)}if(a.pages===1){a.options.autoPlay=false;a.options.buildNavigation=false;a.options.buildArrows=false;a.$controls.hide();a.$nav.hide();a.$forward&&a.$forward.add(a.$back).hide()}else{a.options.autoPlay=a.original[0];a.options.buildNavigation=a.original[1];a.options.buildArrows=a.original[2];a.$controls.show();a.$nav.show();a.$forward&&a.$forward.add(a.$back).show()}a.buildNavigation();if(a.options.autoPlay){a.playing=!a.options.startStopped; a.buildAutoPlay()}a.options.buildArrows&&a.buildNextBackButtons();a.$el.prepend(a.$items.filter(":last").clone().addClass("cloned").removeAttr("id"));a.$el.append(a.$items.filter(":first").clone().addClass("cloned").removeAttr("id"));a.$el.find("li.cloned").each(function(){c(this).html(function(b,d){return d.replace(/<a/gi,"<span").replace(/\/a>/gi,"/span>")})});a.$items=a.$el.find("> li").addClass("panel");a.setDimensions();a.options.resizeContents||c(window).load(function(){a.setDimensions()}); if(a.currentPage>a.pages){a.currentPage=a.pages;a.setCurrentPage(a.pages,false)}a.$nav.find("a").eq(a.currentPage-1).addClass("cur");a.hasEmb=!!a.$items.find("embed[src*=youtube]").length;a.hasSwfo=typeof swfobject!=="undefined"&&swfobject.hasOwnProperty("embedSWF")&&c.isFunction(swfobject.embedSWF)?true:false;a.hasEmb&&a.hasSwfo&&a.$items.find("embed[src*=youtube]").each(function(b){var d=c(this).parent()[0].tagName=="OBJECT"?c(this).parent():c(this);d.wrap('<div id="ytvideo'+b+'"></div>');swfobject.embedSWF(c(this).attr("src")+ "&enablejsapi=1&version=3&playerapiid=ytvideo"+b,"ytvideo"+b,d.attr("width"),d.attr("height"),"10",null,null,{allowScriptAccess:"always",wmode:a.options.addWmodeToObject},{"class":d.attr("class"),style:d.attr("style")})});a.$items.find("a").unbind("focus").bind("focus",function(b){a.$items.find(".focusedLink").removeClass("focusedLink");c(this).addClass("focusedLink");var d=c(this).closest(".panel");if(!d.is(".activePage")){a.gotoPage(a.$items.index(d));b.preventDefault()}})};a.buildNavigation=function(){a.options.buildNavigation&& a.pages>1&&a.$items.filter(":not(.cloned)").each(function(b){var d=b+1;b=c("<a href='#'></a>").addClass("panel"+d).wrap("<li />");a.$nav.append(b.parent());if(c.isFunction(a.options.navigationFormatter)){var e=a.options.navigationFormatter(d,c(this));b.html(e);parseInt(b.css("text-indent"),10)<0&&b.addClass(a.options.tooltipClass).attr("title",e)}else b.text(d);b.bind(a.options.clickControls,function(f){if(!a.flag&&a.options.enableNavigation){a.flag=true;setTimeout(function(){a.flag=false},100);a.gotoPage(d); a.options.hashTags&&a.setHash(d)}f.preventDefault()})})};a.buildNextBackButtons=function(){if(!a.$forward){a.$forward=c('<span class="arrow forward"><a href="#">'+a.options.forwardText+"</a></span>");a.$back=c('<span class="arrow back"><a href="#">'+a.options.backText+"</a></span>");a.$back.bind(a.options.clickArrows,function(b){a.goBack();b.preventDefault()});a.$forward.bind(a.options.clickArrows,function(b){a.goForward();b.preventDefault()});a.$back.add(a.$forward).find("a").bind("focusin focusout", function(){c(this).toggleClass("hover")});a.$wrapper.prepend(a.$forward).prepend(a.$back);a.$arrowWidth=a.$forward.width()}};a.buildAutoPlay=function(){if(!a.$startStop){a.$startStop=c("<a href='#' class='start-stop'></a>").html(a.playing?a.options.stopText:a.options.startText);a.$controls.prepend(a.$startStop);a.$startStop.bind(a.options.clickSlideshow,function(b){if(a.options.enablePlay){a.startStop(!a.playing);if(a.playing)a.options.playRtl?a.goBack(true):a.goForward(true)}b.preventDefault()}).bind("focusin focusout", function(){c(this).toggleClass("hover")});a.startStop(a.playing)}};a.setDimensions=function(){var b,d,e,f,j,i=0,k=a.$window.width(),l=c(window).width();a.$items.each(function(m){e=c(this).children("*");if(a.options.resizeContents){b=parseInt(a.options.width,10)||k;d=parseInt(a.options.height,10)||a.$window.height();c(this).css({width:b,height:d});if(e.length==1){e.css({width:"100%",height:"100%"});e[0].tagName=="OBJECT"&&e.find("embed").andSelf().attr({width:"100%",height:"100%"})}}else{b=c(this).width(); j=b>=l?true:false;if(e.length==1&&j){f=e.width()>=l?k:e.width();c(this).css("width",f);e.css("max-width",f);b=f}b=j?a.options.width||k:b;c(this).css("width",b);d=c(this).outerHeight();c(this).css("height",d)}a.panelSize[m]=[b,d,i];i+=b});a.$el.css("width",i<a.options.maxOverallWidth?i:a.options.maxOverallWidth)};a.gotoPage=function(b,d){if(a.pages!==1){a.$lastPage=a.$items.eq(a.currentPage);if(typeof b==="undefined"||b===null){b=a.options.startPage;a.setCurrentPage(a.options.startPage)}if(!(a.hasEmb&& a.checkVideo(a.playing))){if(b>a.pages+1)b=a.pages;if(b<0)b=1;a.$currentPage=a.$items.eq(b);a.currentPage=b;a.$el.trigger("slide_init",a);a.slideControls(true,false);if(d!==true)d=false;if(!d||a.options.stopAtEnd&&b==a.pages)a.startStop(false);a.$el.trigger("slide_begin",a);a.options.resizeContents||a.$wrapper.filter(":not(:animated)").animate({width:a.panelSize[b][0],height:a.panelSize[b][1]},{queue:false,duration:a.options.animationTime,easing:a.options.easing});a.$window.filter(":not(:animated)").animate({scrollLeft:a.panelSize[b][2]}, {queue:false,duration:a.options.animationTime,easing:a.options.easing,complete:function(){a.endAnimation(b,d)}})}}};a.endAnimation=function(b){if(b===0){a.$window.scrollLeft(a.panelSize[a.pages][2]);b=a.pages}else if(b>a.pages){a.$window.scrollLeft(a.panelSize[1][2]);b=1}a.setCurrentPage(b,false);a.$items.removeClass("activePage").eq(b).addClass("activePage");a.hovered||a.slideControls(false);if(a.hasEmb){b=a.$currentPage.find("object[id*=ytvideo], embed[id*=ytvideo]");b.length&&c.isFunction(b[0].getPlayerState)&& b[0].getPlayerState()>0&&b[0].getPlayerState()!=5&&b[0].playVideo()}a.$el.trigger("slide_complete",a);a.options.autoPlayLocked&&!a.playing&&setTimeout(function(){a.startStop(true)},a.options.resumeDelay-a.options.delay)};a.setCurrentPage=function(b,d){if(b>a.pages+1)b=a.pages;if(b<0)b=1;if(a.options.buildNavigation){a.$nav.find(".cur").removeClass("cur");a.$nav.find("a").eq(b-1).addClass("cur")}if(!d){a.$wrapper.css({width:a.panelSize[b][0],height:a.panelSize[b][1]});a.$wrapper.scrollLeft(0);a.$window.scrollLeft(a.panelSize[b][2])}a.currentPage= b;if(!a.$wrapper.is(".activeSlider")){c(".activeSlider").removeClass("activeSlider");a.$wrapper.addClass("activeSlider")}};a.goForward=function(b){if(b!==true){b=false;a.startStop(false)}a.gotoPage(a.currentPage+1,b)};a.goBack=function(b){if(b!==true){b=false;a.startStop(false)}a.gotoPage(a.currentPage-1,b)};a.gotoHash=function(){var b=window.location.hash.match(a.regex);return b===null?"":parseInt(b[1],10)};a.setHash=function(b){var d="panel"+a.runTimes+"-",e=window.location.hash;if(typeof e!=="undefined")window.location.hash= e.indexOf(d)>0?e.replace(a.regex,d+b):e+"&"+d+b};a.slideControls=function(b){var d=b?"slideDown":"slideUp",e=b?0:a.options.animationTime,f=b?a.options.animationTime:0;b=b?0:1;a.options.toggleControls&&a.$controls.stop(true,true).delay(e)[d](a.options.animationTime/2).delay(f);if(a.options.buildArrows&&a.options.toggleArrows){if(!a.hovered&&a.playing)b=1;a.$forward.stop(true,true).delay(e).animate({right:b*a.$arrowWidth,opacity:f},a.options.animationTime/2);a.$back.stop(true,true).delay(e).animate({left:b* a.$arrowWidth,opacity:f},a.options.animationTime/2)}};a.clearTimer=function(b){if(a.timer){window.clearInterval(a.timer);b||a.$el.trigger("slideshow_stop",a)}};a.startStop=function(b,d){if(b!==true)b=false;b&&!d&&a.$el.trigger("slideshow_start",a);a.playing=b;if(a.options.autoPlay){a.$startStop.toggleClass("playing",b).html(b?a.options.stopText:a.options.startText);if(parseInt(a.$startStop.css("text-indent"),10)<0)a.$startStop.addClass(a.options.tooltipClass).attr("title",b?"Stop":"Start")}if(b){a.clearTimer(true); a.timer=window.setInterval(function(){a.hasEmb&&a.checkVideo(b)||(a.options.playRtl?a.goBack(true):a.goForward(true))},a.options.delay)}else a.clearTimer()};a.checkVideo=function(b){var d,e,f=false;a.$items.find("object[id*=ytvideo], embed[id*=ytvideo]").each(function(){d=c(this);if(d.length&&c.isFunction(d[0].getPlayerState)){e=d[0].getPlayerState();if(b&&(e==1||e>2)&&a.$items.index(d.closest("li.panel"))==a.currentPage&&a.options.resumeOnVideoEnd)f=true;else e>0&&d[0].pauseVideo()}});return f}; a.init()};c.anythingSlider.defaults={width:null,height:null,resizeContents:true,tooltipClass:"tooltip",theme:"default",themeDirectory:"css/theme-{themeName}.css",startPanel:1,hashTags:true,enableKeyboard:true,buildArrows:true,toggleArrows:false,buildNavigation:true,enableNavigation:true,toggleControls:false,appendControlsTo:null,navigationFormatter:null,forwardText:"&raquo;",backText:"&laquo;",enablePlay:true,autoPlay:true,autoPlayLocked:false,startStopped:false,pauseOnHover:true,resumeOnVideoEnd:true, stopAtEnd:false,playRtl:false,startText:"Start",stopText:"Stop",delay:3E3,resumeDelay:15E3,animationTime:600,easing:"swing",onBeforeInitialize:null,onInitialized:null,onShowStart:null,onShowStop:null,onShowPause:null,onShowUnpause:null,onSlideInit:null,onSlideBegin:null,onSlideComplete:null,clickArrows:"click",clickControls:"click focusin",clickSlideshow:"click",addWmodeToObject:"opaque",maxOverallWidth:32766};c.fn.anythingSlider=function(g){return this.each(function(){var h=c(this).data("AnythingSlider"); if((typeof g).match("object|undefined"))if(h)h.updateSlider();else new c.anythingSlider(this,g);else if(/\d/.test(g)&&!isNaN(g)&&h){var a=typeof g=="number"?g:parseInt(c.trim(g),10);a>=1&&a<=h.pages&&h.gotoPage(a)}})}})(jQuery);
