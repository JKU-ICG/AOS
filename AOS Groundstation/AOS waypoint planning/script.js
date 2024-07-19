

var ps3 = {
};

(function(ns) {
    ns.d = {}; // data
    ns.v = {}; // variables 
    ns.m = {}; // methods
    ns.c = {}; // constants
    ns.map = {}; // Leaflet elements

// Creating a Layer object
ns.map.osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxNativeZoom: 19, maxZoom:25});      
ns.map.esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {maxNativeZoom: 19, maxZoom:25,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

// Creating map options
ns.map.mapOptions = {
    center: [48.336922, 14.320400],
    zoom: 18,
    wheelPxPerZoomLevel: 120,
    layers: [ns.map.osm]
};

// Creating a map object
ns.map.map = new L.map('map', ns.map.mapOptions);

ns.d.baseMaps = {
    "OSM": ns.map.osm,
    "ESRI": ns.map.esri
};
ns.d.overlayMaps = {};

ns.map.layerControl = L.control.layers(ns.d.baseMaps, ns.d.overlayMaps, {position: 'bottomleft'}).addTo(ns.map.map);
ns.d.selectedMarker = null;

ns.d.wayPointsDrones = [];
// let wayPointsDrones = [
    //     {id : 1, marker: MARKEROBJECT, waypointdata : {}, wayline: null, timestamp: TIMESTAMP},
    //     {id : 1, marker: MARKEROBJECT, waypointdata : [], wayline: null, timestmap: TIMESTAMP},
    // ]
    
    
ns.d.droneAnimation = []
    // [{id : 1, flowpoints: [], tooltip: div},
    // {id : 2, flowpoints: [], tooltip: div}]
    
ns.d.wayLinesDrones = [];  
    // [{id : 1, wayline : POLYGONLINEOBJECT},{id : 2, wayline : POLYGONLINEOBJECT}]

// initialize wayLines with null value;
ns.m.initWayLinesDrones = function() {
    for (let i=1; i < 11; i++) {
        ns.d.wayLinesDrones.push({id: i, wayline : null})
    };
};

ns.m.initWayLinesDrones();

ns.v.addMarkerToMap = true;
ns.v.showAnimation = false; // show animation of drones - toggle state


ns.c.DRONECOLOURCODES = [
    {id: 1,  colour : '#B30F0F'},
    {id: 2,  colour : '#013A65'},
    {id: 3,  colour: '#A460DC'},
    {id: 4,  colour: '#B07ACB'},
    {id: 5,  colour: '#EB00A0'},
    {id: 6,  colour: '#000000'},
    {id: 7,  colour: '#55647E'},
    {id: 8,  colour: '#784491'},
    {id: 9,  colour: '#2476FF'},
    {id: 10, colour:  '#31571B'}
];

ns.c.ICONSIZE = 32;
ns.c.DRONEMARKERSIZE = 30;

// default values for creating flight object (if no values are given)
ns.c.DEFAULTHOLDTIME = 0;
ns.c.defaultAltitude = 20;
ns.c.defaultSpeed = 0.5;
ns.c.defaultHeading = 0;

// default values for position of drone-tooltip
ns.c.TOOLTIP_OFFSET_X = 10;
ns.c.TOOLTIP_OFFSET_Y = 10;

// API-Endpoint the server is listening on
ns.c.apiEndpoint = "http://localhost:8000/dronedata";

ns.map.map.on('click', function(e) {
    var droneId = document.getElementById('droneSelect').value;
    if (!droneId) {
        alert('No drone selected. Select a drone to add waypoints.');
    } else {

        let pointIndex = ns.d.wayPointsDrones.filter(w => w.id === droneId).length;

        var waypointIcon = ns.m.createWaypointIcon(droneId + '.' + pointIndex, ns.m.getDroneColourCode(droneId));

        var marker = L.marker(e.latlng, {draggable: true, icon:waypointIcon}).addTo(ns.map.map);
        
        var waypoint = {}
        waypoint.id = droneId;
        waypoint.marker = marker;
        waypoint.wayline = null;

        // set defaults for altitude, speed and hold on position
        var altitudeInput = document.getElementById('altitudeInput').value;
        if (altitudeInput === "") {
            altitudeInput = ns.c.defaultAltitude;
        };

        var speedInput = document.getElementById('speedInput').value;
        if (speedInput === "") {
            speedInput = ns.c.defaultSpeed;
        };

        var holdInput = document.getElementById('holdInput').value;
        if (holdInput === "") {
            holdInput = ns.c.DEFAULTHOLDTIME;
        };


        waypoint.data = {
            lat: marker.lat, 
            lng: marker.lng,
            altitude: altitudeInput,
            speed: speedInput,
            camera: document.getElementById('cameraSelect').value,
            holdInput: holdInput,
            gimbalPitch: document.getElementById('gimbalPitchInput').value,
            gimbalYaw: document.getElementById('gimbalYawInput').value,
            heading: document.getElementById('headingInput').value,
        }
        waypoint.timestamp = Date.now();

        ns.d.wayPointsDrones.push(waypoint)

        ns.d.selectedMarker = waypoint.marker;
        ns.m.updateWaypointInformation(ns.d.selectedMarker); // update waypoint information in sidebar

        ns.m.updateSelectedMarkerDiv();

        if (ns.m.isShowWaylines()) {
            ns.m.deleteWaylines();
            ns.m.calculateWaylines();
        };

        // update DroneAnimation
        if (ns.m.isShowAnimation()) {
            ns.m.updateDroneAnimation();
        };

        ns.m.waypointMarkerMethods(waypoint);
    }
});


// methods

ns.m.waypointMarkerMethods = (waypoint) => {
    waypoint.marker.on('click', function() {
        ns.d.selectedMarker = waypoint.marker;
        // waypoint.marker.bindPopup(ns.m.getPopupContentString(waypoint)); // popup for marker
        ns.m.updateSelectedMarkerDiv();
        ns.m.updateWaypointInformation(ns.d.selectedMarker);
    });

    waypoint.marker.on('contextmenu', function() {
        ns.d.selectedMarker = waypoint.marker;
        ns.m.deleteMarker();
        if (ns.m.isShowAnimation()) {
            ns.m.updateDroneAnimation();
        }
    })

    waypoint.marker.on('dragend', function(event){
        ns.d.selectedMarker = waypoint.marker;
        ns.m.updateSelectedMarkerDiv();
        if (ns.m.isShowWaylines()) {
            ns.m.deleteWaylines();
            ns.m.calculateWaylines();
        };                
        ns.m.updateWaypointInformation(waypoint.marker);

        // update DroneAnimation
        if (ns.m.isShowAnimation()) {
            ns.m.updateDroneAnimation();
        };
    });
};

ns.m.updateSelectedMarkerDiv = () => {
    if (ns.d.selectedMarker != null) {
        var waypoint = ns.d.wayPointsDrones.find(w => w.marker === ns.d.selectedMarker);
        var waypointsOfDrone = ns.d.wayPointsDrones.filter(w => w.id === waypoint.id);
        var pointIndex = waypointsOfDrone.indexOf(waypoint);
        selectedMarkerDiv.innerHTML = `Drone-ID: ${waypoint.id}, Waypoint: ${pointIndex}`;
        if (ns.m.isShowAnimation()) {
            ns.m.updateDroneAnimation();
        };
    } else {
        selectedMarkerDiv.innerHTML = 'No waypoint selected.';
    }
}

ns.m.calculateWaylines = () => {
    let uniqueIds = [];
    var coordinates = [];
    

    ns.d.wayPointsDrones.forEach(element => {
        if (!uniqueIds.includes(element.id)) {
            uniqueIds.push(element.id);
        }
    });

    uniqueIds.forEach(id => {
        var colour = ns.m.getDroneColourCode(id);
        var waypointElem = ns.d.wayPointsDrones.filter(w => w.id === id);
        let latlngs = waypointElem.map(x => [x.marker.getLatLng().lat, x.marker.getLatLng().lng]);
        let polyline = L.polyline(latlngs, {color: colour}).addTo(ns.map.map);

        var waylineElement = ns.d.wayLinesDrones.find(w => w.id === parseInt(id));
        waylineElement.wayline = polyline;
    });
};

ns.m.deleteWaylines = () => {
    ns.d.wayLinesDrones.forEach(elem => {
        if (elem.wayline != null) {
            ns.map.map.removeLayer(elem.wayline);
            elem.wayline = null;
        }
    });
}

ns.m.getDroneColourCode = (id) => {
    return ns.c.DRONECOLOURCODES.find(c => c.id === parseInt(id)).colour
}

ns.m.isShowWaylines = () => {
    return document.getElementById('showWaylines').value === 'show';
}

ns.m.updateWaypointInformation = (marker) => {
    var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);
    
    const droneSelect = document.getElementById('droneSelect');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const altitudeInput = document.getElementById('altitudeInput');
    const speedInput = document.getElementById('speedInput');
    const cameraSelect = document.getElementById('cameraSelect');
    const holdInput = document.getElementById('holdInput');
    const gimbalPitchInput = document.getElementById('gimbalPitchInput');
    const gimbalYawInput = document.getElementById('gimbalYawInput');
    const headingInput = document.getElementById('headingInput');

    var waypointData = waypoint.data;

    var position = marker.getLatLng();

    droneSelect.value = waypoint.id;
    latitudeInput.value = position.lat;
    longitudeInput.value = position.lng;
    altitudeInput.value = waypointData.altitude;
    speedInput.value = waypointData.speed;
    cameraSelect.value = waypointData.camera;
    holdInput.value = waypointData.holdInput;
    gimbalPitchInput.value = waypointData.gimbalPitch;
    gimbalYawInput.value = waypointData.gimbalYaw;
    headingInput.value = waypointData.heading;
}

