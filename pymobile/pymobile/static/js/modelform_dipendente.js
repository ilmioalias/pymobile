$(document).ready(function(){
	$(".modelform tbody.field select#id_ruolo").val("agt");
	// var fisso = $("#id_fisso");
	// if (fisso.length){
// 		
	// };
	$(".modelform .retribuzione_table tbody.field input[id*='provvigione_contratto']").attr("value", "50");
	var txt = "blindato: 1, provvigione: 10; ";
	$(".modelform .retribuzione_table tbody.field textarea[id*='provvigione_bonus']").attr("value", txt);
	$(".modelform .retribuzione_table tbody.field input[id*='provvigione_contratto']").after("<span>%</span>");
	$(".modelform tbody.field").on("change", "select#id_ruolo", function(e){
		j_obj = $(this);
		var value = j_obj.attr("value");
		var form = j_obj.closest("form");
		if (value == "agt"){
			var txt = "blindato: 1, provvigione: 10; ";
			form.find(".retribuzione_table textarea[id*='provvigione_bonus']").attr("value", txt);
			form.find(".retribuzione_table input[id*='provvigione_contratto']").attr("value", "50");
			form.find(".retribuzione_table input[id*='provvigione_contratto']").next("span").text("%");
		} else if (value == "tel"){
			var txt = "tipo: sim, provvigione: 1;";
			txt += "gestore: telecom, tipo: ull, provvigione: 10; ";
			txt += "gestore: telecom, tipo: nip, provvigione: 10; ";
			txt += "gestore: telecom, tipo: nip, provvigione: 10; ";
			txt += "tipo: adsl, provvigione: 5; ";
			txt += "tipo: adsl, fascia: premium, provvigione: 10;";
			form.find(".retribuzione_table textarea[id*='provvigione_bonus']").attr("value", txt);
         	form.find(".retribuzione_table input[id*='provvigione_contratto']").attr("value", "10");
			form.find(".retribuzione_table input[id*='provvigione_contratto']").next("span").text("€");			
		};
	});
});