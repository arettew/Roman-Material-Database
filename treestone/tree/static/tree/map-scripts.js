/*-------------------------------------------------------------------------------------*/
// Functions related to the display of page elements 
/*-------------------------------------------------------------------------------------*/

//  Hides "popups" initially 
$(document).ready(function() {
    $(".popup").hide();
    $(".help-text").hide();
});

//  The function that holds the html that creates the close button
function getCloseHtml() {
    return "<span class='close-container'><div class='close' onclick='makeClose()'>&times</div></span>";
}

//  Makes close button function via jquery 
function makeClose() {
    $(".close-container").click(function() {
        if ($(this).parent().attr('id') == "info-box") {
            map.setLayoutProperty('stones-highlighted', 'visibility', 'none');
            map.setLayoutProperty('trees-highlighted', 'visibility', 'none');
        }
        $(this).parent().hide();
    })
}   

//  Control help text
$(document).ready(function() {
    $("#filter-help").mouseover(function() {
        $("#filter-help-text").show();
    });
    $("#filter-help").mouseout(function() {
        $("#filter-help-text").hide(); 
    });

    $("#search-help").mouseover(function() {
        $("#search-help-text").show();
    });
    $("#search-help").mouseout(function() {
        $("#search-help-text").hide(); 
    });
});

//  Control collapsable elements 
$(document).ready(function () {
    $("#type-select-collapse").click(function () {
        $("#type-select").toggle(); 
        if($("#type-select").is(':visible')) {
            $("#type-select-collapse").text('-');
            $("#type-select-collapse").css("background-color", "");
        }
        else {
            $("#type-select-collapse").text('+');
            $("#type-select-collapse").css("background-color", "rgba(255, 255, 255, 0.8)");
        }
    });
});

//  Shows an error message with the message contained in errorMessage
function showErrorMessage(errorMessage) {
    const messageDuration = 2500;
    $("#error-message").text(errorMessage);
    $("#error-message").fadeIn();
    setTimeout(function() {
        $("#error-message").fadeOut();}, messageDuration);
}

/*-------------------------------------------------------------------------------------*/
// Functions related to input 
/*-------------------------------------------------------------------------------------*/

//  Shows value of slider
$(document).ready(function() {
    $("#slider").on('input', function (e) {
        var value = $("#slider").val()
        $("#slider-value").text(value + "km");
    });
});

//  Clears date filters
$(document).ready(function() {
    $("#clear-dates").click(function() {
        $(".date-filter-text").val(''); 
        $(".date-filter-radio").prop('checked', false);
    });
});

//  Validates the dates to make sure that any selection has both date/era 
//  and that the start is before the end
function validateDateFilter() {
    var startEra = getEra("start");
    var endEra = getEra("end");
    var startDate = getDate("start");
    var endDate = getDate("end");

    if ((!startEra && startDate) || (startEra && !startDate)) {
        return false;
    }
    if ((!endEra && endDate) || (endEra && !endDate)) {
        return false; 
    }
    if ((startEra && startDate) && !(endEra && endDate)) {
        return true;
    }
    if (!(startEra && startDate) && (endEra && endDate)) {
        return true;
    }
    return (compareDates(startDate, startEra, endDate, endEra) <= 0);
}

//  Get start or end era based on argument ('start' or 'end')
function getEra(time) {
    return $("input[name='" + time + "-era']:checked").val();
}

//  Get start or end year based on argument ('start' or 'end') 
function getDate(time) {
    return $("#" + time + "-date").val();
}

//  Is there a start/end filter (based on time argument) specified by the user?
function haveDateConstraint(time) {
    return getDate(time) && getEra(time);
}

//  Compares two dates. Returns 0 if the same, a negative if the first date is earlier 
//  than the second, and a positive if the first is later than the second 
function compareDates(firstYear, firstEra, secondYear, secondEra) {
    if (firstEra == "BCE" && secondEra == "CE") {
        return -1;
    }
    if (firstEra == "CE" && secondEra == "BCE") {
        return 1;
    }

    if (firstEra == "BCE") {
        return (secondYear - firstYear);
    }
    else {
        return (firstYear - secondYear);
    }
}

//  Clears the date filter 
function clearDates() {
    alert("HI");
}

