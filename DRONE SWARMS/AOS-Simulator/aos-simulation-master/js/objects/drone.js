class Drone {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;
        this.loader = forest.loader;

        this.flying = false;
        this.goal = new THREE.Vector3();

        this.clock = new THREE.Clock();

        this.loaded = new Promise(async function (resolve) {
            //const path = 'model/drone.stl';
            //const stl = await this.loader.load('stl', path);

            //const droneGeometry = stl;
            //droneGeometry.rotateX(rad(-90)).rotateY(rad(-90)).translate(0, 0, 0);

            //const droneMaterial = new THREE.MeshStandardMaterial({
            //   color: 0x0096ff,
            //   roughness: 0.8,
            //   metalness: 0.8
            //});

            //this.drone = new THREE.Mesh(droneGeometry, droneMaterial);
            //this.drone.scale.multiplyScalar(12 / 100);

            const geometry1 = new THREE.CircleGeometry( 0.001, 0 );
            geometry1.rotateX(rad(-90)).rotateY(rad(-90)).translate(0, 0, 0);
            const material1 = new THREE.MeshBasicMaterial( { color: 0x0096ff } );
            this.drone = new THREE.Mesh( geometry1, material1 );
            this.scene.add( this.drone );
            
            this.drone.position.set(
                this.drone.position.x = 0,  //Change the start coordinates of the drone
                this.drone.position.y = this.config.drone.height,
                this.drone.position.z = 0  
                //this.config.drone.eastWest = 0 ,
                //this.config.drone.height,
                //this.config.drone.northSouth = 0 
            );
            this.drone.setRotationFromEuler(new THREE.Euler(0, rad(this.config.drone.rotation), 0));

            var loader = new THREE.TextureLoader();
            var material = new THREE.MeshLambertMaterial({
                map: loader.load('/model/1.jpg')
            });
            var geometry = new THREE.PlaneGeometry(this.config.forest.ground, this.config.forest.ground);
            geometry.rotateX(rad(-90)).rotateY(rad(-90)).translate(0,0.08, 0);
            var mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(0,0,0)
            this.scene.add(mesh);
            

            this.addDrone();
            this.addCamera();
            this.update();

            // animations
            this.animate = this.animate.bind(this);
            this.groundClick = doubleClick(this.groundClick.bind(this));

            // events
            window.addEventListener('pointerdown', this.groundClick);
            window.addEventListener('pointerup', this.groundClick);

            resolve(this);
        }.bind(this));
    }

    addDrone() {
        setLayer(this.drone, this.stage.layer.drone);
        this.scene.add(this.drone);
    }

    addCamera() {
        this.camera = new Camera(this, this.index);
       
    }

   

    getView() {
        // center
        const center = this.drone.position.clone();

        // coverage
        const coverage = 2 * center.y * Math.tan(rad(this.config.drone.camera.view / 2));

        // rotation
        const rotation = rad(this.config.drone.rotation);

        return {
            center: center,
            coverage: coverage,
            rotation: rotation
        };
    }

    groundClick(e) {
        if (e.target.parentElement.id !== 'stage' || e.which != 1) {
            return;
        }

        // mouse click coordinates
        const mouse = {
            x: (e.clientX / this.root.clientWidth) * 2 - 1,
            y: (e.clientY / this.root.clientHeight) * -2 + 1
        };

        // ray cast target
        const ray = new THREE.Raycaster();
        ray.layers.set(this.stage.layer.ground);
        ray.setFromCamera(new THREE.Vector3(mouse.x, mouse.y, 1), this.stage.camera);

        const intersects = ray.intersectObjects(this.forest.grounds);
        if (intersects.length) {
            // set goal position
            this.goal = intersects[0].point;

            // update config position
            this.config.drone.eastWest = this.drone.position.x;
            this.config.drone.northSouth = this.drone.position.z;

            // flight start
            this.flying = true;
            this.stage.status('Capturing', 0);

            // animate movement
            this.capturesCount = 0;
            this.clock.stop();
            this.clock.start();
            this.animate();
        }
    }

    async setEastWest(position) {
        this.drone.position.x = position;
        await this.update();
    }

    async setNorthSouth(position) {
        this.drone.position.z = position;
        await this.update();
    }

    async animate() {
        // trajectory coordinates
        const start = new THREE.Vector3(this.config.drone.eastWest, this.config.drone.height, this.config.drone.northSouth);
        const end = new THREE.Vector3(this.goal.x, this.config.drone.height, this.goal.z);

        // move duration
        const speed = this.config.drone.speed;
        const moveDistance = start.distanceTo(end);
        const moveDuration = moveDistance / speed;
        if (moveDuration <= 0) {
            return;
        }

        // calculate time
        const elapsedTime = this.clock.getElapsedTime();
        const trajectoryTime = elapsedTime / moveDuration;

        // goal check
        if (elapsedTime <= moveDuration) {

            // calculate trajectory
            const current = new THREE.Vector3();
            const trajectory = new THREE.Line3(start, end);
            trajectory.at(trajectoryTime, current);

            // calculate distance
            const currentDistance = elapsedTime * speed;
            const samplingDistance = this.config.drone.camera.sampling;
            const capturesCount = Math.floor(currentDistance / samplingDistance);

            // update drone position
            this.drone.position.set(current.x, current.y, current.z);
            await this.update();

            // capture image
            if (this.capturesCount < capturesCount) {
                this.capturesCount++;
                await this.camera.capture(true);
            }

            // update capture status
            this.stage.status('Capturing', Math.round(trajectoryTime * 100));

            if (this.flying) {
                // next animation
                requestAnimationFrame(this.animate);
            }
            else {
                // reset position
                await this.setEastWest(0.0);
                await this.setNorthSouth(0.0);

                // capture abort
                this.stage.status();
            }
        }
        else {
            // goal reached
            this.config.drone.eastWest = this.goal.x;
            this.config.drone.northSouth = this.goal.z;

            // flight stop
            this.flying = false;

            // capture finished
            this.stage.status();
        }
    }

    async capture(x,y,prevx,prevy,alts) {
        console.log("no")
        // TODO synchronize drone and persons time frame
        this.config.drone.height = alts;
        this.drone.position.y = alts;
        
        
        const {coverage} = this.getView();


        //this.config.drone.eastWest = this.drone.position.x;
        //this.config.drone.northSouth = this.drone.position.z;

        // ground top-left
        //this.forest.blockMoveTest1();
        //this.forest.blockMoveTest2();
        //this.forest.blockMoveTest3();
        //console.log("value: " +  this.config.drone.drone1x);
        //console.log("value: " +  this.config.drone.drone1y);
        const start = {
            x: this.config.drone.eastWest, //Math.round(-this.config.forest.ground / 2 - coverage / 2),
            y: 0,
            z: this.config.drone.northSouth //Math.round(-this.config.forest.ground / 2 + coverage / 2)
        };

        // ground bottom-right
        const end = {
            x: this.config.drone.endx, //Math.round(this.config.forest.ground / 2 + coverage / 2),
            y: 0,
            z: this.config.drone.endy //Math.round(this.config.forest.ground / 2 + coverage / 2)
        };

        // sampling step distance
        const step = {
            x: 0,
            y: 0,
            z: 0 //this.config.drone.camera.sampling
        };

        // flight start
        this.flying = true;
        this.stage.status('Capturing', 0);
        const sleep = (milliseconds) => {
            return new Promise(resolve => setTimeout(resolve, milliseconds))
        }
        // approximate number of images
        const imageCount = Math.ceil((end.z - start.z) / step.z) * Math.ceil((end.x - start.x) / step.x) + 1;
        //this.forest.removePersons();

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        //console.log("fine")
        var px = parseFloat(urlParams.get('personx')) 
        var py = parseFloat(urlParams.get('persony'))
        var orient = parseFloat(urlParams.get('personorient'))

        this.config.forest.persons.posx = px
        this.config.forest.persons.posy = py
        //this.config.forest.persons.roattion = 90
        console.log("xxxxxxxxxxxxxxxxxxxxxxxxx",orient)
        //console.log("xxxxxxxxxxxxxxxxxxxxxxxxx",px)
        this.config.forest.persons.rotation = orient
        

        this.config.forest.persons1.posx = 65
        this.config.forest.persons1.posy = 65
        //await sleep(1000);
        //this.person.position.set(this.config.forest.persons.posx, current.y, this.config.forest.persons.posy);
        this.forest.addPersons();
        //this.forest.removePersons1();
        //this.person.position.set(this.config.forest.persons.posx, current.y, this.config.forest.persons.posy);
        //this.forest.addPersons1();
        //this.forest.removePersons2();
        //this.person.position.set(this.config.forest.persons.posx, current.y, this.config.forest.persons.posy);
        //this.forest.addPersons2();
        // update drone position
        let i = 0;
        
        let dir = 1 ;  
                //////////////// To move in a diagonal manner     ///////////////////  
        const t = ((this.config.drone.speed * 1000) / this.config.drone.speed)/ this.config.drone.speed ; 

        
        await this.setNorthSouth(y);
        await this.setEastWest(x);
        
        console.log(this.config.forest.persons.posx)
        console.log(this.config.forest.persons.posy)
        console.log(this.config.forest.persons1.posx)
        console.log(this.config.forest.persons1.posy)
        await sleep(2000);

        await this.camera.capture(false);
        
        //await new Promise(r => setTimeout(r, 5000));
        //await sleep(1);
        //this.forest.removePersons();
        this.config.forest.persons.posx = 60 /////////////////////////////60
        this.config.forest.persons.posy = 60

        this.config.forest.persons1.posx = px
        this.config.forest.persons1.posy = py
        this.config.forest.persons1.rotation = orient
        
        await this.forest.addPersons2();
        //await sleep(1000);

        console.log(this.config.forest.persons1.posx)
        console.log(this.config.forest.persons1.posy)
        console.log(this.config.forest.persons.posx)
        console.log(this.config.forest.persons.posy)


        await sleep(2000);
        await this.camera.capture1(false);

        this.config.forest.persons1.posx = 65
        this.config.forest.persons1.posy = 65
        await sleep(1000);
        this.config.forest.persons.posx = px
        this.config.forest.persons.posy = py
       
        console.log("yes")


        //await this.forest.addPersons();
        
        
              

      
        
        
        await sleep(t);
            

        // flight stop
        this.flying = false;
        await this.update();

        // capture 

        //this.stage.status(); 
       
        
    }


    

    async awesome(x,y,prevx,prevy,alts) {

        var from = new THREE.Vector3( prevx, alts, prevy );
        var to = new THREE.Vector3( x, alts, y);
        var direction = to.clone().sub(from);
        var length = direction.length();
        var arrowHelper = new THREE.ArrowHelper(direction.normalize(), from, length, 0xffffff,1.0,1.0 );
        
        this.scene.add( arrowHelper ); 
        

    }

    async robuster(f,g,h) {
        const geometry2 = new THREE.CircleGeometry( 0.4, 32 );
        geometry2.rotateX(rad(-90)).rotateY(rad(-90)).translate(0, 0, 0);
        const material2 = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
        this.drones = new THREE.Mesh( geometry2, material2 );
        this.scene.add( this.drones );
        
        this.drones.position.set(
            this.drones.position.x = f,  //Change the start coordinates of the drone
            this.drones.position.y = h,
            this.drones.position.z = g  
            //this.config.drone.eastWest = 0 ,
            //this.config.drone.height,
            //this.config.drone.northSouth = 0 
        );
        this.drone.setRotationFromEuler(new THREE.Euler(0, rad(this.config.drone.rotation), 0));
        
    }

    async update() {
        const { rotation } = this.getView();

        // set height
        this.drone.position.y = this.config.drone.height;

        // set rotation
        this.drone.setRotationFromEuler(new THREE.Euler(0, rotation, 0));

        // update camera
        await this.camera.update();
    }

    async export(zip,k) {
        const drone = zip.folder(k);

        // export drone
        drone.file('drone.json', JSON.stringify(this.getView(), null, 4));

        // export camera
        await this.camera.export(drone,k);
        
        
    }

    async clear() {
        // flight abort
        this.flying = false;

        // reset position
        await this.setEastWest(0.0);
        await this.setNorthSouth(0.0);

        // clear camera
        await this.camera.clear();
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}


