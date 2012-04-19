$(document).ready(function(){
	function changeFields(j_obj){
		var group = j_obj.find("option:selected").text();
		if (group != "telefonista"){
			$("form.modelform .tel").parents("form.modelform tbody.field").hide();
			$("form.modelform .guest").parents("form.modelform tbody.field").hide();
			$("form.modelform .admin").parents("form.modelform tbody.field").show();
		} else if (group == "telefonista") {
			$("form.modelform .tel").parents("form.modelform tbody.field").show();
			$("form.modelform .guest").parents("form.modelform tbody.field").hide();
			$("form.modelform .admin").parents("form.modelform tbody.field").hide();
		} else if (group == "guest") {
			$("form.modelform .tel").parents("form.modelform tbody.field").hide();
			$("form.modelform .guest").parents("form.modelform tbody.field").show();
			$("form.modelform .admin").parents("form.modelform tbody.field").hide();
		};
	};
	changeFields($("select#id_groups"));
	$("select#id_groups").change(function(e){
		e.preventDefault();
		changeFields($(this)); 
	});
});