ns.m.getPopupContentString = (waypointElement) => {
    // return `<div>id: ${waypointElement.id} - ` + waypointElement.marker.getLatLng().toString() + '</div>'
    return `<div>droneId: ${waypointElement.id} <br> altitude: ${waypointElement.data.altitude} <br> speed: ${waypointElement.data.speed} ` + '</div>'
}

ns.m.updateWaypointDataSelectedMarker = (marker) => {
    var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);

    var waypointData = waypoint.data;
    
    var lat = document.getElementById('latitude').value;
    var lng = document.getElementById('longitude').value;

    if (lat != 0 && lng != 0) {
        var latlng = L.latLng(document.getElementById('latitude').value, document.getElementById('longitude').value);
        waypoint.marker.setLatLng(latlng);
    };

    waypoint.id = document.getElementById('droneSelect').value;
    waypointData.altitude = document.getElementById('altitudeInput').value;
    waypointData.speed = document.getElementById('speedInput').value;
    waypointData.camera = document.getElementById('cameraSelect').value;
    waypointData.holdInput = document.getElementById('holdInput').value;
    waypointData.gimbalPitch = document.getElementById('gimbalPitchInput').value;
    waypointData.gimbalYaw = document.getElementById('gimbalYawInput').value;
    waypointData.heading = document.getElementById('headingInput').value;
}

