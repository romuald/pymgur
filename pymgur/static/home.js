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
			preview.style.display = "block";
		}
		reader.readAsDataURL(input.files[0]);
	} else if ( input === binput ) {
		finput.value = null;
		preview.style.backgroundImage = "url(" + input.value + ")";
		preview.style.display = "block";
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
	preview.style.backgroundImage = 'none';
	preview.style.display = "none";

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

function formSubmit(ev) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", this.action);
	xhr.setRequestHeader("X-From-XHR", "yes");

	var submit = document.querySelector('input[type="submit"]');

	xhr.addEventListener("load", function(e) {
		var response;
		try {
			response = JSON.parse(this.response);
		} catch (e) {}

		submit.disabled = false;
		submit.value = submit.getAttribute('alt-std');

		var errbox = document.querySelector("#error-messages");

		if ( this.status == 201 ) {
			var max_expire = (new Date(
				// expire local secret in 400 days if no expiration
				(new Date()).getTime() + 3456e7
				)).getTime();
			var new_uids = response.map(function(item) {
				var expire = max_expire;
				if ( item.date_expire ) {
					expire = Date.parse(item.date_expire)
				}
				var stored = "e=" + expire + " s=" + item.secret;
				localStorage.setItem("." + item.uid, stored);

				return item.uid;
			});


			localStorage.setItem("new-uids", new_uids.join(","));
			window.location = response[0].href;
		} else if ( this.status == 400 ) {
			submit.disabled = false;
			submit.value = submit.getAttribute('alt-std');
			errbox.innerHTML = "<h3>" + response.error + "</h3>";
		} else if ( this.status == 500 ) {
			errbox.innerHTML = this.response
		} else {
			// XXX handle stuff
			console.error('Unknown response: ' + this.status);
			errbox.innerHTML = this.response;
		}
	});

	xhr.upload.addEventListener("progress", function(e) {
		if (!e.lengthComputable) {
			return;
		}
		var percent = e.loaded / e.total;

		if 	( percent == 1 ) {
			// Unfortunatelly does not trigger with Firefox
			submit.style.backgroundImage = 'none';
			submit.value = submit.getAttribute('alt-waiting');
			return;
		}

		// Set the background image for submit button
		if ( ! /^url/.test(submit.style.backgroundImage) ) {
			var canvas = document.createElement('canvas');
			canvas.setAttribute('width', 10);
			canvas.setAttribute('height', 100);

			var ctx = canvas.getContext('2d');
			ctx.fillStyle = window.getComputedStyle(submit).borderTopColor;
			ctx.fillRect(0, 0, 10, 100);

			submit.style.backgroundImage = 'url(' + canvas.toDataURL() + ')';
		}

		submit.style.backgroundPositionX = (percent * 100) + '%';
	});

	submit.disabled = true;
	submit.value = submit.getAttribute('alt-uploading');

	var fd = new FormData(this);
	for ( var pair of fd.entries() ) {
		// Convert base64 data to binary data to reduce transfer size
		var key = pair[0], value = pair[1];

		if ( /bimage/.test(key) && value.length > 0 ) {
			try {
				var blob = dataURLToBlob(value);
				fd.set(key, blob);
			} catch (e) {}
		}
	}

	xhr.send(fd);
	ev.preventDefault();
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

	form.addEventListener('submit', formSubmit);

	document.addEventListener("paste", pasteImage, false)

	/* Setup image progresion loader  */
	var imgs = document.querySelectorAll('#thumbnails img');
	var loader = document.querySelector('#loader');
	var loaded = 0;

	for (i = 0; i < imgs.length; i++) {
		// Cannot seem to find a DOM event for missing image
		imgs[i].onload = imgs[i].onerror = function() {
			loader.style.width = ((++loaded / imgs.length) * 100) + '%';
		};
		if ( imgs[i].complete ) {
			loaded++;
		}
	}

	if ( loaded ) {
		loader.style.width = ((++loaded / imgs.length) * 100) + '%';
	}
}

function imageFromReader(e) {
	// Creates a new image from a FileReader onload event
	var row = findEmptyRow();
	if ( row === null ) {
		return;
	}

	var input = row.querySelector('input[type*="file"]');
	var binput = row.querySelector('input[name*="bimage"]');

	input.value = null;
	binput.value = e.target.result;

	updateRowPreview(binput);
}

function dataURLToBlob(data) {
	var byteString = atob(data.split(',')[1]);
	var mimeString = data.split(',')[0].split(':')[1].split(';')[0]

	var ab = new ArrayBuffer(byteString.length);
	var ia = new Uint8Array(ab);

	for (var i = 0; i < byteString.length; i++) {
		ia[i] = byteString.charCodeAt(i);
	}
	return new Blob([ab], {type: mimeString});
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
	e.dataTransfer.dropEffect = "copy";

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
		reader.onload = imageFromReader;
		reader.readAsDataURL(file);
	}
}

function pasteImage(e) {
	// Keep event bubbling
	var items = (e.clipboardData || e.originalEvent.clipboardData).items;

	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		if ( item.kind !== "file" || !item.type.startsWith('image/') ) {
			continue;
		}

		var blob = item.getAsFile();
		var reader = new FileReader();
		reader.onload = imageFromReader;
		reader.readAsDataURL(blob);
	}
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}

})();