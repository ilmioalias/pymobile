jQuery(document).ready(function($){
	function saveMailObject(j_obj){
		var form = j_obj.closest("form");
		var hidden = $("<input type='hidden' name='send_mail' />");
		form.append(hidden);
		form.submit();
	};	
	$("input.save_and_send_mail").click(function(e){
		e.preventDefault();
		console.log($(this));
		saveMailObject($(this));	
	});
});