/*-------------------------------------------------------------------------------------*/
// Functions related to querying
/*-------------------------------------------------------------------------------------*/

//  Search for results centered on point 
function search(e, supressZoomError) {
    var searchGeometry = getSearchGeometry(e, $("#slider").val(), supressZoomError);

    //  Construct and show results 
    var searchResults = getCloseHtml();
    if ($('#check-trees').is(':checked')) {
        searchResults += getFormattedSearchResults(searchGeometry, 'trees');
    }
    if ($("#check-stones").is(':checked')) {
        searchResults += getFormattedSearchResults(searchGeometry, 'stones');
    }

    $("#results-box").html(searchResults);
    $("#results-box").show();
    $("li").css('cursor', 'pointer');

}

//  Creates the geometry used to query, either a bbox with the center of the box being the point of the 
//  click, point e, and searchRadius being the distance from the center to each of the sides or the point 
//  of click, if the radius is 0
function getSearchGeometry(e, searchRadius, suppressZoomError) {
    if (searchRadius == 0) {
        return e.point;
    }
    var center = turf.point([e.lngLat.lng, e.lngLat.lat]);
    var circle = turf.circle(center, searchRadius, {'units': 'kilometers'});
    var bboxLngLat = turf.bbox(circle);

    //  bbox format is [swpointlng, swpointlat, nepointlng, nepointlat] as 
    //  according to GeoJSON format 
    var nePointPixels = map.project([bboxLngLat[2], bboxLngLat[3]]);
    var swPointPixels = map.project([bboxLngLat[0], bboxLngLat[1]]);

    if (!suppressZoomError) {
        validateZoom(e, searchRadius);
    }

    return [swPointPixels, nePointPixels];
}

//  Make sure has an appropriate zoom level based on their search radius. Multipliers can be changed 
function validateZoom(e, searchRadius) {
    var bounds = map.getBounds(); 
    var sw = bounds.getSouthWest(); 
    var ne = bounds.getNorthEast(); 
    var swPoint = turf.point([sw.lng, sw.lat]);
    var nePoint = turf.point([ne.lng, ne.lat]);
    var bboxDiagonal = turf.distance(swPoint, nePoint);

    //  Mapbox's functions are less accurate here, returning a smaller radius 
    if (Math.abs(e.lngLat.lat) > 70) {
        showErrorMessage("There isn't any data in this section of the map.");
        return;
    }

    if (bboxDiagonal * 2 < searchRadius) {
        showErrorMessage("Your search radius is larger than your current view. Try zooming out!");
    }

    const MIN_SAFE_DIAG = 3000;
    if (bboxDiagonal < MIN_SAFE_DIAG) {
        return 
    }
    if (searchRadius * 4 < bboxDiagonal) {
        showErrorMessage("Your search radius is smaller than your current view. Try zooming in!");
    }
}

//  Queries the layer specified in type using the given searchGeometry, either a point or
//  a bbox. Returns a string representing results 
function getFormattedSearchResults(searchGeometry, type) {
    var features;
    if (type == 'stones') {
        //  Only stones can be filtered by age 
        var queryFilter = constructFilter();
        features = map.queryRenderedFeatures(searchGeometry, {layers: [type], filter: queryFilter});
    }
    else {
        features = map.queryRenderedFeatures(searchGeometry, {layers: [type]});
    }

    //  Creates string representing results 
    var searchResults = "";
    searchResults += "<b>" + type.charAt(0).toUpperCase() + type.slice(1) + ":</b></br>";
    for (var i = 0; i < features.length; i++) {
        var feature = features[i];
        var name = feature.properties.name;
        //  Because of how MapBox treats features, some features may be 
        //  be split up and returned multiple times in the query 
        if (!searchResults.includes(name)) {
            searchResults += "<li data-type=" + type + " onclick=displayInfo(this)>" + name + "</li>";
        }
    }
    if (features.length == 0) {
        searchResults += "No results found</br>"
    }

    return searchResults;
}

//  Constructs a filter for queryRenderedFeatures based on values 
function constructFilter() {
    if (!validateDateFilter()) {
        //  If dates are not valid, return a filter that includes all items 
        showErrorMessage("Your dates are invalid. They will not be applied as a filter.");
        return ["has", "name"];
    }

    var filter = ["all"];
    if (haveDateConstraint('start')) {
        filter.push(constructDateFilter('start'));
    }
    if (haveDateConstraint('end')) {
        filter.push(constructDateFilter('end'));
    }

    return filter;
}

