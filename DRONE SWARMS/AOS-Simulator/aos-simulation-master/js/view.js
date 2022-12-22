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
            //this.drone[1] = this.drone[2] = this.drone[3] = this.drone[4] = this.drone[5] = this.drone[6] = this.drone[7]= this.drone[8]= this.drone[9] =  new Drone(this.forest, 0);
            //this.drone[10] = this.drone[11] = this.drone[12] = this.drone[13] = this.drone[14] = this.drone[15] = this.drone[16] = this.drone[17]= this.drone[18]= this.drone[19] =  new Drone1(this.forest, 0);
            

            for (var j = 1; j < this.config.drone.noofdrones; j++) {
                this.drone[j] = new Drone(this.forest, 0);;
            
            
            }
           
            //this.drone3 = new Drone(this.forest, 0);
            //this.drone4 = new Drone(this.forest, 0);
            //this.drone5 = new Drone(this.forest, 0);
            //this.drone6 = new Drone(this.forest, 0);
            //this.drone7 = new Drone(this.forest, 0);
            //this.drone8 = new Drone(this.forest, 0);
            //this.drone9 = new Drone(this.forest, 0);
            
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
                    //this.forest.addblocks1();
                    //this.forest.addblocks2();
                    //this.forest.addblocks3();

                });
            });
        });

        // persons folder
        const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'count', 0, 50, 1).onFinishChange(() => {
            //this.forest.removePersons();
            //this.forest.addPersons();
            
        });
        const activitiesFolder = personsFolder.addFolder('activities');
        Object.keys(this.config.forest.persons.activities).forEach((activity) => {
            activitiesFolder.add(this.config.forest.persons.activities, activity).onFinishChange(() => {
                this.forest.persons.forEach((person) => { person.setActivity(); });
                //this.forest.removePersons();
                //this.forest.addPersons();
            });
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'posx', -bound, bound,  1).onFinishChange(() => {
            //this.forest.removePersons();
            //this.forest.addPersons();
            
        });

        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder.add(this.config.forest.persons, 'posy', -bound, bound,  1).onFinishChange(() => {
            //this.forest.removePersons();
            //this.forest.addPersons();
            
        });
        personsFolder.add(this.config.forest.persons, 'rotation', 0, 360,  1).onFinishChange(() => {
            //this.forest.removePersons();
            //this.forest.addPersons();
            
        });

         
        
        const personsFolder1 = forestFolder.addFolder('persons1');
        personsFolder1.add(this.config.forest.persons1, 'count1', 0, 50, 1).onFinishChange(() => {
            //this.forest.removePersons1();
            //this.forest.addPersons1();
            
        });

        // activities folder
        const activitiesFolder1 = personsFolder1.addFolder('activities1');
        Object.keys(this.config.forest.persons1.activities).forEach((activity) => {
            activitiesFolder1.add(this.config.forest.persons1.activities, activity).onFinishChange(() => {
               this.forest.persons1.forEach((person) => { person.setActivity(); });
               //this.forest.removePersons1();
               //this.forest.addPersons1();
            });
        })

        personsFolder1.add(this.config.forest.persons1, 'posx', -bound, bound,  1).onFinishChange(() => {
            //this.forest.removePersons1();
            //this.forest.addPersons1();
            
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder1.add(this.config.forest.persons1, 'posy', -bound, bound,  1).onFinishChange(() => {
            //this.forest.removePersons1();
            //this.forest.addPersons1();
            
        });
        personsFolder1.add(this.config.forest.persons1, 'rotation', 0, 360,  1).onFinishChange(() => {
            //this.forest.removePersons1();
            //this.forest.addPersons1();
            
        });
        
        
       
        const personsFolder2 = forestFolder.addFolder('persons2');
        personsFolder2.add(this.config.forest.persons2, 'count2', 0, 50, 1).onFinishChange(() => {
            //this.forest.removePersons2();
            //this.forest.addPersons2();
            
        });
        // activities folder
        const activitiesFolder2 = personsFolder2.addFolder('activities2');
        Object.keys(this.config.forest.persons2.activities).forEach((activity) => {
            activitiesFolder2.add(this.config.forest.persons2.activities, activity).onFinishChange(() => {
                this.forest.persons2.forEach((person) => { person.setActivity(); });
                //this.forest.removePersons2();
                //this.forest.addPersons2();
            });
        })
        personsFolder2.add(this.config.forest.persons2, 'posx', -bound, bound,  1).onFinishChange(() => {
            //this.forest.removePersons2();
            //this.forest.addPersons2();
           // 
        });
        //const personsFolder = forestFolder.addFolder('persons');
        personsFolder2.add(this.config.forest.persons2, 'posy', 0, 50, 1).onFinishChange(() => {
            //this.forest.removePersons2();
           // this.forest.addPersons2();
            
        });
        personsFolder2.add(this.config.forest.persons2, 'rotation', 0, 360,  1).onFinishChange(() => {
           // this.forest.removePersons2();
           // this.forest.addPersons2();
            
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

        // update drone
        //await this.drone.setEastWest(this.config.drone.eastWest);
       //await this.drone.setNorthSouth(this.config.drone.northSouth);

        // reset camera
        await this.drone.camera.reset();

        // reset persons
        
        //this.forest.persons1.forEach((person) => { person.setActivity(); });
        //this.forest.persons2.forEach((person) => { person.setActivity(); });
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

        // reset persons
       // await this.forest.clear();

        // reset drone
        //await this.drone.reset();

        // capture images  //Enable the line below to activate all drones & make changes in async export
        //await Promise.all([this.drone.capture(), this.drone1.capture(), this.drone2.capture(), this.drone3.capture(), this.drone4.capture(), this.drone5.capture(), this.drone6.capture(), this.drone7.capture(),this.drone8.capture(),this.drone9.capture()]);
        //await this.drone1.capture() && this.drone1.capture();
        //await this.drone.capture();
        //await Promise.all([this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney), this.drone1.capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y),this.drone2.capture(this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y),this.drone3.capture(this.config.drone.drone3x,this.config.drone.drone3y,this.config.drone.prevdrone3x,this.config.drone.prevdrone3y),this.drone4.capture(this.config.drone.drone4x,this.config.drone.drone4y,this.config.drone.prevdrone4x,this.config.drone.prevdrone4y),this.drone5.capture(this.config.drone.drone5x,this.config.drone.drone5y,this.config.drone.prevdrone5x,this.config.drone.prevdrone5y),this.drone6.capture(this.config.drone.drone6x,this.config.drone.drone6y,this.config.drone.prevdrone6x,this.config.drone.prevdrone6y),this.drone7.capture(this.config.drone.drone7x,this.config.drone.drone7y,this.config.drone.prevdrone7x,this.config.drone.prevdrone7y),this.drone8.capture(this.config.drone.drone8x,this.config.drone.drone8y,this.config.drone.prevdrone8x,this.config.drone.prevdrone8y),this.drone9.capture(this.config.drone.drone9x,this.config.drone.drone9y,this.config.drone.prevdrone9x,this.config.drone.prevdrone9y)])
    
        //await Promise.all([this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney), this.drone[1].capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y),this.drone[2].capture(this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y)])
        

        var direction = [this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y,this.config.drone.drone3x,this.config.drone.drone3y,this.config.drone.prevdrone3x,this.config.drone.prevdrone3y,this.config.drone.drone4x,this.config.drone.drone4y,this.config.drone.prevdrone4x,this.config.drone.prevdrone4y,this.config.drone.drone5x,this.config.drone.drone5y,this.config.drone.prevdrone5x,this.config.drone.prevdrone5y,this.config.drone.drone6x,this.config.drone.drone6y,this.config.drone.prevdrone6x,this.config.drone.prevdrone6y,this.config.drone.drone7x,this.config.drone.drone7y,this.config.drone.prevdrone7x,this.config.drone.prevdrone7y,this.config.drone.drone8x,this.config.drone.drone8y,this.config.drone.prevdrone8x,this.config.drone.prevdrone8y,this.config.drone.drone9x,this.config.drone.drone9y,this.config.drone.prevdrone9x,this.config.drone.prevdrone9y,this.config.drone.drone10x,this.config.drone.drone10y,this.config.drone.prevdrone10x,this.config.drone.prevdrone10y,this.config.drone.drone11x,this.config.drone.drone11y,this.config.drone.prevdrone11x,this.config.drone.prevdrone11y,this.config.drone.drone12x,this.config.drone.drone12y,this.config.drone.prevdrone12x,this.config.drone.prevdrone12y,this.config.drone.drone13x,this.config.drone.drone13y,this.config.drone.prevdrone13x,this.config.drone.prevdrone13y,this.config.drone.drone14x,this.config.drone.drone14y,this.config.drone.prevdrone14x,this.config.drone.prevdrone14y,this.config.drone.drone15x,this.config.drone.drone15y,this.config.drone.prevdrone15x,this.config.drone.prevdrone15y,this.config.drone.drone16x,this.config.drone.drone16y,this.config.drone.prevdrone16x,this.config.drone.prevdrone16y,this.config.drone.drone17x,this.config.drone.drone17y,this.config.drone.prevdrone17x,this.config.drone.prevdrone17y,this.config.drone.drone18x,this.config.drone.drone18y,this.config.drone.prevdrone18x,this.config.drone.prevdrone18y,this.config.drone.drone19x,this.config.drone.drone19y,this.config.drone.prevdrone19x,this.config.drone.prevdrone19y,this.config.drone.drone20x,this.config.drone.drone20y,this.config.drone.prevdrone20x,this.config.drone.prevdrone20y,this.config.drone.drone21x,this.config.drone.drone21y,this.config.drone.prevdrone21x,this.config.drone.prevdrone21y,this.config.drone.drone22x,this.config.drone.drone22y,this.config.drone.prevdrone22x,this.config.drone.prevdrone22y,this.config.drone.drone23x,this.config.drone.drone23y,this.config.drone.prevdrone23x,this.config.drone.prevdrone23y,this.config.drone.drone24x,this.config.drone.drone24y,this.config.drone.prevdrone24x,this.config.drone.prevdrone24y,this.config.drone.drone25x,this.config.drone.drone25y,this.config.drone.prevdrone25x,this.config.drone.prevdrone25y,this.config.drone.drone26x,this.config.drone.drone26y,this.config.drone.prevdrone26x,this.config.drone.prevdrone26y,this.config.drone.drone27x,this.config.drone.drone27y,this.config.drone.prevdrone27x,this.config.drone.prevdrone27y,this.config.drone.drone28x,this.config.drone.drone28y,this.config.drone.prevdrone28x,this.config.drone.prevdrone28y,this.config.drone.drone29x,this.config.drone.drone29y,this.config.drone.prevdrone29x,this.config.drone.prevdrone29y,this.config.drone.drone30x,this.config.drone.drone30y,this.config.drone.prevdrone30x,this.config.drone.prevdrone30y,this.config.drone.drone31x,this.config.drone.drone31y,this.config.drone.prevdrone31x,this.config.drone.prevdrone31y,this.config.drone.drone32x,this.config.drone.drone32y,this.config.drone.prevdrone32x,this.config.drone.prevdrone32y,this.config.drone.drone33x,this.config.drone.drone33y,this.config.drone.prevdrone33x,this.config.drone.prevdrone33y,this.config.drone.drone34x,this.config.drone.drone34y,this.config.drone.prevdrone34x,this.config.drone.prevdrone34y,this.config.drone.drone35x,this.config.drone.drone35y,this.config.drone.prevdrone35x,this.config.drone.prevdrone35y,this.config.drone.drone36x,this.config.drone.drone36y,this.config.drone.prevdrone36x,this.config.drone.prevdrone36y,this.config.drone.drone37x,this.config.drone.drone37y,this.config.drone.prevdrone37x,this.config.drone.prevdrone37y,this.config.drone.drone38x,this.config.drone.drone38y,this.config.drone.prevdrone38x,this.config.drone.prevdrone38y,this.config.drone.drone39x,this.config.drone.drone39y,this.config.drone.prevdrone39x,this.config.drone.prevdrone39y,this.config.drone.drone40x,this.config.drone.drone40y,this.config.drone.prevdrone40x,this.config.drone.prevdrone40y,this.config.drone.drone41x,this.config.drone.drone41y,this.config.drone.prevdrone41x,this.config.drone.prevdrone41y,this.config.drone.drone42x,this.config.drone.drone42y,this.config.drone.prevdrone42x,this.config.drone.prevdrone42y,this.config.drone.drone43x,this.config.drone.drone43y,this.config.drone.prevdrone43x,this.config.drone.prevdrone43y,this.config.drone.drone44x,this.config.drone.drone44y,this.config.drone.prevdrone44x,this.config.drone.prevdrone44y,this.config.drone.drone45x,this.config.drone.drone45y,this.config.drone.prevdrone45x,this.config.drone.prevdrone45y,this.config.drone.drone46x,this.config.drone.drone46y,this.config.drone.prevdrone46x,this.config.drone.prevdrone46y,this.config.drone.drone47x,this.config.drone.drone47y,this.config.drone.prevdrone47x,this.config.drone.prevdrone47y,this.config.drone.drone48x,this.config.drone.drone48y,this.config.drone.prevdrone48x,this.config.drone.prevdrone48y,this.config.drone.drone49x,this.config.drone.drone49y,this.config.drone.prevdrone49x,this.config.drone.prevdrone49y]
        
        var alts = [this.config.drone.d2alt,this.config.drone.d3alt,this.config.drone.d4alt,this.config.drone.d5alt,this.config.drone.d6alt,this.config.drone.d7alt,this.config.drone.d8alt,this.config.drone.d9alt,this.config.drone.d10alt]
        await this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,this.config.drone.d1alt);
        
        
        //await  Promise.all([this.drone[1].capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,this.config.drone.d2alt)]);
        
        //await sleep(1000)



        //await  Promise.all([this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,35),this.drone[1].capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,36)]);

        for (var j = 0, n = 1; j < this.config.drone.noofdrones * 4 - 5, n < this.config.drone.noofdrones; j = j + 4, n = n + 1) {
            
            
            await this.drone[n].capture(direction[j],direction[j+1],direction[j+2],direction[j+3],alts[n-1]);
        
            
        
        
        }
        

       
        //await  Promise.all([this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,this.config.drone.d1alt),this.drone[1].capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,this.config.drone.d2alt),this.drone[2].capture(this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y,this.config.drone.d3alt),this.drone[3].capture(this.config.drone.drone3x,this.config.drone.drone3y,this.config.drone.prevdrone3x,this.config.drone.prevdrone3y,this.config.drone.d4alt),this.drone[4].capture(this.config.drone.drone4x,this.config.drone.drone4y,this.config.drone.prevdrone4x,this.config.drone.prevdrone4y,this.config.drone.d5alt),this.drone[5].capture(this.config.drone.drone5x,this.config.drone.drone5y,this.config.drone.prevdrone5x,this.config.drone.prevdrone5y,this.config.drone.d6alt),this.drone[6].capture(this.config.drone.drone6x,this.config.drone.drone6y,this.config.drone.prevdrone6x,this.config.drone.prevdrone6y,this.config.drone.d7alt),this.drone[7].capture(this.config.drone.drone7x,this.config.drone.drone7y,this.config.drone.prevdrone7x,this.config.drone.prevdrone7y,this.config.drone.d8alt),this.drone[8].capture(this.config.drone.drone8x,this.config.drone.drone8y,this.config.drone.prevdrone8x,this.config.drone.prevdrone8y,this.config.drone.d9alt),this.drone[9].capture(this.config.drone.drone9x,this.config.drone.drone9y,this.config.drone.prevdrone9x,this.config.drone.prevdrone9y,this.config.drone.d10alt)]);
        //await sleep(4000);

      
       // await  Promise.all([this.drone[10].capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,this.config.drone.d1alt),this.drone[11].capture(this.config.drone.drone1x,this.config.drone.drone1y,this.config.drone.prevdrone1x,this.config.drone.prevdrone1y,this.config.drone.d2alt),this.drone[12].capture(this.config.drone.drone2x,this.config.drone.drone2y,this.config.drone.prevdrone2x,this.config.drone.prevdrone2y,this.config.drone.d3alt),this.drone[13].capture(this.config.drone.drone3x,this.config.drone.drone3y,this.config.drone.prevdrone3x,this.config.drone.prevdrone3y,this.config.drone.d4alt),this.drone[14].capture(this.config.drone.drone4x,this.config.drone.drone4y,this.config.drone.prevdrone4x,this.config.drone.prevdrone4y,this.config.drone.d5alt),this.drone[15].capture(this.config.drone.drone5x,this.config.drone.drone5y,this.config.drone.prevdrone5x,this.config.drone.prevdrone5y,this.config.drone.d6alt),this.drone[16].capture(this.config.drone.drone6x,this.config.drone.drone6y,this.config.drone.prevdrone6x,this.config.drone.prevdrone6y,this.config.drone.d7alt),this.drone[17].capture(this.config.drone.drone7x,this.config.drone.drone7y,this.config.drone.prevdrone7x,this.config.drone.prevdrone7y,this.config.drone.d8alt),this.drone[18].capture(this.config.drone.drone8x,this.config.drone.drone8y,this.config.drone.prevdrone8x,this.config.drone.prevdrone8y,this.config.drone.d9alt),this.drone[19].capture(this.config.drone.drone9x,this.config.drone.drone9y,this.config.drone.prevdrone9x,this.config.drone.prevdrone9y,this.config.drone.d10alt)]);



        //this.drone.awesome(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney,this.config.drone.d1alt);
        //for (var j = 0, n = 1; j < this.config.drone.noofdrones * 4 - 5, n < this.config.drone.noofdrones; j = j + 4, n = n + 1) {
            
            
        //    this.drone[n].awesome(direction[j],direction[j+1],direction[j+2],direction[j+3],alts[n-1]);
            
        
        
        //}

        //var direction12 = [this.config.drone.dronex,this.config.drone.drone1x,this.config.drone.drone2x,this.config.drone.drone3x,this.config.drone.drone4x,this.config.drone.drone5x,this.config.drone.drone6x,this.config.drone.drone7x,this.config.drone.drone8x,this.config.drone.drone9x,this.config.drone.droney,this.config.drone.drone1y,this.config.drone.drone2y,this.config.drone.drone3y,this.config.drone.drone4y,this.config.drone.drone5y,this.config.drone.drone6y,this.config.drone.drone7y,this.config.drone.drone8y,this.config.drone.drone9y,this.config.drone.d1alt,this.config.drone.d2alt,this.config.drone.d3alt,this.config.drone.d4alt,this.config.drone.d5alt,this.config.drone.d6alt,this.config.drone.d7alt,this.config.drone.d8alt,this.config.drone.d9alt,this.config.drone.d10alt]


        //await this.drone.robuster(direction12[this.config.drone.leader],direction12[this.config.drone.leader+10],direction12[this.config.drone.leader+20]);

             
    //this.forest.addPrsons();
        

        // reset stage camera
        //await this.stage.reset();

        // export zip file
        await timeout(4000)
        await this.export(date);
        
        //await this.export1(date);
        // await this.export2(date);
        // await this.export3(date);
        // await this.export4(date);
        // await this.export5(date);
        // await this.export6(date);
        // await this.export7(date);
        // await this.export8(date);
        // await this.export9(date);
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
            //this.c = [this.drone1.export(zip,2),this.drone2.export(zip,3)];
            //this.c[i];
            //var a = "this.drone.export(zip,2)"
            //var b = i-1
            //var position3 = 10;
            //var output = [a.slice(0, position3), b, a.slice(position3)].join('');
            
            //console.log(output);
            
            
        }
       // await this.drone.export(zip,1);
        //await this.drone1.export(zip,2);
        //await this.drone2.export(zip,3);
        //await this.drone3.export(zip,4);
        //await this.drone4.export(zip,5);
        //await this.drone5.export(zip,6);
        //await this.drone6.export(zip,7);
        //await this.drone7.export(zip,8);
        //await this.drone8.export(zip,9);
        //await this.drone9.export(zip,10);
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

    //automaticDownload(dronex_val,droney_val,drone1x_val,drone1y_val,drone2x_val,drone2y_val,drone3x_val,drone3y_val,drone4x_val,drone4y_val,drone5x_val,drone5y_val,drone6x_val,drone6y_val,drone7x_val,drone7y_val,drone8x_val,drone8y_val,drone9x_val,drone9y_val,person_x,person_y,filename,prevdronex_val,prevdroney_val,prevdrone1x_val,prevdrone1y_val,prevdrone2x_val,prevdrone2y_val,prevdrone3x_val,prevdrone3y_val,prevdrone4x_val,prevdrone4y_val,prevdrone5x_val,prevdrone5y_val,prevdrone6x_val,prevdrone6y_val,prevdrone7x_val,prevdrone7y_val,prevdrone8x_val,prevdrone8y_val,prevdrone9x_val,prevdrone9y_val) {
    automaticDownload(dronex_val,droney_val,drone1x_val,drone1y_val,drone2x_val,drone2y_val,drone3x_val,drone3y_val,drone4x_val,drone4y_val,drone5x_val,drone5y_val,drone6x_val,drone6y_val,drone7x_val,drone7y_val,drone8x_val,drone8y_val,drone9x_val,drone9y_val,person_x,person_y,personorientation,filename,prevdronex_val,prevdroney_val,prevdrone1x_val,prevdrone1y_val,prevdrone2x_val,prevdrone2y_val,prevdrone3x_val,prevdrone3y_val,prevdrone4x_val,prevdrone4y_val,prevdrone5x_val,prevdrone5y_val,prevdrone6x_val,prevdrone6y_val,prevdrone7x_val,prevdrone7y_val,prevdrone8x_val,prevdrone8y_val,prevdrone9x_val,prevdrone9y_val,drone10x_val,drone10y_val,drone11x_val,drone11y_val,drone12x_val,drone12y_val,drone13x_val,drone13y_val,drone14x_val,drone14y_val,drone15x_val,drone15y_val,drone16x_val,drone16y_val,drone17x_val,drone17y_val,drone18x_val,drone18y_val,drone19x_val,drone19y_val,drone20x_val,drone20y_val,drone21x_val,drone21y_val,drone22x_val,drone22y_val,drone23x_val,drone23y_val,drone24x_val,drone24y_val,drone25x_val,drone25y_val,drone26x_val,drone26y_val,drone27x_val,drone27y_val,drone28x_val,drone28y_val,drone29x_val,drone29y_val,drone30x_val,drone30y_val,drone31x_val,drone31y_val,drone32x_val,drone32y_val,drone33x_val,drone33y_val,drone34x_val,drone34y_val,drone35x_val,drone35y_val,drone36x_val,drone36y_val,drone37x_val,drone37y_val,drone38x_val,drone38y_val,drone39x_val,drone39y_val,drone40x_val,drone40y_val,drone41x_val,drone41y_val,drone42x_val,drone42y_val,drone43x_val,drone43y_val,drone44x_val,drone44y_val,drone45x_val,drone45y_val,drone46x_val,drone46y_val,drone47x_val,drone47y_val,drone48x_val,drone48y_val,drone49x_val,drone49y_val,prevdrone10x_val,prevdrone10y_val,prevdrone11x_val,prevdrone11y_val,prevdrone12x_val,prevdrone12y_val,prevdrone13x_val,prevdrone13y_val,prevdrone14x_val,prevdrone14y_val,prevdrone15x_val,prevdrone15y_val,prevdrone16x_val,prevdrone16y_val,prevdrone17x_val,prevdrone17y_val,prevdrone18x_val,prevdrone18y_val,prevdrone19x_val,prevdrone19y_val,prevdrone20x_val,prevdrone20y_val,prevdrone21x_val,prevdrone21y_val,prevdrone22x_val,prevdrone22y_val,prevdrone23x_val,prevdrone23y_val,prevdrone24x_val,prevdrone24y_val,prevdrone25x_val,prevdrone25y_val,prevdrone26x_val,prevdrone26y_val,prevdrone27x_val,prevdrone27y_val,prevdrone28x_val,prevdrone28y_val,prevdrone29x_val,prevdrone29y_val,prevdrone30x_val,prevdrone30y_val,prevdrone31x_val,prevdrone31y_val,prevdrone32x_val,prevdrone32y_val,prevdrone33x_val,prevdrone33y_val,prevdrone34x_val,prevdrone34y_val,prevdrone35x_val,prevdrone35y_val,prevdrone36x_val,prevdrone36y_val,prevdrone37x_val,prevdrone37y_val,prevdrone38x_val,prevdrone38y_val,prevdrone39x_val,prevdrone39y_val,prevdrone40x_val,prevdrone40y_val,prevdrone41x_val,prevdrone41y_val,prevdrone42x_val,prevdrone42y_val,prevdrone43x_val,prevdrone43y_val,prevdrone44x_val,prevdrone44y_val,prevdrone45x_val,prevdrone45y_val,prevdrone46x_val,prevdrone46y_val,prevdrone47x_val,prevdrone47y_val,prevdrone48x_val,prevdrone48y_val,prevdrone49x_val,prevdrone49y_val,d1alt,d2alt,d3alt,d4alt,d5alt,d6alt,d7alt,d8alt,d9alt,d10alt,leads){
    
        // wait till all trees are initialized with peridic checks
       
        var intervalId = setInterval(() => {
            
            // this checks if no element in trees (array) is undefined
            // very hacky, maybe there is a better way to work for the workers???
            //console.log( this.forest.trees.includes(undefined)
            
            
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
                this.config.drone.drone10x = drone10x_val
                this.config.drone.drone10y = drone10y_val
                this.config.drone.drone11x = drone11x_val
                this.config.drone.drone11y = drone11y_val
                this.config.drone.drone12x = drone12x_val
                this.config.drone.drone12y = drone12y_val
                this.config.drone.drone13x = drone13x_val
                this.config.drone.drone13y = drone13y_val
                this.config.drone.drone14x = drone14x_val
                this.config.drone.drone14y = drone14y_val
                this.config.drone.drone15x = drone15x_val
                this.config.drone.drone15y = drone15y_val
                this.config.drone.drone16x = drone16x_val
                this.config.drone.drone16y = drone16y_val
                this.config.drone.drone17x = drone17x_val
                this.config.drone.drone17y = drone17y_val
                this.config.drone.drone18x = drone18x_val
                this.config.drone.drone18y = drone18y_val
                this.config.drone.drone19x = drone19x_val
                this.config.drone.drone19y = drone19y_val
                this.config.drone.drone20x = drone20x_val
                this.config.drone.drone20y = drone20y_val
                this.config.drone.drone21x = drone21x_val
                this.config.drone.drone21y = drone21y_val
                this.config.drone.drone22x = drone22x_val
                this.config.drone.drone22y = drone22y_val
                this.config.drone.drone23x = drone23x_val
                this.config.drone.drone23y = drone23y_val
                this.config.drone.drone24x = drone24x_val
                this.config.drone.drone24y = drone24y_val
                this.config.drone.drone25x = drone25x_val
                this.config.drone.drone25y = drone25y_val
                this.config.drone.drone26x = drone26x_val
                this.config.drone.drone26y = drone26y_val
                this.config.drone.drone27x = drone27x_val
                this.config.drone.drone27y = drone27y_val
                this.config.drone.drone28x = drone28x_val
                this.config.drone.drone28y = drone28y_val
                this.config.drone.drone29x = drone29x_val
                this.config.drone.drone29y = drone29y_val
                this.config.drone.drone30x = drone30x_val
                this.config.drone.drone30y = drone30y_val
                this.config.drone.drone31x = drone31x_val
                this.config.drone.drone31y = drone31y_val
                this.config.drone.drone32x = drone32x_val
                this.config.drone.drone32y = drone32y_val
                this.config.drone.drone33x = drone33x_val
                this.config.drone.drone33y = drone33y_val
                this.config.drone.drone34x = drone34x_val
                this.config.drone.drone34y = drone34y_val
                this.config.drone.drone35x = drone35x_val
                this.config.drone.drone35y = drone35y_val
                this.config.drone.drone36x = drone36x_val
                this.config.drone.drone36y = drone36y_val
                this.config.drone.drone37x = drone37x_val
                this.config.drone.drone37y = drone37y_val
                this.config.drone.drone38x = drone38x_val
                this.config.drone.drone38y = drone38y_val
                this.config.drone.drone39x = drone39x_val
                this.config.drone.drone39y = drone39y_val
                this.config.drone.drone40x = drone40x_val
                this.config.drone.drone40y = drone40y_val
                this.config.drone.drone41x = drone41x_val
                this.config.drone.drone41y = drone41y_val
                this.config.drone.drone42x = drone42x_val
                this.config.drone.drone42y = drone42y_val
                this.config.drone.drone43x = drone43x_val
                this.config.drone.drone43y = drone43y_val
                this.config.drone.drone44x = drone44x_val
                this.config.drone.drone44y = drone44y_val
                this.config.drone.drone45x = drone45x_val
                this.config.drone.drone45y = drone45y_val
                this.config.drone.drone46x = drone46x_val
                this.config.drone.drone46y = drone46y_val
                this.config.drone.drone47x = drone47x_val
                this.config.drone.drone47y = drone47y_val
                this.config.drone.drone48x = drone48x_val
                this.config.drone.drone48y = drone48y_val
                this.config.drone.drone49x = drone49x_val
                this.config.drone.drone49y = drone49y_val

                this.config.forest.persons.posx = person_x
                this.config.forest.persons.posy = person_y
                this.config.forest.persons1.posx = person_x
                this.config.forest.persons1.posy = person_y
                //this.config.forest.persons.rotation = personorientation
                //this.config.forest.persons1.rotation = personorientation
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
                this.config.drone.prevdrone10x = prevdrone10x_val
                this.config.drone.prevdrone10y = prevdrone10y_val
                this.config.drone.prevdrone11x = prevdrone11x_val
                this.config.drone.prevdrone11y = prevdrone11y_val
                this.config.drone.prevdrone12x = prevdrone12x_val
                this.config.drone.prevdrone12y = prevdrone12y_val
                this.config.drone.prevdrone13x = prevdrone13x_val
                this.config.drone.prevdrone13y = prevdrone13y_val
                this.config.drone.prevdrone14x = prevdrone14x_val
                this.config.drone.prevdrone14y = prevdrone14y_val
                this.config.drone.prevdrone15x = prevdrone15x_val
                this.config.drone.prevdrone15y = prevdrone15y_val
                this.config.drone.prevdrone16x = prevdrone16x_val
                this.config.drone.prevdrone16y = prevdrone16y_val
                this.config.drone.prevdrone17x = prevdrone17x_val
                this.config.drone.prevdrone17y = prevdrone17y_val
                this.config.drone.prevdrone18x = prevdrone18x_val
                this.config.drone.prevdrone18y = prevdrone18y_val
                this.config.drone.prevdrone19x = prevdrone19x_val
                this.config.drone.prevdrone19y = prevdrone19y_val
                this.config.drone.prevdrone20x = prevdrone20x_val
                this.config.drone.prevdrone20y = prevdrone20y_val
                this.config.drone.prevdrone21x = prevdrone21x_val
                this.config.drone.prevdrone21y = prevdrone21y_val
                this.config.drone.prevdrone22x = prevdrone22x_val
                this.config.drone.prevdrone22y = prevdrone22y_val
                this.config.drone.prevdrone23x = prevdrone23x_val
                this.config.drone.prevdrone23y = prevdrone23y_val
                this.config.drone.prevdrone24x = prevdrone24x_val
                this.config.drone.prevdrone24y = prevdrone24y_val
                this.config.drone.prevdrone25x = prevdrone25x_val
                this.config.drone.prevdrone25y = prevdrone25y_val
                this.config.drone.prevdrone26x = prevdrone26x_val
                this.config.drone.prevdrone26y = prevdrone26y_val
                this.config.drone.prevdrone27x = prevdrone27x_val
                this.config.drone.prevdrone27y = prevdrone27y_val
                this.config.drone.prevdrone28x = prevdrone28x_val
                this.config.drone.prevdrone28y = prevdrone28y_val
                this.config.drone.prevdrone29x = prevdrone29x_val
                this.config.drone.prevdrone29y = prevdrone29y_val
                this.config.drone.prevdrone30x = prevdrone30x_val
                this.config.drone.prevdrone30y = prevdrone30y_val
                this.config.drone.prevdrone31x = prevdrone31x_val
                this.config.drone.prevdrone31y = prevdrone31y_val
                this.config.drone.prevdrone32x = prevdrone32x_val
                this.config.drone.prevdrone32y = prevdrone32y_val
                this.config.drone.prevdrone33x = prevdrone33x_val
                this.config.drone.prevdrone33y = prevdrone33y_val
                this.config.drone.prevdrone34x = prevdrone34x_val
                this.config.drone.prevdrone34y = prevdrone34y_val
                this.config.drone.prevdrone35x = prevdrone35x_val
                this.config.drone.prevdrone35y = prevdrone35y_val
                this.config.drone.prevdrone36x = prevdrone36x_val
                this.config.drone.prevdrone36y = prevdrone36y_val
                this.config.drone.prevdrone37x = prevdrone37x_val
                this.config.drone.prevdrone37y = prevdrone37y_val
                this.config.drone.prevdrone38x = prevdrone38x_val
                this.config.drone.prevdrone38y = prevdrone38y_val
                this.config.drone.prevdrone39x = prevdrone39x_val
                this.config.drone.prevdrone39y = prevdrone39y_val
                this.config.drone.prevdrone40x = prevdrone40x_val
                this.config.drone.prevdrone40y = prevdrone40y_val
                this.config.drone.prevdrone41x = prevdrone41x_val
                this.config.drone.prevdrone41y = prevdrone41y_val
                this.config.drone.prevdrone42x = prevdrone42x_val
                this.config.drone.prevdrone42y = prevdrone42y_val
                this.config.drone.prevdrone43x = prevdrone43x_val
                this.config.drone.prevdrone43y = prevdrone43y_val
                this.config.drone.prevdrone44x = prevdrone44x_val
                this.config.drone.prevdrone44y = prevdrone44y_val
                this.config.drone.prevdrone45x = prevdrone45x_val
                this.config.drone.prevdrone45y = prevdrone45y_val
                this.config.drone.prevdrone46x = prevdrone46x_val
                this.config.drone.prevdrone46y = prevdrone46y_val
                this.config.drone.prevdrone47x = prevdrone47x_val
                this.config.drone.prevdrone47y = prevdrone47y_val
                this.config.drone.prevdrone48x = prevdrone48x_val
                this.config.drone.prevdrone48y = prevdrone48y_val
                this.config.drone.prevdrone49x = prevdrone49x_val
                this.config.drone.prevdrone49y = prevdrone49y_val
                //console.log("Within Automatic Download");
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
                //this.drone.capture(this.config.drone.dronex,this.config.drone.droney,this.config.drone.prevdronex,this.config.drone.prevdroney);


                
                          
                //await this.export(date);
                //await timeout(4000)
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
    console.log("dronex_val: " + dronex_val);
    var droney_val = parseFloat(urlParams.get('drone1y')) 
    console.log("droney_val: " + droney_val);
    var drone1x_val = parseFloat(urlParams.get('drone2x')) 
    console.log("drone1x_val: " + drone1x_val);
    var drone1y_val = parseFloat(urlParams.get('drone2y')) 
    console.log("drone1y_val: " + drone1y_val);
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
    var drone10x_val = parseFloat(urlParams.get('drone11x')) 
    var drone10y_val = parseFloat(urlParams.get('drone11y'))
    var drone11x_val = parseFloat(urlParams.get('drone12x')) 
    var drone11y_val = parseFloat(urlParams.get('drone12y'))
    var drone12x_val = parseFloat(urlParams.get('drone13x')) 
    var drone12y_val = parseFloat(urlParams.get('drone13y'))
    var drone13x_val = parseFloat(urlParams.get('drone14x')) 
    var drone13y_val = parseFloat(urlParams.get('drone14y'))
    var drone14x_val = parseFloat(urlParams.get('drone15x')) 
    var drone14y_val = parseFloat(urlParams.get('drone15y'))
    var drone15x_val = parseFloat(urlParams.get('drone16x')) 
    var drone15y_val = parseFloat(urlParams.get('drone16y'))
    var drone16x_val = parseFloat(urlParams.get('drone17x')) 
    var drone16y_val = parseFloat(urlParams.get('drone17y'))
    var drone17x_val = parseFloat(urlParams.get('drone18x')) 
    var drone17y_val = parseFloat(urlParams.get('drone18y'))
    var drone18x_val = parseFloat(urlParams.get('drone19x')) 
    var drone18y_val = parseFloat(urlParams.get('drone19y'))
    var drone19x_val = parseFloat(urlParams.get('drone20x')) 
    var drone19y_val = parseFloat(urlParams.get('drone20y'))
    var drone20x_val = parseFloat(urlParams.get('drone21x')) 
    var drone20y_val = parseFloat(urlParams.get('drone21y'))
    var drone21x_val = parseFloat(urlParams.get('drone22x')) 
    var drone21y_val = parseFloat(urlParams.get('drone22y'))
    var drone22x_val = parseFloat(urlParams.get('drone23x')) 
    var drone22y_val = parseFloat(urlParams.get('drone23y'))
    var drone23x_val = parseFloat(urlParams.get('drone24x')) 
    var drone23y_val = parseFloat(urlParams.get('drone24y'))
    var drone24x_val = parseFloat(urlParams.get('drone25x')) 
    var drone24y_val = parseFloat(urlParams.get('drone25y'))
    var drone25x_val = parseFloat(urlParams.get('drone26x')) 
    var drone25y_val = parseFloat(urlParams.get('drone26y'))
    var drone26x_val = parseFloat(urlParams.get('drone27x')) 
    var drone26y_val = parseFloat(urlParams.get('drone27y'))
    var drone27x_val = parseFloat(urlParams.get('drone28x')) 
    var drone27y_val = parseFloat(urlParams.get('drone28y'))
    var drone28x_val = parseFloat(urlParams.get('drone29x')) 
    var drone28y_val = parseFloat(urlParams.get('drone29y'))
    var drone29x_val = parseFloat(urlParams.get('drone30x')) 
    var drone29y_val = parseFloat(urlParams.get('drone30y'))
    var drone30x_val = parseFloat(urlParams.get('drone31x')) 
    var drone30y_val = parseFloat(urlParams.get('drone31y'))
    var drone31x_val = parseFloat(urlParams.get('drone32x')) 
    var drone31y_val = parseFloat(urlParams.get('drone32y'))
    var drone32x_val = parseFloat(urlParams.get('drone33x')) 
    var drone32y_val = parseFloat(urlParams.get('drone33y'))
    var drone33x_val = parseFloat(urlParams.get('drone34x')) 
    var drone33y_val = parseFloat(urlParams.get('drone34y'))
    var drone34x_val = parseFloat(urlParams.get('drone35x')) 
    var drone34y_val = parseFloat(urlParams.get('drone35y'))
    var drone35x_val = parseFloat(urlParams.get('drone36x')) 
    var drone35y_val = parseFloat(urlParams.get('drone36y'))
    var drone36x_val = parseFloat(urlParams.get('drone37x')) 
    var drone36y_val = parseFloat(urlParams.get('drone37y'))
    var drone37x_val = parseFloat(urlParams.get('drone38x')) 
    var drone37y_val = parseFloat(urlParams.get('drone38y'))
    var drone38x_val = parseFloat(urlParams.get('drone39x')) 
    var drone38y_val = parseFloat(urlParams.get('drone39y'))
    var drone39x_val = parseFloat(urlParams.get('drone40x')) 
    var drone39y_val = parseFloat(urlParams.get('drone40y'))
    var drone40x_val = parseFloat(urlParams.get('drone41x')) 
    var drone40y_val = parseFloat(urlParams.get('drone41y'))
    var drone41x_val = parseFloat(urlParams.get('drone42x')) 
    var drone41y_val = parseFloat(urlParams.get('drone42y'))
    var drone42x_val = parseFloat(urlParams.get('drone43x')) 
    var drone42y_val = parseFloat(urlParams.get('drone43y'))
    var drone43x_val = parseFloat(urlParams.get('drone44x')) 
    var drone43y_val = parseFloat(urlParams.get('drone44y'))
    var drone44x_val = parseFloat(urlParams.get('drone45x')) 
    var drone44y_val = parseFloat(urlParams.get('drone45y'))
    var drone45x_val = parseFloat(urlParams.get('drone46x')) 
    var drone45y_val = parseFloat(urlParams.get('drone46y'))
    var drone46x_val = parseFloat(urlParams.get('drone47x')) 
    var drone46y_val = parseFloat(urlParams.get('drone47y'))
    var drone47x_val = parseFloat(urlParams.get('drone48x')) 
    var drone47y_val = parseFloat(urlParams.get('drone48y'))
    var drone48x_val = parseFloat(urlParams.get('drone49x')) 
    var drone48y_val = parseFloat(urlParams.get('drone49y'))
    var drone49x_val = parseFloat(urlParams.get('drone50x')) 
    var drone49y_val = parseFloat(urlParams.get('drone50y')) 
    


    var prevdronex_val = parseFloat(urlParams.get('prevdrone1x')) 
    console.log("prevdronex_val: " + prevdronex_val);
    var prevdroney_val = parseFloat(urlParams.get('prevdrone1y')) 
    console.log("prevdroney_value: " + prevdroney_val);
    var prevdrone1x_val = parseFloat(urlParams.get('prevdrone2x')) 
    console.log("prevdrone1x_val: " + prevdrone1x_val);
    var prevdrone1y_val = parseFloat(urlParams.get('prevdrone2y')) 
    console.log("prevdrone1y_val: " + prevdrone1y_val);
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
    var prevdrone10x_val = parseFloat(urlParams.get('prevdrone11x')) 
    var prevdrone10y_val = parseFloat(urlParams.get('prevdrone11y')) 
    var prevdrone11x_val = parseFloat(urlParams.get('prevdrone12x')) 
    var prevdrone11y_val = parseFloat(urlParams.get('prevdrone12y')) 
    var prevdrone12x_val = parseFloat(urlParams.get('prevdrone13x')) 
    var prevdrone12y_val = parseFloat(urlParams.get('prevdrone13y')) 
    var prevdrone13x_val = parseFloat(urlParams.get('prevdrone14x')) 
    var prevdrone13y_val = parseFloat(urlParams.get('prevdrone14y')) 
    var prevdrone14x_val = parseFloat(urlParams.get('prevdrone15x')) 
    var prevdrone14y_val = parseFloat(urlParams.get('prevdrone15y')) 
    var prevdrone15x_val = parseFloat(urlParams.get('prevdrone16x')) 
    var prevdrone15y_val = parseFloat(urlParams.get('prevdrone16y')) 
    var prevdrone16x_val = parseFloat(urlParams.get('prevdrone17x')) 
    var prevdrone16y_val = parseFloat(urlParams.get('prevdrone17y')) 
    var prevdrone17x_val = parseFloat(urlParams.get('prevdrone18x')) 
    var prevdrone17y_val = parseFloat(urlParams.get('prevdrone18y')) 
    var prevdrone18x_val = parseFloat(urlParams.get('prevdrone19x')) 
    var prevdrone18y_val = parseFloat(urlParams.get('prevdrone19y')) 
    var prevdrone19x_val = parseFloat(urlParams.get('prevdrone20x')) 
    var prevdrone19y_val = parseFloat(urlParams.get('prevdrone20y')) 
    var prevdrone20x_val = parseFloat(urlParams.get('prevdrone21x')) 
    var prevdrone20y_val = parseFloat(urlParams.get('prevdrone21y')) 
    var prevdrone21x_val = parseFloat(urlParams.get('prevdrone22x')) 
    var prevdrone21y_val = parseFloat(urlParams.get('prevdrone22y')) 
    var prevdrone22x_val = parseFloat(urlParams.get('prevdrone23x')) 
    var prevdrone22y_val = parseFloat(urlParams.get('prevdrone23y')) 
    var prevdrone23x_val = parseFloat(urlParams.get('prevdrone24x')) 
    var prevdrone23y_val = parseFloat(urlParams.get('prevdrone24y')) 
    var prevdrone24x_val = parseFloat(urlParams.get('prevdrone25x')) 
    var prevdrone24y_val = parseFloat(urlParams.get('prevdrone25y')) 
    var prevdrone25x_val = parseFloat(urlParams.get('prevdrone26x')) 
    var prevdrone25y_val = parseFloat(urlParams.get('prevdrone26y')) 
    var prevdrone26x_val = parseFloat(urlParams.get('prevdrone27x')) 
    var prevdrone26y_val = parseFloat(urlParams.get('prevdrone27y')) 
    var prevdrone27x_val = parseFloat(urlParams.get('prevdrone28x')) 
    var prevdrone27y_val = parseFloat(urlParams.get('prevdrone28y')) 
    var prevdrone28x_val = parseFloat(urlParams.get('prevdrone29x')) 
    var prevdrone28y_val = parseFloat(urlParams.get('prevdrone29y')) 
    var prevdrone29x_val = parseFloat(urlParams.get('prevdrone30x')) 
    var prevdrone29y_val = parseFloat(urlParams.get('prevdrone30y')) 
    var prevdrone30x_val = parseFloat(urlParams.get('prevdrone31x')) 
    var prevdrone30y_val = parseFloat(urlParams.get('prevdrone31y')) 
    var prevdrone31x_val = parseFloat(urlParams.get('prevdrone32x')) 
    var prevdrone31y_val = parseFloat(urlParams.get('prevdrone32y')) 
    var prevdrone32x_val = parseFloat(urlParams.get('prevdrone33x')) 
    var prevdrone32y_val = parseFloat(urlParams.get('prevdrone33y')) 
    var prevdrone33x_val = parseFloat(urlParams.get('prevdrone34x')) 
    var prevdrone33y_val = parseFloat(urlParams.get('prevdrone34y')) 
    var prevdrone34x_val = parseFloat(urlParams.get('prevdrone35x')) 
    var prevdrone34y_val = parseFloat(urlParams.get('prevdrone35y')) 
    var prevdrone35x_val = parseFloat(urlParams.get('prevdrone36x')) 
    var prevdrone35y_val = parseFloat(urlParams.get('prevdrone36y')) 
    var prevdrone36x_val = parseFloat(urlParams.get('prevdrone37x')) 
    var prevdrone36y_val = parseFloat(urlParams.get('prevdrone37y')) 
    var prevdrone37x_val = parseFloat(urlParams.get('prevdrone38x')) 
    var prevdrone37y_val = parseFloat(urlParams.get('prevdrone38y')) 
    var prevdrone38x_val = parseFloat(urlParams.get('prevdrone39x')) 
    var prevdrone38y_val = parseFloat(urlParams.get('prevdrone39y')) 
    var prevdrone39x_val = parseFloat(urlParams.get('prevdrone40x')) 
    var prevdrone39y_val = parseFloat(urlParams.get('prevdrone40y')) 
    var prevdrone40x_val = parseFloat(urlParams.get('prevdrone41x')) 
    var prevdrone40y_val = parseFloat(urlParams.get('prevdrone41y')) 
    var prevdrone41x_val = parseFloat(urlParams.get('prevdrone42x')) 
    var prevdrone41y_val = parseFloat(urlParams.get('prevdrone42y')) 
    var prevdrone42x_val = parseFloat(urlParams.get('prevdrone43x')) 
    var prevdrone42y_val = parseFloat(urlParams.get('prevdrone43y')) 
    var prevdrone43x_val = parseFloat(urlParams.get('prevdrone44x')) 
    var prevdrone43y_val = parseFloat(urlParams.get('prevdrone44y')) 
    var prevdrone44x_val = parseFloat(urlParams.get('prevdrone45x')) 
    var prevdrone44y_val = parseFloat(urlParams.get('prevdrone45y')) 
    var prevdrone45x_val = parseFloat(urlParams.get('prevdrone46x')) 
    var prevdrone45y_val = parseFloat(urlParams.get('prevdrone46y')) 
    var prevdrone46x_val = parseFloat(urlParams.get('prevdrone47x')) 
    var prevdrone46y_val = parseFloat(urlParams.get('prevdrone47y')) 
    var prevdrone47x_val = parseFloat(urlParams.get('prevdrone48x')) 
    var prevdrone47y_val = parseFloat(urlParams.get('prevdrone48y')) 
    var prevdrone48x_val = parseFloat(urlParams.get('prevdrone49x')) 
    var prevdrone48y_val = parseFloat(urlParams.get('prevdrone49y')) 
    var prevdrone49x_val = parseFloat(urlParams.get('prevdrone50x')) 
    var prevdrone49y_val = parseFloat(urlParams.get('prevdrone50y')) 
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
    view.automaticDownload(dronex_val,droney_val,drone1x_val,drone1y_val,drone2x_val,drone2y_val,drone3x_val,drone3y_val,drone4x_val,drone4y_val,drone5x_val,drone5y_val,drone6x_val,drone6y_val,drone7x_val,drone7y_val,drone8x_val,drone8y_val,drone9x_val,drone9y_val,person_x,person_y,personorientation,filename,prevdronex_val,prevdroney_val,prevdrone1x_val,prevdrone1y_val,prevdrone2x_val,prevdrone2y_val,prevdrone3x_val,prevdrone3y_val,prevdrone4x_val,prevdrone4y_val,prevdrone5x_val,prevdrone5y_val,prevdrone6x_val,prevdrone6y_val,prevdrone7x_val,prevdrone7y_val,prevdrone8x_val,prevdrone8y_val,prevdrone9x_val,prevdrone9y_val,drone10x_val,drone10y_val,drone11x_val,drone11y_val,drone12x_val,drone12y_val,drone13x_val,drone13y_val,drone14x_val,drone14y_val,drone15x_val,drone15y_val,drone16x_val,drone16y_val,drone17x_val,drone17y_val,drone18x_val,drone18y_val,drone19x_val,drone19y_val,drone20x_val,drone20y_val,drone21x_val,drone21y_val,drone22x_val,drone22y_val,drone23x_val,drone23y_val,drone24x_val,drone24y_val,drone25x_val,drone25y_val,drone26x_val,drone26y_val,drone27x_val,drone27y_val,drone28x_val,drone28y_val,drone29x_val,drone29y_val,drone30x_val,drone30y_val,drone31x_val,drone31y_val,drone32x_val,drone32y_val,drone33x_val,drone33y_val,drone34x_val,drone34y_val,drone35x_val,drone35y_val,drone36x_val,drone36y_val,drone37x_val,drone37y_val,drone38x_val,drone38y_val,drone39x_val,drone39y_val,drone40x_val,drone40y_val,drone41x_val,drone41y_val,drone42x_val,drone42y_val,drone43x_val,drone43y_val,drone44x_val,drone44y_val,drone45x_val,drone45y_val,drone46x_val,drone46y_val,drone47x_val,drone47y_val,drone48x_val,drone48y_val,drone49x_val,drone49y_val,prevdrone10x_val,prevdrone10y_val,prevdrone11x_val,prevdrone11y_val,prevdrone12x_val,prevdrone12y_val,prevdrone13x_val,prevdrone13y_val,prevdrone14x_val,prevdrone14y_val,prevdrone15x_val,prevdrone15y_val,prevdrone16x_val,prevdrone16y_val,prevdrone17x_val,prevdrone17y_val,prevdrone18x_val,prevdrone18y_val,prevdrone19x_val,prevdrone19y_val,prevdrone20x_val,prevdrone20y_val,prevdrone21x_val,prevdrone21y_val,prevdrone22x_val,prevdrone22y_val,prevdrone23x_val,prevdrone23y_val,prevdrone24x_val,prevdrone24y_val,prevdrone25x_val,prevdrone25y_val,prevdrone26x_val,prevdrone26y_val,prevdrone27x_val,prevdrone27y_val,prevdrone28x_val,prevdrone28y_val,prevdrone29x_val,prevdrone29y_val,prevdrone30x_val,prevdrone30y_val,prevdrone31x_val,prevdrone31y_val,prevdrone32x_val,prevdrone32y_val,prevdrone33x_val,prevdrone33y_val,prevdrone34x_val,prevdrone34y_val,prevdrone35x_val,prevdrone35y_val,prevdrone36x_val,prevdrone36y_val,prevdrone37x_val,prevdrone37y_val,prevdrone38x_val,prevdrone38y_val,prevdrone39x_val,prevdrone39y_val,prevdrone40x_val,prevdrone40y_val,prevdrone41x_val,prevdrone41y_val,prevdrone42x_val,prevdrone42y_val,prevdrone43x_val,prevdrone43y_val,prevdrone44x_val,prevdrone44y_val,prevdrone45x_val,prevdrone45y_val,prevdrone46x_val,prevdrone46y_val,prevdrone47x_val,prevdrone47y_val,prevdrone48x_val,prevdrone48y_val,prevdrone49x_val,prevdrone49y_val,d1alt,d2alt,d3alt,d4alt,d5alt,d6alt,d7alt,d8alt,d9alt,d10alt,leads);
});

