var deleteObj = function(j_obj){
	var href = j_obj.attr("href");
	var name = j_obj.attr("id").replace(/^del_/, "");
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();
};


var modifyObj = function(j_obj){
	var href = j_obj.attr("href");
	var name = j_obj.attr("id").replace(/^mod_/, "");
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();
};

var cancel = function(){
	window.opener.location.reload(true);
	window.close();
}

var redirectAfter = function(win, url){
	win.close();
	window.location.replace(url);
};

$(document).ready(function(){
	$(".deleteobj").click(function(e){
		e.preventDefault();
		deleteObj($(this));
	});
	$(".modifyobj").click(function(e){
		e.preventDefault();
		modifyObj($(this));
	});
	$(".cancel").click(function(e){
		e.preventDefault();
		cancel();
	});	
});