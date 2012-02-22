$(document).ready(function(){
	$("div.table-container").on("click", "table#retribuzione td.retribuzione a.visualizza", function(e){
		e.preventDefault();
		var img = $(this).find("img");
		var p = $(this).next("p.info");
		if (p.is(":hidden")){
			var new_img_src = img.attr("src").replace(/destra.png/, "basso.png");
			img.attr("src", new_img_src);
			p.show("fast");			
		} else {
			var new_img_src = img.attr("src").replace(/basso.png/, "destra.png");
			img.attr("src", new_img_src);
			p.hide("fast");			
		};
	});
	$("div.table-container").on("click", "table#retribuzione td.variazione a.visualizza", function(e){
		e.preventDefault();
		var img = $(this).find("img");
		var p = $(this).next("p.info");
		if (p.is(":hidden")){
			var new_img_src = img.attr("src").replace(/destra.png/, "basso.png");
			img.attr("src", new_img_src);
			p.show("fast");			
		} else {
			var new_img_src = img.attr("src").replace(/basso.png/, "destra.png");
			img.attr("src", new_img_src);
			p.hide("fast");			
		};
	});	
});