//  Returns a filter piece based on the argument ('start' or 'end')
function constructDateFilter(time) {
    var year = getDate(time);
    var era = getEra(time)
    var multiplier = (era == "BCE") ? -1 : 1;
    var operator = (time == 'start') ? ">=" : "<=";
    return [operator, time + "_date", parseInt(year) * multiplier];
}

/*-------------------------------------------------------------------------------------*/
// Functions related to showing information on search results 
/*-------------------------------------------------------------------------------------*/

//  Displays information about a selected result in results-box 
function displayInfo(item) {
    var itemName = item.textContent;
    var type = item.getAttribute('data-type');
    $.ajax({
        url: '/result_info/',
        type: 'post',
        dataType: 'json',
        data: {
            'itemName': itemName,
            'itemType': type
        },
        success: function(data) {
            //  Adds close button 
            var info = getCloseHtml();

            //  Adds info to window 
            info += "<h3>" + itemName + "</h3>";
            var attributes = data["attributes"]
            for (attribute in attributes) {
                if (attributes[attribute] == null) {
                    // Prefer an empty string to a null value 
                    attributes[attribute] = "";
                }
                info += "<b>" + attribute + "</b></br>";
                info += "<p>" + attributes[attribute] + "</p> ";
            }
            var downloadLink = "/geojson/" + type + "/" + data["pk"]
            info += "<br><div class='left'><a href='" + downloadLink + "'>Download GeoJSON</a></div>"
            if (data["user"]) {
                var editLink = "/" + type + "/edit/" + data["pk"] + "/"
                info += "<div class='right'><a href='" + editLink + "'>Edit</a></div>"
            }
            $("#info-box").html(info);
            $("#info-box").show();

            //  Move links to correct locations 
            $('.right').css('text-align', 'right')
            $('.right').css('float', 'right')
            $('.left').css('text-align', 'left')
            $('.left').css('float', 'left')

            showFeatureGeography(type, itemName);

            //  Shows images if they exist 
            imageUrls = data["image_urls"];
            if (imageUrls != undefined && imageUrls.length > 0) {
                showImages(imageUrls);
            }
            else {
                $("#picture-box").hide();
            }
        },
        failure: function(data) {
            alert('There was a failure getting result data.');
        }
    });
}

//  Filters the map so that the feature to be shown is highlighted
function showFeatureGeography(type, itemName) {
    map.setFilter(type + "-highlighted", null);
    map.setFilter(type + "-point", null);
    map.setFilter(type + "-point", ['all', ['==', '$type', 'Point'], ['==', 'name', itemName]]);
    map.setFilter(type + "-highlighted", ['all', ['==', '$type', 'Polygon'], ['==', 'name', itemName]]);
    map.setLayoutProperty(type + "-highlighted", 'visibility', 'visible');
    map.setLayoutProperty(type + "-point", 'visibility', 'visible');
}

//  Shows the images associated with a search result. 
function showImages(image_urls) {
    //  Set up picture-box to have a close button and prepare it to change the HTML 
    //  within tab div
    $("#picture-box").html(getCloseHtml() + "<div class='tab'></div>");

    htmlString = "";
    //  Create the tab buttons 
    for (var i = 0; i < image_urls.length; i++) {
        htmlString += "<button onclick='openImage(this.textContent)'>Img" + (i+1) + "</button>"
    }
    
    //  Create the tab content, loading the pictures  
    for (var i = 0; i < image_urls.length; i++) {
        htmlString += "<div id=Img" + (i+1) + " class='tabcontent'>";

        var url = image_urls[i];
        htmlString += "<a href='" + url + "' download> <img src=" + url + "></a>";

        htmlString += "</br><p>Click image to download!</p>"
        htmlString += "</div>";
    }
    $(".tab").html(htmlString);
    $("#picture-box").show();

    //  Hide all but first tab content 
    $(".tabcontent").hide(); 
    $("#Img1").show();
}

//  Opens a specific image 
function openImage(imageId) {
    $('.tabcontent').hide();
    $('#' + imageId).show();
}
