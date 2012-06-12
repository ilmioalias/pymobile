function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
};

var getSubModelform = function(j_obj){
	var href = j_obj.attr("href");
	var name = j_obj.attr("id").replace(/^add_/, "");
	var win = window.open(href, name, 'height=480,width=640,resizable=yes,scrollbars=yes');
	win.focus();
};

var closeSubModelform = function(win, newId, newOpt){
	if (newId){
		newId = html_unescape(newId);
		newOpt = html_unescape(newOpt);
	    var elem_id = win.name.replace("^", "add_");
	    var elem = $("#" + elem_id);
	    if (elem){
	    	if (elem.is("select")){
		        var o = new Option(newOpt, newId, true);
		        elem.append(o);
		        elem.attr("disabled", "disabled");
		        var autocomplete = elem.next(".ui-autocomplete-input");
		        if (autocomplete){
		        	autocomplete.attr("value", newOpt);
		        };
	       	} else if (elem.is("input:hidden")){
		        $("span#id_span_cliente").text(newOpt);
		        elem.attr("value", newId);
	       	};
	    };		
	};
    win.close();
};

var cancelForm = function(){
	window.location.href="../"
	// window.opener.location.reload(true);
	// window.close();
};

var openConfirm = function(html){
	var href = html
	var name = "confirm";
	var win = window.open(name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.html(html);
	win.focus();	
};

var saveAddObject = function(j_obj){
	var form = j_obj.closest("form");
	var hidden = $("<input type='hidden' name='add_another' />");
	form.append(hidden);
	form.submit();
	// window.opener.location.reload(true);
	// window.close();
	// var data = form.serializeArray();
	// var url = form.attr("action");
// 	
	// $.ajax({
		// type: "POST",
		// url: url,
		// data: data,
		// datatype: "json",
		// success: function(json){
			// if(json){
				// var form_fieldset_div = form.find(".modelform_fieldset_div");
				// if (json["success"] == "True"){
					// var template = $(json["html"]).find(".modelform_fieldset");
					// form_fieldset_div.html(template);
					// displaySuccessMessage("<b>Elemento Inserito</b>", form);
				// } else {
					// var template = $(json["html"]).find(".modelform_fieldset");
					// form_fieldset_div.html(template);
					// displayErrorMessage("<b>Errore nell'Inserimento</b>", form);					
				// }
			// } else {
				// displayErrorMessage("<b>Errore nell'Inserimento</b>", form);
			// }
		// }
	// });
	// return false;
};

var resetForm = function(id_form){
	$(id_form)[0].reset();
};

var dateStartChanged = function(data_start, data_end){
	var rangeConv = new AnyTime.Converter({format: "%d/%m/%Y"});
	var fromDay = rangeConv.parse(data_start.val()).getTime();
	if (data_end.val()){
		var toDay = rangeConv.parse(data_end.val()).getTime();
		if (toDay <= fromDay){
			data_end.val("");
		}	
	};
	var oneDay = 24*60*60*1000;
	if (data_end.hasClass("scadenza")){
		// nel caso stiamo settando la data di scadenza di un contratto
		var earliest = new Date(fromDay);
		earliest.setFullYear(earliest.getFullYear() + 2);
	} else {
		var earliest = new Date(fromDay+oneDay);	
	};
  	earliest.setHours(0,0,0,0);
  	data_end.removeAttr("disabled").AnyTime_noPicker().AnyTime_picker({
  		earliest: earliest,
        format: "%d/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});		
};

var initModelformClickHandler = function(){
	$("form.modelform").on("click", "tbody.field a.add_subform", function(e){
		e.preventDefault();
		getSubModelform($(this));
	});
	$("input.modelform_save_and_add").click(function(){
		saveAddObject($(this));
		return false;
	});
	$("tbody.field input.date").AnyTime_picker({
		format: "%d/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});
	$("tbody.field input.datetime").AnyTime_picker({
		format: "%d/%m/%Y %H:%i",
		labelTitle: "Seleziona il giorno e l'ora",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
		labelHour: "Ora",
		labelMinute: "Minuto",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});
	$("tbody.field input.time").AnyTime_picker({
		format: "%H:%i",
		labelTitle: "Seleziona l'ora",
		labelHour: "Ora",
		labelMinute: "Minuto",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});
	$("form.modelform .cancel").click(function(e){
		e.preventDefault();
		cancelForm();
	});
	$("form.modelform input.dateclear").click(function(e){
		e.preventDefault();
		console.log("ciao");
		$(this).prev(".date, .datetime").val("").change();
	});
	$("form.modelform input.date_end").attr("disabled", "true");
	$("form.modelform input.date_start").AnyTime_picker({
		format: "%d/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});		
	$("form.modelform input.date_start").change(function(e){
		e.preventDefault();
		var data_start = $(this);
		// troviamo la data_end corrispondente alla data_start cambiata
		var field = data_start.attr("id").replace(/inizio$/, "");
		var data_end = $("form.modelform input.date_end").filter("#" + field + "fine");
		if (data_end.length == 0){			var data_end = $("form.modelform input.date_end").filter("#id_data_scadenza");
		};
		dateStartChanged(data_start, data_end);
	});
	$("form.modelform select#id_cliente:visible").combobox();
	$("form.modelform select#id_referente:visible").combobox();
	$("form.modelform select#id_telefonista:visible").combobox();
	$("form.modelform select#id_agente:visible").combobox();
	// $("form.modelform select#id_gestore").combobox();
	$("form.modelform select#id_dipendente:visible").combobox();
	$("form.modelform select#id_tariffa:visible").combobox();
	$("form.modelform select#id_appuntamento:visible").combobox();
	// il seguente serve per selezionare le select del piano tariffario nelle form dei contratti
	$("form.modelform select[id*='id_pianotariffario_set']:visible").filter(function() {
        return this.id.match(/tariffa/);
    }).combobox();
    $("form.modelform select#id_appuntamento:visible").combobox();
    $("form.modelform select#id_profile:visible").combobox();
    // FIXME: la funzione unload mi pare un poco invasiva
    // meglio spostare tutto in una nuova pagina invece che su un popup?
    // FIXME: sistemate assolutamente il reload della pagina quando il popup viene chiuso
    // $(window).unload(function(){
		// window.opener.location.reload();
    // });
};

$(document).ready(function(){
	initModelformClickHandler();
});