/*-------------------------------------------------------------------------------------*/
// Functions related to loading map data 
/*-------------------------------------------------------------------------------------*/

//  Gets featureData depending on whether "trees" or "stones" is type
function loadFeatureData(type) {
    $.ajax({
        url: '/get_features/',
        type: 'post',
        data: {
            'type': type
        },
        dataType: 'json',
        success: function(data) {
            //  Data is a dictionary, with GeoJSON indexed by item name. See views.py
            addFeatureData(map, data, type);
        },
        failure: function(data) {
            alert('There was a failure loading map data.');
        }
    });
}

//  TODO: consider making this a part of the database rather than something created with each load 
//  Populates map with feature data, with featureType differentiating between trees and stones
function addFeatureData(map, data, featureType) { 

    //  Consolidates features for each entry into one FeatureCollection for the layer
    var allFeatures = [];
    for (feature in data) {
        var featureGeojson = JSON.parse(data[feature]['geojson']);
        if (featureGeojson["type"] == "FeatureCollection") {
            //  FeatureCollections cannot be members of a FeatureCollection
            var curFeatures = featureGeojson["features"];
            for (var i = 0; i < curFeatures.length; i++) {
                var curFeatureGeometry = curFeatures[i]['geometry'];
                allFeatures.push(createFeature(feature, data[feature], curFeatureGeometry));
            }
        }
        else {
            allFeatures.push(createFeature(feature, data[feature], featureGeojson));
        }
    }

    //  Adds the information to the map, with the name of the source and feature being the 
    // featureType
    map.addSource(featureType, {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": allFeatures
        }
    });

    map.addLayer({
        "id": featureType,
        "type": "fill",
        "source": featureType,
        "paint": {
            "fill-color": "#888888",
            //  The goal is to make this effectively invisible, but layer must be  set to 
            //  visible in order to be able to query
            "fill-opacity": 0.01
        }
    });

    //  The highlighted layer which displays highlighted geographical areas of the stones/trees
    map.addLayer({
        "id": featureType + "-highlighted",
        "type": "fill",
        "source": featureType,
        "layout": {
            "visibility": "none"
        },
        "paint": {
            "fill-color": "#6e599f",
            "fill-opacity": 0.5
        }
    });

    map.addLayer({
        "id": featureType + "-point",
        "type": "circle",
        "source": featureType,
        "layout": {
            "visibility": "none"
        },
        "paint": {
            "circle-radius": 5
        }
    });
}

//  Creates a feature 
function createFeature(featureName, featureAttributes, geometry) {
    var feature = {};
    var properties = {};

    properties['name'] = featureName;
    if ('start_date' in featureAttributes) {
        properties['start_date'] = featureAttributes['start_date'];
    }
    if ('end_date' in featureAttributes) {
        properties['end_date'] = featureAttributes['end_date'];
    }

    feature['type'] = 'Feature';
    feature['properties'] = properties;
    feature['geometry'] = geometry;

    return feature;
}
