class View {
    constructor(root, config, presets) {
        this.root = root;
        this.config = config;
        this.presets = presets;
        this.loader = new Loader();
       

        // init stage
        this.stage = new Stage(this.root, this.config, this.loader);
        this.stage.loaded.then(() => {

            // init dom
            this.splitter(['#top', '#bottom']);
            this.background(this.config.material.color.background);

            // init objects
            this.forest = new Forest(this.stage, 0);
            
            this.drone = new Drone(this.forest, 0);
            
            for (var j = 1; j < this.config.drone.noofdrones; j++) {
                this.drone[j] = new Drone(this.forest, 0);
            }

            this.drone.loaded.then(() => {
                this.controls(this.root.querySelector('#controls'), presets);
            });
            
            this.forest.loaded.then(() => {
                this.update({ type: 'loaded' });
            });

            // init events
            window.addEventListener('hashchange', (event) => {
                this.update(event);
            });
        });
    }

    splitter(container) {
        const options = {
            gutterSize: 5,
            sizes: [80, 20],
            minSize: [0, 0],
            cursor: 'ns-resize',
            direction: 'vertical',
            onDrag: () => { this.stage.update(); },
            gutter: () => {
            const gutter = document.createElement('div');
                gutter.id = 'gutter';
                return gutter;
            }
        };

        // init split
        Split(container, options);

        // update stage
        this.stage.update();
    }

    background(color) {
        // canvas background
        this.stage.renderer.setClearColor(color);

        // document background
        document.body.style.backgroundColor = hexColor(color);
    }