ns.m.deleteMarker = () => {
    if (ns.d.selectedMarker !== null) {
    ns.map.map.removeLayer(ns.d.selectedMarker);
    var elem = ns.d.wayPointsDrones.find(w => w.marker === ns.d.selectedMarker);
    
    var droneId = elem.id;

    const index = ns.d.wayPointsDrones.indexOf(elem);
    
    if (index > -1) {
        ns.d.wayPointsDrones.splice(index, 1);
    };

    ns.m.deleteWaylines();
    ns.m.reorderAllWaypoints();
    if (ns.m.isShowAnimation()) {
        ns.m.updateDroneAnimation();
    };

    if (ns.m.isShowWaylines()) {
        ns.m.calculateWaylines();
    };

    ns.d.selectedMarker = null; // Reset selected marker variable
    ns.m.updateSelectedMarkerDiv();

    ns.d.droneAnimation.forEach(element => {
        if (element.flowpoints.length == 0) {
            ns.m.hideTooltip(element.tooltip);
        }
    });

    } else {
    alert('No marker selected.');
    }
};

ns.m.deleteAllMarkerOfDroneId = () => {
    if (ns.d.selectedMarker !== null) {
        ns.map.map.removeLayer(ns.d.selectedMarker);
        var droneId = ns.d.wayPointsDrones.find(w => w.marker === ns.d.selectedMarker).id;

        var element = ns.d.wayPointsDrones.find(w => w.id === droneId);

        while (element !== undefined) {
            var index = ns.d.wayPointsDrones.indexOf(element);
            ns.map.map.removeLayer(element.marker);
            if (index > -1) {
                ns.d.wayPointsDrones.splice(index, 1);
            };

            element = ns.d.wayPointsDrones.find(w => w.id === droneId);
        }

        var droneAnimationElem = ns.d.droneAnimation.find(d => d.id === parseInt(droneId));
        droneAnimationElem.flowpoints = []
        ns.m.hideTooltip(droneAnimationElem.tooltip);
        
        ns.m.deleteWaylines();
        ns.m.reorderAllWaypoints();
        if (ns.m.isShowAnimation()) {
            ns.m.updateDroneAnimation();
        };
    
        if (ns.m.isShowWaylines()) {
            ns.m.calculateWaylines();
        };
        
        ns.d.selectedMarker = null; // Reset selected marker variable
        

        ns.m.updateSelectedMarkerDiv();
    
        ns.d.droneAnimation.forEach(element => {
            if (element.flowpoints.length == 0) {
                ns.m.hideTooltip(element.tooltip);
            }
        });
    
        } else {
        alert('No marker selected.');
        }
};

