$(document).ready(function(){
	var data_richiamare_field = $("form #id_data_richiamare").parents("tbody.field");
	data_richiamare_field.hide("fast");
	var richiamare = $("form #id_richiamare");
	if (richiamare.attr("checked")){
		data_richiamare_field.show("fast");
	};
	richiamare.change(function(e){
		if (richiamare.attr("checked")){
			data_richiamare_field.show("fast");
		} else {
			data_richiamare_field.hide("fast");		
		};
	});
});
