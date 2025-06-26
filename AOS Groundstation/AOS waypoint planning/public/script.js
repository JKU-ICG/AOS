var ps3 = {
};

(function (ns) {
    ns.d = {}; // data
    ns.v = {}; // variables 
    ns.m = {}; // methods
    ns.c = {}; // constants
    ns.map = {}; // Leaflet elements
    ns.v.saveImages = 'off';

    // Creating a Layer object
    ns.map.osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxNativeZoom: 19, maxZoom: 25 });
    ns.map.esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxNativeZoom: 19, maxZoom: 25,
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

    ns.map.layerControl = L.control.layers(ns.d.baseMaps, ns.d.overlayMaps, { position: 'bottomleft' }).addTo(ns.map.map);
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
    ns.m.initWayLinesDrones = function () {
        for (let i = 1; i < 11; i++) {
            ns.d.wayLinesDrones.push({ id: i, wayline: null });
        }
    };

    ns.m.initWayLinesDrones();

    ns.v.addMarkerToMap = true;
    ns.v.showAnimation = false; // show animation of drones - toggle state

    ns.c.DRONECOLOURCODES = [
        { id: 1, colour: '#B30F0F' },
        { id: 2, colour: '#013A65' },
        { id: 3, colour: '#A460DC' },
        { id: 4, colour: '#B07ACB' },
        { id: 5, colour: '#EB00A0' },
        { id: 6, colour: '#000000' },
        { id: 7, colour: '#55647E' },
        { id: 8, colour: '#784491' },
        { id: 9, colour: '#2476FF' },
        { id: 10, colour: '#31571B' }
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
    ns.c.defaultWaypointThreshold = 2.0;
    ns.c.WAYPOINT_THRESHOLD = ns.c.defaultWaypointThreshold;

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
        .addEventListener('click', function () {

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
    ns.m.haversineDistance = function (latlng1, latlng2) {
        var R = 6371000; // Earth radius in meters
        var lat1 = latlng1.lat * Math.PI / 180;
        var lat2 = latlng2.lat * Math.PI / 180;
        var dLat = (latlng2.lat - latlng1.lat) * Math.PI / 180;
        var dLon = (latlng2.lng - latlng1.lng) * Math.PI / 180;
        var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    };

    ns.m.calc3DDistance = function (fpA, fpB) {
        if (!fpA?.latlng || !fpB?.latlng) {
            console.error("Missing fp.latlng:", fpA, fpB);
            return Infinity;
        }
        const h = ns.m.haversineDistance(fpA.latlng, fpB.latlng);
        const dz = fpB.altitude - fpA.altitude;
        return Math.sqrt(h * h + dz * dz);
    };

    // Detect collisions, even single‑waypoint drones
    ns.m.detectCollisions3D = function () {
        ns.m.updateDroneAnimation();

        const collisions = [];
        const seen = {};

        // build drones[] with at least one fp.latlng per drone
        const drones = ns.d.droneAnimation.map(drone => {
            let fp = [...drone.flowpoints];
            const wps = ns.d.wayPointsDrones.filter(w => +w.id === drone.id);
            if (fp.length === 0 && wps.length === 1) {
                const geo = wps[0].marker.getLatLng();
                fp = [{ latlng: geo, altitude: +wps[0].data.altitude, timestep: 0 }];
            }
            return { id: drone.id, flowpoints: fp };
        }).filter(d => d.flowpoints.length);

        if (drones.length < 2) return collisions;

        // pad to same length
        const M = Math.max(...drones.map(d => d.flowpoints.length));
        drones.forEach(d => {
            const last = d.flowpoints[d.flowpoints.length - 1];
            for (let t = d.flowpoints.length; t < M; t++) {
                d.flowpoints.push({ ...last, timestep: t });
            }
        });

        // step through time & pairwise
        for (let t = 0; t < M; t++) {
            for (let i = 0; i < drones.length; i++) {
                for (let j = i + 1; j < drones.length; j++) {
                    const key = `${Math.min(drones[i].id, drones[j].id)}-` +
                        `${Math.max(drones[i].id, drones[j].id)}`;
                    if (seen[key]) continue;

                    const A = drones[i].flowpoints[t];
                    const B = drones[j].flowpoints[t];
                    const d = ns.m.calc3DDistance(A, B);
                    if (d <= ns.c.COLLISION_THRESHOLD) {
                        const la = A.latlng, lb = B.latlng;
                        const mid = { lat: (la.lat + lb.lat) / 2, lng: (la.lng + lb.lng) / 2 };
                        collisions.push({
                            time: (A.timestep + B.timestep) / 2,
                            droneA: drones[i].id,
                            droneB: drones[j].id,
                            collisionPoint: mid,
                            distance: d
                        });
                        seen[key] = true;
                    }
                }
            }
        }
        return collisions;
    };

    ns.m.showCollisionMarkers = function (collisions) {
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
                radius: thresholdMeters / 2,
                color: 'red',
                weight: 2,
                fillColor: 'red',
                fillOpacity: 0.4,
            }).addTo(ns.map.map);

            // — little black dot = exact collision point
            const blackDot = L.circleMarker(midLatLng, {
                radius: 3,
                color: 'black',
                fillOpacity: 1,
                weight: 1
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
    document.addEventListener('DOMContentLoaded', function () {
        const integrationButton = document.getElementById('integrationButton');
        const anomalyButton = document.getElementById('anomalyButton');

        const saveImagesSelect = document.getElementById('saveImagesSelect');
        saveImagesSelect.value = ns.v.saveImages;
        saveImagesSelect.addEventListener('change', function () {
            ns.v.saveImages = this.value;
            console.log('Save images flag is now', ns.v.saveImages);
        });

        integrationButton.classList.add('btn-custom-off');
        anomalyButton.classList.add('btn-custom-off');

        integrationButton.addEventListener('click', function () {
            toggleButton(this);
            // landingBtn.classList.replace('btn-secondary', 'btn-success');
            if (this.getAttribute('data-state') === 'on') {
                integrationButton.classList.replace('btn-secondary', 'btn-success');
            } else {
                integrationButton.classList.replace('btn-success', 'btn-secondary');
            }
            if (ns.d.selectedMarker) {
                ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                ns.m.refreshWaypointsAndAnimations();
            }
        });

        // NEW: waypoint threshold listener
        const wpThr = document.getElementById('waypointThresholdInput');
        // start with the default
        wpThr.value = ns.c.WAYPOINT_THRESHOLD.toFixed(1);
        wpThr.addEventListener('input', function () {
            const v = parseFloat(this.value);
            if (!isNaN(v) && v >= 0) {
                ns.c.WAYPOINT_THRESHOLD = v;
                console.log('Waypoint threshold set to', v, 'm');
            }
        });

        anomalyButton.addEventListener('click', function () {
            toggleButton(this);
            if (this.getAttribute('data-state') === 'on') {
                anomalyButton.classList.replace('btn-secondary', 'btn-success');
            } else {
                anomalyButton.classList.replace('btn-success', 'btn-secondary');
            }
            if (ns.d.selectedMarker) {
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
            element.addEventListener('input', function () {
                if (ns.d.selectedMarker) {
                    ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                    ns.m.refreshWaypointsAndAnimations();
                }
            });
            element.addEventListener('change', function () {
                if (ns.d.selectedMarker) {
                    ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
                    ns.m.refreshWaypointsAndAnimations();
                }
            });
        });

        // --- New: Event listener for the collision detection button ---
        const detectCollisionsBtn = document.getElementById('detectCollisionsBtn');
        if (detectCollisionsBtn) {
            detectCollisionsBtn.addEventListener('click', function () {
                var collisions = ns.m.detectCollisions3D();
                console.log("Detected collisions:", collisions);
                ns.m.showCollisionMarkers(collisions);
            });
        }
        // --- End new addition ---
    });

    ns.map.map.on('click', function (e) {
        // If the user is holding Ctrl, bail out (so you can measure instead)
        if (e.originalEvent && e.originalEvent.ctrlKey) {
            return;
        }

        if (e.originalEvent.altKey) return;

        var droneId = document.getElementById('droneSelect').value;
        if (!droneId) {
            alert('No drone selected. Select a drone to add waypoints.');
        } else {
            let pointIndex = ns.d.wayPointsDrones.filter(w => w.id === droneId).length;
            var waypointIcon = ns.m.createWaypointIcon(droneId + '.' + pointIndex, ns.m.getDroneColourCode(droneId));
            var marker = L.marker(e.latlng, { draggable: true, icon: waypointIcon }).addTo(ns.map.map);

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
            // if (ns.m.isShowAnimation()) {
            //     ns.m.updateDroneAnimation();
            // }
            ns.m.updateDroneAnimation();

            ns.m.waypointMarkerMethods(waypoint);
        }
    });
    // Helper function to capitalize first letter (add this if you don't have it already)
    String.prototype.capitalize = function () {
        return this.charAt(0).toUpperCase() + this.slice(1);
    };

    ns.m.waypointMarkerMethods = (waypoint) => {
        waypoint.marker.on('click', function () {
            // Modified: Check if this marker is already selected. If yes, do nothing.
            if (ns.d.selectedMarker === waypoint.marker) {
                return;
            }
            ns.d.selectedMarker = waypoint.marker;
            // waypoint.marker.bindPopup(ns.m.getPopupContentString(waypoint)); // popup for marker
            ns.m.updateSelectedMarkerDiv();
            ns.m.updateWaypointInformation(ns.d.selectedMarker);
        });

        waypoint.marker.on('contextmenu', function () {
            ns.d.selectedMarker = waypoint.marker;
            ns.m.deleteMarker();
            // if (ns.m.isShowAnimation()) {
            //     ns.m.updateDroneAnimation();
            // }
            ns.m.updateDroneAnimation();
        })

        waypoint.marker.on('dragend', function (event) {
            ns.d.selectedMarker = waypoint.marker;
            ns.m.updateSelectedMarkerDiv();
            if (ns.m.isShowWaylines()) {
                ns.m.deleteWaylines();
                ns.m.calculateWaylines();
            };
            ns.m.updateWaypointInformation(waypoint.marker);

            // update DroneAnimation
            // if (ns.m.isShowAnimation()) {
            //     ns.m.updateDroneAnimation();
            // };
            ns.m.updateDroneAnimation();
        });
    };

    ns.m.updateSelectedMarkerDiv = () => {
        if (ns.d.selectedMarker == null) {
            selectedMarkerDiv.innerHTML = 'No waypoint selected.';
            return;
        }

        // try to find it
        const waypoint = ns.d.wayPointsDrones.find(w => w.marker === ns.d.selectedMarker);
        if (!waypoint) {
            // the previously-selected marker has gone away: reset selection
            ns.d.selectedMarker = null;
            selectedMarkerDiv.innerHTML = 'No waypoint selected.';
            return;
        }

        // only now is it safe to do waypoint.id, indexOf, etc.
        const waypointsOfDrone = ns.d.wayPointsDrones.filter(w => w.id === waypoint.id);
        const pointIndex = waypointsOfDrone.indexOf(waypoint);
        selectedMarkerDiv.innerHTML = `Drone-ID: ${waypoint.id}, Waypoint: ${pointIndex}`;
        ns.m.updateDroneAnimation();
    };


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
            let polyline = L.polyline(latlngs, { color: colour }).addTo(ns.map.map);

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

        // Set the selected marker to the clicked waypoint marker
        ns.d.selectedMarker = marker;

        var waypoint = ns.d.wayPointsDrones.find(w => w.marker === marker);

        // Proceed only if waypoint is found
        if (!waypoint) {
            // marker no longer in our list → clear out the details panel
            ns.d.selectedMarker = null;
            selectedMarkerDiv.innerHTML = 'No waypoint selected.';
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

        // if (ns.m.isShowAnimation()) {
        //     ns.m.updateDroneAnimation();
        // }
        ns.m.updateDroneAnimation();
    };

    ns.m.getPopupContentString = (waypointElement) => {
        // return `<div>id: ${waypointElement.id} - ` + waypointElement.marker.getLatLng().toString() + '</div>'
        return `<div>droneId: ${waypointElement.id} <br> altitude: ${waypointElement.data.altitude} <br> speed: ${waypointElement.data.speed} ` + '</div>'
    }

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
            // if (ns.m.isShowAnimation()) {
            //     ns.m.updateDroneAnimation();
            // };
            ns.m.updateDroneAnimation();

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
            // if (ns.m.isShowAnimation()) {
            //     ns.m.updateDroneAnimation();
            // };
            ns.m.updateDroneAnimation();

            if (ns.m.isShowWaylines()) {
                ns.m.calculateWaylines();
            };

            ns.d.selectedMarker = null; // Reset selected marker variable
            ns.m.updateSelectedMarkerDiv();
            ns.m._clearGridForDrone(droneId);

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

        Object.keys(ns.d.grids).forEach(id => ns.m._clearGridForDrone(id));

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
                elem.marker.setIcon(ns.m.createWaypointIcon(`${elem.id}.${pointIndex}`, ns.m.getDroneColourCode(elem.id)));
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
            className: "waypoint-icon",
            iconSize: [ns.c.ICONSIZE, ns.c.ICONSIZE],
            iconAnchor: [ns.c.ICONSIZE / 2, ns.c.ICONSIZE / 2],
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
            className: "drone-icon",
            iconSize: [ns.c.DRONEMARKERSIZE, ns.c.DRONEMARKERSIZE],
            iconAnchor: [ns.c.DRONEMARKERSIZE / 2, ns.c.DRONEMARKERSIZE / 2],
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
        for (let i = 1; i < 11; i++) {
            ns.d.droneAnimation.push({
                id: i,
                flowpoints: [],
                travelMarker: null,
                tooltip: ns.m.createTooltip()
            })
        };
    };

    ns.m.initDroneAnimation();

    ns.m.calculateFlowPoints = () => {
        ns.d.droneAnimation.forEach(elem => {
            ns.m.calculateDroneAnimation(elem.id);
        });
    };

    ns.m.calculateDroneAnimation = (id) => {
        const anim = ns.d.droneAnimation.find(d => d.id === id);
        const flowpoints = anim.flowpoints = [];
        const wpElems = ns.d.wayPointsDrones.filter(w => +w.id === id);

        if (wpElems.length === 0) return;

        // pull arrays for simpler access
        const latLngs = wpElems.map(w => w.marker.getLatLng());
        const holdTimes = wpElems.map(w => parseInt(w.data.holdInput) || 0);
        const speeds = wpElems.map(w => parseFloat(w.data.speed) || ns.c.defaultSpeed);
        const altitudes = wpElems.map(w => Number(w.data.altitude) || ns.c.defaultAltitude);
        const headings = wpElems.map(w => Number(w.data.heading) || ns.c.defaultHeading);

        // precompute segment info
        const segCount = latLngs.length - 1;
        const distances = [], pixels = [], angles = [],
            altDeltas = [], headDeltas = [];

        for (let i = 0; i < segCount; i++) {
            distances.push(latLngs[i].distanceTo(latLngs[i + 1]));
            pixels.push(ns.m.calcEuclideanDistance(latLngs[i], latLngs[i + 1]));
            angles.push(ns.m.calculateAngleFromCoordinates(latLngs[i], latLngs[i + 1]));
            altDeltas.push(altitudes[i + 1] - altitudes[i]);
            headDeltas.push(((headings[i + 1] - headings[i] + 540) % 360) - 180);
        }

        // build flowpoints
        for (let i = 0; i < segCount; i++) {
            const startGeo = latLngs[i],
                distMeters = distances[i],
                travelSec = Math.max(1, Math.ceil(distMeters / speeds[i])),
                pxPerSec = pixels[i] / travelSec,
                dLat = latLngs[i + 1].lat - startGeo.lat,
                dLng = latLngs[i + 1].lng - startGeo.lng,
                dAlt = altDeltas[i],
                dHead = headDeltas[i];

            // 1) HOLD at the beginning
            const startPt = ns.map.map.latLngToLayerPoint(startGeo);
            for (let t = 0; t <= holdTimes[i]; t++) {
                flowpoints.push({
                    timestep: flowpoints.length,
                    travelPoint: startPt,
                    latlng: startGeo,
                    headingAngle: headings[i],
                    altitude: altitudes[i]
                });
            }

            // 2) MOVE in 1‑second steps
            for (let sec = 1; sec < travelSec; sec++) {
                const frac = sec / travelSec;
                const pix = ns.m.calculateTravelPoint(angles[i], sec * pxPerSec, startGeo);
                const geo = L.latLng(
                    startGeo.lat + frac * dLat,
                    startGeo.lng + frac * dLng
                );
                flowpoints.push({
                    timestep: flowpoints.length,
                    travelPoint: pix,
                    latlng: geo,
                    headingAngle: headings[i] + frac * dHead,
                    altitude: altitudes[i] + frac * dAlt
                });
            }

            // 3) if this is the last segment, push the final waypoint
            if (i === segCount - 1) {
                const endGeo = latLngs[i + 1];
                const endPt = ns.map.map.latLngToLayerPoint(endGeo);
                flowpoints.push({
                    timestep: flowpoints.length,
                    travelPoint: endPt,
                    latlng: endGeo,
                    headingAngle: headings[i + 1],
                    altitude: altitudes[i + 1]
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
            var diff = (headingAngles[i + 1] - headingAngles[i] + 180) % 360 - 180;
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
            var diff = altitudes[i + 1] - altitudes[i];
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
                    elem.travelMarker = L.marker(ns.map.map.layerPointToLatLng(elem.flowpoints[elem.flowpoints.length - 1]["travelPoint"]), { icon: droneIcon, zIndexOffset: 1500 });
                    elem.travelMarker.setRotationAngle(elem.flowpoints[elem.flowpoints.length - 1]["headingAngle"]);
                    ns.m.setTooltipContent(elem.tooltip, elem.flowpoints[elem.flowpoints.length - 1]);
                    ns.m.setTooltipPosition(elem.tooltip, elem.travelMarker);
                    ns.m.showTooltip(elem.tooltip);
                    elem.travelMarker.addTo(ns.map.map);
                } else {
                    elem.travelMarker = L.marker(ns.map.map.layerPointToLatLng(elem.flowpoints[timestep]["travelPoint"]), { icon: droneIcon, zIndexOffset: 1500 });
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

        return Math.atan2(y, x);
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

    // ns.m.isShowAnimation = () => {
    //     return document.getElementById('showAnimation').value === 'show';
    // }

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
                        lat: latlng.lat,
                        lng: latlng.lng,
                        speed: wp.data.speed,
                        lengthOfStay: wp.data.holdInput,
                        altitude: wp.data.altitude,
                        camera: wp.data.camera,
                        gimbalPitch: wp.data.gimbalPitch,
                        gimbalYaw: wp.data.gimbalYaw,
                        heading: wp.data.heading,
                        integrationWindow: wp.data.integrationWindow,
                        minposeDistance: wp.data.minposeDistance,
                        integration: wp.data.integration,
                        anomaly: wp.data.anomaly
                    }
                );
            });
        });

        // if waypoint data is empty, do not send saveImages
        if (Object.keys(flightPlanning).length === 0) {
            return flightPlanning;
        }
        // if waypoint data is not empty, send saveImages
        else {
            flightPlanning.saveImages = ns.v.saveImages;
            flightPlanning.waypointThreshold = ns.c.WAYPOINT_THRESHOLD;
            return flightPlanning;
        }
    }

    // Modified retrieveFlightPlanningObject to persist the selected waypoint using a unique key "droneId.index"
    ns.m.retrieveFlightPlanningObject = (data) => {
        ns.d.selectedMarker = null;
        ns.d.wayPointsDrones = [];

        // remove the saveImages information from the data object
        delete data.saveImages;
        delete data.waypointThreshold;

        for (var id in data) {
            var waypoints = data[id];
            var pointIndex = 0;
            waypoints.forEach((waypointdata) => {
                // icon
                var waypointIcon = ns.m.createWaypointIcon(id + '.' + pointIndex, ns.m.getDroneColourCode(id));

                // marker
                var lat = waypointdata['lat'];
                var lng = waypointdata['lng'];

                var latlng = L.latLng([lat, lng]);
                var marker = L.marker(latlng, { draggable: true, icon: waypointIcon }).addTo(ns.map.map);

                var waypoint = {};
                waypoint.id = id;

                console.log(waypoint.id, typeof (waypoint.id));

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
                // if (ns.m.isShowAnimation()) {
                //     ns.m.updateDroneAnimation();
                // };
                ns.m.updateDroneAnimation();
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

    document.getElementById('showWaylines').addEventListener('click', function () {
        var button = document.getElementById('showWaylines');
        if (ns.m.isShowWaylines()) {
            ns.m.deleteWaylines();
            button.value = 'hide';
            button.innerHTML = 'Show Segments'
        } else {
            ns.m.calculateWaylines();
            button.value = 'show';
            button.innerHTML = 'Hide Segments';
        }
    })

    document.getElementById('removeMarkerBtn').addEventListener('click', function () {
        ns.m.deleteMarker();
    });

    document.getElementById('removeAllMarkerOfDroneIdBtn').addEventListener('click', function () {
        ns.m.deleteAllMarkerOfDroneId();
    });

    document.getElementById('removeAllMarkerBtn').addEventListener('click', function () {
        ns.m.deleteAllMarker();
        ns.m.deleteWaylines();
    });

    document.getElementById('droneAnimationSlider').addEventListener('input', function (e) {
        ns.m.removeAllTravelMarkers();
        ns.m.showTravelPointAtTimestep(e.target.value);
    });

    // document.getElementById('showAnimation').addEventListener('click', function() {
    //     var button = document.getElementById('showAnimation');
    //     var sliderContainer = document.getElementById('rangeSliderDiv');
    //     if (ns.m.isShowAnimation()) {
    //         ns.m.removeAllTravelMarkers();
    //         ns.m.hideAllTooltips();
    //         button.value = 'hide';
    //         sliderContainer.style.display = "none";
    //         button.innerHTML = 'Show animation'
    //     } else {
    //         ns.m.updateDroneAnimation();
    //         ns.m.showAllTooltips();
    //         sliderContainer.style.display = "block";
    //         button.value = 'show';
    //         button.innerHTML = 'Hide animation';
    //     }
    // });

    // Modified send button: update selected waypoint data before sending.
    document.getElementById('sendWaypointsBtn').addEventListener('click', function (e) {
        if (ns.d.selectedMarker) {
            ns.m.updateWaypointDataSelectedMarker(ns.d.selectedMarker);
        }
        e.preventDefault();
        e.stopPropagation();

        ns.m.sendDroneDataToApi();
    });

    // map events
    ns.map.map.on('dragend', function () {
        // if (ns.m.isShowAnimation()) {
        //     ns.m.updateDroneAnimation();
        // };
        ns.m.updateDroneAnimation();
    });

    ns.map.map.on('zoomend', function () {
        // if (ns.m.isShowAnimation()) {
        //     ns.m.updateDroneAnimation();
        // };
        ns.m.updateDroneAnimation();
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
        // uniqueDroneIds.forEach(id => ns.m._clearGridForDrone(id));
        // if (ns.m.isShowAnimation()) {
        //     ns.m.updateDroneAnimation();
        // }
        ns.m.updateDroneAnimation();

        ns.m.updateSelectedMarkerDiv();
    };

    document.getElementById('removeAllExceptLastBtn').addEventListener('click', function () {
        ns.m.deleteAllWaypointsExceptLast();
    });

    // ------------------------------
    // Grid Waypoints 
    // ------------------------------

    // per-drone grid state
    ns.d.grids = {};

    ns.m._updateGridInputs = function (droneId) {
        const G = ns.d.grids[droneId];
        if (!G || !G.rectangle) return;

        // reuse stored metre dimensions (unchanged by rotate/move)
        const widthM = G.widthM.toFixed(3),
            heightM = G.heightM.toFixed(3);

        document.getElementById('gridWidthInput').value = widthM;
        document.getElementById('gridHeightInput').value = heightM;
        // center
        const centerLL = ns.map.map.options.crs.unproject(G.centerProj);
        document.getElementById('gridLatInput').value = centerLL.lat.toFixed(10);
        document.getElementById('gridLngInput').value = centerLL.lng.toFixed(10);


        // refresh sidebar if selected WP moved
        if (ns.d.selectedMarker) {
            ns.m.updateWaypointInformation(ns.d.selectedMarker);
            ns.m.updateSelectedMarkerDiv();
        }
    };

    // 1) Init Draw, Rotate, Toggle & Resize controls
    ns.m.initGridControls = function () {
        // Draw
        document.getElementById('drawGridBtn').addEventListener('click', () => {
            const id = document.getElementById('droneSelect').value;
            if (!id) return alert('Select a drone first.');
            if (!ns.map.gridDrawControl) {
                ns.map.gridDrawControl = new L.Draw.Rectangle(ns.map.map, {
                    shapeOptions: {
                        color: ns.m.getDroneColourCode(id),
                        weight: 2,
                        fillOpacity: 0.1
                    }
                });
                ns.map.map.on(L.Draw.Event.CREATED, ns.m.onGridRectangleCreated);
            }
            ns.map.gridDrawControl.enable();
        });

        // NEW: Auto-draw Grid button
        document.getElementById('drawGridAutoBtn').addEventListener('click', () => {
            const id = document.getElementById('droneSelect').value;
            if (!id) return alert('Select a drone first.');

            // parse inputs
            const lat = parseFloat(document.getElementById('gridLatInput').value);
            const lng = parseFloat(document.getElementById('gridLngInput').value);
            const widthM = parseFloat(document.getElementById('gridWidthInput').value);
            const heightM = parseFloat(document.getElementById('gridHeightInput').value);
            if ([lat, lng, widthM, heightM].some(v => isNaN(v) || v <= 0)) {
                return alert('Please enter valid, positive numbers for lat, lng, width and height.');
            }

            // compute SW and NE corners geodesically
            const center = turf.point([lng, lat]);
            const halfH = heightM / 2;
            const halfW = widthM / 2;
            const south = turf.destination(center, halfH, 180, { units: 'meters' });
            const swGeo = turf.destination(south, halfW, 270, { units: 'meters' });
            const north = turf.destination(center, halfH, 0, { units: 'meters' });
            const neGeo = turf.destination(north, halfW, 90, { units: 'meters' });

            const swLL = L.latLng(swGeo.geometry.coordinates[1], swGeo.geometry.coordinates[0]);
            const neLL = L.latLng(neGeo.geometry.coordinates[1], neGeo.geometry.coordinates[0]);
            const bounds = L.latLngBounds(swLL, neLL);

            // delegate to helper
            ns.m._createGridFromBounds(id, bounds);
        });

        // Live‐update grid whenever centre/size inputs change
        const onGridParamsChange = () => {
            const id = document.getElementById('droneSelect').value;
            if (!id) return;
            const G = ns.d.grids[id];
            if (!G || !G.rectangle) return;   // only if a grid is already drawn

            ns.m.updateGridFromInputs(id);
        };

        ['gridLatInput', 'gridLngInput', 'gridWidthInput', 'gridHeightInput']
            .forEach(elId => {
                document.getElementById(elId)
                    .addEventListener('input', onGridParamsChange);
            });

        // Auto-rotate on angle change
        document.getElementById('gridRotationInput').addEventListener('input', () => {
            const idField = document.getElementById('droneSelect');
            const id = idField.value;
            let angle = parseFloat(document.getElementById('gridRotationInput').value);

            if (!id || isNaN(angle)) return;

            // wrap into [0,360):
            angle = ((angle % 360) + 360) % 360;

            // put the wrapped value back into the field
            document.getElementById('gridRotationInput').value = angle;

            // apply rotation & update the UI
            ns.m.rotateLastGrid(id, angle);
            ns.m._updateGridInputs(id);
        });


        // Dynamic X/Y spacing inputs
        const onSpacingChange = () => {
            const id = document.getElementById('droneSelect').value;
            if (!id) return;
            const G = ns.d.grids[id];
            if (!G || !G.origCorners) return;
            G.spacingX = parseFloat(document.getElementById('gridSpacingXInput').value);
            G.spacingY = parseFloat(document.getElementById('gridSpacingYInput').value);
            ns.m.generateGridWaypoints(id);
        };
        document.getElementById('gridSpacingXInput').addEventListener('input', onSpacingChange);
        document.getElementById('gridSpacingYInput').addEventListener('input', onSpacingChange);

        // When drone changes, update spacing & angle inputs and toggle button
        document.getElementById('droneSelect').addEventListener('change', () => {
            const id = document.getElementById('droneSelect').value;
            const G = ns.d.grids[id] || {};
            document.getElementById('gridSpacingXInput').value = G.spacingX || '3.0';
            document.getElementById('gridSpacingYInput').value = G.spacingY || '3.0';
            document.getElementById('gridRotationInput').value = G.currentAngle || 0;
            ns.m.updateToggleButtonState();
        });

        // Toggle Grid Visibility Button
        if (!ns.map.toggleGridControl) {
            ns.map.toggleGridControl = L.control({ position: 'bottomright' });
            ns.map.toggleGridControl.onAdd = map => {
                const btn = L.DomUtil.create('button', 'btn-toggle-grid');
                btn.id = 'toggleGridBtn';
                Object.assign(btn.style, {
                    background: 'white',
                    padding: '4px 8px',
                    cursor: 'pointer',
                    font: '14px sans-serif'
                });
                L.DomEvent.disableClickPropagation(btn);
                btn.addEventListener('click', ns.m.toggleGridVisibility);
                return btn;
            };
            ns.map.toggleGridControl.addTo(ns.map.map);
        }

        // Initialize button state
        ns.m.updateToggleButtonState();
    };

    // Helper: refresh toggle-button
    ns.m.updateToggleButtonState = function () {
        const btn = document.getElementById('toggleGridBtn');
        const id = document.getElementById('droneSelect').value;
        const G = ns.d.grids[id];
        if (!btn) return;
        if (!id || !G || !G.rectangle) {
            btn.style.display = 'none';
        } else {
            btn.style.display = '';
            btn.innerHTML = G.visible
                ? `Hide Grid (${id})`
                : `Show Grid (${id})`;
        }
    };

    // 2) Show/hide handler
    ns.m.toggleGridVisibility = function () {
        const id = document.getElementById('droneSelect').value;
        if (!id) return alert('Select a drone first.');
        const G = ns.d.grids[id];
        if (!G || !G.rectangle) return alert('No grid drawn for that drone.');

        if (G.visible) {
            ns.map.map.removeLayer(G.rectangle);
            ns.map.map.removeLayer(G.centerMarker);
            ns.map.map.removeLayer(G.labelMarker);
            (G.handles || []).forEach(h => ns.map.map.removeLayer(h));
            G.visible = false;
        } else {
            G.rectangle.addTo(ns.map.map);
            G.centerMarker.addTo(ns.map.map);
            G.labelMarker.addTo(ns.map.map);
            (G.handles || []).forEach(h => h.addTo(ns.map.map));
            G.visible = true;
        }
        ns.m.updateToggleButtonState();
    };

    // 3) Rectangle creation
    ns.m.onGridRectangleCreated = function (e) {
        const map = ns.map.map,
            crs = map.options.crs,
            id = document.getElementById('droneSelect').value,
            bounds = e.layer.getBounds();

        if (!ns.d.grids[id]) ns.d.grids[id] = {};
        const G = ns.d.grids[id];

        // remove old
        [G.rectangle, G.centerMarker, G.labelMarker].forEach(l => l && map.removeLayer(l));
        (G.handles || []).forEach(h => map.removeLayer(h));
        (G.lastWaypoints || []).forEach(wp => map.removeLayer(wp.marker));

        // draw new rectangle
        G.rectangle = L.rectangle(bounds, {
            color: ns.m.getDroneColourCode(id),
            weight: 2,
            fillOpacity: 0.1
        }).addTo(map);

        L.DomEvent.disableClickPropagation(G.rectangle.getElement());

        // compute dims
        const sw = bounds.getSouthWest(),
            ne = bounds.getNorthEast();
        G.widthM = sw.distanceTo(L.latLng(sw.lat, ne.lng));
        G.heightM = sw.distanceTo(L.latLng(ne.lat, sw.lng));

        // store corners for rotation/resizing
        const ring = G.rectangle.getLatLngs()[0].slice(0, 4);
        G.origCorners = ring.map(ll => crs.project(ll));
        const centerLL = bounds.getCenter();
        G.centerProj = crs.project(centerLL);
        G.currentAngle = 0;

        // save initial X/Y spacings
        G.spacingX = parseFloat(document.getElementById('gridSpacingXInput').value) || G.spacingX;
        G.spacingY = parseFloat(document.getElementById('gridSpacingYInput').value) || G.spacingY;

        // center pin and label
        G.centerMarker = L.marker(centerLL, { title: 'Grid Center' }).addTo(map);
        const NW = ring[1], NEpt = ring[2];
        const mid = L.latLng((NW.lat + NEpt.lat) / 2, (NW.lng + NEpt.lng) / 2);
        const labelPt = map.latLngToLayerPoint(mid);
        const labelLL = map.layerPointToLatLng([labelPt.x, labelPt.y - 10]);
        const edgeDeg = ns.m.calculateAngleFromCoordinates(NW, NEpt) * 180 / Math.PI;
        G.labelMarker = L.marker(labelLL, {
            interactive: false,
            icon: L.divIcon({
                className: 'dimension-label',
                html: `<div style="transform:rotate(${edgeDeg}deg);white-space:nowrap;">
                        ${G.heightM.toFixed(3)} m × ${G.widthM.toFixed(3)} m
                    </div>`
            })
        }).addTo(map);

        const manual = ns.d.wayPointsDrones.filter(
            wp => wp.id === id && !wp._isGrid
        );
        ns.d.grids[id].anchorWp = manual.length
            ? manual[manual.length - 1]
            : null;

        // build & stash grid waypoints
        G.lastWaypoints = ns.m.generateGridWaypoints(id);

        // allow Alt-drag & corner handles
        ns.m._bindGridDrag(id);
        ns.m.addGridResizeHandles(id);

        // mark visible
        G.visible = true;
        ns.m.updateToggleButtonState();

        // disable draw tool
        ns.map.gridDrawControl.disable();
        // update grid inputs
        ns.m._updateGridInputs(id);
    };

    // 4) Generate grid waypoints (using Turf for true-metre spacing)
    ns.m.generateGridWaypoints = function (droneId) {
        const map = ns.map.map,
            crs = map.options.crs,
            G = ns.d.grids[droneId];

        // 1) Validate spacings
        const sx = G.spacingX, sy = G.spacingY;
        if (sx < 0 || sy < 0) {
            alert('Enter non-negative X and Y spacings.');
            return [];
        }
        if (sx === 0 && sy === 0) {
            alert('At least one spacing must be > 0.');
            return [];
        }

        // 2) Build projected grid axes from stored corners
        const [Psw, Pnw, Pne, Pse] = G.origCorners;
        const u = L.point(Pse.x - Psw.x, Pse.y - Psw.y),
            v = L.point(Pnw.x - Psw.x, Pnw.y - Psw.y);

        const wProj = Math.hypot(u.x, u.y),
            hProj = Math.hypot(v.x, v.y),
            wGeo = G.widthM,
            hGeo = G.heightM;

        const cols = sx > 0 ? Math.floor(wGeo / sx) + 1 : 1,
            rows = sy > 0 ? Math.floor(hGeo / sy) + 1 : 1;

        const uUnit = L.point(u.x / wProj, u.y / wProj),
            vUnit = L.point(v.x / hProj, v.y / hProj);

        const spacingProjU = sx > 0 ? sx * (wProj / wGeo) : 0,
            spacingProjV = sy > 0 ? sy * (hProj / hGeo) : 0;

        // 3) Generate “snake” pattern of LatLngs
        const latlngs = [];
        for (let i = 0; i < rows; i++) {
            const row = [];
            for (let j = 0; j < cols; j++) {
                const Px = Psw.x + uUnit.x * (j * spacingProjU) + vUnit.x * (i * spacingProjV),
                    Py = Psw.y + uUnit.y * (j * spacingProjU) + vUnit.y * (i * spacingProjV);
                row.push(crs.unproject(L.point(Px, Py)));
            }
            if (i % 2) row.reverse();
            latlngs.push(...row);
        }

        // === A) Remove only the old grid waypoints ===
        (G.lastWaypoints || []).forEach(wp => map.removeLayer(wp.marker));
        ns.d.wayPointsDrones = ns.d.wayPointsDrones.filter(
            wp => !(wp.id === droneId && wp._isGrid)
        );

        // === B) Create & tag new grid waypoints ===
        const newGrid = [];
        latlngs.forEach(ll => {
            const idx = ns.d.wayPointsDrones.filter(w => w.id === droneId).length;
            const icon = ns.m.createWaypointIcon(`${droneId}.${idx}`, ns.m.getDroneColourCode(droneId));
            const mk = L.marker(ll, { draggable: true, icon }).addTo(map);

            const wp = {
                id: droneId,
                marker: mk,
                wayline: null,
                timestamp: Date.now(),
                _origProj: crs.project(ll),
                _isGrid: true,
                data: {
                    lat: ll.lat,
                    lng: ll.lng,
                    altitude: parseFloat(document.getElementById('altitudeInput').value) || ns.c.defaultAltitude,
                    speed: parseFloat(document.getElementById('speedInput').value) || ns.c.defaultSpeed,
                    camera: document.getElementById('cameraSelect').value || '',
                    holdInput: parseFloat(document.getElementById('holdInput').value) || ns.c.DEFAULTHOLDTIME,
                    gimbalPitch: parseFloat(document.getElementById('gimbalPitchInput').value) || 0,
                    gimbalYaw: parseFloat(document.getElementById('gimbalYawInput').value) || 0,
                    heading: parseFloat(document.getElementById('headingInput').value) || ns.c.defaultHeading,
                    integrationWindow: parseInt(document.getElementById('integrationWindowInput').value, 10) || ns.c.defaultIntegrationWindow,
                    minposeDistance: parseFloat(document.getElementById('minposeDistanceInput').value) || ns.c.defaultMinposeDistance,
                    integration: document.getElementById('integrationButton').getAttribute('data-state') || 'off',
                    anomaly: document.getElementById('anomalyButton').getAttribute('data-state') || 'off'
                }
            };

            ns.d.wayPointsDrones.push(wp);
            ns.m.waypointMarkerMethods(wp);
            newGrid.push(wp);
            mk.on('click', () => {
                document.getElementById('droneSelect').value = droneId;
                ns.m.updateToggleButtonState();
            });
        });

        // === C) Temporarily pull them off the tail ===
        ns.d.wayPointsDrones.splice(-newGrid.length, newGrid.length);

        // === D) Insert new grid right after the fixed anchor ===
        let insertAt;
        if (G.anchorWp) {
            insertAt = ns.d.wayPointsDrones.indexOf(G.anchorWp) + 1;
        } else {
            // if no anchor, front of this drone’s block
            const firstManual = ns.d.wayPointsDrones.findIndex(wp => wp.id === droneId);
            insertAt = firstManual >= 0 ? firstManual : ns.d.wayPointsDrones.length;
        }
        ns.d.wayPointsDrones.splice(insertAt, 0, ...newGrid);

        // === E) Renumber all waypoints & refresh ===
        ns.m.reorderAllWaypoints();
        ns.m.deleteWaylines();
        ns.m.calculateWaylines();
        ns.m.updateDroneAnimation();

        // === F) Store & return ===
        G.lastWaypoints = newGrid;
        return newGrid;
    };

    // Regenerate existing grid for a given drone
    ns.m.regenerateGrid = function (droneId) {
        const map = ns.map.map;
        const G = ns.d.grids[droneId];
        if (!G || !G.origCorners) return;

        // 1) remove old markers from map & from global array
        (G.lastWaypoints || []).forEach(wp => {
            map.removeLayer(wp.marker);
            const i = ns.d.wayPointsDrones.indexOf(wp);
            if (i > -1) ns.d.wayPointsDrones.splice(i, 1);
        });

        // 2) rebuild bounds from *rotated* corners
        const llCorners = G.origCorners.map(pt => map.options.crs.unproject(pt));
        const bounds = L.latLngBounds(llCorners);

        // 3) generate new waypoints (same count, same orientation)
        G.lastWaypoints = ns.m.generateGridWaypoints(bounds, droneId);
    };

    // 5) Absolute rotation (angleDeg)
    ns.m.rotateLastGrid = function (droneId, angleDeg) {
        const map = ns.map.map,
            crs = map.options.crs,
            G = ns.d.grids[droneId];
        if (!G || !G.rectangle) return alert('Draw a grid first.');

        const delta = angleDeg - (G.currentAngle || 0);
        if (delta === 0) return;
        const θ = -delta * Math.PI / 180,
            C = G.centerProj;

        G.origCorners = G.origCorners.map(P => {
            const dx = P.x - C.x, dy = P.y - C.y;
            return L.point(
                C.x + dx * Math.cos(θ) - dy * Math.sin(θ),
                C.y + dx * Math.sin(θ) + dy * Math.cos(θ)
            );
        });

        // rebuild rectangle
        map.removeLayer(G.rectangle);
        const newLL = G.origCorners.map(pt => crs.unproject(pt));
        G.rectangle = L.polygon(newLL, { color: ns.m.getDroneColourCode(droneId), weight: 2, fillOpacity: 0.1 });
        if (G.visible) G.rectangle.addTo(map);

        // rebuild center
        map.removeLayer(G.centerMarker);
        const centerLL = L.latLngBounds(newLL).getCenter();
        G.centerMarker = L.marker(centerLL, { title: 'Grid Center' });
        if (G.visible) G.centerMarker.addTo(map);
        G.centerProj = crs.project(centerLL);

        // rebuild label
        map.removeLayer(G.labelMarker);
        const NW = newLL[1], NE = newLL[2];
        const mid = L.latLng((NW.lat + NE.lat) / 2, (NW.lng + NE.lng) / 2);
        const midPt = map.latLngToLayerPoint(mid);
        const labelLL = map.layerPointToLatLng([midPt.x, midPt.y - 10]);
        const edgeDeg = ns.m.calculateAngleFromCoordinates(NW, NE) * 180 / Math.PI;
        G.labelMarker = L.marker(labelLL, {
            interactive: false,
            icon: L.divIcon({
                className: 'dimension-label',
                html: `<div style="transform:rotate(${edgeDeg}deg); white-space:nowrap;">
                    ${G.heightM.toFixed(3)} m × ${G.widthM.toFixed(3)} m
                    </div>`
            })
        });
        if (G.visible) G.labelMarker.addTo(map);

        // rotate waypoints
        G.lastWaypoints.forEach(wp => {
            const P = wp._origProj,
                dx = P.x - C.x, dy = P.y - C.y,
                P2 = L.point(
                    C.x + dx * Math.cos(θ) - dy * Math.sin(θ),
                    C.y + dx * Math.sin(θ) + dy * Math.cos(θ)
                );
            wp._origProj = P2;
            const ll2 = crs.unproject(P2);
            wp.marker.setLatLng(ll2);
            wp.data.lat = ll2.lat; wp.data.lng = ll2.lng;
        });

        // rebind drag & handles
        ns.m._bindGridDrag(droneId);
        ns.m.addGridResizeHandles(droneId);

        G.currentAngle = angleDeg;

        if (ns.m.isShowWaylines()) { ns.m.deleteWaylines(); ns.m.calculateWaylines(); }
        // if (ns.m.isShowAnimation()) ns.m.updateDroneAnimation();
        ns.m.updateDroneAnimation();

        ns.m.updateToggleButtonState();

        // refresh sidebar if needed
        if (ns.d.selectedMarker) {
            ns.m.updateWaypointInformation(ns.d.selectedMarker);
            ns.m.updateSelectedMarkerDiv();
        }

        ns.m._updateGridInputs(droneId);
    };

    // 6) Alt-drag binding
    ns.m._bindGridDrag = function (droneId) {
        const map = ns.map.map,
            G = ns.d.grids[droneId];
        const grab = evt => {
            if (!evt.originalEvent.altKey) return;
            map.dragging.disable();
            G.lastWaypoints.forEach(wp => wp.marker.dragging.disable());
            let lastLL = evt.latlng;
            const onMove = mv => {
                ns.m.moveGrid(droneId,
                    mv.latlng.lat - lastLL.lat,
                    mv.latlng.lng - lastLL.lng
                );
                lastLL = mv.latlng;
            };
            const onUp = () => {
                map.off('mousemove', onMove);
                map.off('mouseup', onUp);
                map.dragging.enable();
                G.lastWaypoints.forEach(wp => wp.marker.dragging.enable());
                // after move, reset handles
                ns.m.addGridResizeHandles(droneId);
            };
            map.on('mousemove', onMove);
            map.on('mouseup', onUp);
        };
        G.rectangle.off('mousedown').on('mousedown', grab);
        G.lastWaypoints.forEach(wp => {
            wp.marker.off('mousedown').on('mousedown', grab);
        });
    };

    // 7) Move grid + waypoints
    ns.m.moveGrid = function (droneId, dLat, dLng) {
        const map = ns.map.map,
            crs = map.options.crs,
            G = ns.d.grids[droneId];
        if (!G) return;

        // shift polygon
        const pts = G.rectangle.getLatLngs()[0]
            .map(pt => L.latLng(pt.lat + dLat, pt.lng + dLng));
        G.rectangle.setLatLngs([pts]);

        // shift center & label
        [G.centerMarker, G.labelMarker].forEach(mk => {
            const ll = mk.getLatLng();
            mk.setLatLng([ll.lat + dLat, ll.lng + dLng]);
        });

        // shift waypoints
        G.lastWaypoints.forEach(wp => {
            const ll = wp.marker.getLatLng();
            wp.marker.setLatLng([ll.lat + dLat, ll.lng + dLng]);
            wp.data.lat = ll.lat + dLat;
            wp.data.lng = ll.lng + dLng;
        });

        // recapture base for rotate/resize
        const newBounds = G.rectangle.getBounds(),
            newCenter = newBounds.getCenter(),
            ring = G.rectangle.getLatLngs()[0].slice(0, 4);

        G.centerProj = crs.project(newCenter);
        G.origCorners = ring.map(ll => crs.project(ll));
        G.lastWaypoints.forEach(wp => {
            wp._origProj = crs.project(wp.marker.getLatLng());
        });

        if (ns.m.isShowWaylines()) { ns.m.deleteWaylines(); ns.m.calculateWaylines(); }
        // if (ns.m.isShowAnimation()) ns.m.updateDroneAnimation();
        ns.m.updateDroneAnimation();

        // refresh handles
        ns.m.addGridResizeHandles(droneId);

        // refresh sidebar if needed
        if (ns.d.selectedMarker) {
            const moved = G.lastWaypoints.find(wp => wp.marker === ns.d.selectedMarker);
            if (moved) {
                ns.m.updateWaypointInformation(ns.d.selectedMarker);
                ns.m.updateSelectedMarkerDiv();
            }
        }

        ns.m._updateGridInputs(droneId);
    };

    // 8) Add corner handles for resizing
    ns.m.addGridResizeHandles = function (droneId) {
        const G = ns.d.grids[droneId], map = ns.map.map;
        if (!G || !G.rectangle) return;
        // remove old
        (G.handles || []).forEach(h => map.removeLayer(h));
        G.handles = [];
        // corners: SW, NW, NE, SE
        const cornersLL = G.rectangle.getLatLngs()[0].slice(0, 4);
        cornersLL.forEach((ll, idx) => {
            const handle = L.marker(ll, {
                draggable: true,
                icon: L.divIcon({
                    className: 'grid-corner-handle',
                    iconSize: [8, 8],
                    html: ''
                }),
                zIndexOffset: 1000
            }).addTo(map);

            const el = handle.getElement();
            if (el) {
                L.DomEvent.disableClickPropagation(el);
                L.DomEvent.disableScrollPropagation(el);
            }
            handle.on('drag', e => ns.m.resizeGridCorner(droneId, idx, e.target.getLatLng()));
            G.handles.push(handle);
        });
    };

    // 9) Corner-drag resizing
    ns.m.resizeGridCorner = function (droneId, cornerIdx, newLL) {
        const map = ns.map.map,
            crs = map.options.crs,
            G = ns.d.grids[droneId];
        if (!G || !G.origCorners) return;

        // Center in projected coords
        const C = G.centerProj;

        // 1) Compute new origCorners based on dragged corner
        const [Psw, Pnw, Pne, Pse] = G.origCorners;
        const u = L.point(Pse.x - Psw.x, Pse.y - Psw.y),
            v = L.point(Pnw.x - Psw.x, Pnw.y - Psw.y),
            h2 = Math.hypot(v.x, v.y) / 2,
            w2 = Math.hypot(u.x, u.y) / 2,
            uUnit = L.point(u.x / (2 * w2), u.y / (2 * w2)),
            vUnit = L.point(v.x / (2 * h2), v.y / (2 * h2)),
            Pn = crs.project(newLL),
            dP = L.point(Pn.x - C.x, Pn.y - C.y);

        // project displacement onto axes
        let w2n = dP.x * uUnit.x + dP.y * uUnit.y,
            h2n = dP.x * vUnit.x + dP.y * vUnit.y;

        // enforce correct quadrant for each corner
        const sign = [{ w: -1, h: -1 }, { w: -1, h: 1 }, { w: 1, h: 1 }, { w: 1, h: -1 }][cornerIdx];
        w2n = Math.abs(w2n) * sign.w;
        h2n = Math.abs(h2n) * sign.h;

        // rebuild projected corners
        G.origCorners = [
            L.point(C.x - uUnit.x * w2n - vUnit.x * h2n, C.y - uUnit.y * w2n - vUnit.y * h2n),
            L.point(C.x - uUnit.x * w2n + vUnit.x * h2n, C.y - uUnit.y * w2n + vUnit.y * h2n),
            L.point(C.x + uUnit.x * w2n + vUnit.x * h2n, C.y + uUnit.y * w2n + vUnit.y * h2n),
            L.point(C.x + uUnit.x * w2n - vUnit.x * h2n, C.y + uUnit.y * w2n - vUnit.y * h2n)
        ];

        // 2) Unproject to lat/lng and update dims
        const newLLs = G.origCorners.map(pt => crs.unproject(pt));
        G.widthM = newLLs[0].distanceTo(newLLs[3]);
        G.heightM = newLLs[0].distanceTo(newLLs[1]);

        // 3) Update rectangle, center marker & label
        G.rectangle.setLatLngs([newLLs]);
        const centerLL = crs.unproject(C);
        G.centerMarker.setLatLng(centerLL);

        const NW = newLLs[1], NE = newLLs[2];
        const mid = L.latLng((NW.lat + NE.lat) / 2, (NW.lng + NE.lng) / 2);
        const midPt = map.latLngToLayerPoint(mid);
        const labelLL = map.layerPointToLatLng([midPt.x, midPt.y - 10]);
        const edgeDeg = ns.m.calculateAngleFromCoordinates(NW, NE) * 180 / Math.PI;
        G.labelMarker.setLatLng(labelLL);
        G.labelMarker.setIcon(L.divIcon({
            className: 'dimension-label',
            html: `<div style="transform:rotate(${edgeDeg}deg);white-space:nowrap;">
                    ${G.heightM.toFixed(3)} m x ${G.widthM.toFixed(3)} m
                </div>`
        }));

        // 4) Move corner handles
        (G.handles || []).forEach((h, i) => h.setLatLng(newLLs[i]));

        // 5) Remove old waypoints (map + array)
        (G.lastWaypoints || []).forEach(wp => {
            map.removeLayer(wp.marker);
            const idx = ns.d.wayPointsDrones.indexOf(wp);
            if (idx > -1) ns.d.wayPointsDrones.splice(idx, 1);
        });

        // 6) Regenerate grid waypoints inside the rotated/resized rectangle
        G.lastWaypoints = ns.m.generateGridWaypoints(droneId);

        // 7) Refresh waylines & animation
        if (ns.m.isShowWaylines()) { ns.m.deleteWaylines(); ns.m.calculateWaylines(); }
        // if (ns.m.isShowAnimation()) ns.m.updateDroneAnimation();
        ns.m.updateDroneAnimation();
        ns.m._updateGridInputs(droneId);
    };

    // 10) Helper: programmatic rectangle + grid creation
    ns.m._createGridFromBounds = function (droneId, bounds) {
        const map = ns.map.map,
            crs = map.options.crs;

        // Ensure we have a grid state object
        if (!ns.d.grids[droneId]) ns.d.grids[droneId] = {};
        const G = ns.d.grids[droneId];

        // --- remove old layers ---
        [G.rectangle, G.centerMarker, G.labelMarker].forEach(l => l && map.removeLayer(l));
        (G.handles || []).forEach(h => map.removeLayer(h));
        (G.lastWaypoints || []).forEach(wp => map.removeLayer(wp.marker));

        // --- draw new rectangle ---
        G.rectangle = L.rectangle(bounds, {
            color: ns.m.getDroneColourCode(droneId),
            weight: 2,
            fillOpacity: 0.1
        }).addTo(map);
        L.DomEvent.disableClickPropagation(G.rectangle.getElement());

        // --- compute dimensions ---
        const sw = bounds.getSouthWest(),
            ne = bounds.getNorthEast();
        G.widthM = sw.distanceTo(L.latLng(sw.lat, ne.lng));
        G.heightM = sw.distanceTo(L.latLng(ne.lat, sw.lng));

        // --- store corners & center for rotation/resizing ---
        const ring = G.rectangle.getLatLngs()[0].slice(0, 4),
            projCorners = ring.map(ll => crs.project(ll)),
            centerLL = bounds.getCenter(),
            centerProj = crs.project(centerLL);

        G.origCorners = projCorners;
        G.centerProj = centerProj;
        G.currentAngle = 0;

        // --- store current X/Y spacings ---
        G.spacingX = parseFloat(document.getElementById('gridSpacingXInput').value) || 0;
        G.spacingY = parseFloat(document.getElementById('gridSpacingYInput').value) || 0;

        // --- draw center marker & label ---
        G.centerMarker = L.marker(centerLL, { title: 'Grid Center' }).addTo(map);
        const NW = ring[1], NEpt = ring[2],
            mid = L.latLng((NW.lat + NEpt.lat) / 2, (NW.lng + NEpt.lng) / 2),
            lblPt = map.latLngToLayerPoint(mid),
            labelLL = map.layerPointToLatLng([lblPt.x, lblPt.y - 10]),
            deg = ns.m.calculateAngleFromCoordinates(NW, NEpt) * 180 / Math.PI;
        G.labelMarker = L.marker(labelLL, {
            interactive: false,
            icon: L.divIcon({
                className: 'dimension-label',
                html: `<div style="transform:rotate(${deg}deg);white-space:nowrap;">
                        ${G.heightM.toFixed(3)} m x ${G.widthM.toFixed(3)} m
                    </div>`
            })
        }).addTo(map);

        const manual = ns.d.wayPointsDrones.filter(
            wp => wp.id === droneId && !wp._isGrid
        );
        ns.d.grids[droneId].anchorWp = manual.length
            ? manual[manual.length - 1]
            : null;
        // --- generate & insert new grid waypoints (uses your patched function) ---
        G.lastWaypoints = ns.m.generateGridWaypoints(droneId);

        // --- bind controls & update UI ---
        G.visible = true;
        ns.m._bindGridDrag(droneId);
        ns.m.addGridResizeHandles(droneId);
        ns.m.updateToggleButtonState();
        ns.m._updateGridInputs(droneId);
    };

    ns.m.updateGridFromInputs = function (droneId) {
        const map = ns.map.map,
            crs = map.options.crs,
            G = ns.d.grids[droneId];
        if (!G || !G.rectangle) return;

        // — 1) preserve the index of any selected grid‐waypoint —
        let selIndex = null;
        if (ns.d.selectedMarker) {
            const selWp = (G.lastWaypoints || [])
                .find(wp => wp.marker === ns.d.selectedMarker);
            if (selWp) selIndex = G.lastWaypoints.indexOf(selWp);
        }

        // — 2) parse & validate the new centre/size inputs —
        const lat = parseFloat(document.getElementById('gridLatInput').value),
            lng = parseFloat(document.getElementById('gridLngInput').value),
            widthM = parseFloat(document.getElementById('gridWidthInput').value),
            heightM = parseFloat(document.getElementById('gridHeightInput').value);
        if ([lat, lng, widthM, heightM].some(v => isNaN(v) || v <= 0)) return;

        // — 3) compute new bounds via Turf as before —
        const centre = turf.point([lng, lat]),
            halfH = heightM / 2,
            halfW = widthM / 2;
        const south = turf.destination(centre, halfH, 180, { units: 'meters' }),
            swGeo = turf.destination(south, halfW, 270, { units: 'meters' }),
            north = turf.destination(centre, halfH, 0, { units: 'meters' }),
            neGeo = turf.destination(north, halfW, 90, { units: 'meters' });

        const swLL = L.latLng(swGeo.geometry.coordinates[1], swGeo.geometry.coordinates[0]),
            neLL = L.latLng(neGeo.geometry.coordinates[1], neGeo.geometry.coordinates[0]),
            bounds = L.latLngBounds(swLL, neLL);

        // — 4) update the polygon’s corner array (preserving rotation) —
        const sw = bounds.getSouthWest(),
            ne = bounds.getNorthEast(),
            nw = L.latLng(ne.lat, sw.lng),
            se = L.latLng(sw.lat, ne.lng),
            corners = [sw, nw, ne, se];

        // apply stored rotation
        const angleRad = -G.currentAngle * Math.PI / 180;
        const rotated = (G.currentAngle !== 0)
            ? corners.map(ll => {
                const P = crs.project(ll),
                    dx = P.x - G.centerProj.x,
                    dy = P.y - G.centerProj.y,
                    P2 = L.point(
                        G.centerProj.x + dx * Math.cos(angleRad) - dy * Math.sin(angleRad),
                        G.centerProj.y + dx * Math.sin(angleRad) + dy * Math.cos(angleRad)
                    );
                return crs.unproject(P2);
            })
            : corners;

        G.rectangle.setLatLngs([rotated]);

        // — 5) recompute dims, store new origCorners & centrePin —
        G.widthM = sw.distanceTo(L.latLng(sw.lat, ne.lng));
        G.heightM = sw.distanceTo(L.latLng(ne.lat, sw.lng));
        G.origCorners = rotated.map(ll => crs.project(ll));

        // new
        const centreLL = L.latLng(
            parseFloat(document.getElementById('gridLatInput').value),
            parseFloat(document.getElementById('gridLngInput').value)
        );
        G.centerProj = map.options.crs.project(centreLL);
        G.centerMarker.setLatLng(centreLL);

        // — 6) update the dimension label —
        const [c1, c2] = [rotated[1], rotated[2]],
            mid = L.latLng((c1.lat + c2.lat) / 2, (c1.lng + c2.lng) / 2),
            lblPt = map.latLngToLayerPoint(mid),
            labelLL = map.layerPointToLatLng([lblPt.x, lblPt.y - 10]),
            edgeDeg = ns.m.calculateAngleFromCoordinates(c1, c2) * 180 / Math.PI;
        G.labelMarker.setLatLng(labelLL);
        G.labelMarker.setIcon(L.divIcon({
            className: 'dimension-label',
            html: `<div style="transform:rotate(${edgeDeg}deg);white-space:nowrap;">
                        ${G.heightM.toFixed(3)} m x ${G.widthM.toFixed(3)} m
                    </div>`
        }));

        // — 7) **Regenerate** the grid waypoints (reads the fixed G.anchorWp) —
        //     and capture the fresh array for indexing:
        const newGrid = ns.m.generateGridWaypoints(droneId);

        // — 8) restore the selectedMarker if it was one of the grid points —
        if (selIndex !== null && newGrid[selIndex]) {
            ns.d.selectedMarker = newGrid[selIndex].marker;
        }

        // — 9) finally refresh the sidebar for that (new) selection —
        if (ns.d.selectedMarker) {
            ns.m.updateWaypointInformation(ns.d.selectedMarker);
            ns.m.updateSelectedMarkerDiv();
        }

        // — 10) re‐draw resize handles & update html inputs —
        G.lastWaypoints = ns.m.generateGridWaypoints(droneId);
        ns.m.addGridResizeHandles(droneId);
    };

    ns.m._clearGridForDrone = function (droneId) {
        const G = ns.d.grids[droneId];
        if (!G) return;
        // remove rectangle, center & label
        if (G.rectangle) ns.map.map.removeLayer(G.rectangle);
        if (G.centerMarker) ns.map.map.removeLayer(G.centerMarker);
        if (G.labelMarker) ns.map.map.removeLayer(G.labelMarker);
        // remove any resize‐handles
        (G.handles || []).forEach(h => ns.map.map.removeLayer(h));
        // remove any stored grid‐waypoints
        (G.lastWaypoints || []).forEach(wp => ns.map.map.removeLayer(wp.marker));
        // finally delete the state
        delete ns.d.grids[droneId];
        ns.m.updateToggleButtonState();
    };


    // 11) Kick-off
    document.addEventListener('DOMContentLoaded', ns.m.initGridControls);

    // ────────────────────────────────────────────────────────
    // ↓ Replace your old toggle code with this ↓
    // ────────────────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', () => {
        const takeoffBtn = document.getElementById('takeoffBtn');
        const landingBtn = document.getElementById('landingBtn');

        function sendFlight(cmd) {
            fetch('http://localhost:8001/flight', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flight: cmd })
            })
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .then(json => console.log('✅ flight', json))
                .catch(err => console.error('❌ flight', err));
        }

        takeoffBtn.addEventListener('click', () => {
            sendFlight('takeoff');
            // highlight takeoff, reset landing
            takeoffBtn.classList.replace('btn-secondary', 'btn-success');
            landingBtn.classList.replace('btn-success', 'btn-secondary');
        });

        landingBtn.addEventListener('click', () => {
            sendFlight('landing');
            // highlight landing, reset takeoff
            landingBtn.classList.replace('btn-secondary', 'btn-success');
            takeoffBtn.classList.replace('btn-success', 'btn-secondary');
        });
    });
    // ────────────────────────────────────────────────────────

}(ps3));