class Camera {
    constructor(drone, index) {
        this.root = drone.root;
        this.config = drone.config;
        this.loader = drone.loader;
        this.scene = drone.scene;
        this.stage = drone.stage;
        this.forest = drone.forest;
        this.drone = drone;
        this.index = index;

        const { center, coverage, rotation } = this.drone.getView();

        this.center = center;
        this.coverage = coverage;
        this.rotation = rotation;

        this.rays = [];
        this.boxes = [];

        this.planes = [];
        this.persons = [];
        this.captures = [];

        this.layers = [
            this.stage.layer.trees,
            this.stage.layer.persons,
            this.stage.layer.camera
        ];

        this.planeMaterial = new THREE.MeshStandardMaterial({
            color: this.config.material.color.plane,
            side: THREE.DoubleSide
        });

        this.textMaterial = new THREE.MeshPhongMaterial({
            color: 0x990000,
            specular: 0xff2222
        });

        this.lineMaterial = new THREE.LineBasicMaterial({
            color: 0x6cc2cd
        });

        // view lines
        this.viewLines = [];
        for (let i = 0; i < 4; i++) {
            const viewLinePoints = [new THREE.Vector3(0, this.config.drone.height, 0), new THREE.Vector3(0, 0, 0)];
            const viewLineGeometry = new THREE.BufferGeometry().setFromPoints(viewLinePoints);
            this.viewLines.push(new THREE.Line(viewLineGeometry, this.lineMaterial));
        }

        // plane
        const rectangleGeometry = new THREE.PlaneGeometry();
        rectangleGeometry.rotateX(rad(-90));
        const rectangle = new THREE.Mesh(rectangleGeometry, this.planeMaterial);

        // plane border
        const border = new THREE.LineSegments(new THREE.EdgesGeometry(rectangleGeometry), this.lineMaterial);
        border.matrixAutoUpdate = true;

        // plane text
        const textGeometry = new THREE.TextGeometry('', { font: this.stage.font });
        textGeometry.rotateX(rad(-90));
        const text = new THREE.Mesh(textGeometry, this.textMaterial);
        text.userData = { clone: text.clone() };

        // init plane
        this.plane = {
            rectangle: rectangle,
            border: border,
            text: text
        };

        // init slider
        this.slider = new Slider(document.querySelector('#captures'), this.config, this.loader);

        this.loaded = new Promise(async function (resolve) {
            this.addView();
            this.addPlane();
            this.addRenderer();
            this.addPreview();
            this.update();

            // animations
            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);

            resolve(this);
        }.bind(this));
    }

    addView() {
        const view = new THREE.Group();
        this.viewLines.forEach((viewLine) => {
            view.add(viewLine);
        });

        setLayer(view, this.stage.layer.drone);
        //this.scene.add(view);
    }

    addPlane() {
        setLayer(this.plane.rectangle, this.stage.layer.camera);
        //this.scene.add(this.plane.rectangle);

        setLayer(this.plane.border, this.stage.layer.drone);
        //this.scene.add(this.plane.border);

        setLayer(this.plane.text, this.stage.layer.drone);
        //this.scene.add(this.plane.text);
    }

    addRenderer() {
        // init preview camera
        this.camera = new THREE.PerspectiveCamera(this.config.drone.camera.view, 1, 0.1, 1000);
        this.scene.add(this.camera);

        // init preview renderer
        this.renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true, antialias: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // set default layer
        this.setLayers(this.layers);
    }

    addPreview() {
        const resolution = this.getResolution();

        // preview container
        const previewContainer = document.createElement('div');
        previewContainer.className = 'image';

        // preview image
        const { canvas: previewCanvas, ctx: previewContext } = getCanvas(resolution.x, resolution.z);
        previewContext.fillStyle = hexColor(this.config.material.color.plane);
        previewContext.fillRect(0, 0, previewCanvas.width, previewCanvas.height);
        previewContainer.append(previewCanvas);

        // render container
        const renderContainer = document.createElement('div');
        renderContainer.className = 'image';
        renderContainer.append(this.renderer.domElement);

        // append to slider
        this.slider.previews.append(previewContainer);
        this.slider.previews.append(renderContainer);
    }

    setLayers(layers) {
        this.camera.layers.disableAll();

        // enable default layer (light)
        this.camera.layers.enable(0);

        // enable required layers
        Object.values(layers).forEach((layer) => {
            this.camera.layers.enable(layer);
        });
        this.render();
    }

    getResolution() {
        return new THREE.Vector3(this.config.drone.camera.resolution, 0, this.config.drone.camera.resolution);
    }

    getPlane() {
        // plane
        const plane = this.plane.rectangle.clone();
        plane.material = this.plane.rectangle.material.clone();
        plane.geometry = this.plane.rectangle.geometry.clone();
        plane.translateY(0);

        // add to scene
        setLayer(plane, this.stage.layer.ground);
        this.planes.push(plane);
        this.scene.add(plane);

        return plane;
    }

    getText() {
        let planeText = this.plane.text.userData.clone;
        let { offset, coverage, rotation } = planeText.userData;

        const updateText = this.coverage !== coverage || this.rotation !== rotation;
        if (updateText) {
            // plane text
            const text = this.coverage.toFixed(2) + ' x ' + this.coverage.toFixed(2);
            const textGeometry = new THREE.TextGeometry(text, { font: this.stage.font, size: this.coverage / 10, height: 0.01 });
            textGeometry.rotateX(rad(-90));
            planeText.geometry.copy(textGeometry);

            // plane text width/height
            const textSize = new THREE.Vector3();
            new THREE.Box3().setFromObject(planeText).getSize(textSize);

            // plane text center offset
            offset = Math.sqrt((textSize.x / 2) ** 2 + (textSize.z / 2) ** 2);
        }

        // update text data
        planeText.userData = {
            offset: offset,
            center: this.center,
            coverage: this.coverage,
            rotation: this.rotation
        };

        // plane text position 
        const x = this.center.x - offset * Math.cos(this.rotation);
        const z = this.center.z + offset * Math.sin(this.rotation);

        return {
            text: planeText,
            position: new THREE.Vector3(x, 0.005, z)
        };
    }

    async animate() {
        await this.render();
        requestAnimationFrame(this.animate);
    }

    async render() {
        this.renderer.setSize(this.config.drone.camera.resolution, this.config.drone.camera.resolution);
        this.renderer.domElement.removeAttribute('style');
        this.renderer.render(this.scene, this.camera);
    }

    async capture(preview) {
        const index = this.captures.length;
        const image = new Image(this, index);
        console.log("going")
        
        return await image.capture(preview);
    }
    async capture1(preview) {
        const index = this.captures.length;
        const image = new Image1(this, index);
        
        return await image.capture(preview);
    }

   
   
    async update() {
        const { center, coverage, rotation } = this.drone.getView();

        // update properties
        this.center = center;
        this.coverage = coverage;
        this.rotation = rotation;

        // view corners (right-top, left-top, left-bottom, right-bottom)
        const cornerAngles = [45, 135, 225, 315];
        const cornerDistance = Math.sqrt((coverage / 2) ** 2 + (coverage / 2) ** 2);

        // update view lines 
        this.viewLines.forEach((viewLine, i) => {
            const theta = rad(cornerAngles[i]) - rotation;
            const x = center.x + cornerDistance * Math.cos(theta);
            const z = center.z + cornerDistance * Math.sin(theta);

            const from = new THREE.Vector3(center.x, center.y, center.z);
            const to = new THREE.Vector3(x, 0, z);
            viewLine.geometry.setFromPoints([from, to]);
        });

        // update plane
        this.plane.rectangle.scale.set(coverage, 1, coverage);
        this.plane.rectangle.position.set(center.x, 0.01, center.z);
        this.plane.rectangle.setRotationFromEuler(new THREE.Euler(0, rotation, 0));

        // update plane border
        this.plane.border.scale.set(coverage, 1, coverage);
        this.plane.border.position.set(center.x, 0.5, center.z);
        this.plane.border.setRotationFromEuler(new THREE.Euler(0, rotation, 0));

        // update plane text
        const { position } = this.getText();
        this.plane.text.setRotationFromEuler(new THREE.Euler(0, rotation, 0));
        this.plane.text.position.set(position.x, 0.005, position.z);

        // update camera position
        this.camera.fov = this.config.drone.camera.view;
        this.camera.position.set(center.x, center.y, center.z);
        this.camera.lookAt(center.x, 0, center.z);
        this.camera.rotateZ(rotation);
        this.camera.updateProjectionMatrix();
        this.render();
    }

    async export(zip,k) {
        const camera = zip.folder('camera');
        const data = { captures: [] };
        const data1 = { persons: [] };

        // append persons
        this.persons.forEach((person) => {
            data1.persons.push({
                imageC0: person.image,
                centers: person.centers
            });
        });

        // append captures
        this.captures.forEach((capture, i) => {
            data.captures.push({
                name: capture.name,
                imageC0: capture.image,
                center: capture.center
            });

            // export images
            const base64 = canvasImage(capture.canvas.full);
            //const filename = `imageC${k-1}-${capture.image}-${this.config.drone.camera.type}.png`;
            const filename = `imageC${k-1}-${capture.image}-${capture.name}.png`;
            camera.file(filename, base64, { base64: true });

            // update export status
            this.stage.status('Exporting', Math.round(i * 100 / this.captures.length));
        });

        // export config
        camera.file('camera.json', JSON.stringify(data, null, 4));
        camera.file('person.json', JSON.stringify(data1, null, 4));
    }




    
    
   

    async clear() {
        // clear planes
        this.planes.forEach((capture) => { this.scene.remove(capture); });
        this.planes = [];

        // clear rays
        this.rays.forEach((ray) => { this.scene.remove(ray); });
        this.rays = [];

        // clear boxes
        this.boxes.forEach((ray) => { this.scene.remove(ray); });
        this.boxes = [];

        // clear persons
        this.persons = [];

        // clear captures
        this.captures = [];

        // clear slider
        await this.slider.clear();

        // add initial preview
        this.addPreview();
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}


