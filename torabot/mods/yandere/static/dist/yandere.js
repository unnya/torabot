define("torabot/yandere/0.1.0/yandere",["./create_tag_search_regex","./retrieve_tag_search","./reorder_search_results","./split_result","main/search"],function(a,b){var c={create_tag_search_regex:a("./create_tag_search_regex"),retrieve_tag_search:a("./retrieve_tag_search"),reorder_search_results:a("./reorder_search_results"),split_result:a("./split_result"),complete_tag:function(a){var b=c.create_tag_search_regex(a,{global:!0}),d=c.retrieve_tag_search(b,c.options.source,{max_results:100});d=c.reorder_search_results(a,d);var e=d;return c.bubble_rating_tags(e,a),e=e.slice(0,null!=c.options.max_results?c.options.max_results:10),c.split_result(e)},bubble_rating_tags:function(a,b){-1!="sqe".indexOf(b)&&a.unshift("0`"+b+"` ")},match:function(a,b){var d=c.complete_tag(a);b($.map(d[0],function(a){return{value:a}}))},init:function(b){c.options=b,a("main/search").$q.typeahead({hint:!0,highlight:!0,minLength:1},{name:"yandere",displayKey:"value",source:c.match})}};b.init=c.init}),define("torabot/yandere/0.1.0/create_tag_search_regex",[],function(a,b,c){c.exports=function(a,b){var c=a.split(""),d=[],e="(([^`]*_)?";if($.map(c,function(a){var b=RegExp.escape(a);e+=b}),e+=")",d.push(e),-1!=a.indexOf("_")){var f=a.split("_",1)[0],g=a.slice(f.length+1);f=RegExp.escape(f),g=RegExp.escape(g);var e="(";e+="("+f+"[^`]*_"+g+")",e+="|",e+="("+g+"[^`]*_"+f+")",e+=")",d.push(e)}if(!b.top_results_only){var e="(";$.map(c,function(a){var b=RegExp.escape(a);e+=b,e+="[^`]*"}),e+=")",d.push(e)}var h=d.join("|");return h="(\\d+)[^ ]*`("+h+")[^`]*`[^ ]* ",new RegExp(h,b.global?"g":"")}}),define("torabot/yandere/0.1.0/retrieve_tag_search",[],function(a,b,c){c.exports=function(a,b,c){var d=[],e=10;for(null!=c.max_results&&(e=c.max_results);d.length<e;){var f=a.exec(b);if(!f)break;var g=f[0];-1==g.indexOf(":deletethistag:")&&-1==d.indexOf(g)&&d.push(g)}return d}}),define("torabot/yandere/0.1.0/reorder_search_results",["torabot/yandere/0.1.0/create_tag_search_regex"],function(a,b,c){c.exports=function(b,c){var d=a("torabot/yandere/0.1.0/create_tag_search_regex")(b,{top_results_only:!0,global:!1}),e=[],f=[];return $.map(c,function(a){d.test(a)?e.push(a):f.push(a)}),e.concat(f)}}),define("torabot/yandere/0.1.0/split_result",[],function(a,b,c){c.exports=function(a){var b=[],c=[];return $.map(a,function(a){var d=a.match(/(\d+)`([^`]*)`(([^ ]*)`)? /);if(!d)throw ReportError("Unparsable cached tag: '"+a+"'",null,null,null,null),"Unparsable cached tag: '"+a+"'";var a=d[2],e=d[4];e=d[4]?e.split("`"):[],-1==b.indexOf(a)&&(b.push(a),c.push(e))}),[b,c]}});