ns.m.deleteAllMarker = () => {
    ns.m.deleteWaylines();

    ns.m.hideAllTooltips();
    ns.m.removeAllTravelMarkers();
    ns.d.wayPointsDrones.forEach(element => {
        ns.map.map.removeLayer(element.marker);
    });


    ns.d.selectedMarker = null;
    ns.d.wayPointsDrones = [];
    ns.d.wayLinesDrones = [];
    ns.d.droneAnimation = [];

    ns.m.initDroneAnimation();
    ns.m.initWayLinesDrones();
};

ns.m.reorderAllWaypoints = () => {
    let uniqueIds = [];      

    ns.d.wayPointsDrones.forEach(element => {
        if (!uniqueIds.includes(element.id)) {
            uniqueIds.push(element.id);
        }
    });

    uniqueIds.forEach(id => {
        var waypointsOfDrone = ns.d.wayPointsDrones.filter(w => w.id === id);
        waypointsOfDrone.forEach(elem => {
            var pointIndex = waypointsOfDrone.indexOf(elem);
            elem.marker.setIcon(ns.m.createWaypointIcon( `${elem.id}.${pointIndex}`, ns.m.getDroneColourCode(elem.id)));
        });
    });
}


ns.m.createSVGWithCircle = (value, color) => {
    // Construct the SVG string
    var svgString = `<svg width="${ns.c.ICONSIZE}" height="${ns.c.ICONSIZE}" xmlns="http://www.w3.org/2000/svg">`;
    svgString += `<circle cx="${ns.c.ICONSIZE / 2}" cy="${ns.c.ICONSIZE / 2}" r="${ns.c.ICONSIZE / 2}" fill="${color}" />`;
    svgString += `<text x="${ns.c.ICONSIZE / 2}" y="${ns.c.ICONSIZE / 2}" text-anchor="middle" style="font-family:helvetica;" alignment-baseline="central" font-size="12" fill="white">${value}</text>`;
    svgString += '</svg>';

    return svgString;
};

ns.m.createWaypointIcon = (index, color) => {
    return L.divIcon({
            html: ns.m.createSVGWithCircle(index, color),
            className:"waypoint-icon",
            iconSize:     [ns.c.ICONSIZE, ns.c.ICONSIZE],
            iconAnchor:   [ns.c.ICONSIZE/2, ns.c.ICONSIZE/2],
        });
}

ns.m.createDroneSVG = (colourCode) => {
    var svgString = `<svg xmlns="http://www.w3.org/2000/svg" height="${ns.c.DRONEMARKERSIZE}" viewBox="0 -960 960 960" width="${ns.c.DRONEMARKERSIZE}">
    <!-- White circle background -->
    <circle cx="480" cy="-480" r="400" fill="white"/>
    <!-- Circle with arrow -->
    <path d="M440-320h80v-168l64 64 56-56-160-160-160 160 56 56 64-64v168Zm40 240q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z" fill="${colourCode}"/>
    </svg>`

    return svgString;
}

ns.m.createDroneIcon = (colourCode) => {
    var droneIcon = L.divIcon({
        html: ns.m.createDroneSVG(colourCode),
        className:"drone-icon",
        iconSize:     [ns.c.DRONEMARKERSIZE, ns.c.DRONEMARKERSIZE],
        iconAnchor:   [ns.c.DRONEMARKERSIZE / 2, ns.c.DRONEMARKERSIZE / 2],
    });
    return droneIcon;
}


