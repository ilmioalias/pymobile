$(document).ready(function(){
	$(".modelform tbody.field select#id_gestore").val("tim");
	$(".modelform tbody.field select#id_gestore").each(function(){
		j_obj = $(this);
		var value = j_obj.attr("value");
		var form = j_obj.closest("form");
		form.find(".hidden").closest(".modelform tbody.field").hide();
		form.find("."+value).closest(".modelform tbody.field").fadeIn("slow");					
	});
	$(".modelform tbody.field").on("change", "select#id_gestore", function(e){
		j_obj = $(this);
		var value = j_obj.attr("value");
		var form = j_obj.closest("form");
		form.find(".hidden").closest(".modelform tbody.field").hide();
		// if (value == "edison"){
			// form.find("tbody.modelfield label[for='id_sac']").text("Provvigione S.A.C.");	
		// } else {
			// form.find("tbody.modelfield label[for='id_sac']").text("Provvigione per contratto");
		// };
		form.find("."+value).closest(".modelform tbody.field").fadeIn("slow");
	});
});