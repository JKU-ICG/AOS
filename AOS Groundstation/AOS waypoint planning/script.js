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

    // This variable is used to persist the selected waypoint key across updates.
    ns.d.persistedSelectedKey = null;

    ns.d.wayPointsDrones = [];
    // let wayPointsDrones = [
    //     {id : 1, marker: MARKEROBJECT, waypointdata : {}, wayline: null, timestamp: TIMESTAMP},
    //     {id : 1, marker: MARKEROBJECT, waypointdata : [], wayline: null, timestmap: TIMESTAMP},
    // ]
        
    ns.d.droneAnimation = []
    // [{id : 1, flowpoints: [], tooltip: div},
    //  {id : 2, flowpoints: [], tooltip: div}]
        
    ns.d.wayLinesDrones = [];  
    // [{id : 1, wayline : POLYGONLINEOBJECT},{id : 2, wayline : POLYGONLINEOBJECT}]

    // initialize wayLines with null value;
    ns.m.initWayLinesDrones = function() {
        for (let i = 1; i < 11; i++) {
            ns.d.wayLinesDrones.push({id: i, wayline: null});
        }
    };

    ns.m.initWayLinesDrones();

    ns.v.addMarkerToMap = true;
    ns.v.showAnimation = false; // show animation of drones - toggle state

    ns.c.DRONECOLOURCODES = [
        {id: 1,  colour: '#B30F0F'},
        {id: 2,  colour: '#013A65'},
        {id: 3,  colour: '#A460DC'},
        {id: 4,  colour: '#B07ACB'},
        {id: 5,  colour: '#EB00A0'},
        {id: 6,  colour: '#000000'},
        {id: 7,  colour: '#55647E'},
        {id: 8,  colour: '#784491'},
        {id: 9,  colour: '#2476FF'},
        {id: 10, colour: '#31571B'}
    ];

    ns.c.ICONSIZE = 32;
    ns.c.DRONEMARKERSIZE = 30;

    // default values for creating flight object (if no values are given)
    ns.c.DEFAULTHOLDTIME = 0;
    ns.c.defaultAltitude = 20;
    ns.c.defaultSpeed = 0.5;
    ns.c.defaultHeading = 0;
    ns.c.defaultIntegrationWindow = 30;
    ns.c.defaultMinposeDistance = 0.5;

    // default values for position of drone-tooltip
    ns.c.TOOLTIP_OFFSET_X = 10;
    ns.c.TOOLTIP_OFFSET_Y = 10;

    // API-Endpoint the server is listening on
    ns.c.apiEndpoint = "http://localhost:8000/dronedata";

    // ------------------------------
    // Collision Detection Section (Corrected with Flowpoint Existence Checks)
    // ------------------------------

    // Define the collision threshold in meters.
    // ns.c.COLLISION_THRESHOLD = 2.0; // adjust as needed

    document
        .getElementById('detectCollisionsBtn')
        .addEventListener('click', function() {
            
            // 1) read & parse the input
            const raw = document.getElementById('collisionThresholdInput').value;
            const val = parseFloat(raw);
            // guard against empty / NaN
            if (!isNaN(val) && val >= 0) {
            ns.c.COLLISION_THRESHOLD = val;
            }

            // 2) now run detection with the updated threshold
            const collisions = ns.m.detectCollisions3D();
            console.log('using threshold', ns.c.COLLISION_THRESHOLD, 'm →', collisions);
            ns.m.showCollisionMarkers(collisions);
    });
    
    // Helper function: Haversine distance between two geographic points.
    ns.m.haversineDistance = function(latlng1, latlng2) {
        var R = 6371000; // Earth radius in meters
        var lat1 = latlng1.lat * Math.PI / 180;
        var lat2 = latlng2.lat * Math.PI / 180;
        var dLat = (latlng2.lat - latlng1.lat) * Math.PI / 180;
        var dLon = (latlng2.lng - latlng1.lng) * Math.PI / 180;
        var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon/2) * Math.sin(dLon/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    };

    ns.m.calc3DDistance = function(fpA, fpB) {
        if (!fpA?.latlng || !fpB?.latlng) {
            console.error("Missing fp.latlng:", fpA, fpB);
            return Infinity;
        }
        const h = ns.m.haversineDistance(fpA.latlng, fpB.latlng);
        const dz = fpB.altitude - fpA.altitude;
        return Math.sqrt(h*h + dz*dz);
    };
    
    // Detect collisions, even single‑waypoint drones
    ns.m.detectCollisions3D = function() {
        ns.m.updateDroneAnimation();
    
        const collisions = [];
        const seen = {};
    
        // build drones[] with at least one fp.latlng per drone
        const drones = ns.d.droneAnimation.map(drone => {
            let fp = [...drone.flowpoints];
            const wps = ns.d.wayPointsDrones.filter(w => +w.id === drone.id);
            if (fp.length === 0 && wps.length === 1) {
                const geo = wps[0].marker.getLatLng();
                fp = [{ latlng: geo, altitude:+wps[0].data.altitude, timestep:0 }];
            }
            return { id: drone.id, flowpoints: fp };
        }).filter(d => d.flowpoints.length);
    
        if (drones.length < 2) return collisions;
    
        // pad to same length
        const M = Math.max(...drones.map(d=>d.flowpoints.length));
        drones.forEach(d => {
            const last = d.flowpoints[d.flowpoints.length-1];
            for (let t=d.flowpoints.length; t<M; t++) {
                d.flowpoints.push({ ...last, timestep:t });
            }
        });
    
        // step through time & pairwise
        for (let t=0; t<M; t++) {
            for (let i=0; i<drones.length; i++) {
                for (let j=i+1; j<drones.length; j++) {
                    const key = `${Math.min(drones[i].id,drones[j].id)}-` +
                                `${Math.max(drones[i].id,drones[j].id)}`;
                    if (seen[key]) continue;
    
                    const A = drones[i].flowpoints[t];
                    const B = drones[j].flowpoints[t];
                    const d = ns.m.calc3DDistance(A, B);
                    if (d <= ns.c.COLLISION_THRESHOLD) {
                        const la = A.latlng, lb = B.latlng;
                        const mid = { lat:(la.lat+lb.lat)/2, lng:(la.lng+lb.lng)/2 };
                        collisions.push({
                            time:       (A.timestep+B.timestep)/2,
                            droneA:     drones[i].id,
                            droneB:     drones[j].id,
                            collisionPoint: mid,
                            distance:   d
                        });
                        seen[key] = true;
                    }
                }
            }
        }
        return collisions;
    };
    
    // ns.m.showCollisionMarkers = function(collisions) {
    //     // clear old
    //     ns.d.collisionMarkers?.forEach(l=>ns.map.map.removeLayer(l));
    //     ns.d.collisionMarkers = [];
        
    //     const regionRadiusPx = (ns.c.DRONEMARKERSIZE/2) + 5;

    //     collisions.forEach(c => {
    //         const { lat, lng } = c.collisionPoint;
    
    //         // true‑meters red circle
    //         const rc = L.circle([lat,lng], {
    //             radius:      regionRadiusPx,
    //             color:       'red',
    //             fillColor:   'red',
    //             fillOpacity: 0.6,
    //             weight:      2
    //         }).addTo(ns.map.map);
    
    //         // fixed black dot
    //         const bd = L.circleMarker([lat,lng], {
    //             radius:      3,
    //             color:       'black',
    //             fillOpacity: 1,
    //             weight:      1
    //         }).addTo(ns.map.map);
    
    //         const popupMessage = `Drone ${c.droneA} collides with Drone ${c.droneB}  at (${lat.toFixed(8)}, ${lng.toFixed(8)}) with a distance of ${c.distance.toFixed(3)} m.`;
        
    //         bd.bindPopup(popupMessage, {
    //             autoClose: false,
    //             closeOnClick: false
    //         }).openPopup();  // immediately open so the user sees it

    
    //         ns.d.collisionMarkers.push(rc, bd);
    //     });
    // };

    // ------------------------------
    // End of Collision Detection Section
    // ------------------------------


    // New Additions

    // ns.m.showCollisionMarkers = function(collisions) {
    //     // 1) clear out old markers
    //     if (ns.d.collisionMarkers) {
    //       ns.d.collisionMarkers.forEach(l => ns.map.map.removeLayer(l));
    //     }
    //     ns.d.collisionMarkers = [];
      
    //     // 2) pick a fixed pixel radius
    //     //    let’s say we want it to be exactly the same diameter as your drone icon:
    //     const pxRadius = ns.c.DRONEMARKERSIZE / 2 + 10;  // 5px of “halo” padding
      
    //     collisions.forEach(c => {
    //       const { lat, lng } = c.collisionPoint;
      
    //       // a) PIXEL‑fixed red circleMarker
    //         const redZone = L.circleMarker([lat, lng], {
    //             radius:      pxRadius,       // **pixels** only
    //             color:       'red',
    //             fillColor:   'red',
    //             fillOpacity: 0.4,
    //             weight:      2
    //         }).addTo(ns.map.map);
        
    //         // b) the small black dot stays the same
    //         const blackDot = L.circleMarker([lat, lng], {
    //             radius:      3,
    //             color:       'black',
    //             fillOpacity: 1,
    //             weight:      1
    //         }).addTo(ns.map.map);
      
    //         const popupMessage = `Drone ${c.droneA} collides with Drone ${c.droneB}  at (${lat.toFixed(8)}, ${lng.toFixed(8)}) with a distance of ${c.distance.toFixed(3)} m.`;

    //         blackDot.bindPopup(popupMessage, {
    //             autoClose: false,
    //             closeOnClick: false
    //         }).openPopup();  // immediately open so the user sees it

      
    //         ns.d.collisionMarkers.push(redZone, blackDot);
    //     });
    // };

    ns.m.showCollisionMarkers = function(collisions) {
        // 1) clear old markers
        if (ns.d.collisionMarkers) {
            ns.d.collisionMarkers.forEach(l => ns.map.map.removeLayer(l));
        }
        ns.d.collisionMarkers = [];

        // 2) read the user’s threshold (in meters) from the input
        let raw = document.getElementById('collisionThresholdInput').value;
        let thr = parseFloat(raw);
        // fallback to your constant if invalid
        const thresholdMeters = (!isNaN(thr) && thr >= 0)
            ? thr
            : ns.c.COLLISION_THRESHOLD;

        // 3) fixed‐pixel red halo radius (unchanged)
        // const pxRadius = ns.c.DRONEMARKERSIZE/2 + 10;

        collisions.forEach(c => {
            const { lat, lng } = c.collisionPoint;
            const midLatLng = [lat, lng];

            // — black circle = threshold area (in CRUDE METERS)
            const redArea = L.circle(midLatLng, {
            radius:      thresholdMeters/2,
            color:       'red',
            weight:      2,
            fillColor:   'red',
            fillOpacity: 0.4,
            }).addTo(ns.map.map);

            // — little black dot = exact collision point
            const blackDot = L.circleMarker(midLatLng, {
            radius:      3,
            color:       'black',
            fillOpacity: 1,
            weight:      1
            }).addTo(ns.map.map);
      
            const popupMessage = `Drone ${c.droneA} collides with Drone ${c.droneB}  at (${lat.toFixed(8)}, ${lng.toFixed(8)}) with a distance of ${c.distance.toFixed(3)} m.`;

            blackDot.bindPopup(popupMessage, {
                autoClose: false,
                closeOnClick: false
            }).openPopup();  // immediately open so the user sees it

      
            ns.d.collisionMarkers.push(blackDot, redArea);
        });
    };
    
      
    function toggleButton(button) {
        const currentState = button.getAttribute('data-state');
        const newState = currentState === 'off' ? 'on' : 'off';
        button.setAttribute('data-state', newState);
        button.textContent = button.textContent.replace(currentState.capitalize(), newState.capitalize());
        button.classList.toggle('btn-custom-off');
        button.classList.toggle('btn-custom-on');
    }

    // Initialize buttons and attach event listeners once after DOM load
    document.addEventListener('DOMContentLoaded', function() {
        const integrationButton = document.getElementById('integrationButton');
        const anomalyButton = document.getElementById('anomalyButton');
        
        integrationButton.classList.add('btn-custom-off');
        anomalyButton.classList.add('btn-custom-off');
        
        integrationButton.addEventListener('click', function() {
            toggleButton(this);
            if(ns.d.selectedMarker){
                ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                ns.m.refreshWaypointsAndAnimations();
            }
        });
        
        anomalyButton.addEventListener('click', function() {
            toggleButton(this);
            if(ns.d.selectedMarker){
                ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                ns.m.refreshWaypointsAndAnimations();
            }
        });

        // Attach both input and change event listeners for real-time updates
        const fieldsToWatch = [
            'altitudeInput',
            'speedInput',
            'cameraSelect',
            'holdInput',
            'gimbalPitchInput',
            'gimbalYawInput',
            'headingInput',
            'integrationWindowInput',
            'minposeDistanceInput'
        ];
        fieldsToWatch.forEach(id => {
            const element = document.getElementById(id);
            element.addEventListener('input', function() {
                if(ns.d.selectedMarker){
                    ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                    ns.m.refreshWaypointsAndAnimations();
                }
            });
            element.addEventListener('change', function() {
                if(ns.d.selectedMarker){
                    ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                    ns.m.refreshWaypointsAndAnimations();
                }
            });
        });
        
        // --- New: Event listener for the collision detection button ---
        const detectCollisionsBtn = document.getElementById('detectCollisionsBtn');
        if (detectCollisionsBtn) {
            detectCollisionsBtn.addEventListener('click', function() {
                var collisions = ns.m.detectCollisions3D();
                console.log("Detected collisions:", collisions);
                ns.m.showCollisionMarkers(collisions);
            });
        }
        // --- End new addition ---
    });

    ns.map.map.on('click', function(e) {
        var droneId = document.getElementById('droneSelect').value;
        if (!droneId) {
            alert('No drone selected. Select a drone to add waypoints.');
        } else {
            let pointIndex = ns.d.wayPointsDrones.filter(w => w.id === droneId).length;
            var waypointIcon = ns.m.createWaypointIcon(droneId + '.' + pointIndex, ns.m.getDroneColourCode(droneId));
            var marker = L.marker(e.latlng, {draggable: true, icon: waypointIcon}).addTo(ns.map.map);
            
            var waypoint = {};
            waypoint.id = droneId;
            waypoint.marker = marker;
            waypoint.wayline = null;

            // set defaults for altitude, speed and hold on position
            var altitudeInput = document.getElementById('altitudeInput').value || ns.c.defaultAltitude;
            var speedInput = document.getElementById('speedInput').value || ns.c.defaultSpeed;
            var holdInput = document.getElementById('holdInput').value || ns.c.DEFAULTHOLDTIME;

            // Get values from the new inputs
            var integrationWindowInput = document.getElementById('integrationWindowInput').value || ns.c.defaultIntegrationWindow;
            var minposeDistanceInput = document.getElementById('minposeDistanceInput').value || ns.c.defaultMinposeDistance;

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
                integrationWindow: parseInt(integrationWindowInput),
                minposeDistance: parseFloat(minposeDistanceInput),
                integration: document.getElementById('integrationButton').getAttribute('data-state'),
                anomaly: document.getElementById('anomalyButton').getAttribute('data-state')
            };
            waypoint.timestamp = Date.now();

            ns.d.wayPointsDrones.push(waypoint);

            ns.d.selectedMarker = waypoint.marker;
            ns.m.updateWaypointInformation(ns.d.selectedMarker); // update waypoint information in sidebar

            ns.m.updateSelectedMarkerDiv();

            if (ns.m.isShowWaylines()) {
                ns.m.deleteWaylines();
                ns.m.calculateWaylines();
            }

            // update DroneAnimation
            if (ns.m.isShowAnimation()) {
                ns.m.updateDroneAnimation();
            }

            ns.m.waypointMarkerMethods(waypoint);
        }
    });
    // Helper function to capitalize first letter (add this if you don't have it already)
    String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
    };

