jQuery(document).ready(function($){
	resetTotalForm();
		
	$("tbody a#add_datopianotariffario").click(function(e){
		// event handler per aggiungere dinamicamente form per le tariffe
		e.preventDefault();
		addDatoPTForm($(this));		     
	});	

	function resetTotalForm(){	
		// resettiamo il numero di form per i dati
		var formsets = $("table.formset_table");
		formsets.each(function(){
			var in_tot = $(this).find("tbody.formset_management").find("input[id*='-TOTAL_FORMS']");
			var n_tables = $(this).find("table.form_table").length;
			console.log(n_tables);
			in_tot.attr("value", n_tables);	
		});
	};
	
	function addDatoPTForm(j_obj){
		var parent = j_obj.closest("tbody");
		var empty_form = parent.next("tbody").find("table.empty_form:hidden");
		console.log(empty_form);
		var in_tot = parent.siblings("tbody.formset_management").find("input[id*='-TOTAL_FORMS']");
		console.log(in_tot);
		var forms_count = in_tot.attr("value");
		console.log(forms_count);
		var new_forms_count = parseInt(forms_count) + 1;
	    // creiamo la nuova form da aggiungere
		var new_form = empty_form.clone(true);
		new_form.attr("class", "form_table");
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
	    console.log(in_tot.val());
	    
	    // inseriamo la nuova form
	    var obj = parent.prev("tbody.forms");
	    new_form.hide().appendTo(obj).fadeIn(1000).css('display', '');
		
	};	
});	
