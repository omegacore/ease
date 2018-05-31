//Copied from M. Shankar's svg_viewer and hacked a bit by A. Wallace

// viewerVars is a struct that contains all the information needed for the viewer;
// To debug, a useful first step is look at viewerVars in the browser console.
var viewerVars = {};// This is one of the integration points with the server.

// This should default to a path relative location that works from the appliance UI.
// To develop/debug, override this to a absolute URL of the server with the data you are going to use for debugging/developing.
viewerVars.serverURL = "https://pswww.slac.stanford.edu/archiveviewer/retrieval";
//Set up an ssh tunnel to pslogin -L 8700:pswww.slac.stanford.edu:80
// viewerVars.serverURL = "http://localhost:8700/archiveviewer/retrieval";//remote work with port forwarding

// User typed a pattern, we search for PV's matching this pattern.

//Note pvTagId is a variable set when the modal is opened. It is defined for each "add PV" button, look at the alert_config.html
function searchForPVsMatchingPattern(pvNamePattern) {
	if (pvNamePattern == null){
		var pattern = $("#pvNamePattern").val();
	}
	else{
		var pattern = pvNamePattern;
	}	
	if(pattern) {
		console.log("Search and add PVs for pattern " + pattern);
		console.log("URL "+viewerVars.serverURL);
		var list = $("#pvNameSearchMatchingList");
		list.empty();
		$("#pvSearchWidget-container box1 info-container nameSearchMatchingError").empty();
		$.getJSON( viewerVars.serverURL + "/bpl/getMatchingPVs?limit=50&pv=" + pattern, function(matchingPVs){
			//Add the pattern that was just searched for if glob
			testglobp = /[\*\?]/;
			if(testglobp.test(pattern)){
				list.append('<li class="list-group-item"><div class="d-flex justify-content-between"><div class"pv">' + pattern + '</div><span class="badge badge-secondary badge-pill">Matches: '+ matchingPVs.length +'</span></div></li>');
			}
			//Adding the results
			if(matchingPVs.length > 0) {
				matchingPVs.forEach(function(matchingPV) { list.append('<li class="list-group-item"><div class="pv">' + matchingPV + '</div></li>') });
				$("#pvNameSearchMatchingList li").click(function() { $(this).toggleClass('list-group-item-info'); });
			} else {
				$("#pvSearchWidget-container box1 info-container nameSearchMatchingError").html("No PV names matched your search. Search using GLOB patterns, for example, QUAD:*:BDES");
			}
			return;
		});
	}
}

function addSelectedSearchPVs(e) {
	var triggerPVList = $("#triggerPVList");
	$("#pvNameSearchMatchingList li.list-group-item-info").each(function() {
		triggerPVList.append('<li class="list-group-item">' + $(this).find("div.pv").text() + '</li>');
		triggerPVList.children().last().click(function() { $(this).toggleClass('list-group-item-info'); });
	});
	$("#pvNameSearchMatchingList li.list-group-item-info").each(function() { $(this).remove() });
}

function addAllSearchPVs() {
	var triggerPVList = $("#triggerPVList");
	$("#pvNameSearchMatchingList li").each(function() { triggerPVList.append('<li class="list-group-item">' + $(this).text() + '</li>')});
	$("#pvNameSearchMatchingList").empty();
}

function removeSelectedTriggerPVs () {
	$("#triggerPVList li.list-group-item-info").each(function() { $(this).remove() });
}

function removeAllTriggerPVs () {
	$("#triggerPVList").empty();
}

function populateTriggerPVs() {
	//Get the values for restoration
	var origVals = $("#"+pvTagId).val()
    if (origVals){
		//Push selected triggers back to the list
		var restoreList = origVals.split(',');
		var triggerPVList = $("#triggerPVList");
		restoreList.forEach(function(element){
			//I am ashamed of this repeated code.
			console.log(element);
			triggerPVList.append('<li class="list-group-item">' + element + '</li>');
			triggerPVList.children().last().click(function() { $(this).toggleClass('list-group-item-info') });
		});
	}
}

function saveTriggerPVs() {
	//Get all the selected triggers
	var triggerPVList = $("#triggerPVList li");
	
	//Remove duplicates
	var seen = {};
	triggerPVList.each(function() {
		var txt = $(this).text();
		if (seen[txt])
			$(this).remove();
		else
			seen[txt] = true;
	});

	//Build the list of triggers
	var list = [];
	triggerPVList.each(function() {
		list.push($(this).text());
	});

	//Push the list to the hidden value field
	$("#"+pvTagId).val("");
	if(triggerPVList.length > 0) { 
		$("#"+pvTagId).val(list);
	 }

	 //Clear the list
	 $("#triggerPVList").empty();
}