// changes 24.09.2024 (working)
// ns.map.map.on('click', function(e) {
//     var droneId = document.getElementById('droneSelect').value;
//     if (!droneId) {
//         alert('No drone selected. Select a drone to add waypoints.');
//     } else {
//         let pointIndex = ns.d.wayPointsDrones.filter(w => w.id === droneId).length;
//         var waypointIcon = ns.m.createWaypointIcon(droneId + '.' + pointIndex, ns.m.getDroneColourCode(droneId));
//         var marker = L.marker(e.latlng, {draggable: true, icon:waypointIcon}).addTo(ns.map.map);
        
//         var waypoint = {}
//         waypoint.id = droneId;
//         waypoint.marker = marker;
//         waypoint.wayline = null;

//         // set defaults for altitude, speed and hold on position
//         var altitudeInput = document.getElementById('altitudeInput').value || ns.c.defaultAltitude;
//         var speedInput = document.getElementById('speedInput').value || ns.c.defaultSpeed;
//         var holdInput = document.getElementById('holdInput').value || ns.c.DEFAULTHOLDTIME;

//         // Get values from the new inputs
//         var integrationWindowInput = document.getElementById('integrationWindowInput').value || ns.c.defaultIntegrationWindow;
//         var minposeDistanceInput = document.getElementById('minposeDistanceInput').value || ns.c.defaultMinposeDistance;

