class Stage {
    constructor(root, config, loader) {
        this.root = root;
        this.config = config;
        this.loader = loader;

        this.name = document.title;
        this.layer = {
            ground: 1,
            trees: 2,
            persons: 3,
            drone: 4,
            camera: 5
        };

        this.loaded = new Promise(async function (resolve) {
            const path = 'font/opensans.json';
            const font = await this.loader.load('font', path);

            this.fov = 40; //60
            this.font = font;
            this.scene = new THREE.Scene();

            // stage directional light
            this.directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            this.directionalLight.position.set(100, 100, 100);

            // stage ambient light
            this.ambientLight = new THREE.AmbientLight(0xffffff, 1);

            // stage camera
            this.camera = new THREE.PerspectiveCamera(this.fov, this.root.clientWidth / this.root.clientHeight, 0.1, 1000);
            this.camera.add(this.directionalLight);
            this.camera.add(this.ambientLight);
            this.scene.add(this.camera);

            // stage camera layers
            Object.values(this.layer).forEach((layer) => {
                this.camera.layers.enable(layer);
            });

            // renderer
            this.renderer = new THREE.WebGLRenderer({ logarithmicDepthBuffer: true, preserveDrawingBuffer: true, antialias: true });
            this.renderer.setPixelRatio(window.devicePixelRatio);

            // controls
            this.controls = new THREE.MapControls(this.camera, this.renderer.domElement);
            this.controls.minDistance = 0.1;
            this.controls.maxDistance = 500;
            this.controls.enablePan = true;

            // user interface
            this.stats = new Stats();
            this.root.querySelector('#info').append(this.stats.dom);
            this.root.querySelector('#stage').append(this.renderer.domElement);

            // reset stage
            this.reset();

            // animations
            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);

            // events
            this.update = this.update.bind(this);
            window.addEventListener('resize', this.update);

            resolve(this);
        }.bind(this));
    }

    status(message, percent) {
        let status = this.name;
        if (message) {
            status = getType(percent) === 'number' ? `${message} (${percent}%)` : message;
        }
        document.title = status;
    }

    async animate() {
        await this.render();
        requestAnimationFrame(this.animate);
    }

    async render() {
        this.stats.begin();
        this.controls.update();
        
        this.renderer.render(this.scene, this.camera);
        
        //this.renderer.forceContextLoss();
        //this.renderer.context = null;
        //this.renderer.domElement = null;
        //this.renderer = null;
        this.stats.end();
    }

    async update() {
        //await timeout(4000)
        this.renderer.setSize(this.root.clientWidth, this.root.clientHeight);
        this.camera.aspect = this.root.clientWidth / this.root.clientHeight;
        this.camera.updateProjectionMatrix();
    }

    async export(zip) {
        const stage = zip.folder('stage');

        // navigator
        const navigator = {};
        for (let key in window.navigator) {
            if (['string', 'array', 'number'].includes(getType(window.navigator[key]))) {
                navigator[key] = window.navigator[key];
            }
        }

        // client
        const client = {
            stage: {
                clientWidth: this.root.clientWidth,
                clientHeight: this.root.clientHeight
            },
            screen: {
                width: window.screen.width,
                height: window.screen.height,
                availWidth: window.screen.availWidth,
                availHeight: window.screen.availHeight,
                devicePixelRatio: window.devicePixelRatio
            },
            intl: {
                dateTimeFormat: Intl.DateTimeFormat().resolvedOptions(),
                numberFormat: Intl.NumberFormat().resolvedOptions()
            },
            location: window.location,
            navigator: navigator
        };

        // export config
        stage.file('client.json', JSON.stringify(client, null, 4));

        // export image
        const image = canvasImage(this.renderer.domElement);
        stage.file('image.png', image, { base64: true });
        const image1 = canvasImage1(this.renderer.domElement);
        stage.file('cropped_image.png', image1, { base64: true });
    }

    async reset() {
        const size = this.config.forest.ground;
        const coverage = 2 * this.config.drone.height * Math.tan(rad(this.config.drone.camera.view / 2));
        const height = (size + 2 * coverage) / (2 * Math.tan(rad(this.fov / 2)));

        // reset camera position
        this.camera.setRotationFromEuler(new THREE.Euler(0, 0, 0));
        this.camera.position.set(0.0, height * 1.1, 0.0);
        this.controls.target.set(0.0, 0.0, 0.0);

        // update camera
        await this.update();
        await this.render();

        // reset status
        await sleep(100);
    }
}