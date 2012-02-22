var displaySuccessMessage = function(msg, elem) {
	var msg_div = $('<div class="success_msg"><p>' + msg + '</p></div>');
	msg_div.prependTo(elem).fadeIn('slow').animate({ opacity: 1.0 }, 
		3000).fadeOut('slow',function(){ $(msg_div).html(""); });
}

var displayErrorMessage = function(msg, elem_parent) {
	var msg_div = $('<div class="error_msg"><p>' + msg + '</p></div>');
	msg_div.prependTo(elem).fadeIn('slow').animate({ opacity: 1.0 }, 
		3000).fadeOut('slow',function(){ $(msg_div).html(""); });
}
