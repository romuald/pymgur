function HomeLoaded() {
	var i;
	var imgs = document.querySelectorAll('#latest img');

	var loader = document.querySelector('#loader');
	var loaded = 0;

	for (i = 0; i < imgs.length; i++) {
		// Cannot seem to find a DOM event for missing image
		imgs[i].onload = imgs[i].onerror = function() {
			loader.style.width = ((++loaded / imgs.length) * 100) + '%';
		};
	}

	function inputChange(ev) {
		var reader = new FileReader();
		var preview = this.parentNode.querySelector(".upload-preview");
		reader.onload = function() {
			// XXX check state just in case
			preview.style.backgroundImage = "url(" + this.result + ")";
		}
		reader.readAsDataURL(this.files[0]);
	}

	var uprows = document.querySelectorAll(".imagerow");
	for (i = 0; i < uprows.length; i++) {
		var input = uprows[i].querySelector('input[type="file"]');
		input.addEventListener("change", inputChange);
		input.style.display = "none";
	}
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}