//         waypoint.data = {
//             lat: marker.lat,
//             lng: marker.lng,
//             altitude: altitudeInput,
//             speed: speedInput,
//             camera: document.getElementById('cameraSelect').value,
//             holdInput: holdInput,
//             gimbalPitch: document.getElementById('gimbalPitchInput').value,
//             gimbalYaw: document.getElementById('gimbalYawInput').value,
//             heading: document.getElementById('headingInput').value,
//             integrationWindow: integrationWindowInput,
//             minposeDistance: parseFloat(minposeDistanceInput)
//         }
//         waypoint.timestamp = Date.now();

//         ns.d.wayPointsDrones.push(waypoint)

//         ns.d.selectedMarker = waypoint.marker;
//         ns.m.updateWaypointInformation(ns.d.selectedMarker); // update waypoint information in sidebar

//         ns.m.updateSelectedMarkerDiv();

//         if (ns.m.isShowWaylines()) {
//             ns.m.deleteWaylines();
//             ns.m.calculateWaylines();
//         };

//         // update DroneAnimation
//         if (ns.m.isShowAnimation()) {
//             ns.m.updateDroneAnimation();
//         };

//         ns.m.waypointMarkerMethods(waypoint);
//     }
// });

// Additions are done

// methods

ns.m.waypointMarkerMethods = (waypoint) => {
    waypoint.marker.on('click', function() {
        // Modified: Check if this marker is already selected. If yes, do nothing.
        if (ns.d.selectedMarker === waypoint.marker) {
            return;
        }
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

// ns.m.updateWaypointInformation = (marker) => {
//     var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);
    
//     const droneSelect = document.getElementById('droneSelect');
//     const latitudeInput = document.getElementById('latitude');
//     const longitudeInput = document.getElementById('longitude');
//     const altitudeInput = document.getElementById('altitudeInput');
//     const speedInput = document.getElementById('speedInput');
//     const cameraSelect = document.getElementById('cameraSelect');
//     const holdInput = document.getElementById('holdInput');
//     const gimbalPitchInput = document.getElementById('gimbalPitchInput');
//     const gimbalYawInput = document.getElementById('gimbalYawInput');
//     const headingInput = document.getElementById('headingInput');
//     const integrationWindowInput = document.getElementById('integrationWindowInput');
//     const minposeDistanceInput = document.getElementById('minposeDistanceInput');
//     // const integrationButton = document.getElementById('integrationButton');
//     // const anomalyButton = document.getElementById('anomalyButton');

//     var waypointData = waypoint.data;

//     var position = marker.getLatLng();

//     // Update integration button
//     var integrationButton = document.getElementById('integrationButton');
//     integrationButton.setAttribute('data-state', waypoint.data.integration);
//     integrationButton.textContent = 'Integration: ' + waypoint.data.integration.capitalize();
//     integrationButton.classList.toggle('btn-custom-off', waypoint.data.integration === 'off');
//     integrationButton.classList.toggle('btn-custom-on', waypoint.data.integration === 'on');

//     // Update anomaly button
//     var anomalyButton = document.getElementById('anomalyButton');
//     anomalyButton.setAttribute('data-state', waypoint.data.anomaly);
//     anomalyButton.textContent = 'Anomaly: ' + waypoint.data.anomaly.capitalize();
//     anomalyButton.classList.toggle('btn-custom-off', waypoint.data.anomaly === 'off');
//     anomalyButton.classList.toggle('btn-custom-on', waypoint.data.anomaly === 'on');

//     droneSelect.value = waypoint.id;
//     latitudeInput.value = position.lat;
//     longitudeInput.value = position.lng;
//     altitudeInput.value = waypointData.altitude;
//     speedInput.value = waypointData.speed;
//     cameraSelect.value = waypointData.camera;
//     holdInput.value = waypointData.holdInput;
//     gimbalPitchInput.value = waypointData.gimbalPitch;
//     gimbalYawInput.value = waypointData.gimbalYaw;
//     headingInput.value = waypointData.heading;
//     integrationWindowInput.value = waypointData.integrationWindow;
//     minposeDistanceInput.value = waypointData.minposeDistance;
//     integrationButton.setAttribute('data-state', waypointData.integration);
//     anomalyButton.setAttribute('data-state', waypointData.anomaly);
// }

ns.m.updateWaypointInformation = (marker) => {

    // Set the selected marker to the clicked waypoint marker
    ns.d.selectedMarker = marker;

    var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);

    // Proceed only if waypoint is found
    if (!waypoint) {
        console.error("Waypoint not found for the clicked marker.");
        alert("Waypoint not found for the clicked marker.");
        return;
    }

    // Log the waypoint data to the console when it's selected
    console.log("Selected Waypoint Data:", waypoint.data);

    // Populate input fields with current data
    document.getElementById('latitude').value = marker.getLatLng().lat;
    document.getElementById('longitude').value = marker.getLatLng().lng;	
    
    document.getElementById('droneSelect').value = waypoint.id;
    document.getElementById('altitudeInput').value = waypoint.data.altitude;
    document.getElementById('speedInput').value = waypoint.data.speed;
    document.getElementById('cameraSelect').value = waypoint.data.camera;
    document.getElementById('holdInput').value = waypoint.data.holdInput;
    document.getElementById('gimbalPitchInput').value = waypoint.data.gimbalPitch;
    document.getElementById('gimbalYawInput').value = waypoint.data.gimbalYaw;
    document.getElementById('headingInput').value = waypoint.data.heading;
    document.getElementById('integrationWindowInput').value = waypoint.data.integrationWindow;
    document.getElementById('minposeDistanceInput').value = waypoint.data.minposeDistance;

    // Note: Input event listeners have been attached globally on DOMContentLoaded.
    // Therefore, they are not reattached here to avoid duplicates.

    // Update toggle buttons (integration and anomaly)
    const integrationButton = document.getElementById('integrationButton');
    const anomalyButton = document.getElementById('anomalyButton');

    integrationButton.setAttribute('data-state', waypoint.data.integration);
    integrationButton.textContent = 'Integration: ' + waypoint.data.integration.capitalize();
    integrationButton.classList.toggle('btn-custom-off', waypoint.data.integration === 'off');
    integrationButton.classList.toggle('btn-custom-on', waypoint.data.integration === 'on');

    anomalyButton.setAttribute('data-state', waypoint.data.anomaly);
    anomalyButton.textContent = 'Anomaly: ' + waypoint.data.anomaly.capitalize();
    anomalyButton.classList.toggle('btn-custom-off', waypoint.data.anomaly === 'off');
    anomalyButton.classList.toggle('btn-custom-on', waypoint.data.anomaly === 'on');

    // Removed reattaching of click events for toggle buttons here, as they are attached globally.
};

ns.m.refreshWaypointsAndAnimations = () => {
    ns.m.deleteWaylines();
    ns.m.calculateWaylines();

    if (ns.m.isShowAnimation()) {
        ns.m.updateDroneAnimation();
    }
};

ns.m.getPopupContentString = (waypointElement) => {
    // return `<div>id: ${waypointElement.id} - ` + waypointElement.marker.getLatLng().toString() + '</div>'
    return `<div>droneId: ${waypointElement.id} <br> altitude: ${waypointElement.data.altitude} <br> speed: ${waypointElement.data.speed} ` + '</div>'
}

// ns.m.updateWaypointDataSelectedMarker = (marker) => {
//     var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);

//     var waypointData = waypoint.data;
    
//     var lat = document.getElementById('latitude').value;
//     var lng = document.getElementById('longitude').value;

//     if (lat != 0 && lng != 0) {
//         var latlng = L.latLng(document.getElementById('latitude').value, document.getElementById('longitude').value);
//         waypoint.marker.setLatLng(latlng);
//     };

//     waypoint.id = document.getElementById('droneSelect').value;
//     waypointData.altitude = document.getElementById('altitudeInput').value;
//     waypointData.speed = document.getElementById('speedInput').value;
//     waypointData.camera = document.getElementById('cameraSelect').value;
//     waypointData.holdInput = document.getElementById('holdInput').value;
//     waypointData.gimbalPitch = document.getElementById('gimbalPitchInput').value;
//     waypointData.gimbalYaw = document.getElementById('gimbalYawInput').value;
//     waypointData.heading = document.getElementById('headingInput').value;
//     waypointData.integrationWindow = document.getElementById('integrationWindowInput').value;
//     waypointData.minposeDistance = document.getElementById('minposeDistanceInput').value;
//     waypointData.integration = document.getElementById('integrationButton').getAttribute('data-state');
//     waypointData.anomaly = document.getElementById('anomalyButton').getAttribute('data-state');
// }

ns.m.updateWaypointDataSelectedMarker = (marker) => {
    if (!marker) {
        console.error("No marker selected for updating.");
        // alert("No marker selected for updating.");
        return;
    }

    const waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);

    // Check if waypoint is found; if not, log error and return
    if (!waypoint) {
        console.error("Waypoint for the selected marker not found.");
        // alert("Waypoint for the selected marker not found.");
        return;
    }
    
    const waypointData = waypoint.data;

    waypointData.altitude = document.getElementById('altitudeInput').value || ns.c.defaultAltitude;
    waypointData.speed = document.getElementById('speedInput').value || ns.c.defaultSpeed;
    waypointData.camera = document.getElementById('cameraSelect').value;
    waypointData.holdInput = document.getElementById('holdInput').value || ns.c.DEFAULTHOLDTIME;
    waypointData.gimbalPitch = document.getElementById('gimbalPitchInput').value;
    waypointData.gimbalYaw = document.getElementById('gimbalYawInput').value;
    waypointData.heading = document.getElementById('headingInput').value;
    waypointData.integrationWindow = document.getElementById('integrationWindowInput').value || ns.c.defaultIntegrationWindow;
    waypointData.minposeDistance = document.getElementById('minposeDistanceInput').value || ns.c.defaultMinposeDistance;
    waypointData.integration = document.getElementById('integrationButton').getAttribute('data-state');
    waypointData.anomaly = document.getElementById('anomalyButton').getAttribute('data-state');

    // Log the updated waypoint data to the console
    console.log("Updated Waypoint Data:", waypointData);
};

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
    const anim       = ns.d.droneAnimation.find(d => d.id === id);
    const flowpoints = anim.flowpoints = [];
    const wpElems    = ns.d.wayPointsDrones.filter(w => +w.id === id);
  
    if (wpElems.length === 0) return;
  
    // pull arrays for simpler access
    const latLngs   = wpElems.map(w => w.marker.getLatLng());
    const holdTimes = wpElems.map(w => parseInt(w.data.holdInput) || 0);
    const speeds    = wpElems.map(w => parseFloat(w.data.speed) || ns.c.defaultSpeed);
    const altitudes = wpElems.map(w => Number(w.data.altitude) || ns.c.defaultAltitude);
    const headings  = wpElems.map(w => Number(w.data.heading) || ns.c.defaultHeading);
  
    // precompute segment info
    const segCount = latLngs.length - 1;
    const distances = [], pixels = [], angles = [],
          altDeltas = [], headDeltas = [];
  
    for (let i = 0; i < segCount; i++) {
      distances.push(latLngs[i].distanceTo(latLngs[i+1]));  
      pixels.push(ns.m.calcEuclideanDistance(latLngs[i], latLngs[i+1]));  
      angles.push(ns.m.calculateAngleFromCoordinates(latLngs[i], latLngs[i+1]));
      altDeltas.push(altitudes[i+1] - altitudes[i]);
      headDeltas.push(((headings[i+1] - headings[i] + 540) % 360) - 180);
    }
  
    // build flowpoints
    for (let i = 0; i < segCount; i++) {
      const startGeo   = latLngs[i],
            distMeters = distances[i],
            travelSec  = Math.max(1, Math.ceil(distMeters / speeds[i])),
            pxPerSec   = pixels[i] / travelSec,
            dLat       = latLngs[i+1].lat - startGeo.lat,
            dLng       = latLngs[i+1].lng - startGeo.lng,
            dAlt       = altDeltas[i],
            dHead      = headDeltas[i];
  
      // 1) HOLD at the beginning
      const startPt = ns.map.map.latLngToLayerPoint(startGeo);
      for (let t = 0; t <= holdTimes[i]; t++) {
        flowpoints.push({
          timestep:     flowpoints.length,
          travelPoint:  startPt,
          latlng:       startGeo,
          headingAngle: headings[i],
          altitude:     altitudes[i]
        });
      }
  
      // 2) MOVE in 1‑second steps
      for (let sec = 1; sec < travelSec; sec++) {
        const frac = sec / travelSec;
        const pix  = ns.m.calculateTravelPoint(angles[i], sec * pxPerSec, startGeo);
        const geo  = L.latLng(
          startGeo.lat + frac * dLat,
          startGeo.lng + frac * dLng
        );
        flowpoints.push({
          timestep:     flowpoints.length,
          travelPoint:  pix,
          latlng:       geo,
          headingAngle: headings[i] + frac * dHead,
          altitude:     altitudes[i] + frac * dAlt
        });
      }
  
      // 3) if this is the last segment, push the final waypoint
      if (i === segCount - 1) {
        const endGeo = latLngs[i+1];
        const endPt  = ns.map.map.latLngToLayerPoint(endGeo);
        flowpoints.push({
          timestep:     flowpoints.length,
          travelPoint:  endPt,
          latlng:       endGeo,
          headingAngle: headings[i+1],
          altitude:     altitudes[i+1]
        });
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
                    integrationWindow: wp.data.integrationWindow,
                    minposeDistance: wp.data.minposeDistance,
                    integration: wp.data.integration,
                    anomaly: wp.data.anomaly
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

// Modified retrieveFlightPlanningObject to persist the selected waypoint using a unique key "droneId.index"
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
                integrationWindow: waypointdata['integrationWindow'],
                minposeDistance: waypointdata['minposeDistance'],
                integration: waypointdata['integration'],
                anomaly: waypointdata['anomaly']
            };
            waypoint.timestamp = Date.now();
            
            ns.m.waypointMarkerMethods(waypoint);
            ns.d.wayPointsDrones.push(waypoint);

            // Compute key as "droneId.index"
            let key = `${id}.${pointIndex}`;
            if (ns.d.persistedSelectedKey && key === ns.d.persistedSelectedKey) {
                ns.d.selectedMarker = marker;
                ns.m.updateWaypointInformation(marker);
                ns.m.updateSelectedMarkerDiv();
            }
            pointIndex++;
        });
    }
    // Clear persisted key once selection is restored
    ns.d.persistedSelectedKey = null;
};

