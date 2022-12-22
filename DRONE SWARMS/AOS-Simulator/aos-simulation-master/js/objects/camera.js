/*class Camera {
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
            color: 0x990000
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
        this.scene.add(view);
    }

    addPlane() {
        setLayer(this.plane.rectangle, this.stage.layer.camera);
        this.scene.add(this.plane.rectangle);

        setLayer(this.plane.border, this.stage.layer.drone);
        this.scene.add(this.plane.border);

        setLayer(this.plane.text, this.stage.layer.drone);
        this.scene.add(this.plane.text);
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
        this.plane.border.position.set(center.x, 0.01, center.z);
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

    async export(zip) {
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
                imageC0: capture.image,
                center: capture.center
            });

            // export images
            const base64 = canvasImage(capture.canvas.full);
            const filename = `imageC0-${capture.image}-${this.config.drone.camera.type}.png`;
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
}*/