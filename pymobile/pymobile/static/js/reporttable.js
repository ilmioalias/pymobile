var search_cur = "";
var sort_cur=""; 

var updateTable = function(html_data){
	var table = $(html_data);
	$(".table-container").html(table);		
};

var getSort = function(j_obj){
	var href = j_obj.attr("href").slice(1);
	if (href){
		var parameters = href.split("&");
		for (var i in parameters){
			p = parameters[i].split("=");
			k = p[0];
			if (k == "sort"){
				return {"sort": p[1]};
			}
		}
	};
};

var sortTable = function (j_obj){
	var data_dict = {};
	var sort = getSort(j_obj);
	var search = search_cur;
	jQuery.extend(data_dict, sort, search);
	if (data_dict){
		console.log(data_dict);
		$.get(".",
			data_dict,
			function(data){
				updateTable(data);
				sort_cur = sort;
			}
		);			
	};
};

var getFilter = function(form){
	var dict = {};
	form.find("input:text").each(function(){
		if ($(this).attr("value")){
			var key = "f" + $(this).attr("name");
			var value = $(this).attr("value");
			var cls = $(this).attr("class");
			if (!(key in dict)){
				dict[key] = new Array();
			};
			if (cls){
				if (cls == "data_start"){
					dict[key].push(">" + value);
				} else if (cls  == "data_end"){
					dict[key].push("<" + value);
				} else if (cls.indexOf("ui-autocomplete-input") == -1){
					dict[key].push(value);
				}				
			} else {
				dict[key].push(value);
			};			
		}	
	});
	form.find("input[type=checkbox]:not(:checked)").each(function() {
		var key = "f" + $(this).attr("name");
		var value = $(this).attr("value");
		if (!(key in dict)){
			dict[key] = new Array();
		};
		dict[key].push("!" + value);		
	});
	form.find("select").each(function() {
		// var value = $(this).children("option:selected").attr("value");
		var key = "f" + $(this).attr("name");
		var opts = $(this).children("option:selected");
		if (opts.length > 0){
			if (!(key in dict)){
				dict[key] = new Array();
			};		
			opts.each(function(){
				var value = $(this).attr("value");
				if (value){
					dict[key].push("=" + value);
				}			
			});
		};		
	});
	return dict;	
};

var filterTable = function(j_obj){
	var form = j_obj.closest("form");
	var data_dict = {};
	var search = getFilter(form);
	var sort = sort_cur;
	jQuery.extend(data_dict, sort, search);
	if (data_dict){
		var url = "./?"
		for (k in data_dict){
			for (v in data_dict[k]){
				url += k + "=" + data_dict[k][v] + "&"
			};
		};
		$.get(url,
			function(data){
				updateTable(data);
				search_cur = search;
			}
		);	
	} else {
		resetFilterTable(j_obj);
	}
};

var resetFilterTable = function(j_obj){
	// if (window.location.search){
	window.location.reload(true);
	// return;
	// };
	// var form = j_obj.closest("form");
	// form[0].reset();
	// form.find(".data_end").attr("disabled", "true");
	// var data_dict = {};
	// jQuery.extend(data_dict, sort_cur);
	// if (data_dict){
		// console.log(data_dict);
		// $.get(".",
			// data_dict,
			// function(data){
				// updateTable(data);
				// search_cur = "";
			// }
		// );			
	// };
};

var getPage = function(j_obj){
	var href = j_obj.attr("href").slice(1);
	if (href){
		var parameters = href.split("&");
		for (var i in parameters){
			p = parameters[i].split("=");
			k = p[0];
			if (k == "pag"){
				return {"pag": p[1]};
			}
		}
	};
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
	var oneDay = 24*60*60*1000;
  	var erliest = new Date(fromDay+oneDay);
  	erliest.setHours(0,0,0,0);
  	data_end.removeAttr("disabled").AnyTime_noPicker().AnyTime_picker({
  		earliest: erliest,
        format: "%e/%m/%Y"
	});		
};

var redirectAfter = function(win, url){
	window.location.replace(url);
	win.close();
};

var tableClickHandlers = function(){
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
	$("#filter_reporttable_search").click(function(e){
		e.preventDefault();
		filterTable($(this));
	});
	$("#filter_reporttable_reset").click(function(e){
		e.preventDefault();
		resetFilterTable($(this));
	});
	$("form#filter_reporttable_form input.data_end").attr("disabled", "true");
	$("form#filter_reporttable_form input.data_start").AnyTime_picker({
		format: "%e/%m/%Y",
		labelTitle: "Seleziona il giorno",
		labelDayOfMonth: "Giorno del mese",
		labelMonth: "Mese",
		labelYear: "Anno"
	});		
	$("form#filter_reporttable_form input.data_start").change(function(e){
		e.preventDefault();
		var data_start = $(this)
		// troviamo la data_end corrispondente alla data_start cambiata
		var field = data_start.attr("id").replace(/da$/, "");
		var data_end = $("#filter_reporttable_form input.data_end").filter("#" + field + "a");
		dateStartChanged(data_start, data_end);
	});
	$("form#filter_reporttable_form select#id_periodo").change(function(e){
		var opt = $(this).find("option:selected");
		if (opt.val() == "manual"){
			var html = $("<table id='manual_period'>");
			html.append('<tr><td>da</td><td><input id="id_periodo_inizio" class="date_start" type="text" name="data"></td></tr>');
			html.append('<tr><td>a</td><td><input id="id_periodo_fine" class="date_end" type="text" name="data"></td></tr>');
			$(this).after(html).show("fast");
			$("form#filter_reporttable_form input#id_periodo_fine").attr("disabled", "true");
			$("form#filter_reporttable_form input#id_periodo_inizio").AnyTime_noPicker().AnyTime_picker({
				format: "%e/%m/%Y",
				labelTitle: "Seleziona il giorno",
				labelDayOfMonth: "Giorno del mese",
				labelMonth: "Mese",
				labelYear: "Anno"
			});		
			$("form#filter_reporttable_form input#id_periodo_inizio").change(function(e){
				e.preventDefault();
				var data_start = $(this)
				var data_end = $("#filter_reporttable_form input#id_periodo_fine");
				dateStartChanged(data_start, data_end);
			});			
		} else {
			var tab = $("form#filter_reporttable_form table#manual_period")
			if (tab.length > 0){	
				tab.hide("fast");
				tab.remove();
			};
		};
	});
};

$(document).ready(function(){
	if ($("#filter_reporttable_form").length){
		$("#filter_reporttable_form")[0].reset();
	};
	$("select.reporttable_actions").val("delete");
	tableClickHandlers();
});
