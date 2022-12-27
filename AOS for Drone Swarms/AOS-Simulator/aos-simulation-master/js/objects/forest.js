class Forest {
    constructor(stage, index) {
        this.root = stage.root;
        this.config = stage.config;
        this.loader = stage.loader;
        this.scene = stage.scene;
        this.stage = stage;
        this.index = index;

        this.trees = [...new Array(this.config.forest.size)];
        this.persons = [... new Array(this.config.forest.persons.count)];
        this.persons1 = [... new Array(this.config.forest.persons1.count)];
        this.persons2 = [... new Array(this.config.forest.persons2.count2)];
        this.block1 = [... new Array(this.config.forest.blocks1)];
        this.block2= [... new Array(this.config.forest.blocks2)];
        this.block3 = [... new Array(this.config.forest.blocks3)];
        

        this.grounds = [];
        this.treePositions = [];
        this.blockPositions1 = [];
        this.blockPositions2 = [];
        this.blockPositions3 = [];
        this.workers = getWorkers();
        this.workersSubscriber = [];

        this.groundMaterial = new THREE.MeshLambertMaterial({
            color: this.config.material.color.ground,
            side: THREE.DoubleSide
        });

        this.treeMaterial = new THREE.MeshStandardMaterial({
            color: this.config.material.color.tree,
            roughness: 1.0,
            metalness: 0.3
        });

        this.twigMaterials = {
            'needle-leaf': new THREE.MeshStandardMaterial({
                color: this.config.material.color.twig,
                roughness: 1.0,
                metalness: 0.3,
                alphaTest: 0.1
            }),
            'broad-leaf': new THREE.MeshStandardMaterial({
                color: this.config.material.color.twig,
                roughness: 1.0,
                metalness: 0.3,
                alphaTest: 0.1
            })
        };

        this.loaded = new Promise(async function (resolve) {
            for (const type in this.twigMaterials) {
                this.twigMaterials[type].map = await this.loader.load('texture', `img/${type}.png`);
            }
 
            

            this.init();
            this.addGround();
            this.addTrees();
            this.addPersons();
            this.addPersons2();
            this.update();

            // tree worker message
            this.workersMessage(async (finished) => {
                if (!finished) {
                    return;
                }

                // trees and persons finished
                await Promise.all(this.persons.map((p) => { return p.loaded; }));
                await Promise.all(this.persons2.map((p) => { return p.loaded; }));
                this.stage.status();

                resolve(this);
            });
        }.bind(this));
    }
    
    init() {
        // TODO refactor position logic
        
        
        const coverage = 2 * this.config.drone.height * Math.tan(rad(this.config.drone.camera.view / 2));
        const sizeOuter = this.config.forest.ground + 2 * coverage;
        const sizeInner = this.config.forest.ground ;

        // ground position constraints
        const treeMargin = 1;
        const treePositionMin = -sizeInner /  2.1 + treeMargin;
        const treePositionMax = sizeInner /   2.1 - treeMargin;
        console.log('treePositionMinold', treePositionMin  )
        console.log('treePositionMinnew', treePositionMax  )

        // divide ground into grids
        const gridCount = Math.floor(Math.sqrt(this.config.forest.size));
        console.log('gridcount',gridCount)
        const gridSize = 2 * treePositionMax / gridCount;
        console.log('gridsize',gridSize)

        // calculate tree positions
       
    

        // for density 300 (just an example of the positions of the trees which  can also be read from json file)

        var treex = [-31.070054800395702, 39.322567307236845, -18.86775577755071, -20.140911746703487, -17.938452995599345, 28.249951940948904, 33.81218775964912, -40.16605814656119, -37.99260184782714, -27.406175958638705, -43.13940670123346, 12.614486707701943, -18.755852395028327, -10.561233352532719, -29.748327268284346, 22.5733262151657, -5.314956623186057, 26.556145463090317, -39.83133636891495, -19.490526551358446, -7.838723194301499, 28.618028743563528, -20.09318740276355, 27.0272814070799, 8.976936119379058, -35.064073642869346, -35.23777932240696, -36.878423775506114, -15.657029675892069, -9.472333969701673, -18.764499273668847, -26.842674772523836, -3.1178599392112734, -2.6912723878551206, 8.68383864219893, 22.027380545810985, -25.438809771994535, -28.894243402470735, 22.212137965800558, 35.543795969157216, -23.348207475729268, 43.96037164477926, -28.27757208380556, -36.0501052030558, 8.024578711916938, -8.612982250517032, -46.4722911148278, 16.779125388435794, -45.545674436575524, -7.126989304889898, 34.87768095582577, -10.735640507952546, -41.21860165891949, -38.35020166535537, 40.46842663120225, 37.06761910445656, -2.0726357088870606, -8.187431710359698, 14.572745393540847, 3.513945262419756, 28.327460742042657, -23.41355320320321, 0.5921590969031052, -19.304149143990028, 3.8980745771433725, 28.702385811484945, -24.334445055944755, -2.25502837943068, -46.24725096699567, 1.9717576276945588, -39.12701198436291, -9.865232533312401, -18.940852921192178, -16.98177056327374, 22.357948273660313, 42.377316253220016, 22.307443462300427, 26.249263911877737, 5.682376729744419, -2.47072535486896, -6.070688005122108, 41.864685235048846, 35.19653192070519, 8.766227080234787, -37.48262829783896, -9.322448854121482, -27.00580417709906, 31.37793960265436, -31.911606794947936, 14.874140448097135, 12.359988145723277, 41.34244314735894, -34.97329194770978, 6.928433714007236, -25.17365383980507, -30.752498414650628, -39.74932080813749, -8.842913541349446, 3.514619601920089, 39.45927888203486, 31.094153619516852, 2.3669578522127157, -35.10108955852564, -34.15468021622151, -43.01779186038847, -9.024563667337357, 19.477663675103713, 7.327467603970483, -25.002232012488705, 12.643723635217171, 30.552369710773743, 18.00700873990641, -6.264085814057823, -35.37583061370523, 12.446920240548383, 16.608168307104304, 23.908021876626833, -17.25210072852356, 17.061159558110134, 20.958877610767118, 13.53318469398268, 7.395409612777101, 25.795883150790324, 34.881542250191245, 36.659476608854156, 43.76944557924322, 17.766139289850724, 1.6318615175568416, 14.607711784343254, -10.292785769290314, 22.374856062745565, 44.571976783857835, -39.62240513535531, -36.13625590293504, 37.798601979152245, 20.112277441105235, 9.52022156578717, 39.51357014698839, 2.042042411816629, 43.83073507240831, -43.325781852913956, 43.50613989415653, 19.546645224969495, -27.637576220983657, -32.46752601129455, 4.7214563528837274, -35.13679684795733, 10.55857038309803, 36.5519232408752, -5.11666872096929, -32.26593984600035, 45.60992453820653, 7.20229666477189, 45.14350051410289, 2.9268203022008907, 34.09605327608276, 34.92839518235913, -2.445639764764069, 17.102868404396094, 30.850864559124076, -24.646603444263633, -13.253102109646582, 10.668330132049114, -35.22157678906821, 10.305005983713748, 33.83110288689034, 5.440828730099783, -7.67079111170739, 38.161997007332765, 45.410236663210924, -6.254414267442558, 28.113639615518352, 5.635823456238722, -19.81906206726543, -16.559740768939783, -22.98601306009837, -26.87856444866171, 46.15703476689232, -37.73995438311799, -18.790949947203913, -7.269017758104396, 17.406619380279786, 17.318842860123745, -5.27798632068754, 35.76529597425185, -44.38221741404384, 22.7609484662892, 41.48362930557626, -41.19001547468209, -10.997019472318545, 19.653116632918127, 22.273531714064507, -16.011315418166568, 35.469616546826074, 33.031043874351816, 28.129928007201844, -0.46389254055927065, 34.93917471510553, -30.071790471603904, 0.4549361990998837, 46.155588353485456, 42.590185157192835, -26.179755810524654, -20.375735468302558, -18.903475900373518, -13.822755282133096, 2.3372586282475725, -37.36185833046749, -2.088817274519666, 29.056442605250083, 14.998843225658947, -36.889662808016155, 34.67210402680128, -9.228919841360995, -24.558170956883444, 18.850478756330237, 6.578729143982244, 10.633925406695795, -1.3638912472435858, -5.382552790681997, -24.760362809761222, 27.049066730695685, -12.147780661060871, -44.217853928508845, 45.023285285298144, 4.179697579045511, 38.54761710407045, -30.519575254312116, -23.262259935773915, -42.222687731070494, -5.0182326837306945, -19.2160345068726, 28.653663604041547, -2.9156483167539387, 16.633719078321654, -45.37698894400709, -14.055331452742585, 38.30788083286256, 36.010904341775486, 28.69388814092703, 19.2988158789162, 20.59698213455761, 0.3324982630344615, 5.573736371597488, 29.415135144400004, 29.979321108958004, 1.2669028869698211, -23.23639783977817, -17.58485218985435, 2.9111191859359455, 39.79405335211793, 16.225972552578206, -38.37397294359109, -12.613812799750903, 21.9740555775804, -25.98031493930865, -37.75173959817443, 13.486092761499101, -41.468079713654035, 12.767275621627519, 37.226530550407155, 32.67090712098152, 11.114803598931285, -38.62311850293288, -42.32999328043742, 37.07285578561145, -6.342788190726415, -45.11739278215559, -10.630392778701344, -44.7988965217799, 18.75063041281871, 16.934119345077974, -11.590457434462659, -33.618963948542635, -30.83049427769731, -19.515763861546354, -20.233465762800428, 46.51809506413713, -28.57865353005919, -15.756605308954585, 40.20017742282263, -45.634359129004345, 8.331908392830305, -10.94919213069077, -18.372788377960763, -28.959553576967554, -7.618561338410839, -30.51905349381128, 29.735161792377607, 19.594105279671574, -41.36469700512795, 42.9380815458349, -17.671026242348386, -27.67481439195056, 20.476475952366812, -39.83004078095446, 9.685170366670395, 18.558450543415052, -21.36151199166799, -4.589762208269672]
        var treey = [43.522514674951104, -29.023608131686945, 26.839677400331887, 25.232188370889997, 30.486485671634973, -26.77430812767195, 29.81254291928918, 33.52704087994698, 0.40172996079293055, 29.761460254510325, 32.74523656103725, 12.252932291672783, -11.756848877221076, -0.7875994124564711, -34.54290060741843, 25.47674136873231, -28.66981765898757, -1.6879740609947276, 7.281081176335843, -34.54150498646597, 18.177093736669384, -32.827467054955186, 5.582770603438011, 32.97045479917429, -40.55077510528903, -45.96380065373773, 12.007532418460901, -28.318696571484036, -35.142910068012576, 13.346426048710109, 2.622527353240681, -18.496170018836253, 32.14769557900022, -16.135412735772928, -1.0170185655147388, -10.795742784115795, -5.9143790788409945, 2.8141900707379928, -23.896701374106335, -17.324375468249215, -19.197745750091585, 30.103664410862223, -21.134769945207356, 37.2521898142735, 3.373718958444579, -34.718290936976246, 9.802056035782938, -43.63360939155449, -20.52407094716458, -35.048925606664966, -2.6620532673690938, 31.336923904721093, -17.25810946137708, -36.87150139585924, -2.873212628301977, -35.12221455094836, 9.992517522333678, 27.791504150235085, -7.089635885263319, 25.053718011237443, -10.879081376828, -16.470459184864325, -11.930136653140215, 14.838938564395123, -13.40105030685971, -7.653338063117081, -10.983097365646142, 1.9500639316100559, -30.90163058571564, 42.96845354281647, -46.51932093102197, -38.358057285987144, -36.94988549918759, -28.325908523145934, -14.230647470739177, 15.2152422969655, -39.68352422974058, -22.33123542263947, -43.863101397360666, 17.064199844522353, 44.339593682385555, 20.216147430532377, 41.79583276202387, -45.330079195767, -20.64087112193686, -27.61944111283871, 41.006735195037905, 33.73981961584008, -19.93211887385955, 15.940847843223278, -12.516832327152146, 32.43351523038115, -19.08185182409712, 38.17753325500933, 9.533496221628473, 3.242335367096913, 42.50953614610163, -43.86052387590417, -29.40474092880011, 36.40770860280999, 7.188719906498838, -35.21272911084314, -8.009068785629443, -36.00772278037587, 38.53921797968984, 44.92313221590383, 43.75914551133492, -33.08710540909082, -11.604768743142078, -14.633778496996012, -43.67498878440582, 3.715341145631946, 22.268470676261654, -29.847070528959225, -30.973270849011627, -9.086156622751208, 24.636465908229553, 3.9345545229183134, 35.15715948601286, -29.171026480739254, 30.540603393821126, -40.865035956986794, 36.061921781365164, -13.26245290517648, 20.20675378840925, -44.89179035658362, 2.342080971150903, 36.749447973077615, 9.144522323115137, 21.51476127247857, 13.539656910374681, 13.315676607846555, -11.672098771507756, 17.804528831627078, 33.39343536770442, -3.7213717268576074, 36.35412051185529, -19.031639979365274, -29.896101158163894, 0.834980869563791, -25.283905715641783, -21.767384800982715, 40.50373936668224, 46.29253222901929, 27.033760106413173, 21.514201922794804, 0.7334020541902615, 7.559902386199447, -2.450893814980599, -23.159293489080635, -35.26530418843511, -40.33070312962601, -3.7938485892113496, 38.42817974275528, 17.178963268936457, 24.58823230703072, -28.556416697843126, -40.28384737044565, 37.548121199534386, 39.96169437415406, 12.143738105447483, -5.874214641982176, 29.50821413595022, 18.03866742756255, -25.697228641653368, -22.136426867803763, -20.413784497826043, -43.29967165847671, 8.83744763191428, -11.278167190949754, 40.19445374743007, -40.93877879064158, -18.907571219830515, -43.834564731438256, 14.094751882066731, 41.76344952373145, -28.34547566873433, 45.150576195382975, 12.652586065159452, -22.262957530155777, 7.268821395948048, -25.396422830063553, -34.03739207777946, 10.563445993454081, -37.984895038202666, 7.743066719020466, -34.05745836497454, -28.60231419314052, -46.05485374037894, 40.91990032478592, -43.67597537608288, 16.747712763775798, 39.36246902638374, -35.247831135339865, 17.37565961915, 3.392242881867644, 31.70417176837913, -39.74119011398363, -36.49987473743104, 24.30328701216334, 4.900112739414718, -30.251347456475443, -44.749399035816104, -27.965829325176465, 44.02576217841492, -42.161576893031835, -43.9502298468682, 30.040334472749223, 7.32368021188519, 12.575876891555552, 24.239439360395366, -30.49373189404988, 11.18457836924835, -21.092120025731255, 33.193547158927736, -16.746502643463874, 1.3578697728549836, 21.012372992911125, -24.361311799270343, -3.638643958573611, 16.94922082724597, 44.348336894070094, -18.84249607418996, 16.73832737108343, -4.263475010586547, 33.102495180163636, -43.27076518116767, -13.178005271366318, -36.731694880370746, -39.68203037464772, -38.116058307700214, 40.51665933175891, -44.354269522228435, -8.616240133595532, -37.082275867408455, 23.231727644870713, -17.80440258393153, 7.314822025495609, 14.649811878567773, 27.857585852267068, 35.369922835782646, 0.849848521094811, -3.4390401687166197, 11.695185924370067, 16.828514410001766, -14.173306204949725, 25.18941801445079, -4.065226390068715, 8.390570329315992, 43.27250259523887, 46.40541992181856, 27.60924687722345, -18.419711235811086, 29.680995346779348, 3.488629038064477, 30.268348020429283, 22.296570817438635, 45.53875801032882, 24.947392220646595, -19.509765982990743, 26.82539832982581, -7.713259957365945, -6.796773719260678, -4.813925596452497, -5.714976051555304, -23.61586861866251, -18.557762376524195, 0.8658243298187762, 18.11331179226924, 45.370413849387816, 41.88206798977067, -22.374777356863145, 7.644202231853281, 40.76646597674011, 32.247276139884896, 19.73159448432761, -2.052949260365574, -14.715097835863773, -0.3113824345583569, 23.771758094977937, -13.052278214297699, -8.871303460175412, 14.558462082775776, -10.83597390921405, -4.257723943473348, 20.386419626586807, 1.2207199562595026, 23.780458600824005, 21.512901114545006, 36.00293775414709, 7.251887848588539, 0.5058168961420475, 9.796895076232794, 13.567231470574352, 22.567661116673513, 10.490699017291426, 5.536917280087195, 13.334385257108819, 16.432417810139192, 10.396645619279726]

        
        this.treePositions = [];
        
    
    
        
        for (let k = 0; k < 1; k++) {
            const treePositions = [];
            for (let i = 0; i < 1; i++) {
                for (let j = 0; j < 1; j++) {
                    // calculate min and max values within grid
                    const gridPositionMinX = treePositionMin + j * gridSize;
                    const gridPositionMaxX = treePositionMin + (j + 1) * gridSize;
                    const gridPositionMinZ = treePositionMin + i * gridSize;
                    const gridPositionMaxZ = treePositionMin + (i + 1) * gridSize;
                    
                    
                    // apply random position within grid
                    for (let l = 0; l < this.config.forest.size; l++) {
                        treePositions.push(new THREE.Vector3(
                            (treex[l]),
                            0.01,
                            (treey[l])


                        ));
                     
                    }
                    

                    
                }
                
            }
            

            // shuffle grid positions and append to existing
           this.treePositions = this.treePositions.concat(shuffle(treePositions,k));
            
        }
        
    }

   
    workersMessage(callback) {
        this.workersSubscriber.push(callback);
    }

    getGround(size) {
        const geometry = new THREE.PlaneGeometry();
        geometry.rotateX(rad(90));

        const ground = new THREE.Mesh(geometry, this.groundMaterial);
        ground.scale.set(size, 1, size);

        setLayer(ground, this.stage.layer.ground);
        return ground;
    }

    getTree(index) {
        const seed = randomInt(0, this.config.forest.trees.homogeneity * 100, index);
        //console.log('seedeer',seed)

        // merge config
        const config = {
            levels: this.config.forest.trees.levels,
            twigScale: this.config.forest.trees.twigScale,
            ... this.config.forest.trees.branching,
            ... this.config.forest.trees.trunk
        };

        // add random config value noise 
        for (let key in config) {
            if (randomFloat(0.0, 1.0, seed) < 0.5) {
                config[key] = config[key] * randomFloat(this.config.forest.trees.homogeneity / 100, 1.0, seed);
            }
        }

        // set index and seed
        config.index = index;
        config.seed = seed;

        return config;
    }
    getblock1(index) {
        const block1 = new Block1(this).mesh;
        block1.position.x = this.blockPositions1[0].x;
        block1.position.z = this.blockPositions1[0].z;
        
        return block1;
    }
    getblock2(index) {
        const block2 = new Block2(this).mesh;
        block2.position.x = this.blockPositions2[0].x;
        block2.position.z = this.blockPositions2[0].z;
        
        return block2;
    }
    getblock3(index) {
        const block3 = new Block3(this).mesh;
        block3.position.x = this.blockPositions3[0].x;
        block3.position.z = this.blockPositions3[0].z;
        
        return block3;
    }

    getPerson(index) {
        return new Person(this, index);
    }
    getPerson1(index) {
        return new Person1(this, index);
    }
    getPerson2(index) {
        return new Person2(this, index);
    }
    addGround() {
        const size = this.config.forest.ground;
        const coverage = 2 * this.config.drone.height * Math.tan(rad(this.config.drone.camera.view / 2));

        // inner ground
        const inner = this.getGround(size);
        this.grounds.push(inner);
        this.scene.add(inner);

        // outer ground
        const outer = this.getGround(size + 2 * coverage);
        outer.material.transparent = true;
        outer.material.opacity = 0.7;
        outer.position.y = -0.01;
        this.grounds.push(outer);
        //this.scene.add(outer);
    }

    addTrees() {
        const workerConfigs = [];
        for (let i = 0; i < this.trees.length; i++) {
            workerConfigs.push(this.getTree(i));
        }

        // init workers
        this.workers.forEach((worker) => { worker.terminate(); });
        this.workers = getWorkers();

        // worker status
        let done = 0;
        this.stage.status('Loading', 0);

        // start workers
        splitArray(workerConfigs, this.workers.length).forEach((configs, i) => {
            this.workers[i].postMessage({
                method: 'getTrees',
                params: {
                    configs: configs,
                    chunks: 10
                }
            });

            this.workers[i].onmessage = ((e) => {
                const { trees } = e.data;

                trees.forEach((tree) => {
                    // tree trunk
                    const treeGeometry = new THREE.BufferGeometry();
                    treeGeometry.setAttribute('position', createFloatAttribute(tree.verts, 3));
                    treeGeometry.setAttribute('normal', normalizeAttribute(createFloatAttribute(tree.normals, 3)));
                    treeGeometry.setAttribute('uv', createFloatAttribute(tree.UV, 2));
                    treeGeometry.setIndex(createIntAttribute(tree.faces, 1));

                    // tree twigs
                    const twigGeometry = new THREE.BufferGeometry();
                    twigGeometry.setAttribute('position', createFloatAttribute(tree.vertsTwig, 3));
                    twigGeometry.setAttribute('normal', normalizeAttribute(createFloatAttribute(tree.normalsTwig, 3)));
                    twigGeometry.setAttribute('uv', createFloatAttribute(tree.uvsTwig, 2));
                    twigGeometry.setIndex(createIntAttribute(tree.facesTwig, 1));

                    // tree twigs leaf type
                    let twigLeafType = this.config.forest.trees.type;
                    if (twigLeafType == 'mixed-leaf') {
                        twigLeafType = ['needle-leaf', 'broad-leaf'][randomInt(0, 1, tree.index)];
                    }

                    // tree trunk and twigs
                    const treeGroup = new THREE.Group();
                    treeGroup.add(new THREE.Mesh(treeGeometry, this.treeMaterial));
                    treeGroup.add(new THREE.Mesh(twigGeometry, this.twigMaterials[twigLeafType]));

                    // tree position
                    treeGroup.scale.multiplyScalar(3);
                    treeGroup.position.set(
                        this.treePositions[tree.index].x,
                        this.treePositions[tree.index].y,
                        this.treePositions[tree.index].z
                    );
                    treeGroup.rotateY(rad(randomInt(0, 360, tree.index)));

                    // update tree
                    if (this.trees[tree.index]) {
                        treeGroup.position.set(
                            this.trees[tree.index].position.x,
                            this.trees[tree.index].position.y,
                            this.trees[tree.index].position.z
                        );
                        this.scene.remove(this.trees[tree.index]);
                    }

                    // add tree
                    setLayer(treeGroup, this.stage.layer.trees);
                    this.trees[tree.index] = treeGroup;
                    this.scene.add(treeGroup);

                    // update workers status
                    this.stage.status('Loading', Math.round(++done * 100 / this.trees.length));
                });

                // workers finished
                const finished = this.trees.length == done;
                this.workersSubscriber.forEach((callback) => { callback(finished); });
            }).bind(this);
        });

        // update ground
        this.update();
    }
    addblocks1() {
        const block1 = [];
        for (let i = 0; i <= 0; i++) {
            block1.push(this.getblock1(i));
            
        }
        // append persons
        block1.forEach((block1, i) => {
            this.block1[i] = block1;
            this.scene.add(block1);
           
        });
    }
    addblocks2() {
        const block2 = [];
        for (let i = 0; i <= 0; i++) {
            block2.push(this.getblock2(i));
            
        }
        // append persons
        block2.forEach((block2, i) => {
            this.block2[i] = block2;
            this.scene.add(block2);
           
        });
    }
    addblocks3() {
        const block3 = [];
        for (let i = 0; i <= 0; i++) {
            block3.push(this.getblock3(i));
            
        }
        // append persons
        block3.forEach((block3, i) => {
            this.block3[i] = block3;
            this.scene.add(block3);
           
        });
    }
    blockMoveTest1(currentTime) {
        if(!currentTime) {
            this.startTime = 0;
            requestAnimationFrame(this.blockMoveTest1);
            return;
        }
        else if (!this.startTime) {
            this.startTime = currentTime;
        }
        const start = new THREE.Vector3( this.config.forest.block1startx, 0, this.config.forest.block1starty);
        const end = new THREE.Vector3(this.config.forest.block1endx , 0, this.config.forest.block1endy);
        
        const blockSpeed = this.config.forest.blockSpeed;

        const moveDuration = start.distanceTo(end) / blockSpeed * 1000;
        
        if (moveDuration <=0) {
            return;
        }
        const deltaTime = currentTime - this.startTime;
        const trajectoryTime = deltaTime / moveDuration;
        
        if(deltaTime <= moveDuration) {
            const current = new THREE.Vector3();
            const trajectory = new THREE.Line3(start, end);
            trajectory.at(trajectoryTime, current);

            this.block1.forEach((block1) => {
            this.block1[1] = block1;
                
            block1.position.x = current.x;
            block1.position.z = current.z;
            })
            requestAnimationFrame(this.blockMoveTest1);
        }
        else {
            
        }
                
    }
    blockMoveTest2(currentTime) {
        if(!currentTime) {
            this.startTime = 0;
            requestAnimationFrame(this.blockMoveTest2);
            return;
        }
        else if (!this.startTime) {
            this.startTime = currentTime;
        }
        const start = new THREE.Vector3( this.config.forest.block2startx, 0, this.config.forest.block2starty);
        const end = new THREE.Vector3(this.config.forest.block2endx , 0, this.config.forest.block2endy);
        
        const blockSpeed = this.config.forest.blockSpeed;

        const moveDuration = start.distanceTo(end) / blockSpeed * 1000;
        
        if (moveDuration <=0) {
            return;
        }
        const deltaTime = currentTime - this.startTime;
        const trajectoryTime = deltaTime / moveDuration;
        
        if(deltaTime <= moveDuration) {
            const current = new THREE.Vector3();
            const trajectory = new THREE.Line3(start, end);
            trajectory.at(trajectoryTime, current);

            this.block2.forEach((block2) => {
            this.block2[1] = block2;
                
            block2.position.x = current.x;
            block2.position.z = current.z;
            })
            requestAnimationFrame(this.blockMoveTest2);
        }
        else {
            
        }
                
    }
    blockMoveTest3(currentTime) {
        if(!currentTime) {
            this.startTime = 0;
            requestAnimationFrame(this.blockMoveTest3);
            return;
        }
        else if (!this.startTime) {
            this.startTime = currentTime;
        }
        const start = new THREE.Vector3( this.config.forest.block3startx, 0, this.config.forest.block3starty);
        const end = new THREE.Vector3(this.config.forest.block3endx , 0, this.config.forest.block3endy);
        
        const blockSpeed = this.config.forest.blockSpeed;

        const moveDuration = start.distanceTo(end) / blockSpeed * 1000;
        
        if (moveDuration <=0) {
            return;
        }
        const deltaTime = currentTime - this.startTime;
        const trajectoryTime = deltaTime / moveDuration;
        
        if(deltaTime <= moveDuration) {
            const current = new THREE.Vector3();
            const trajectory = new THREE.Line3(start, end);
            trajectory.at(trajectoryTime, current);

            this.block3.forEach((block3) => {
            this.block3[1] = block3;
                
            block3.position.x = current.x;
            block3.position.z = current.z;
            })
            requestAnimationFrame(this.blockMoveTest3);
        }
        else {
            
        }
                
    }


    addPersons() {
        const persons = [];
        for (let i = 0; i < this.persons.length; i++) {
            this.persons[i] = this.getPerson(i);
        }
    }
    addPersons1() {
        for (let i = 0; i < this.persons1.length; i++) {
            this.persons1[i] = this.getPerson1(i);
        }
    }
    addPersons2() {
        for (let i = 0; i < this.persons2.length; i++) {
            this.persons2[i] = this.getPerson2(i);
        }
    }

    removeTrees() {
        // remove all trees
        this.trees.forEach((tree) => { this.scene.remove(tree); });
        this.trees = [...new Array(this.config.forest.size)];

        // update positions
        this.init();
    }

    removePersons() {
        // remove all persons
        this.persons.forEach(async (person) => { this.scene.remove(person.person); });
        this.persons = [... new Array(this.config.forest.persons.count)];
    }
    removePersons1() {
        // remove all persons
        this.persons1.forEach(async (person1) => { this.scene.remove(person1.person1); });
        this.persons1 = [... new Array(this.config.forest.persons1.count1)];
    }
    removePersons2() {
        // remove all persons
        this.persons2.forEach(async (person2) => { this.scene.remove(person2.person2); });
        this.persons2 = [... new Array(this.config.forest.persons2.count2)];
    }
    removeblocks1() {
        // remove all persons
        this.block1.forEach(async (block1) => { this.scene.remove(block1); });
        this.block1 = [... new Array(this.config.forest.blocks1)];
    }
    removeblocks2() {
        // remove all persons
        this.block2.forEach(async (block2) => { this.scene.remove(block2); });
        this.block2 = [... new Array(this.config.forest.blocks2)];
    }
    removeblocks3() {
        // remove all persons
        this.block3.forEach(async (block3) => { this.scene.remove(block3); });
        this.block3 = [... new Array(this.config.forest.blocks3)];
    }
    async update() {
        const coverage = 2 * this.config.drone.height * Math.tan(rad(this.config.drone.camera.view / 2));
        const sizeInner = this.config.forest.ground;
        const sizeOuter = sizeInner + 2 * coverage;
        

        // ground position constraints
        const treeMargin = 1;
        //const treePositionMin = -sizeInner / 2 + coverage / 2 + treeMargin;
        //const treePositionMax = sizeInner / 2 - coverage / 2 - treeMargin;
        const treePositionMin = -sizeInner /  2.1 + treeMargin;
        const treePositionMax = sizeInner /   2.1 - treeMargin;

        // hide trees outside margin area
        this.trees.forEach((tree) => {
            if (tree) {
                const treeInsideX = tree.position.x >= treePositionMin && tree.position.x <= treePositionMax;
                const treeInsideY = tree.position.z >= treePositionMin && tree.position.z <= treePositionMax;
                tree.visible = treeInsideX && treeInsideY;
            }
        });

        // update ground size
        this.grounds[0].scale.set(sizeInner, 1, sizeInner);
        this.grounds[1].scale.set(sizeOuter, 1, sizeOuter);


        const block1Margin = 2;
        const block1PositionMin = -sizeInner / 2 + block1Margin;
        const block1PositionMax = sizeInner / 2 - block1Margin;
        const block2Margin = 2;
        const block2PositionMin = -sizeInner / 2 + block2Margin;
        const block2PositionMax = sizeInner / 2 - block2Margin;
        const block3Margin = 2;
        const block3PositionMin = -sizeInner / 2 + block3Margin;
        const block3PositionMax = sizeInner / 2 - block3Margin;

        this.blockPositions1 = [];
        for (let i = 0; i <= 0; i++) {
            this.blockPositions1.push({
                x: this.config.forest.block1startx, // randomFloat(personPositionMin, personPositionMax),
                y: 0,
                z: this.config.forest.block1starty //randomFloat(personPositionMin, personPositionMax)
                
            });
        }
        this.blockPositions2 = [];
        for (let i = 0; i <= 0; i++) {
            this.blockPositions2.push({
                x: this.config.forest.block2startx, // randomFloat(personPositionMin, personPositionMax),
                y: 0,
                z: this.config.forest.block2starty //randomFloat(personPositionMin, personPositionMax)
                
            });
        }
        this.blockPositions3 = [];
        for (let i = 0; i <= 0; i++) {
            this.blockPositions3.push({
                x: this.config.forest.block3startx, // randomFloat(personPositionMin, personPositionMax),
                y: 0,
                z: this.config.forest.block3starty //randomFloat(personPositionMin, personPositionMax)
                
            });
        }

        this.block1.forEach((block1) => {
            if (block1) {
                const block1InsideX = block1.position.x > block1PositionMin && block1.position.x < block1PositionMax;
                const block1InsideY = block1.position.z > block1PositionMin && block1.position.z < block1PositionMax;
                block1.visible = block1InsideX && block1InsideY;
            }
        });
        this.block2.forEach((block2) => {
            if (block2) {
                const block2InsideX = block2.position.x > block2PositionMin && block2.position.x < block2PositionMax;
                const block2InsideY = block2.position.z > block2PositionMin && block2.position.z < block2PositionMax;
                block2.visible = block2InsideX && block2InsideY;
            }
        });
        this.block3.forEach((block3) => {
            if (block3) {
                const block3InsideX = block3.position.x > block3PositionMin && block3.position.x < block3PositionMax;
                const block3InsideY = block3.position.z > block3PositionMin && block3.position.z < block3PositionMax;
                block3.visible = block3InsideX && block3InsideY;
            }
        });
    }

    async export(zip) {
        const forest = zip.folder('forest');

        // export trees
        const trees = { positions: [] };
        for (let i = 0; i < this.trees.length; i++) {
            const tree = this.trees[i];
            if (tree.visible) {
                trees.positions.push(tree.position);
            }
        }
        forest.file('trees.json', JSON.stringify(trees, null, 4));

        // export persons
        const persons = { tracks: [] };
        for (let i = 0; i < this.persons.length; i++) {
           const person = this.persons[i];
           persons.tracks.push(person.track);
        }
        forest.file('persons.json', JSON.stringify(persons, null, 4));

    }

    async clear() {
        // clear all persons
        this.persons.forEach(async (person) => { await person.clear(); });
        this.persons1.forEach(async (person1) => { await person1.clear(); });
        //this.persons2.forEach(async (person2) => { await person2.clear(); });
       
    }

    async reset() {
        
        await this.clear();
       
        await this.update();

        
        this.addblocks1();
        this.addblocks2();
        this.addblocks3();
        
       
        await sleep(100);
    }
}


