jQuery(document).ready(function($){
	var options = {
		format: "%d/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
	};
	console.log("eccomi");
	options.earliest = $("input#earliest").val();
	options.latest = $("input#latest").val();
	var data_inizio = $("form.modelform input#id_data_inizio");
	var data_fine = $("form.modelform input#id_data_fine");
	data_inizio.AnyTime_noPicker().AnyTime_picker(options);
	if (data_fine.length){
		if (!data_inizio.val()){
			data_fine.attr("disabled", "true");
		} else {
			dataInizioChanged(data_inizio, data_fine, options);		
		};
		data_inizio.change(function(e){
			e.preventDefault();	
			dataInizioChanged(data_inizio, data_fine, options);
		});
	};	
	function dataInizioChanged(inizio, fine, opts){
		var rangeConv = new AnyTime.Converter({format: "%d/%m/%Y"});
		var fromDay = rangeConv.parse(inizio.val()).getTime();
		if (fine.val()){
			var toDay = rangeConv.parse(fine.val()).getTime();
			if (toDay < fromDay){
				fine.val("");
			}	
		};
	  	var e = new Date(fromDay);
	  	e.setHours(0,0,0,0);
	  	opts.earliest = e;
	  	fine.removeAttr("disabled").AnyTime_noPicker().AnyTime_picker(opts);		
	};		
});
