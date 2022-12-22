/*class Image {
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
        this.type = this.config.drone.camera.type;

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
}*/

