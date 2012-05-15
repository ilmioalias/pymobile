jQuery(document).ready(function($){
	$("form:not(#login_form) input[type='text']").not("#id_email").not("#id_username").keyup(function(e){
		console.log($(this).val());
		var value = $(this).val().toUpperCase()
		$(this).val(value);
		console.log($(this).val());
	});
});