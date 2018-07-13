//  Changes the color from green to blue 
function changeColor() {
    document.body.style.background = "lightblue";
}

//  Hide the map if there's no geojson 
function hideMap() {
    $("#object-container").css("height", "90%");
    $("#edit-container").css("height", "90%");
    $("#map").hide();
}

//  Load geojson from the main and edit objects to map 
function loadGeojson(data) {
    mainObjectGeojson = data["mainObjectGeosjon"];
    editGeojson = data["editGeojson"];
    
    if (mainObjectGeojson) {
        addGeojsonLayers("main", mainObjectGeojson, "#000000");
    }
    addGeojsonLayers("edit", editGeojson, "#ff0000")
}

//  Add a geojson layer to the map with the specific name and color using geojson
function addGeojsonLayers(name, geojson, color) {
    data = createData(JSON.parse(geojson));

    map.addSource(name, {
        "type": "geojson",
        "data": data
    });

    map.addLayer({
        "id": name + "-highlighted",
        "type": "fill",
        "source": name,
        "layout": {
        },
        "paint": {
            "fill-color": color,
            "fill-opacity": 0.5
        },
        "filter": ["==", "$type", "Polygon"]
    });

    map.addLayer({
        "id": name + "-point",
        "type": "circle",
        "source": name,
        "layout": {
        },
        "paint": {
            "circle-radius": 5,
            "circle-color": color
        },
        "filter": ["==", "$type", "Point"]
    });
}

// Create the data section of a source to add to the map (according to Mapbox specifications)
function createData(geojson) {
    var data = {}; 
    if (geojson["type"] == "FeatureCollection") {
        data["type"] = "FeatureCollection"; 
        data["features"] = geojson["features"];
    }
    else {
        data["type"] = "Feature"; 
        data["geometry"] = geojson; 
    }
    return data; 
}