class Image {
    constructor(camera, index) {
        this.root = camera.root;
        this.config = camera.config;
        this.loader = camera.loader;
        this.scene = camera.scene;
        this.stage = camera.stage;
        this.forest = camera.forest;
        this.drone = camera.drone;
        this.camera = camera;
        this.index = index;

        this.center = this.camera.center;
        this.coverage = this.camera.coverage;
        this.rotation = this.camera.rotation;

        this.plane = this.camera.getPlane();
        this.resolution = this.camera.getResolution();
        this.type = 'color';

        this.borderPoints = this.camera.viewLines.map(getPoints);

        this.loaded = new Promise(async function (resolve) {
            resolve(this);
        }.bind(this));
    }

    getCanvas(layers) {
        // enable desired layers
        this.camera.setLayers(layers);

        // clone canvas
        const canvas = cloneCanvas(this.camera.renderer.domElement, { grayscale: this.type === 'monochrome' });

        // enable default layers
        this.camera.setLayers(this.camera.layers);

        return canvas;
    }

 
    translate(point) {
        // get min values for each axes
        const min = new THREE.Vector3(
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].x; })),
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].y; })),
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].z; }))
        );

        // subtract min point value for each border points axes
        const borderPointsGround = this.borderPoints.map((p) => { return p.map((a) => { return a.sub(min); })[1]; });

        // get max values for each axes
        const max = new THREE.Vector3(
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.x; })),
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.y; })),
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.z; }))
        );

        // convert simulation coordinates (meter) into image coordinates (pixel)
        return new THREE.Vector3(
            Math.fround(point.x * this.resolution.x / max.x),
            Math.fround(point.y * this.resolution.x / max.x),
            Math.fround(point.z * this.resolution.z / max.z)
        );
    }

    async capture(preview) {
        const integrate = preview && this.config.drone.camera.images > 0;

        // check persons loaded
        const persons = this.forest.persons.filter((p) => { return !!p.person; });
        if (persons.length != this.forest.persons.length) {
            return;
        }

        // capture persons positions
        return this.capturePersons(integrate).then((persons) => {
            // capture image pixels
            return this.captureImage(integrate).then((captures) => {
                // integrate preview images
                return integrate ? this.integrateImages(persons, captures) : undefined;
                
            });
        });
    }



    async capturePersons(integrate) {
        const positions = this.forest.persons.map((p) => { return p.person.position; });

        // get persons centers
        const centers = positions.map((position) => {
            const rendered = new THREE.Vector3();
            rendered.x = position.x;
            rendered.y = 0;
            rendered.z = position.z;
            const processed = this.translate(rendered);
            return {
                rendered: rendered,
                processed: processed
            };
        });

        // persons object
        const person = {
            image: this.index + 1 + '0',
            centers: centers
        };

        // append persons to camera
        this.camera.persons.push(person);

        // return last persons
        const last = Math.max(this.camera.persons.length - this.config.drone.camera.images, 0);
        return this.camera.persons.slice(last);
    }

    async captureImage(integrate) {
        const rendered = new THREE.Vector3();
        rendered.x = this.center.x;
        rendered.y = this.center.y;
        rendered.z = this.center.z;
        const processed = this.translate(rendered);

        // render canvas per layer
        const canvas = {
            trees: integrate ? this.getCanvas([this.stage.layer.trees]) : undefined,
            persons: integrate ? this.getCanvas([this.stage.layer.persons]) : undefined,
            full: this.getCanvas([this.stage.layer.trees, this.stage.layer.persons, this.stage.layer.camera])
        };

        // capture object
        const capture = {
            //image: this.index + 1 + '0' ,
            name: 'color',
            image: this.index + 1 ,
            center: {
                rendered: rendered,
                processed: processed
            },
            canvas: canvas
        };

        if (integrate) {
            // canvas container
            const container = document.createElement('div');
            container.className = 'image';

            // append image
            container.append(canvas.full);
            this.camera.slider.addImage(container);
        }

        // append captures to camera
        this.camera.captures.push(capture);

        // return last captures
        const last = Math.max(this.camera.captures.length - this.config.drone.camera.images, 0);
        return this.camera.captures.slice(last);
    }



    

    async integrateImages(persons, captures) {
        const { canvas: canvasPersons, ctx: ctxPersons } = getCanvas(this.resolution.x, this.resolution.z);
        const { canvas: canvasTrees, ctx: ctxTrees } = getCanvas(this.resolution.x, this.resolution.z);

        // integrate last images
        const center = captures[captures.length - 1].center.processed;
        captures.forEach((capture) => {
            if (!capture.canvas.persons || !capture.canvas.trees) {
                return;
            }

            // delta between image centers
            const delta = new THREE.Vector3();
            delta.copy(center).sub(capture.center.processed);

            // integrate persons
            ctxPersons.globalCompositeOperation = 'lighten';
            ctxPersons.drawImage(capture.canvas.persons, -delta.x, -delta.z);

            // integrate trees
            ctxTrees.globalCompositeOperation = 'darken';
            ctxTrees.drawImage(capture.canvas.trees, -delta.x, -delta.z);
        });

        // transparent background
        const integratedTrees = transparentCanvas(canvasTrees, 0x000000);
        const integratedPersons = transparentCanvas(canvasPersons, 0x000000);

        // ground image
        const { canvas: canvas, ctx: ctx } = getCanvas(this.resolution.x, this.resolution.z);
        ctx.fillStyle = hexColor(this.config.material.color.plane);
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // draw integrated persons
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(integratedPersons, 0, 0);

        // draw integrated trees
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(integratedTrees, 0, 0);

        // canvas container
        const container = document.createElement('div');
        container.className = 'image';

        // append preview
        container.append(canvas);
        this.camera.slider.addPreview(container);

        // return integrated image
        return canvas;
    }

    
}






