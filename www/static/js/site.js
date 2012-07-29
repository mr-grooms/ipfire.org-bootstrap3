$.query = function(name){
	var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
	return results[1] || 0;
}

$("a.download-splash").click(function(event) {
	event.preventDefault();
	linkLocation = this.href;

	window.location = "http://downloads.ipfire.org/download-splash?file="+linkLocation;
});

if (/.*download-splash.*/i.test(window.location.href)) {
	$("p.download-path").ready(function(){
		var valid = false;
		var allowed_prefixes = [
			"http://downloads.ipfire.org/",
		]

		var file_url = $.query("file");

		// Only accept URLs beginning with our known prefix.
		for (i in allowed_prefixes) {
			prefix = allowed_prefixes[i];
			if (file_url.substring(0, prefix.length) == prefix) {
				valid = true;
			}
        }

        if (valid) {
			$("p.download-path").prepend($("<a>", {
				href: encodeURI(file_url),
				text: file_url
			}))
			setTimeout(function() { window.location = file_url }, "2000");
		}
	});
}