    controls(root) {
        const bound = this.config.forest.ground / 2 + this.drone.getView().coverage;

        // gui root
        this.gui = new dat.GUI({ autoPlace: false, width: 320 });
        this.gui.closed = !!getLocalStorage('gui').closed;
        this.gui.useLocalStorage = true;
        root.append(this.gui.domElement);

        // drone folder
        const droneFolder = this.gui.addFolder('drone');
        droneFolder.add(this.config.drone, 'speed', 1, 20, 1).onChange(() => this.drone.update())
        droneFolder.add(this.config.drone, 'height', 1, 100, 1).onChange(() => this.drone.update()).onFinishChange(() => this.forest.update()).listen();
        droneFolder.add(this.config.drone, 'rotation', -180, 180, 1).onChange(() => this.drone.update())
        droneFolder.add(this.config.drone, 'eastWest', -bound, bound, 1).onChange((v) => this.drone.setEastWest(v))
        droneFolder.add(this.config.drone, 'northSouth', -bound, bound, 1).onChange((v) => this.drone.setNorthSouth(v))
        droneFolder.add(this.config.drone, 'endx', -bound, bound, 1).onChange(() => this.drone.update())
        droneFolder.add(this.config.drone, 'endy', -bound, bound, 1).onChange(() => this.drone.update())

        // camera folder
        const cameraFolder = droneFolder.addFolder('camera');
        cameraFolder.add(this.config.drone.camera, 'view', 10, 160, 1).onChange(() => this.drone.update()).onFinishChange(() => this.forest.update()).listen();
        cameraFolder.add(this.config.drone.camera, 'resolution', 128, 1024, 1).onChange(() => this.drone.update()).listen();
        cameraFolder.add(this.config.drone.camera, 'sampling', 0.1, 10.0, 0.1).onChange(() => this.drone.update()).listen();
        cameraFolder.add(this.config.drone.camera, 'images', 0, 60, 1).onChange(() => this.drone.update()).listen();
        cameraFolder.add(this.config.drone.camera, 'type', ['color', 'monochrome']).onChange(() => this.drone.reset()).listen();

        // cpu folder
        const cpuFolder = droneFolder.addFolder('cpu');
        cpuFolder.add(this.config.drone.cpu, 'speed', 0.1, 2.0, 0.1).onChange(() => this.drone.update()).listen();

        // forest folder
        const forestFolder = this.gui.addFolder('forest');
        const forestFolders = [
            forestFolder.add(this.config.forest, 'size', 0, 2000, 1),
            forestFolder.add(this.config.forest, 'ground', 10, 500, 1)
        ];

        // forest folders
        forestFolders.forEach((folder) => {
            folder.onFinishChange(() => {
                this.forest.removeTrees();
                this.forest.addTrees();
                this.forest.removePersons();
                this.forest.removePersons1();
                this.forest.removePersons2();
                
                //this.forest.addPersons();
                //this.forest.addPersons1();
                //this.forest.addPersons2();
                //this.forest.addblocks1();
                //this.forest.addblocks2();
                //this.forest.addblocks3();
               
                this.drone.reset();
            });
        });
      
        forestFolder.add(this.config.forest, 'blocks1', 0, 20, 1).onFinishChange(() => {
            this.forest.removeblocks1();
            //this.forest.addblocks1();
            
            
        });
        forestFolder.add(this.config.forest, 'blocks2', 0, 20, 1).onFinishChange(() => {
            this.forest.removeblocks2();
            //this.reset();
            
        });
        forestFolder.add(this.config.forest, 'blocks3', 0, 20, 1).onFinishChange(() => {
            this.forest.removeblocks3();
            //this.reset();
            
        });
        forestFolder.add(this.config.forest, 'block1startx', -bound, bound, 0.5).onFinishChange(() => {
            
            this.forest.removeblocks1();
            this.forest.addblocks1();
            this.reset1();
            
        });
        forestFolder.add(this.config.forest, 'block1starty', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
            this.forest.removeblocks1();
            this.forest.addblocks1();
            this.reset1();
            
        });
        forestFolder.add(this.config.forest, 'block1endx', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block1endy', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block2startx', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block2starty', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block2endx', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block2endy', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block3startx', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block3starty', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block3endx', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'block3endy', -bound, bound, 0.5).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'blockOrientation', 0, 360, 45).onFinishChange(() => {
            //this.reset();
        });
        forestFolder.add(this.config.forest, 'blockSpeed', 0, 360, 1).onFinishChange(() => {
            //this.reset();
        });
        // trees folder
        const treesFolder = forestFolder.addFolder('trees');
        const treesFolders = [
            treesFolder.add(this.config.forest.trees, 'levels', 0, 10, 1),
            treesFolder.add(this.config.forest.trees, 'twigScale', 0.0, 1.0, 0.05),
            treesFolder.add(this.config.forest.trees, 'homogeneity', 50, 100, 1),
            treesFolder.add(this.config.forest.trees, 'type', ['needle-leaf', 'broad-leaf', 'mixed-leaf'])
        ];

        // branching folder
        const branchingFolder = treesFolder.addFolder('branching');
        const branchingFolders = [
            branchingFolder.add(this.config.forest.trees.branching, 'initialBranchLength', 0.1, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'lengthFalloffFactor', 0.1, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'lengthFalloffPower', 0.1, 1.5, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'clumpMax', 0.0, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'clumpMin', 0.0, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'branchFactor', 2.0, 4.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'dropAmount', -1.0, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'growAmount', -1.0, 1.0, 0.05),
            branchingFolder.add(this.config.forest.trees.branching, 'sweepAmount', -1.0, 1.0, 0.05)
        ];

        // trunk folder
        const trunkFolder = treesFolder.addFolder('trunk');
        const trunkFolders = [
            trunkFolder.add(this.config.forest.trees.trunk, 'maxRadius', 0.05, 0.5, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'climbRate', 0.05, 2.0, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'trunkKink', 0.0, 0.5, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'treeSteps', 0.0, 20.0, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'taperRate', 0.7, 1.0, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'radiusFalloffRate', 0.5, 0.9, 0.05),
            trunkFolder.add(this.config.forest.trees.trunk, 'twistRate', 0.0, 20.0, 1),
            trunkFolder.add(this.config.forest.trees.trunk, 'trunkLength', 0.1, 5.0, 0.05)
        ];

        // trees folders
        [treesFolders, branchingFolders, trunkFolders].forEach((folders) => {
            folders.forEach((folder) => {
                folder.onChange(() => {
                    this.forest.addTrees();
                    

                });
            });
        });

        // persons folder
        const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'count', 0, 50, 1).onFinishChange(() => {
            
        });
        const activitiesFolder = personsFolder.addFolder('activities');
        Object.keys(this.config.forest.persons.activities).forEach((activity) => {
            activitiesFolder.add(this.config.forest.persons.activities, activity).onFinishChange(() => {
                this.forest.persons.forEach((person) => { person.setActivity(); });
              
            });
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'posx', -bound, bound,  1).onFinishChange(() => {
           
        });

        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'posy', -bound, bound,  1).onFinishChange(() => {
            
            
        });
        personsFolder.add(this.config.forest.persons, 'rotation', 0, 360,  1).onFinishChange(() => {
            
            
        });

         
        
        const personsFolder1 = forestFolder.addFolder('persons1');
        personsFolder1.add(this.config.forest.persons1, 'count1', 0, 50, 1).onFinishChange(() => {
           
        });

        // activities folder
        const activitiesFolder1 = personsFolder1.addFolder('activities1');
        Object.keys(this.config.forest.persons1.activities).forEach((activity) => {
            activitiesFolder1.add(this.config.forest.persons1.activities, activity).onFinishChange(() => {
               this.forest.persons1.forEach((person) => { person.setActivity(); });
               
            });
        })

        personsFolder1.add(this.config.forest.persons1, 'posx', -bound, bound,  1).onFinishChange(() => {
           
            
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder1.add(this.config.forest.persons1, 'posy', -bound, bound,  1).onFinishChange(() => {
          
            
        });
        personsFolder1.add(this.config.forest.persons1, 'rotation', 0, 360,  1).onFinishChange(() => {
          
            
        });
        
        
       
        const personsFolder2 = forestFolder.addFolder('persons2');
        personsFolder2.add(this.config.forest.persons2, 'count2', 0, 50, 1).onFinishChange(() => {
            
            
        });
        // activities folder
        const activitiesFolder2 = personsFolder2.addFolder('activities2');
        Object.keys(this.config.forest.persons2.activities).forEach((activity) => {
            activitiesFolder2.add(this.config.forest.persons2.activities, activity).onFinishChange(() => {
                this.forest.persons2.forEach((person) => { person.setActivity(); });
                
            });
        })
        personsFolder2.add(this.config.forest.persons2, 'posx', -bound, bound,  1).onFinishChange(() => {
           
           
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder2.add(this.config.forest.persons2, 'posy', 0, 50, 1).onFinishChange(() => {
          
            
        });
        personsFolder2.add(this.config.forest.persons2, 'rotation', 0, 360,  1).onFinishChange(() => {
          
            
        });
        

        


        // material folder
        const materialFolder = this.gui.addFolder('material');

        // color folder
        const colorFolder = materialFolder.addFolder('color');
        colorFolder.addColor(this.config.material.color, 'tree').onChange((v) => {
            this.forest.treeMaterial.color.setHex(v);
        });
        colorFolder.addColor(this.config.material.color, 'twig').onChange((v) => {
            Object.values(this.forest.twigMaterials).forEach((material) => {
                material.color.setHex(v);
            });
        });
        colorFolder.addColor(this.config.material.color, 'ground').onChange((v) => {
            this.forest.groundMaterial.color.setHex(v);
            this.drone.update();
        });
        colorFolder.addColor(this.config.material.color, 'plane').onChange((v) => {
            this.drone.camera.planeMaterial.color.setHex(v);
            this.drone.camera.clear();
            this.drone.update();
        });
        colorFolder.addColor(this.config.material.color, 'person').onChange((v) => {
            this.forest.persons.forEach((person) => {
                person.surfaceMaterial.color.setHex(v);
                person.jointsMaterial.color.setHex(shadeColor(v, 0.5));
            });
        });
        colorFolder.addColor(this.config.material.color, 'person1').onChange((v) => {
            this.forest.persons1.forEach((person1) => {
                person1.surfaceMaterial.color.setHex(v);
                person1.jointsMaterial.color.setHex(shadeColor(v, 0.5));
            });
        });
        colorFolder.addColor(this.config.material.color, 'person2').onChange((v) => {
            this.forest.persons2.forEach((person2) => {
                person2.surfaceMaterial.color.setHex(v);
                person2.jointsMaterial.color.setHex(shadeColor(v, 0.5));
            });
        });
        
        colorFolder.addColor(this.config.material.color, 'background').onChange(this.background.bind(this));
        colorFolder.addColor(this.config.material.color, 'block1').onFinishChange(this.reset.bind(this));
        colorFolder.addColor(this.config.material.color, 'block2').onFinishChange(this.reset.bind(this));
        colorFolder.addColor(this.config.material.color, 'block3').onFinishChange(this.reset.bind(this));

        // config preset
        this.gui.add(this.config, 'preset', this.presets).onChange((preset) => {
            this.gui.load.preset = preset;
            window.location.reload();
        });

        // config actions
        this.gui.add(this, 'capture');
        this.gui.add(this, 'export');
        this.gui.add(this, 'reset');
    }

    async update(event) {
        // get config from hash
        const hash = getHash();

        // set config from hash
        const changed = await setConfig(this.config, hash);

        // check event type
        const loadEvent = event.type === 'loaded';
        const hashEvent = event.type === 'hashchange';
        const changeEvent = loadEvent || (hashEvent && changed);
        if (!changeEvent) {
            return;
        }

        // update forest
        await this.forest.update();

        // reset camera
        await this.drone.camera.reset();

        await sleep(100);

        // execute capture
        if ('capture' in hash) {
            await this.capture();
        }

        // execute export
        if ('export' in hash) {
            await this.export();
        }

        // execute reset
        if ('reset' in hash) {
            await this.reset();
        }
    }

    async capture() {
        const date = new Date().yyyymmddhhmmss();

        var direction = [this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y,this.config.drone.drone3x,this.config.drone.drone3y,this.config.drone.prevdrone3x,this.config.drone.prevdrone3y,this.config.drone.drone4x,this.config.drone.drone4y,this.config.drone.prevdrone4x,this.config.drone.prevdrone4y,this.config.drone.drone5x,this.config.drone.drone5y,this.config.drone.prevdrone5x,this.config.drone.prevdrone5y,this.config.drone.drone6x,this.config.drone.drone6y,this.config.drone.prevdrone6x,this.config.drone.prevdrone6y,this.config.drone.drone7x,this.config.drone.drone7y,this.config.drone.prevdrone7x,this.config.drone.prevdrone7y,this.config.drone.drone8x,this.config.drone.drone8y,this.config.drone.prevdrone8x,this.config.drone.prevdrone8y,this.config.drone.drone9x,this.config.drone.drone9y,this.config.drone.prevdrone9x,this.config.drone.prevdrone9y,this.config.drone.drone10x,this.config.drone.drone10y,this.config.drone.prevdrone10x,this.config.drone.prevdrone10y,this.config.drone.drone11x,this.config.drone.drone11y,this.config.drone.prevdrone11x,this.config.drone.prevdrone11y,this.config.drone.drone12x,this.config.drone.drone12y,this.config.drone.prevdrone12x,this.config.drone.prevdrone12y,this.config.drone.drone13x,this.config.drone.drone13y,this.config.drone.prevdrone13x,this.config.drone.prevdrone13y,this.config.drone.drone14x,this.config.drone.drone14y,this.config.drone.prevdrone14x,this.config.drone.prevdrone14y,this.config.drone.drone15x,this.config.drone.drone15y,this.config.drone.prevdrone15x,this.config.drone.prevdrone15y,this.config.drone.drone16x,this.config.drone.drone16y,this.config.drone.prevdrone16x,this.config.drone.prevdrone16y,this.config.drone.drone17x,this.config.drone.drone17y,this.config.drone.prevdrone17x,this.config.drone.prevdrone17y,this.config.drone.drone18x,this.config.drone.drone18y,this.config.drone.prevdrone18x,this.config.drone.prevdrone18y,this.config.drone.drone19x,this.config.drone.drone19y,this.config.drone.prevdrone19x,this.config.drone.prevdrone19y,this.config.drone.drone20x,this.config.drone.drone20y,this.config.drone.prevdrone20x,this.config.drone.prevdrone20y,this.config.drone.drone21x,this.config.drone.drone21y,this.config.drone.prevdrone21x,this.config.drone.prevdrone21y,this.config.drone.drone22x,this.config.drone.drone22y,this.config.drone.prevdrone22x,this.config.drone.prevdrone22y,this.config.drone.drone23x,this.config.drone.drone23y,this.config.drone.prevdrone23x,this.config.drone.prevdrone23y,this.config.drone.drone24x,this.config.drone.drone24y,this.config.drone.prevdrone24x,this.config.drone.prevdrone24y,this.config.drone.drone25x,this.config.drone.drone25y,this.config.drone.prevdrone25x,this.config.drone.prevdrone25y,this.config.drone.drone26x,this.config.drone.drone26y,this.config.drone.prevdrone26x,this.config.drone.prevdrone26y,this.config.drone.drone27x,this.config.drone.drone27y,this.config.drone.prevdrone27x,this.config.drone.prevdrone27y,this.config.drone.drone28x,this.config.drone.drone28y,this.config.drone.prevdrone28x,this.config.drone.prevdrone28y,this.config.drone.drone29x,this.config.drone.drone29y,this.config.drone.prevdrone29x,this.config.drone.prevdrone29y,this.config.drone.drone30x,this.config.drone.drone30y,this.config.drone.prevdrone30x,this.config.drone.prevdrone30y,this.config.drone.drone31x,this.config.drone.drone31y,this.config.drone.prevdrone31x,this.config.drone.prevdrone31y,this.config.drone.drone32x,this.config.drone.drone32y,this.config.drone.prevdrone32x,this.config.drone.prevdrone32y,this.config.drone.drone33x,this.config.drone.drone33y,this.config.drone.prevdrone33x,this.config.drone.prevdrone33y,this.config.drone.drone34x,this.config.drone.drone34y,this.config.drone.prevdrone34x,this.config.drone.prevdrone34y,this.config.drone.drone35x,this.config.drone.drone35y,this.config.drone.prevdrone35x,this.config.drone.prevdrone35y,this.config.drone.drone36x,this.config.drone.drone36y,this.config.drone.prevdrone36x,this.config.drone.prevdrone36y,this.config.drone.drone37x,this.config.drone.drone37y,this.config.drone.prevdrone37x,this.config.drone.prevdrone37y,this.config.drone.drone38x,this.config.drone.drone38y,this.config.drone.prevdrone38x,this.config.drone.prevdrone38y,this.config.drone.drone39x,this.config.drone.drone39y,this.config.drone.prevdrone39x,this.config.drone.prevdrone39y,this.config.drone.drone40x,this.config.drone.drone40y,this.config.drone.prevdrone40x,this.config.drone.prevdrone40y,this.config.drone.drone41x,this.config.drone.drone41y,this.config.drone.prevdrone41x,this.config.drone.prevdrone41y,this.config.drone.drone42x,this.config.drone.drone42y,this.config.drone.prevdrone42x,this.config.drone.prevdrone42y,this.config.drone.drone43x,this.config.drone.drone43y,this.config.drone.prevdrone43x,this.config.drone.prevdrone43y,this.config.drone.drone44x,this.config.drone.drone44y,this.config.drone.prevdrone44x,this.config.drone.prevdrone44y,this.config.drone.drone45x,this.config.drone.drone45y,this.config.drone.prevdrone45x,this.config.drone.prevdrone45y,this.config.drone.drone46x,this.config.drone.drone46y,this.config.drone.prevdrone46x,this.config.drone.prevdrone46y,this.config.drone.drone47x,this.config.drone.drone47y,this.config.drone.prevdrone47x,this.config.drone.prevdrone47y,this.config.drone.drone48x,this.config.drone.drone48y,this.config.drone.prevdrone48x,this.config.drone.prevdrone48y,this.config.drone.drone49x,this.config.drone.drone49y,this.config.drone.prevdrone49x,this.config.drone.prevdrone49y]
        
        var alts = [this.config.drone.d2alt,this.config.drone.d3alt,this.config.drone.d4alt,this.config.drone.d5alt,this.config.drone.d6alt,this.config.drone.d7alt,this.config.drone.d8alt,this.config.drone.d9alt,this.config.drone.d10alt]
        await this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,this.config.drone.d1alt);
     
        for (var j = 0, n = 1; j < this.config.drone.noofdrones * 4 - 5, n < this.config.drone.noofdrones; j = j + 4, n = n + 1) {
            
            
            await this.drone[n].capture(direction[j],direction[j+1],direction[j+2],direction[j+3],alts[n-1]);
        
            
        
        
        }

        // export zip file
        await timeout(4000)
        await this.export(date);
   
    }
    

    async export(date) {
        
        const zip = new JSZip();

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        var filename = (urlParams.get('filename'))
        //console.log("filename: " + filename);

        
        //const zipName = `${this.stage.name}-${this.config.drone.dronex}.zip`;
        const zipName = `${filename}.zip`;
        // export status
        

        // add folders
        

        
        await this.forest.export(zip);
        await this.drone.export(zip,1);
        
        
        
       

        for (var i = 1; i < this.config.drone.noofdrones; i++) {
            await this.drone[i].export(zip,i+1);
            
            
        }
     
        // add config file
        await this.stage.export(zip);
        zip.file('config.json', JSON.stringify(this.config, null, 4));

        // compression status
        this.stage.status('Compressing', 0);

        // generate zip file
        await zip.generateAsync({
            type: 'blob',
            compression: 'DEFLATE',
            compressionOptions: { level: 6 }
        }, (zipMeta) => {
            this.stage.status('Compressing', Math.round(zipMeta.percent));
        }).then((zipData) => {
            // compression finished
            this.stage.status();

            // download zip file
            saveAs(zipData, zipName);

            // update hash for next array value
            const next = getHash('next') | 0;
            setHash('next', next + 1);
        
        });
        
    }
    

    async reset() {
        await this.forest.reset();
        await this.drone.reset();
        await this.drone1.reset();
        await this.drone2.reset();
        await this.drone3.reset();
        await this.drone4.reset();
        await this.drone5.reset();
        await this.drone6.reset();
        await this.drone7.reset();
        await this.drone8.reset();
        await this.drone9.reset();
   
    }
    async reset1() {
        await this.forest.reset();
        
   
    }

    automaticDownload(dronex_val,droney_val,drone1x_val,drone1y_val,drone2x_val,drone2y_val,drone3x_val,drone3y_val,drone4x_val,drone4y_val,drone5x_val,drone5y_val,drone6x_val,drone6y_val,drone7x_val,drone7y_val,drone8x_val,drone8y_val,drone9x_val,drone9y_val,person_x,person_y,personorientation,filename,prevdronex_val,prevdroney_val,prevdrone1x_val,prevdrone1y_val,prevdrone2x_val,prevdrone2y_val,prevdrone3x_val,prevdrone3y_val,prevdrone4x_val,prevdrone4y_val,prevdrone5x_val,prevdrone5y_val,prevdrone6x_val,prevdrone6y_val,prevdrone7x_val,prevdrone7y_val,prevdrone8x_val,prevdrone8y_val,prevdrone9x_val,prevdrone9y_val,d1alt,d2alt,d3alt,d4alt,d5alt,d6alt,d7alt,d8alt,d9alt,d10alt,leads){
    
        // wait till all trees are initialized with peridic checks
       
        var intervalId = setInterval(() => {
            
            // this checks if no element in trees (array) is undefined
            
            
            
            if(this.forest.trees.includes(undefined)==false){ // all trees are initialized
                this.config.drone.leader = leads
                this.config.drone.dronex = dronex_val
              
                this.config.drone.droney = droney_val
                
                this.config.drone.drone1x = drone1x_val
                this.config.drone.drone1y = drone1y_val
                this.config.drone.drone2x = drone2x_val
                this.config.drone.drone2y = drone2y_val
                this.config.drone.drone3x = drone3x_val
                this.config.drone.drone3y = drone3y_val
                this.config.drone.drone4x = drone4x_val
                this.config.drone.drone4y = drone4y_val
                this.config.drone.drone5x = drone5x_val
                this.config.drone.drone5y = drone5y_val
                this.config.drone.drone6x = drone6x_val
                this.config.drone.drone6y = drone6y_val
                this.config.drone.drone7x = drone7x_val
                this.config.drone.drone7y = drone7y_val
                this.config.drone.drone8x = drone8x_val
                this.config.drone.drone8y = drone8y_val
                this.config.drone.drone9x = drone9x_val
                this.config.drone.drone9y = drone9y_val
                
                this.config.forest.persons.posx = person_x
                this.config.forest.persons.posy = person_y
                this.config.forest.persons1.posx = person_x
                this.config.forest.persons1.posy = person_y
               
                this.config.drone.prevdronex = prevdronex_val
                this.config.drone.prevdroney = prevdroney_val
                this.config.drone.prevdrone1x = prevdrone1x_val
                this.config.drone.prevdrone1y = prevdrone1y_val
                this.config.drone.prevdrone2x = prevdrone2x_val
                this.config.drone.prevdrone2y = prevdrone2y_val
                this.config.drone.prevdrone3x = prevdrone3x_val
                this.config.drone.prevdrone3y = prevdrone3y_val
                this.config.drone.prevdrone4x = prevdrone4x_val
                this.config.drone.prevdrone4y = prevdrone4y_val
                this.config.drone.prevdrone5x = prevdrone5x_val
                this.config.drone.prevdrone5y = prevdrone5y_val
                this.config.drone.prevdrone6x = prevdrone6x_val
                this.config.drone.prevdrone6y = prevdrone6y_val
                this.config.drone.prevdrone7x = prevdrone7x_val
                this.config.drone.prevdrone7y = prevdrone7y_val
                this.config.drone.prevdrone8x = prevdrone8x_val
                this.config.drone.prevdrone8y = prevdrone8y_val
                this.config.drone.prevdrone9x = prevdrone9x_val
                this.config.drone.prevdrone9y = prevdrone9y_val
                
               
                this.config.drone.d1alt = d1alt
                this.config.drone.d2alt = d2alt
                this.config.drone.d3alt = d3alt
                this.config.drone.d4alt = d4alt
                this.config.drone.d5alt = d5alt
                this.config.drone.d6alt = d6alt
                this.config.drone.d7alt = d7alt
                this.config.drone.d8alt = d8alt
                this.config.drone.d9alt = d9alt
                this.config.drone.d10alt = d10alt
                
                const date = new Date().yyyymmddhhmmss();
                this.capture();
                
                clearInterval(intervalId); // stop periodic checks

                // drone reached event: 'droneReached'
                this.drone.root.addEventListener( 'droneReached', () => {
                    //this.export();        
                }, false);
            }

        }, 25000);
    }
}


function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
var view = null;

document.addEventListener('DOMContentLoaded', async () => {
    // make Math.random() globally predictable
    Math.seedrandom(document.title);

    // load preset and config
    const preset = await getPreset(configs);
    const config = await getConfig(preset);

    // init view
    view = new View(document.querySelector('#top'), config, true);
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    var person_x = parseFloat(urlParams.get('personx')) 
    var person_y = parseFloat(urlParams.get('persony'))
    var personorientation = parseFloat(urlParams.get('personorientation'))
    var filename = (urlParams.get('filename'))
    
   
    console.log("filename: " + filename);
    //console.log("fine")
    var dronex_val = parseFloat(urlParams.get('drone1x')) 
    var droney_val = parseFloat(urlParams.get('drone1y')) 
    var drone1x_val = parseFloat(urlParams.get('drone2x')) 
    var drone1y_val = parseFloat(urlParams.get('drone2y')) 
    var drone2x_val = parseFloat(urlParams.get('drone3x')) 
    var drone2y_val = parseFloat(urlParams.get('drone3y')) 
    var drone3x_val = parseFloat(urlParams.get('drone4x')) 
    var drone3y_val = parseFloat(urlParams.get('drone4y')) 
    var drone4x_val = parseFloat(urlParams.get('drone5x')) 
    var drone4y_val = parseFloat(urlParams.get('drone5y')) 
    var drone5x_val = parseFloat(urlParams.get('drone6x')) 
    var drone5y_val = parseFloat(urlParams.get('drone6y')) 
    var drone6x_val = parseFloat(urlParams.get('drone7x')) 
    var drone6y_val = parseFloat(urlParams.get('drone7y')) 
    var drone7x_val = parseFloat(urlParams.get('drone8x')) 
    var drone7y_val = parseFloat(urlParams.get('drone8y')) 
    var drone8x_val = parseFloat(urlParams.get('drone9x')) 
    var drone8y_val = parseFloat(urlParams.get('drone9y')) 
    var drone9x_val = parseFloat(urlParams.get('drone10x')) 
    var drone9y_val = parseFloat(urlParams.get('drone10y'))

    var prevdronex_val = parseFloat(urlParams.get('prevdrone1x')) 
    var prevdroney_val = parseFloat(urlParams.get('prevdrone1y')) 
    var prevdrone1x_val = parseFloat(urlParams.get('prevdrone2x')) 
    var prevdrone1y_val = parseFloat(urlParams.get('prevdrone2y')) 
    var prevdrone2x_val = parseFloat(urlParams.get('prevdrone3x')) 
    var prevdrone2y_val = parseFloat(urlParams.get('prevdrone3y')) 
    var prevdrone3x_val = parseFloat(urlParams.get('prevdrone4x')) 
    var prevdrone3y_val = parseFloat(urlParams.get('prevdrone4y')) 
    var prevdrone4x_val = parseFloat(urlParams.get('prevdrone5x')) 
    var prevdrone4y_val = parseFloat(urlParams.get('prevdrone5y')) 
    var prevdrone5x_val = parseFloat(urlParams.get('prevdrone6x')) 
    var prevdrone5y_val = parseFloat(urlParams.get('prevdrone6y')) 
    var prevdrone6x_val = parseFloat(urlParams.get('prevdrone7x')) 
    var prevdrone6y_val = parseFloat(urlParams.get('prevdrone7y')) 
    var prevdrone7x_val = parseFloat(urlParams.get('prevdrone8x')) 
    var prevdrone7y_val = parseFloat(urlParams.get('prevdrone8y')) 
    var prevdrone8x_val = parseFloat(urlParams.get('prevdrone9x')) 
    var prevdrone8y_val = parseFloat(urlParams.get('prevdrone9y')) 
    var prevdrone9x_val = parseFloat(urlParams.get('prevdrone10x')) 
    var prevdrone9y_val = parseFloat(urlParams.get('prevdrone10y')) 
    
    var d1alt = parseFloat(urlParams.get('altd1'))
    var d2alt = parseFloat(urlParams.get('altd2'))
    var d3alt = parseFloat(urlParams.get('altd3'))
    var d4alt = parseFloat(urlParams.get('altd4'))
    var d5alt = parseFloat(urlParams.get('altd5'))
    var d6alt = parseFloat(urlParams.get('altd6'))
    var d7alt = parseFloat(urlParams.get('altd7'))
    var d8alt = parseFloat(urlParams.get('altd8'))
    var d9alt = parseFloat(urlParams.get('altd9'))
    var d10alt = parseFloat(urlParams.get('altd10'))
    var leads = parseFloat(urlParams.get('leader'))
   
    await timeout(20000)
    view.automaticDownload(dronex_val,droney_val,drone1x_val,drone1y_val,drone2x_val,drone2y_val,drone3x_val,drone3y_val,drone4x_val,drone4y_val,drone5x_val,drone5y_val,drone6x_val,drone6y_val,drone7x_val,drone7y_val,drone8x_val,drone8y_val,drone9x_val,drone9y_val,person_x,person_y,personorientation,filename,prevdronex_val,prevdroney_val,prevdrone1x_val,prevdrone1y_val,prevdrone2x_val,prevdrone2y_val,prevdrone3x_val,prevdrone3y_val,prevdrone4x_val,prevdrone4y_val,prevdrone5x_val,prevdrone5y_val,prevdrone6x_val,prevdrone6y_val,prevdrone7x_val,prevdrone7y_val,prevdrone8x_val,prevdrone8y_val,prevdrone9x_val,prevdrone9y_val,d1alt,d2alt,d3alt,d4alt,d5alt,d6alt,d7alt,d8alt,d9alt,d10alt,leads);
});

