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
		var nextRow = this.parentNode.nextElementSibling;
		var add = this.parentNode.querySelector('.upload-widget')
		var remove = this.parentNode.querySelector('.remove-widget')

		reader.onload = function() {
			// XXX check state just in case
			preview.style.backgroundImage = "url(" + this.result + ")";
			add.style.display = 'none';
			remove.style.display = 'block';
			if ( nextRow ) {
				nextRow.style.display = "";
			}
		}
		reader.readAsDataURL(this.files[0]);
	}

	var uprows = document.querySelectorAll(".imagerow");
	for (i = 0; i < uprows.length; i++) {
		var row = uprows[i]
		var input = row.querySelector('input[type="file"]');

		input.addEventListener("change", inputChange);
		input.style.display = "none";

		if ( i > 0 ) {
			row.style.display = "none";
		}

		var remove = row.querySelector('.remove-widget');
		remove.addEventListener("click", function(e) {
			e.preventDefault();
			var input = this.parentNode.querySelector('input[type="file"]');

			input.value = null;
			var preview = this.parentNode.querySelector(".upload-preview");
			preview.style.backgroundImage = 'inherit';
			this.style.display = "";

			var add = this.parentNode.querySelector('.upload-widget');
			add.style.display = 'block';
		})
	}
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}