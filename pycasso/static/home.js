(function() {
"use strict";


function updateRowPreview(input) {
	var row = input.parentNode;

	var preview = row.querySelector(".add-preview");
	var next_row = row.nextElementSibling;
	var add_widget = row.querySelector('.add-widget')
	var remove_widget = row.querySelector('.remove-widget')
	var finput = row.querySelector('input[type="file"]');
	var binput = row.querySelector('input[name*="bimage"]');
	
	add_widget.style.display = 'none';
	remove_widget.style.display = 'block';

	if ( next_row ) {
		next_row.style.display = "";
	}

	
	if ( input === finput ) {
		binput.value = "";
		var reader = new FileReader();
		reader.onload = function() {
			preview.style.backgroundImage = "url(" + this.result + ")";
		}
		reader.readAsDataURL(input.files[0]);
	} else if ( input === binput ) {
		finput.value = null;
		preview.style.backgroundImage = "url(" + input.value + ")";
	} else {
		console.error("Unknown input", input);
	}
}

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


	var uprows = document.querySelectorAll(".imagerow");
	for (i = 0; i < uprows.length; i++) {
		var row = uprows[i]
		var input = row.querySelector('input[type="file"]');

		input.addEventListener("change", function() {
			updateRowPreview(this);
		});
		input.style.display = "none";

		if ( i > 0 ) {
			row.style.display = "none";
		}

		var remove = row.querySelector('.remove-widget');
		remove.addEventListener("click", function(e) {
			e.preventDefault();
			var input = this.parentNode.querySelector('input[type="file"]');
			input.value = null;
			var binput = this.parentNode.querySelector('input[name*="bimage"]');
			binput.value = "";

			var preview = this.parentNode.querySelector(".add-preview");
			preview.style.backgroundImage = 'inherit';

			var add = this.parentNode.querySelector('.add-widget');
			add.style.display = 'block';

			this.style.display = "";
		});
	}

	var form = document.querySelector('#upload-form');
	form.addEventListener("dragenter", dragenter, false);
	form.addEventListener("dragover", dragover, false);
	form.addEventListener("drop", drop, false);
	form.addEventListener("dragleave", dragleave, false);
}

function dragenter(e) {
	e.stopPropagation();
	e.preventDefault();

 	this.classList.add('drag');
}

function dragover(e) {
	e.stopPropagation();
	e.preventDefault();
}

function findEmptyRow() {
	var uprows = document.querySelectorAll(".imagerow");

	for ( var i=0, l=uprows.length; i<l; i++ ) {
		var row = uprows[i];
		var input = row.querySelector('input[type="file"]');
		var binput = row.querySelector('input[name*="bimage"]');

		if ( input.value == "" && binput.value == "" ) {
			return row;
		}
	}
	return null;
}

function drop(e) {
	console.log("meh??");
	e.stopPropagation();
	e.preventDefault();

	this.classList.remove('drag');

	var file = e.dataTransfer.files[0];
	if ( ! file.type.startsWith('image/') ) {
		return;
	}

    var reader = new FileReader();
    var row = findEmptyRow();
    reader.onload = function(e) {
    	if ( row === null ) {
    		return;
    	}

    	var input = row.querySelector('input[type*="file"]');
		var binput = row.querySelector('input[name*="bimage"]');

		input.value = null;
		binput.value = e.target.result
		updateRowPreview(binput);
    };
    reader.readAsDataURL(file);
}

function dragleave(e) {
	e.stopPropagation();
	e.preventDefault();
	
	if ( e.target == this ) {
		this.classList.remove('drag');
		return;	
	}
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}

})();