ns.m.formatNumber = (number) => {
    number = Math.round((number + Number.EPSILON) * 100) / 100
    return new Intl.NumberFormat('de-DE').format(number);
}

ns.m.createTooltip = () => {
    var tooltip = document.createElement("div");
    tooltip.className = 'travelmarker-tooltip';
    tooltip.style.display = 'none';
    ns.map.map.getPanes().tooltipPane.appendChild(tooltip);
    return tooltip;
};
    

// init droneAnimation
ns.m.initDroneAnimation = () => {
    for (let i=1; i < 11; i++) {
        ns.d.droneAnimation.push({
            id: i, 
            flowpoints : [], 
            travelMarker: null, 
            tooltip: ns.m.createTooltip()})
    };
};

ns.m.initDroneAnimation();

ns.m.calculateFlowPoints = () => {
    ns.d.droneAnimation.forEach(elem => {
        ns.m.calculateDroneAnimation(elem.id);
    });
};

ns.m.calculateDroneAnimation = (id) => {
    let flowpoints = ns.d.droneAnimation.find(d => d.id === id).flowpoints;

    let waypointElems = ns.d.wayPointsDrones.filter(w => parseInt(w.id) === id);

    if (waypointElems.length > 0 ) {
    let latLngs = waypointElems.map(x => x.marker.getLatLng());
    let holdTimes = waypointElems.map(x => x.data.holdInput);
    let speeds = waypointElems.map(x=>x.data.speed);
    let distances = [];
    let euclideanDistances = [];
    let angles = [];
    
    let heading = waypointElems.map(x => x.data.heading).map(Number);
    let angularDistances = ns.m.calcAngularDistancesHeading(heading);
    
    let altitudes = waypointElems.map(x => x.data.altitude).map(Number);
    let altitudeDistances = ns.m.calcAltitudeDistances(altitudes);

    for (let i = 0; i < (latLngs.length - 1); i++) {
        var from = latLngs[i];
        var to = latLngs[i+1];

        distances.push(from.distanceTo(to));
        euclideanDistances.push(ns.m.calcEuclideanDistance(from, to));
        angles.push(ns.m.calculateAngleFromCoordinates(from, to));
    }

    for (let i = 0; i < distances.length; i++) {
        // flowpoints for hold at position
        if (holdTimes[i] === '') {
            var holdTime = 0;
        } else {
            var holdTime = parseInt(holdTimes[i]);
        }


        for (let t = 0; t <= holdTime; t++) {
            flowpoints.push({
                "timestep" : flowpoints.length,
                "travelPoint" : ns.map.map.latLngToLayerPoint(latLngs[i]), 
                "headingAngle" : heading[i],
                "altitude" : altitudes[i]
            })
        };

        // flowpoints for moving between to positions
        if (speeds[i] === '') {
            var speed = ns.c.defaultSpeed;
        } else {
            var speed = parseFloat(speeds[i])
        }
        var travelTime = Math.ceil(parseFloat(distances[i]) / speed);
        
        var speedInPixel = euclideanDistances[i] / travelTime;
        
        var angularSpeed = angularDistances[i] / travelTime;
        var startHeadingAngle = heading[i];

        var altitudeSpeed = altitudeDistances[i] / travelTime;
        var startAltitude = altitudes[i];

        for (let tt = 1; tt < travelTime; tt++) {
            var distanceNextPoint = tt * speedInPixel;
            
            var currentAngle = startHeadingAngle + tt * angularSpeed;
            var currentAltitude = startAltitude + tt * altitudeSpeed;

            var travelPoint = ns.m.calculateTravelPoint(angles[i], distanceNextPoint, latLngs[i])

            flowpoints.push({
                "timestep" : flowpoints.length,
                "travelPoint" : travelPoint, 
                "headingAngle" : currentAngle,
                "altitude" : currentAltitude
            });

        }

        // flowpoints at end point of each waypoint
        if (i === (distances.length - 1)) {
            flowpoints.push({
                "timestep" : flowpoints.length,
                "travelPoint" : ns.map.map.latLngToLayerPoint(latLngs[i+1]), 
                "headingAngle" : heading[heading.length - 1],
                "altitude" : altitudes[altitudes.length - 1]
            }) // adds finishing point to flowpoints
        }

    }
}
};

