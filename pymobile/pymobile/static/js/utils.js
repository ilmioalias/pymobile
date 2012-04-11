jQuery(document).ready(function($){
	console.log("ciao");
	$("form:not[id=login_form] input[type='text']").not("[id='id_username']").not("[id='id_email']").keyup(function(e){
		console.log("val_0 " + $(this).val());
	});	
	$("form:not[id=login_form]").on("keyup", "input[type='text']:not[id='id_username']:not[id='id_email']", function(e){
		console.log("val_0 " + $(this).val());
		$(this).val($(this).val().toUpperCase());
		console.log("val_1 " + $(this).val());
	});
});