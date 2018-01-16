(function() {
	"use strict";

	var i, l, 	match;
	var now = (new Date()).getTime();
	var to_remove = [];
	for ( i = 0, l = localStorage.length; i < l; i++ ) {
		var key = localStorage.key(i);
		// .<uid>
		if ( key.indexOf(".") == 0 && (match = /e=(\d+)/.exec(localStorage[key])) ) {
			var expire = parseInt(match[1], 10);
			if ( expire <  now ) {
				console.log('key ' + key + ' expired, remove from local storage');
				to_remove.push(key);
			}
		}
	}
	to_remove.map(function(x){localStorage.removeItem(x)});

	match = /\/(.+?)$/.exec(window.location.pathname);
	var uid = match && match[1];
	var secret_data = localStorage.getItem("." + uid);
	var image_secret = null;
	if ( secret_data && (match = /s=(\S+)/.exec(secret_data)) ) {
		image_secret = match[1];
	}

	var new_uids = localStorage.getItem("new-uids");
	// In the future will allow to display multiple new when posting a set
	if ( image_secret && new_uids ) {
		var secret_block = document.querySelector('#secret-info');
		var secret_b = secret_block.querySelector("b");

		secret_b.innerHTML = image_secret
		secret_block.style.display = "block";
		localStorage.removeItem("new-uids");
	}

	if ( image_secret ) {
		var input = document.querySelector('form input[name="secret"]');
		input.value = image_secret;
	}

	var action_switch = document.querySelector('#action-switch');
	var actions_div = document.querySelector('#actions');
	action_switch.addEventListener('click', function(e) {
		e.preventDefault();
		actions_div.classList.toggle('hidden');

		if ( !actions_div.classList.contains('hidden') ) {
			window.scrollTo(0, actions_div.offsetTop);
		}
	})
	
	actions_div.classList.add('hidden');

	/* Setup image progresion loader  */
	var imgs = document.querySelectorAll('#thumbnails img');
	var loader = document.querySelector('#loader');
	var loaded = 0;

	for (i = 0; i < imgs.length; i++) {
		// Cannot seem to find a DOM event for missing image
		imgs[i].onload = imgs[i].onerror = function() {
			loader.style.width = ((++loaded / imgs.length) * 100) + '%';
		};
	}
})()