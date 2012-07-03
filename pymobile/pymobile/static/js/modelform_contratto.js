// <<<<<<< HEAD
// var addTariffaForm = function(j_obj){
	// var last_tr = j_obj.closest("tr").prev("tr");
	// var in_tot = $("#id_pianotariffario_set-TOTAL_FORMS");
	// var forms_count = in_tot.attr("value");
	// var new_forms_count = parseInt(forms_count) + 1;
//     
    // // creiamo la nuova form da aggiungere
	// var new_form = j_obj.closest("tr").next("tr").clone(true);
	// new_form.find(":input").each(function(){
		// console.log($(this));
		// var id = $(this).attr("id");
		// var new_id = id.replace("__prefix__", forms_count);
		// $(this).attr("id", new_id);
		// var name = $(this).attr("name");
		// var new_name = name.replace("__prefix__", forms_count);
		// $(this).attr("name", new_name);
	// });
	// new_form.find("label").each(function(){
		// var lfor = $(this).attr("for");
		// var new_lfor = lfor.replace("__prefix__", forms_count);
		// $(this).attr("for", new_lfor);
	// });
//     
    // // aggiorniamo il numero di form
    // in_tot.val(new_forms_count);
//     
    // // inseriamo la nuova form
    // // var button = $('<input type="button" class="del_pt" value="Cancella" />');
	// // chilnew_form.append(button).hide().insertAfter(pt_fs.find(".tariffa_fieldset:last")).fadeIn(1000);
	// new_form.hide().insertAfter(last_tr).fadeIn(1000);
	// $("form.modelform select#id_pianotariffario_set-"+forms_count+"-tariffa").combobox();
// 	
	// // aggiungiamo l'event handler per il bottone "Cancella"
	// // $(".del_pt").click(function(e){
// =======
jQuery(document).ready(function($){
	resetTotalForm();
	// $("form button.back"),click(function(e){
// >>>>>>> master
		// e.preventDefault();
		// history.go(-1);
	// });
	
	$("tbody a#add_datopianotariffario").click(function(e){
		// event handler per aggiungere dinamicamente form per le tariffe
		e.preventDefault();
		console.log("eccomi");
		addDatoPTForm($(this));		     
	});	
	$("tbody.pianotariffario button.add_tariffa").click(function(e){
		// event handler per aggiungere dinamicamente form per le tariffe
		e.preventDefault();
		addTariffaForm($(this));		     
	});
	
	function addTariffaForm(j_obj){
		var last_tr = j_obj.closest("tr").prev("tr");
		var in_tot = $("#id_pianotariffario_set-TOTAL_FORMS");
		var forms_count = in_tot.attr("value");
		var new_forms_count = parseInt(forms_count) + 1;
	    
	    // creiamo la nuova form da aggiungere
		var new_form = $("tr.empty_form:hidden").clone(true);
		// var options = $("select#id_pianotariffario_set-0-tariffa option");
		// console.log(options);
		// new_form.find("select#id_pianotariffario_set-__prefix__-tariffa option").after(options);
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

	function resetTotalForm(){
		// sottraiamo 2 perché una "tr" è per il bottone ed un'altra per la empty_form
		var empty_form = $("tr.empty_form:hidden");
		var options = $("select#id_pianotariffario_set-0-tariffa option").not("[value='']").clone(true);
		empty_form.find("select#id_pianotariffario_set-__prefix__-tariffa option").after(options);
		var n_trs = $("tbody.pianotariffario > tr").length - 2;
		$("#id_pianotariffario_set-TOTAL_FORMS").attr("value", n_trs);
		$("tbody.formset_info:first").find("input[id*='-TOTAL_FORMS']").attr("value", 0);;
	};
	
	function addDatoPTForm(j_obj){
		var last_tr = j_obj.closest("tbody").prev("tbody");
		var in_tot = j_obj.closest("tbody").siblings("tbody.formset_info:first").find("input[id*='-TOTAL_FORMS']");
		// var in_tot = $("#id_datopianotariffario_set-TOTAL_FORMS");
		var forms_count = in_tot.attr("value");
		var new_forms_count = parseInt(forms_count) + 1;
	    // creiamo la nuova form da aggiungere
		var new_form = $("tbody.empty_datopianotariffario:hidden").first().clone(true);
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
	    // $("<tr><td>").insertAfter(last_tr).fadeIn(1000);
		new_form.hide().insertAfter(last_tr).fadeIn(1000).css('display', '');
	};	
});	
