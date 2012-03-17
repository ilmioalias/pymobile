var search_cur = "";
var sort_cur=""; 

var updateTable = function(html_data){
	var table = $(html_data);
	$(".table-container").html(table);		
};

var getSort = function(j_obj){
	var href = j_obj.attr("href").slice(1);
	return href;
	// if (href){
		// var parameters = href.split("&");
		// for (var i in parameters){
			// p = parameters[i].split("=");
			// k = p[0];
			// if (k == "in-sort"){
				// return {"sort": p[1]};
			// };
		// };
	// };
};

var sortTable = function(j_obj){
	var data_dict = {};
	var sort = getSort(j_obj);
	var search = search_cur;
	if (sort || search){
		var url = "?" + sort + "&" + search;
		console.log(url);
		$.get(url,
			function(data){
				updateTable(data);
			}
		);			
	};
	// jQuery.extend(data_dict, sort, search);
	// if (data_dict){
		// console.log(data_dict);
		// $.get(".",
			// data_dict,
			// function(data){
				// updateTable(data);
				// sort_cur = sort;
			// }
		// );			
	// };
};

var getFilter = function(form){
	var url = ""
	// var dict = {};
	form.find("input:text").each(function(){
		if ($(this).attr("value")){
			var key = "f" + $(this).attr("name");
			var value = $(this).attr("value");
			var cls = $(this).attr("class");
			// if (!(key in dict)){
				// dict[key] = new Array();
			// };
			if (cls){
				if (cls == "date_start"){
					// dict[key].push(">" + value);
					url += key + "=>" + value + "&";
				} else if (cls  == "date_end"){
					// dict[key].push("<" + value);
					url += key + "=<" + value + "&";
				} else if (cls.indexOf("ui-autocomplete-input") == -1){
					// dict[key].push(value);
					url += key + "==" + value + "&";
				};				
			} else {
				url += key + "=" + value + "&";
				// dict[key].push(value);
			};			
		}	
	});
	form.find("input[type=checkbox]:not(:checked)").each(function() {
		var key = "f" + $(this).attr("name");
		var value = $(this).attr("value");
		// if (!(key in dict)){
			// dict[key] = new Array();
		// };
		url += key + "=!" + value + "&";
		// dict[key].push("!" + value);		
	});
	form.find("select").each(function() {
		// var value = $(this).children("option:selected").attr("value");
		var key = "f" + $(this).attr("name");
		var opts = $(this).children("option:selected");
		if (opts.length > 0){
			// if (!(key in dict)){
				// dict[key] = new Array();
			// };		
			opts.each(function(){
				var value = $(this).attr("value");
				if (value){
					url += key + "==" + value + "&";
					// dict[key].push("=" + value);
				}			
			});
		};		
	});
	console.log(url);
	return url;
	// return dict;	
};

var filterTable = function(j_obj){
	var form = j_obj.closest("form");
	var data_dict = {};
	var search = getFilter(form);
	var sort = sort_cur;
	if (sort || search){
		var url = "?" + sort + "&" + search;
		$.get(url,
			function(data){
				updateTable(data);
				search_cur = search;
			}
		);	
	} else {
		resetFilterTable(j_obj);
	};	
	// jQuery.extend(data_dict, sort, search);
	// if (data_dict){
		// var url = "./?"
		// for (k in data_dict){
			// for (v in data_dict[k]){
				// url += k + "=" + data_dict[k][v] + "&"
			// };
		// };
		// $.get(url,
			// function(data){
				// updateTable(data);
				// search_cur = search;
			// }
		// );	
	// } else {
		// resetFilterTable(j_obj);
	// }
};

var resetFilterTable = function(j_obj){
	// if (window.location.search){
	// window.location.reload(true);
	// return;
	// };
	var form = j_obj.closest("form");
	form[0].reset();
	form.find(".data_end").AnyTime_noPicker().attr("disabled", "true");
	$.get(".",
		function(data){
			updateTable(data);
			search_cur = "";
		}
	);			
};

var getPage = function(j_obj){
	var href = j_obj.attr("href").slice(1);
	return href;
	// if (href){
		// var parameters = href.split("&");
		// for (var i in parameters){
			// p = parameters[i].split("=");
			// k = p[0];
			// if (k == "pag"){
				// return {"pag": p[1]};
			// }
		// }
	// };
};

var changePage = function(j_obj){
	var page = getPage(j_obj);
	var data_dict = {};
	jQuery.extend(data_dict, page, sort_cur, search_cur);
	if (data_dict){
		console.log(data_dict);
		$.get(".",
			data_dict,
			function(data){
				updateTable(data);
			}
		);		
	};
};

