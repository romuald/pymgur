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
		var preview = this.parentNode.querySelector(".add-preview");
		var nextRow = this.parentNode.nextElementSibling;
		var add = this.parentNode.querySelector('.add-widget')
		var remove = this.parentNode.querySelector('.remove-widget')
		var binput = this.parentNode.querySelector(".add-preview");
		binput.value = "";

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
			var binput = this.parentNode.querySelector('input[name*="bimage"]');
			binput.value = "";

			var preview = this.parentNode.querySelector(".add-preview");
			preview.style.backgroundImage = 'inherit';

			var add = this.parentNode.querySelector('.add-widget');
			add.style.display = 'block';

			this.style.display = "";
		});
	/*
		row.addEventListener("dragenter", dragenter);
		row.addEventListener("dragover", dragover);
		row.addEventListener("drop", drop);
		row.addEventListener("dragleave", dragleave);
		*/
	}
	//return;

	var form = document.querySelector('#upload-form');
	form.addEventListener("dragenter", dragenter, false);
	form.addEventListener("dragover", dragover, false);
	form.addEventListener("drop", drop, false);
	form.addEventListener("dragleave", dragleave, false);

}

function isDescendant(parent, child) {
	if ( child == null ) {
		return false;
	}
     var node = child.parentNode;
     while (node != null) {
         if (node == parent) {
             return true;
         }
         node = node.parentNode;
     }
     return false;
}

function dragenter(e) {
	e.stopPropagation();
	e.preventDefault();
 	//console.log("enter", e, this);
 	this.classList.add('drag');
}

function dragover(e) {
	e.stopPropagation();
	e.preventDefault();
	//console.log("over", e, this);
}
function drop(e) {
	e.stopPropagation();
	e.preventDefault();

	this.classList.remove('drag');

	var file = e.dataTransfer.files[0];
	if ( ! file.type.startsWith('image/') ) {
		return;
	}
    var reader = new FileReader();
    reader.onload = function(e) {
    	
    	var uprows = document.querySelectorAll(".imagerow");

    	var found = null;
    	for ( var j=0, l=uprows.length; j<l; j++ ) {
    		var row = uprows[j];
    		var input = row.querySelector('input[name*="image"]');
    		var binput = row.querySelector('input[name*="bimage"]');

    		if ( input.value == "" && binput.value == "" ) {
    			console.log('Found: ' + j)

    			input.value = null;
				binput.value = e.target.result.substring(e.target.result.indexOf(',') + 1);

		    	var preview = row.querySelector(".add-preview");
				var nextRow = uprows[j+1];
				var add = row.querySelector('.add-widget')
				var remove = row.querySelector('.remove-widget')

				preview.style.backgroundImage = "url(" + e.target.result + ")";
				add.style.display = 'none';
				remove.style.display = 'block';
				if ( nextRow ) {
					nextRow.style.display = "";
				}
    			break;
    		} else {
    			console.log('Discard ' + j + 'v=' + input.value + ", bv=" + binput.value.substring(0, 20))
    		}
    	}
    	if ( found === null ) { return }

		
    	

    };
    reader.readAsDataURL(file);
	console.log(file, file.type);

}

function dragleave(e) {
	e.stopPropagation();
	e.preventDefault();
	
	if ( e.target == this ) { //&& !isDescendant(this, e.relatedTarget) ) {
		this.classList.remove('drag');
		console.log("leaving", e, this);
		return;	
	}
	
}

if ( document.readyState === "loading" ) {
	document.addEventListener("DOMContentLoaded", HomeLoaded);
} else {
	HomeLoaded();
}