function HomeLoaded() {
	var imgs = document.querySelectorAll('#latest img');

	var loader = document.querySelector('#loader');
	var loaded = 0;

	for (var i = 0; i < imgs.length; i++) {
		// Cannot seem to find a DOM event for missing image
		imgs[i].onload = imgs[i].onerror = function() {
			loader.style.width = ((++loaded / imgs.length) * 100) + '%';
		};
	}
	var upicon =  document.querySelector("#imageup");
	var upinput = document.querySelector("#image-up");

	upinput.addEventListener("change", function() {
		var reader = new FileReader();
		reader.onload = function() {
			upicon.setAttribute("style", "background-image: url(" +  this.result + ")");
		}
		reader.readAsDataURL(this.files[0]);
	})

	
	upicon.addEventListener("click", function(ev) {
		ev.preventDefault();
		upinput.click();
	})
	upinput.parentNode.style.display = "none";
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}