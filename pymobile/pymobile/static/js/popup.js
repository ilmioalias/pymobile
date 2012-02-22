var popup_shown=false;

function showPopup(href){
	if(popup_shown==false){
		loadPopupContent(href);
	}
}

//disabling popup with jQuery magic!  
function disablePopup(){  
	$(".popup_bg").fadeOut("slow");  
	$(".popup").fadeOut("slow");
	// $("#popup").hide();
	$(".popup_content").html("");
	popup_shown=false;   
}

//loading popup with jQuery magic!  
function loadPopupContent(href){
	$.getJSON(href, function(data){
		$(".popup_content").html(data);
		popup_shown=true;
		centerPopup();
		$(".popup_bg").css({ "opacity": "0.7" });  
		$(".popup_bg").fadeIn("slow");  
		$(".popup").fadeIn("slow");			
	})
}
	// $("#popup_content").load(href, function(){
		// popup_shown=true; 
		// centerPopup();
		// $("#popup_bg").css({ "opacity": "0.7" });  
		// $("#popup_bg").fadeIn("slow");  
		// $("#popup").fadeIn("slow");		 
	// }) 
// } 

//centering popup  
function centerPopup(){  
	//request data for centering  
	var windowWidth = $(window).width();
	var windowHeight = $(window).height();
	var popupHeight = $(".popup").height(); 
	var popupWidth = $(".popup").width();  
	//centering  
	$(".popup").css({ 
		"top": windowHeight/2-200,  
		"left": windowWidth/2-200  
	})      
}  

var popupInit = function(){
	$(".popup").hide();
	
	//chiudiamo il popup cliccando sulla pagina principale
	$(".popup_bg").click(function(){
		if(popup_shown){  
			disablePopup();
		}
	})
	
	//chiudiamo il popup cliccando sulla pagina principale
	$(".popup_close").click(function(){
		if(popup_shown){  
			disablePopup();
		}
	})	
}