ns.m.calcEuclideanDistance = (fromLatLng, toLatLng) => {
    var from = ns.map.map.latLngToLayerPoint(fromLatLng);
    var to = ns.map.map.latLngToLayerPoint(toLatLng);

    var deltaX = to.x - from.x;
    var deltaY = to.y - from.y;

    return Math.sqrt(Math.pow(deltaX, 2) + Math.pow(deltaY, 2))
};

ns.m.calcAngularDistancesHeading = (headingAngles) => {
    // headingAngles => heading angles in a list of one drone
    var angularDistances = [];

    for (let i = 0; i < (headingAngles.length - 1); i++) {
        var diff = (headingAngles[i+1] - headingAngles[i] + 180) % 360 - 180;
        if (diff < -180) {
            diff = diff + 360;
        }
        angularDistances.push(diff)
    }
    return angularDistances;
}; 

ns.m.calcAltitudeDistances = (altitudes) => {
    // altitudes => altitudes in an array of one drone
    var altitudeDistances = [];

    for (let i = 0; i < (altitudes.length - 1); i++) {
        var diff = altitudes[i+1] - altitudes[i];
        altitudeDistances.push(diff);
    }
    return altitudeDistances;
}

ns.m.showTravelPointAtTimestep = (timestep) => {
    ns.d.droneAnimation.forEach(elem => {
        if (elem.flowpoints.length > 0) {
            var droneColour = ns.m.getDroneColourCode(elem.id);
            var droneIcon = ns.m.createDroneIcon(droneColour);
            if (timestep >= elem.flowpoints.length) {
                elem.travelMarker = L.marker(ns.map.map.layerPointToLatLng(elem.flowpoints[elem.flowpoints.length - 1]["travelPoint"]), {icon: droneIcon, zIndexOffset: 1500});
                elem.travelMarker.setRotationAngle(elem.flowpoints[elem.flowpoints.length - 1]["headingAngle"]);
                ns.m.setTooltipContent(elem.tooltip, elem.flowpoints[elem.flowpoints.length - 1]);
                ns.m.setTooltipPosition(elem.tooltip, elem.travelMarker);
                ns.m.showTooltip(elem.tooltip);
                elem.travelMarker.addTo(ns.map.map);
            } else {
                elem.travelMarker = L.marker(ns.map.map.layerPointToLatLng(elem.flowpoints[timestep]["travelPoint"]), {icon: droneIcon, zIndexOffset: 1500});
                elem.travelMarker.setRotationAngle(elem.flowpoints[timestep]["headingAngle"]);
                ns.m.setTooltipContent(elem.tooltip, elem.flowpoints[timestep]);
                ns.m.setTooltipPosition(elem.tooltip, elem.travelMarker);
                ns.m.showTooltip(elem.tooltip);
                elem.travelMarker.addTo(ns.map.map);
            }
        }
    })
};

ns.m.removeAllTravelMarkers = () => {
    ns.d.droneAnimation.forEach(elem => {
        if (elem.travelMarker != null) {
            ns.map.map.removeLayer(elem.travelMarker);
            elem.travelMarker = null;
        }
    });
};

ns.m.calculateTravelPoint = (radian, distance, startPoint) => {
    startPoint = ns.map.map.latLngToLayerPoint(startPoint);
    var x = startPoint.x + distance * Math.cos(radian);
    var y = startPoint.y + distance * Math.sin(radian);
    return L.point(x, y);
}

ns.m.calculateAngleFromCoordinates = (latLngA, latLngB) => {
    var pointA = ns.map.map.latLngToLayerPoint(latLngA);
    var pointB = ns.map.map.latLngToLayerPoint(latLngB);

    var y = pointB.y - pointA.y;
    var x = pointB.x - pointA.x;

    return Math.atan2(y,x);
}

ns.m.atan2Degree = (atan2) => {
    atan2 = atan2 * 180 / Math.PI;
    atan2 = atan2 + 90; // add 90 degree to turn coordinate system => North = 0°
    return (atan2 + 360) % 360;
}

ns.m.setMaxValueRangeSlider = () => {
    var max = 0;
    ns.d.droneAnimation.forEach(elem => {
        if (elem.flowpoints.length > max) {
            max = elem.flowpoints.length;
        }
    });
    document.getElementById('droneAnimationSlider').max = max;
};

