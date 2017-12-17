function HomeLoaded() {
	var xhr = new XMLHttpRequest();

	xhr.addEventListener("load", function(ev) {
		var parent = document.querySelector("#latest");
		var tmpl = document.querySelector("#latest-tmpl");
		tmpl.remove();
		tmpl.removeAttribute("id");

		// May be used to determine when all images are loaded
		var count = this.response.length;
		for (var i=0, l=count; i < l; i++) {
			var div = tmpl.cloneNode(true);

			var img = div.querySelector("img")
			img.src = this.response[i].thumbnail_href;
			/*
			img.onload = function() {
				if ( --count <= 0 ) {
					;
				}
			};*/

			var a = div.querySelector("a");
			a.setAttribute("href", this.response[i].href);
			parent.appendChild(div);
		}
	});

	xhr.responseType = "json";
	xhr.open("GET", "/i/latest");
	xhr.send();
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}