// Modified sendDroneDataToApi to store the selected waypoint key before sending
ns.m.sendDroneDataToApi = () => {
    // Persist the selected waypoint key if one is selected
    if (ns.d.selectedMarker) {
        var waypoint = ns.d.wayPointsDrones.find(w => w.marker === ns.d.selectedMarker);
        if (waypoint) {
            let waypointsOfDrone = ns.d.wayPointsDrones.filter(w => w.id === waypoint.id);
            let index = waypointsOfDrone.indexOf(waypoint);
            ns.d.persistedSelectedKey = `${waypoint.id}.${index}`;
        }
    } else {
        ns.d.persistedSelectedKey = null;
    }

    console.log("Before sending, persisted key:", ns.d.persistedSelectedKey);

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
            
            // alert("The project has been submitted and loaded successfully.");
        })

        .catch((error) => {
            console.log(error);
            // alert("An error occurred while sending the data to the server.")
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

// Modified send button: update selected waypoint data before sending.
document.getElementById('sendWaypointsBtn').addEventListener('click', function(e) {
    if(ns.d.selectedMarker){
         ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
    }
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

ns.m.deleteAllWaypointsExceptLast = () => {
    let uniqueDroneIds = [...new Set(ns.d.wayPointsDrones.map(wp => wp.id))];

    uniqueDroneIds.forEach(droneId => {
        let waypointsForDrone = ns.d.wayPointsDrones.filter(wp => wp.id === droneId);

        // If there are multiple waypoints, delete all except the last one
        if (waypointsForDrone.length > 1) {
            waypointsForDrone.slice(0, -1).forEach(waypoint => {
                ns.map.map.removeLayer(waypoint.marker); // Remove marker from the map
                ns.d.wayPointsDrones = ns.d.wayPointsDrones.filter(wp => wp !== waypoint); // Remove from memory
            });
        }

        // Clear associated flowpoints and tooltips for this drone
        let droneAnimation = ns.d.droneAnimation.find(d => d.id === parseInt(droneId));
        if (droneAnimation) {
            droneAnimation.flowpoints = []; // Clear flowpoints
            ns.m.hideTooltip(droneAnimation.tooltip); // Hide tooltip
        }

        // Update the last waypoint's index and icon
        let lastWaypoint = waypointsForDrone[waypointsForDrone.length - 1];
        if (lastWaypoint) {
            lastWaypoint.marker.setIcon(ns.m.createWaypointIcon(`${droneId}.0`, ns.m.getDroneColourCode(droneId)));
        }
    });

    // Recalculate waylines and refresh animations
    ns.m.deleteWaylines();
    if (ns.m.isShowWaylines()) {
        ns.m.calculateWaylines();
    }

    if (ns.m.isShowAnimation()) {
        ns.m.updateDroneAnimation();
    }

    ns.m.updateSelectedMarkerDiv();
};

document.getElementById('removeAllExceptLastBtn').addEventListener('click', function() {
    ns.m.deleteAllWaypointsExceptLast();
});

}(ps3));
    
