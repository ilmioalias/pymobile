$(document).ready(function(){
	$("div#modeltable_div").on("click", "div.table-container table a.view_details", function(e){
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