(function() {
"use strict";

var FINPUT = 'input[type="file"]';
var BINPUT = 'input[type="hidden"][name*="bimage"]'

function updateRowPreview(input) {
	var row = input.parentNode;

	var preview = row.querySelector(".add-preview");
	var next_row = row.nextElementSibling;
	var add_widget = row.querySelector('.add-widget')
	var remove_widget = row.querySelector('.remove-widget')
	var finput = row.querySelector(FINPUT);
	var binput = row.querySelector(BINPUT);

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

function removeImage(e) {
	e.preventDefault();

	var row = this.parentNode
	var input = row.querySelector(FINPUT);
	var binput = row.querySelector(BINPUT);
	input.value = null;
	binput.value = "";

	var preview = row.querySelector(".add-preview");
	preview.style.backgroundImage = 'inherit';

	var add = this.parentNode.querySelector('.add-widget');
	add.style.display = 'block';

	this.style.display = "";

	hideEmptyRows();
}

function findEmptyRow() {
	var uprows = document.querySelectorAll(".imagerow");

	for ( var i=0; i < uprows.length; i++ ) {
		var row = uprows[i];
		var finput = row.querySelector(FINPUT);
		var binput = row.querySelector(BINPUT);

		if ( finput.value == "" && binput.value == "" ) {
			return row;
		}
	}
	return null;
}

function hideEmptyRows() {
	var uprows = document.querySelectorAll(".imagerow");
	var empty = 0;
	for ( var i = 0; i < uprows.length; i++ ) {
		var row = uprows[i];
		var shown = ! (row.style.display === 'none');

		if ( ! shown ) {
			continue;
		}

		var finput = row.querySelector(FINPUT);
		var binput = row.querySelector(BINPUT);

		if ( finput.value == "" && binput.value == "" && empty++ > 0 ) {
			// Does not trigger the first time
			row.style.display = 'none';
		}
	}
}

function HomeLoaded() {
	var i;

	/* Setup event for upload rows */
	var uprows = document.querySelectorAll(".imagerow");
	var shown = 0;
	for (i = 0; i < uprows.length; i++) {
		var row = uprows[i]
		var input = row.querySelector(FINPUT);
		var binput = row.querySelector(BINPUT);

		input.addEventListener("change", function() {
			updateRowPreview(this);
		});
		input.style.display = "none";

		if ( input.value != "" ) {
			updateRowPreview(input);
		} else if ( binput.value != "" ) {
			updateRowPreview(binput);
		} else if ( shown++ > 0 ) {
			row.style.display = "none";
		}

		row.querySelector('.remove-widget').addEventListener("click", removeImage);
	}


	/* Setup drag&drop for form */
	var form = document.querySelector('#upload-form');
	form.addEventListener("dragenter", dragEnter, false);
	form.addEventListener("dragover", dragOver, false);
	form.addEventListener("drop", dropImage, false);
	form.addEventListener("dragleave", dragLeave, false);

	/* Setup image progresion loader  */
	var imgs = document.querySelectorAll('#latest img');
	var loader = document.querySelector('#loader');
	var loaded = 0;

	for (i = 0; i < imgs.length; i++) {
		// Cannot seem to find a DOM event for missing image
		imgs[i].onload = imgs[i].onerror = function() {
			loader.style.width = ((++loaded / imgs.length) * 100) + '%';
		};
	}
}

function dragEnter(e) {
	e.stopPropagation();
	e.preventDefault();

	this.classList.add('drag');
}

function dragLeave(e) {
	e.stopPropagation();
	e.preventDefault();

	if ( e.target == this ) {
		this.classList.remove('drag');
		return;
	}
}

function dragOver(e) {
	e.stopPropagation();
	e.preventDefault();
}

function dropImage(e) {
	e.stopPropagation();
	e.preventDefault();

	this.classList.remove('drag');

	for ( var i=0; i < e.dataTransfer.files.length; i++ ) {
		var file = e.dataTransfer.files[i];
		if ( !file.type.startsWith('image/') ) {
			continue;
		}
		var reader = new FileReader();
		reader.onload = function(e) {
			var row = findEmptyRow();
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
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}

})();