var dateStartChanged = function(data_start, data_end){
	var rangeConv = new AnyTime.Converter({format: "%e/%m/%Y"});
	var fromDay = rangeConv.parse(data_start.val()).getTime();
	if (data_end.val()){
		var toDay = rangeConv.parse(data_end.val()).getTime();
		if (toDay <= fromDay){
			data_end.val("");
		}	
	};
	// var oneDay = 24*60*60*1000;
  	// var erliest = new Date(fromDay+oneDay);
  	var erliest = new Date(fromDay);
  	erliest.setHours(0,0,0,0);
  	data_end.removeAttr("disabled").AnyTime_noPicker().AnyTime_picker({
  		earliest: erliest,
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

var addRow = function(j_obj){
	var href = j_obj.attr("href");
	var name = "Aggiungi Oggetto";
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();	
};

var modifyRow = function(j_obj){
	var href = j_obj.attr("href");
	var name = j_obj.attr("id").replace(/^mod_/, "");
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();
};

var deleteRow = function(j_obj){
	var href = j_obj.attr("href");
	var name = j_obj.attr("id").replace(/^del_/, "");
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();
};

var deleteRows = function(rows){
	var href = "del/?";
	rows.each(function(){
		var id = $(this).attr("value");
		href += "id=" + id + "&";
	});
	var name = "Delete Objects";
	var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
	win.focus();
};

var redirectAfter = function(win, url){
	window.location.replace(url);
	win.close();
};

var selectAllRow = function(j_obj){
	var table = j_obj.closest("#modeltable");
	table.find("tbody input.selection").each(function(){
 		console.log($(this));
		if (j_obj.attr("checked")){
			$(this).attr("checked", true);	
		} else {
			$(this).attr("checked", false);
		}
	});
};

var assignRows = function(rows, agt){
	var href = "assign/?";
	rows.each(function(){
		var row_id = $(this).attr("value");
		href += "id=" + row_id + "&";
	});
	if (agt){
		var agente_id = agt.attr("value");
		href += "agente=" + agente_id;
		var name = "Assign Objects";
		var win = window.open(href, name, 'height=600,width=800,resizable=yes,scrollbars=yes');
		win.focus();		
	};
};

var tableClickHandlers = function(){
	$("div.table-container").on("click", "thead input.selection_header", function(e){
		selectAllRow($(this));
	});
	$("div.table-container").on("click", "tbody input.selection", function(e){
		if (!$(this).attr("checked")){
			var header = $("div.table-container thead input.selection_header");
			if (header.attr("checked")){
				header.attr("checked", false);
			};
		};
	});	
	$("select.modeltable_actions").change(function(e){
		var opt_sel = $(this).find("option:selected").attr("value");
		if ($(this).siblings(".assign").length){
			if (opt_sel != "assign") {
				$(this).siblings(".assign").hide("fast");
			} else {
				$(this).siblings(".assign").show("fast");
			};
		};
	});
	$("button.modeltable_actions_ok").click(function(e){
		e.preventDefault();
		var action = $(this).siblings("select.modeltable_actions").find("option:selected").attr("value");
		var rows = $("#modeltable td > input.selection:checked");
		if (rows.length > 0){
			if (action == "delete") {
				deleteRows(rows);		
			} else if (action == "assign") {
				var agt = $(this).siblings("span.assign").find("select#id_assign").find("option:selected");
				if (agt){
					assignRows(rows, agt);
				};
			};
		};
	});	
	$("div.table-container").on("click", "th.sortable > a", function(e){
		e.preventDefault();
		sortTable($(this));
	});	
	$("div.table-container").on("click", "li.pagination a.next", function(e){
		e.preventDefault();
		changePage($(this));
	});
	$("div.table-container").on("click", "li.pagination a.previous", function(e){
		e.preventDefault();
		changePage($(this));
	});		
	$("div.table-container").on("click", "a.deleterow", function(e){
		e.preventDefault();
		deleteRow($(this));
	});
	// $("div#modeltable_div").on("click", "a.addrow", function(e){
		// e.preventDefault();
		// addRow($(this));
	// });
	// $("div#modeltable_div").on("click", "a.modifyrow", function(e){
		// e.preventDefault();
		// modifyRow($(this));
	// });		
	$("#filter_modeltable_search").click(function(e){
		e.preventDefault();
		filterTable($(this));
	});
	$("#filter_modeltable_reset").click(function(e){
		e.preventDefault();
		resetFilterTable($(this));
	});
	$("form#filter_modeltable_form input.date_end").attr("disabled", "true");
	$("form#filter_modeltable_form input.date_start").AnyTime_picker({
		format: "%d/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno",
		firstDOW: 1,
		dayAbbreviations: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
		monthAbbreviations : ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
	});		
	$("form#filter_modeltable_form input.date_start").change(function(e){
		e.preventDefault();
		var data_start = $(this);
		// troviamo la data_end corrispondente alla data_start cambiata
		var field = data_start.attr("id").replace(/inizio$/, "");
		var data_end = $("#filter_modeltable_form input.date_end").filter("#" + field + "fine");
		dateStartChanged(data_start, data_end);
	});
	// $("#id_assign").combobox();
};

$(document).ready(function(){
	if ($("#filter_modeltable_form").length){
		$("#filter_modeltable_form")[0].reset();
	};
	$("select.modeltable_actions").val("delete");
	tableClickHandlers();
});