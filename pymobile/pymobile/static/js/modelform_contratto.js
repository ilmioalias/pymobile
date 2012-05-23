var addTariffaForm = function(j_obj){
	var last_tr = j_obj.closest("tr").prev("tr");
	var in_tot = $("#id_pianotariffario_set-TOTAL_FORMS");
	var forms_count = in_tot.attr("value");
	var new_forms_count = parseInt(forms_count) + 1;
    
    // creiamo la nuova form da aggiungere
	var new_form = j_obj.closest("tr").next("tr").clone(true);
	new_form.find(":input").each(function(){
		var id = $(this).attr("id");
		var new_id = id.replace("__prefix__", forms_count);
		$(this).attr("id", new_id);
		var name = $(this).attr("name");
		var new_name = name.replace("__prefix__", forms_count);
		$(this).attr("name", new_name);
	});
	new_form.find("label").each(function(){
		var lfor = $(this).attr("for");
		var new_lfor = lfor.replace("__prefix__", forms_count);
		$(this).attr("for", new_lfor);
	});
    
    // aggiorniamo il numero di form
    in_tot.val(new_forms_count);
    
    // inseriamo la nuova form
    // var button = $('<input type="button" class="del_pt" value="Cancella" />');
	// chilnew_form.append(button).hide().insertAfter(pt_fs.find(".tariffa_fieldset:last")).fadeIn(1000);
	new_form.hide().insertAfter(last_tr).fadeIn(1000);
	$("form.modelform select#id_pianotariffario_set-"+forms_count+"-tariffa").combobox();
	
	// aggiungiamo l'event handler per il bottone "Cancella"
	// $(".del_pt").click(function(e){
		// e.preventDefault();
// 		
		// $(this).parents(".tariffa_fieldset:first").fadeOut("fast", function(){
			// $(this).remove();
// 			
			// // aggiorniamo il numero di form
			// var forms_count = pt_fs.find("#id_" + name_fs + "-TOTAL_FORMS").attr("value");
			// var new_forms_count = parseInt(forms_count) - 1;
	    	// in_tot.attr("value", new_forms_count);							
		// });			
	// });	
};

var resetTotalTariffaForm = function(){
	// sottraiamo 2 perché una "tr" è per il bottone ed un'altra per la empty_form
	var n_trs = $("tbody.pianotariffario > tr").length - 2;
	$("#id_pianotariffario_set-TOTAL_FORMS").attr("value", n_trs);
};

var addDatoPTForm = function(j_obj){
	var last_tr = j_obj.closest("tr");
	var in_tot = $("#id_datopianotariffario_set-TOTAL_FORMS");
	var forms_count = in_tot.attr("value");
	var new_forms_count = parseInt(forms_count) + 1;
    // creiamo la nuova form da aggiungere
	// var new_form = j_obj.closest("tr").next("tr").clone(true);
	var new_form = $("#empty_pianotariffario").clone(true);
	new_form.find(":input").each(function(){
		var id = $(this).attr("id");
		var new_id = id.replace("__prefix__", forms_count);
		$(this).attr("id", new_id);
		var name = $(this).attr("name");
		var new_name = name.replace("__prefix__", forms_count);
		$(this).attr("name", new_name);
	});
	new_form.find("label").each(function(){
		var lfor = $(this).attr("for");
		var new_lfor = lfor.replace("__prefix__", forms_count);
		$(this).attr("for", new_lfor);
	});
    
    // aggiorniamo il numero di form
    in_tot.val(new_forms_count);
    
    // inseriamo la nuova form
    $("<tr><td></td></tr>").insertAfter(last_tr).fadeIn(1000);
	new_form.hide().insertAfter(last_tr).fadeIn(1000);
};

$(document).ready(function(){
	resetTotalTariffaForm();
	// $("form button.back"),click(function(e){
		// e.preventDefault();
		// history.go(-1);
	// });
	$("tbody.pianotariffario a#add_datopianotariffario").click(function(e){
		// event handler per aggiungere dinamicamente form per le tariffe
		e.preventDefault();
		addDatoPTForm($(this));		     
	});	
	$("tbody.pianotariffario button.add_tariffa").click(function(e){
		// event handler per aggiungere dinamicamente form per le tariffe
		e.preventDefault();
		addTariffaForm($(this));		     
	});
});