ns.m.setDronesToCurrentTimestep = () => {
    var val = document.getElementById('droneAnimationSlider').value;
    ns.m.showTravelPointAtTimestep(val);
};

ns.m.resetFlowpoints = () => {
    ns.d.droneAnimation.forEach(elem => {
        elem.flowpoints = [];
    });
};

ns.m.updateDroneAnimation = () => {
    ns.m.resetFlowpoints();
    ns.m.removeAllTravelMarkers();
    ns.m.calculateFlowPoints();
    ns.m.setMaxValueRangeSlider();
    ns.m.setDronesToCurrentTimestep();
}

ns.m.isShowAnimation = () => {
    return document.getElementById('showAnimation').value === 'show';
}

ns.m.createFlightPlanningObject = () => {
    let uniqueIds = [];
    let flightPlanning = {};

    ns.d.wayPointsDrones.forEach(element => {
        if (!uniqueIds.includes(element.id)) {
            uniqueIds.push(element.id);
        }
    });

    uniqueIds.forEach(id => {
        var items = ns.d.wayPointsDrones.filter(w => w.id === id);

        flightPlanning[`${id}`] = [];

        items.forEach(wp => {
            var latlng = wp.marker.getLatLng();
            if (wp.data.altitude === '') {
                wp.data.altitude = ns.c.defaultAltitude;
            };

            if (wp.data.holdInput === '') {
                wp.data.holdInput = ns.c.DEFAULTHOLDTIME;
            };

            if (wp.data.speed === '') {
                wp.data.speed = ns.c.defaultSpeed;
            };
            
            flightPlanning[`${id}`].push(
                {   
                    lat : latlng.lat, 
                    lng : latlng.lng,
                    speed : wp.data.speed,
                    lengthOfStay : wp.data.holdInput,
                    altitude : wp.data.altitude,
                    camera : wp.data.camera,
                    gimbalPitch : wp.data.gimbalPitch,
                    gimbalYaw : wp.data.gimbalYaw,
                    heading: wp.data.heading,
                }
            );
        });
    });
    return flightPlanning;
}

ns.d.wayPointsDrones = [];
// let wayPointsDrones = [
    //     {id : 1, marker: MARKEROBJECT, waypointdata : {}, wayline: null, timestamp: TIMESTAMP},
    //     {id : 1, marker: MARKEROBJECT, waypointdata : [], wayline: null, timestmap: TIMESTAMP},
    // ]

ns.m.retrieveFlightPlanningObject = (data) => {
    ns.d.selectedMarker = null;
    ns.d.wayPointsDrones = [];
    for (var id in data) {
        var waypoints = data[id];
        var pointIndex = 0;
        waypoints.forEach ((waypointdata) => {
            // icon
            var waypointIcon = ns.m.createWaypointIcon(id + '.' + pointIndex, ns.m.getDroneColourCode(id));

            // marker
            var lat = waypointdata['lat'];
            var lng = waypointdata['lng'];

            var latlng = L.latLng([lat, lng]);
            var marker = L.marker(latlng, {draggable: true, icon:waypointIcon}).addTo(ns.map.map);
            
            var waypoint = {};
            waypoint.id = id;

            console.log(waypoint.id, typeof(waypoint.id));

            waypoint.marker = marker;
            waypoint.wayline = null;
            waypoint.data = {
                lat: lat,
                lng: lng,
                altitude: waypointdata['altitude'],
                speed: waypointdata['speed'],
                camera: waypointdata['camera'],
                holdInput: waypointdata['lengthOfStay'],
                gimbalPitch: waypointdata['gimbalPitch'],
                gimbalYaw: waypointdata['gimbalYaw'],
                heading: waypointdata['heading'],
            },
            
            waypoint.timestamp = Date.now();
            
            pointIndex++;
            ns.m.waypointMarkerMethods(waypoint);
            ns.d.wayPointsDrones.push(waypoint);
    });
    }


}

