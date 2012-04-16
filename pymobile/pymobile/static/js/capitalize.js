jQuery(document).ready(function($){
	$("form:not(#login_form) input[type='text']").not("#id_email").not("#id_username").keyup(function(e){
		$(this).val($(this).val().toUpperCase());
	});
});