class Image1 {
    constructor(camera, index) {
        this.root = camera.root;
        this.config = camera.config;
        this.loader = camera.loader;
        this.scene = camera.scene;
        this.stage = camera.stage;
        this.forest = camera.forest;
        this.drone = camera.drone;
        this.camera = camera;
        this.index = index;

        this.center = this.camera.center;
        this.coverage = this.camera.coverage;
        this.rotation = this.camera.rotation;

        this.plane = this.camera.getPlane();
        this.resolution = this.camera.getResolution();
        this.type = 'monochrome';

        this.borderPoints = this.camera.viewLines.map(getPoints);

        this.loaded = new Promise(async function (resolve) {
            resolve(this);
        }.bind(this));
    }

    getCanvas(layers) {
        // enable desired layers
        this.camera.setLayers(layers);

        // clone canvas
        const canvas = cloneCanvas(this.camera.renderer.domElement, { grayscale: this.type === 'monochrome' });

        // enable default layers
        this.camera.setLayers(this.camera.layers);

        return canvas;
    }

 
    translate(point) {
        // get min values for each axes
        const min = new THREE.Vector3(
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].x; })),
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].y; })),
            Math.min.apply(Math, this.borderPoints.map((p) => { return p[1].z; }))
        );

        // subtract min point value for each border points axes
        const borderPointsGround = this.borderPoints.map((p) => { return p.map((a) => { return a.sub(min); })[1]; });

        // get max values for each axes
        const max = new THREE.Vector3(
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.x; })),
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.y; })),
            Math.max.apply(Math, borderPointsGround.map((p) => { return p.z; }))
        );

        // convert simulation coordinates (meter) into image coordinates (pixel)
        return new THREE.Vector3(
            Math.fround(point.x * this.resolution.x / max.x),
            Math.fround(point.y * this.resolution.x / max.x),
            Math.fround(point.z * this.resolution.z / max.z)
        );
    }

    async capture(preview) {
        const integrate = preview && this.config.drone.camera.images > 0;

        // check persons loaded
        const persons = this.forest.persons.filter((p) => { return !!p.person; });
        if (persons.length != this.forest.persons.length) {
            return;
        }

        // capture persons positions
        return this.capturePersons(integrate).then((persons) => {
            // capture image pixels
            return this.captureImage(integrate).then((captures) => {
                // integrate preview images
                return integrate ? this.integrateImages(persons, captures) : undefined;
                
            });
        });
    }



    async capturePersons(integrate) {
        const positions = this.forest.persons.map((p) => { return p.person.position; });

        // get persons centers
        const centers = positions.map((position) => {
            const rendered = new THREE.Vector3();
            rendered.x = position.x;
            rendered.y = 0;
            rendered.z = position.z;
            const processed = this.translate(rendered);
            return {
                rendered: rendered,
                processed: processed
            };
        });

        // persons object
        const person = {
            image: this.index + 1 + '0',
            centers: centers
        };

        // append persons to camera
        this.camera.persons.push(person);

        // return last persons
        const last = Math.max(this.camera.persons.length - this.config.drone.camera.images, 0);
        return this.camera.persons.slice(last);
    }

    async captureImage(integrate) {
        const rendered = new THREE.Vector3();
        rendered.x = this.center.x;
        rendered.y = 0;
        rendered.z = this.center.z;
        const processed = this.translate(rendered);

        // render canvas per layer
        const canvas = {
            trees: integrate ? this.getCanvas([this.stage.layer.trees]) : undefined,
            persons: integrate ? this.getCanvas([this.stage.layer.persons]) : undefined,
            full: this.getCanvas([this.stage.layer.trees, this.stage.layer.persons, this.stage.layer.camera])
        };

        // capture object
        const capture = {
            //image: this.index + 1 + '0' ,
            name: 'monochrome',
            image: this.index + 1 ,
            center: {
                rendered: rendered,
                processed: processed
            },
            canvas: canvas
        };

        if (integrate) {
            // canvas container
            const container = document.createElement('div');
            container.className = 'image';

            // append image
            container.append(canvas.full);
            this.camera.slider.addImage(container);
        }

        // append captures to camera
        this.camera.captures.push(capture);

        // return last captures
        const last = Math.max(this.camera.captures.length - this.config.drone.camera.images, 0);
        return this.camera.captures.slice(last);
    }



    

    async integrateImages(persons, captures) {
        const { canvas: canvasPersons, ctx: ctxPersons } = getCanvas(this.resolution.x, this.resolution.z);
        const { canvas: canvasTrees, ctx: ctxTrees } = getCanvas(this.resolution.x, this.resolution.z);

        // integrate last images
        const center = captures[captures.length - 1].center.processed;
        captures.forEach((capture) => {
            if (!capture.canvas.persons || !capture.canvas.trees) {
                return;
            }

            // delta between image centers
            const delta = new THREE.Vector3();
            delta.copy(center).sub(capture.center.processed);

            // integrate persons
            ctxPersons.globalCompositeOperation = 'lighten';
            ctxPersons.drawImage(capture.canvas.persons, -delta.x, -delta.z);

            // integrate trees
            ctxTrees.globalCompositeOperation = 'darken';
            ctxTrees.drawImage(capture.canvas.trees, -delta.x, -delta.z);
        });

        // transparent background
        const integratedTrees = transparentCanvas(canvasTrees, 0x000000);
        const integratedPersons = transparentCanvas(canvasPersons, 0x000000);

        // ground image
        const { canvas: canvas, ctx: ctx } = getCanvas(this.resolution.x, this.resolution.z);
        ctx.fillStyle = hexColor(this.config.material.color.plane);
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // draw integrated persons
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(integratedPersons, 0, 0);

        // draw integrated trees
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(integratedTrees, 0, 0);

        // canvas container
        const container = document.createElement('div');
        container.className = 'image';

        // append preview
        container.append(canvas);
        this.camera.slider.addPreview(container);

        // return integrated image
        return canvas;
    }

    
}