ns.m.sendDroneDataToApi = () => {
    console.log("before", ns.d.wayPointsDrones);
    const request = new Request(ns.c.apiEndpoint, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(JSON.stringify(ns.m.createFlightPlanningObject())),
    });
    
    fetch(request)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            ns.m.deleteWaylines();
            ns.m.deleteAllMarker();

            data = JSON.parse(data);
            ns.m.retrieveFlightPlanningObject(data);

            if (ns.m.isShowWaylines()) { 
                ns.m.calculateWaylines();
            };
    
            // update DroneAnimation
            if (ns.m.isShowAnimation()) {
                ns.m.updateDroneAnimation();
            };
            
            alert("The project has been submitted and loaded successfully.");
        })

        .catch((error) => {
            console.log(error);
            alert("An error occurred while sending the data to the server.")
        })
};

ns.m.setTooltipContent = (tooltip, flowpoint) => {
    content = `<p>alt: ${ns.m.formatNumber(flowpoint.altitude)} m</p>`
    tooltip.innerHTML = content;
}

ns.m.hideAllTooltips = () => {
    ns.d.droneAnimation.forEach(elem => {
        elem.tooltip.style.display = 'none'
    });
};

ns.m.showAllTooltips = () => {
    ns.d.droneAnimation.forEach(elem => {
        if (elem.flowpoints.length > 0) {
            elem.tooltip.style.display = 'block';
        };
    });
};

ns.m.showTooltip = (tooltip) => {
    tooltip.style.display = 'block';
};

ns.m.hideTooltip = (tooltip) => {
    tooltip.style.display = 'none';
};

ns.m.setTooltipPosition = (tooltip, marker) => {
    var markerLatLng = marker.getLatLng();
    var pos = ns.map.map.latLngToLayerPoint(markerLatLng);

    tooltip.style.left = (pos.x + ns.c.TOOLTIP_OFFSET_X) + 'px';
    tooltip.style.top = (pos.y + ns.c.TOOLTIP_OFFSET_Y) + 'px';
};

// events
document.getElementById('updateWaypoint').addEventListener('click', function() {
    if (ns.d.selectedMarker !== null) {
        ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
        
        ns.m.deleteWaylines();
        ns.m.reorderAllWaypoints();
        ns.m.calculateWaylines();
        ns.m.updateSelectedMarkerDiv();

        if (!ns.m.isShowWaylines()) {
            ns.m.deleteWaylines();
        };
    } else {
        alert('No marker selected.');
    }
});

document.getElementById('showWaylines').addEventListener('click', function() {
    var button = document.getElementById('showWaylines');
    if (ns.m.isShowWaylines()) {
        ns.m.deleteWaylines();
        button.value = 'hide';
        button.innerHTML = 'Show waylines'
    } else {
        ns.m.calculateWaylines();
        button.value = 'show';
        button.innerHTML = 'Hide waylines';
    }
})

document.getElementById('removeMarkerBtn').addEventListener('click', function() {
    ns.m.deleteMarker();
});

document.getElementById('removeAllMarkerOfDroneIdBtn').addEventListener('click', function() {
    ns.m.deleteAllMarkerOfDroneId();
});

document.getElementById('removeAllMarkerBtn').addEventListener('click', function() {
    ns.m.deleteAllMarker();
    ns.m.deleteWaylines();
});

document.getElementById('droneAnimationSlider').addEventListener('input', function(e) {
    ns.m.removeAllTravelMarkers();
    ns.m.showTravelPointAtTimestep(e.target.value);
});

document.getElementById('showAnimation').addEventListener('click', function() {
    var button = document.getElementById('showAnimation');
    var sliderContainer = document.getElementById('rangeSliderDiv');
    if (ns.m.isShowAnimation()) {
        ns.m.removeAllTravelMarkers();
        ns.m.hideAllTooltips();
        button.value = 'hide';
        sliderContainer.style.display = "none";
        button.innerHTML = 'Show animation'
    } else {
        ns.m.updateDroneAnimation();
        ns.m.showAllTooltips();
        sliderContainer.style.display = "block";
        button.value = 'show';
        button.innerHTML = 'Hide animation';
    }
});

document.getElementById('sendWaypointsBtn').addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();

    ns.m.sendDroneDataToApi();
});

// map events
ns.map.map.on('dragend', function() {
    if (ns.m.isShowAnimation()) {
        ns.m.updateDroneAnimation();
    };
});

ns.map.map.on('zoomend', function() {
    if (ns.m.isShowAnimation()) {
        ns.m.updateDroneAnimation();
    };
});

}(ps3));
