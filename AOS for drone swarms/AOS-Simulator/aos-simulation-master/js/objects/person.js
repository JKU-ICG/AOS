class Person {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.loader = forest.loader;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const personMargin = 1;
        const personPositionMin = -this.config.forest.ground / 2 + personMargin;
        const personPositionMax = this.config.forest.ground / 2 - personMargin;

        this.initialPosition = new THREE.Vector3(
            0, //randomFloat(personPositionMin, personPositionMax),
            0,
            0 //randomFloat(personPositionMin, personPositionMax)
        );
        this.initialDirection = 0 //randomInt(0, 360, index);
        //this.lastPosition = this.initialPosition.clone();
        this.lastDirection = this.initialDirection;

        this.track = [];
        this.actions = [];

        this.currentActivity;
        this.activityMapping = {
            laying: {
                name: 'laying',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            sitting: {
                name: 'sitting',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            standing: {
                name: 'standing',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            waving: {
                name: 'waving',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            injured: {
                name: 'injured',
                weight: 0.0,
                height: 1.8,
                speed: 1.7
            },
            walking: {
                name: 'walking',
                weight: 0.0,
                height: 1.8,
                speed: 1
            },
            running: {
                name: 'running',
                weight: 0.0,
                height: 1.8,
                speed: 3.9
            },
            idle: {
                name: 'idle',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            }
        };

        this.gender = parseInt(this.index % 2, 10);
        this.offset = [0.0, 0.04][this.gender];

        this.surfaceMaterial = new THREE.MeshStandardMaterial({
            color: this.config.material.color.person,
            roughness: 0.7,
            metalness: 0.7,
            
        });

        this.jointsMaterial = new THREE.MeshStandardMaterial({
            color: shadeColor(this.config.material.color.person, 0.4),
            roughness: 0.7,
            metalness: 0.7,
            SVGFEPointLightElement:100
        });

        this.clock = new THREE.Clock();

        this.loaded = new Promise(async function (resolve) {
            const path = ['model/RBWJ.glb', 'model/female.glb'][this.gender];
            const gltf = await this.loader.load('gltf', path);

            // init person
            this.person = THREE.SkeletonUtils.clone(gltf.scene);
            this.person.traverse((o) => {
                if (o.isMesh) {
                    const joints = o.name.includes('Joints');
                    //o.material = joints ? this.jointsMaterial : this.surfaceMaterial;
                }
            });
            this.person.scale.multiplyScalar(20 / 1000);
            this.setPosition(this.initialPosition, this.initialDirection);
            
            this.track.push({ position: this.initialPosition, direction: this.initialDirection });

            // init animation mixer
            this.animations = gltf.animations.length;
            this.mixer = new THREE.AnimationMixer(this.person);
            this.setTime(1.0);

            // init actions
            for (let i = 0; i < this.animations; ++i) {
                let clip = gltf.animations[i].clone();
                let name = clip.name;

                // add actions
                if (this.activityMapping[name]) {
                    const action = this.mixer.clipAction(clip);
                    this.activityMapping[name].action = action;
                    this.addAction(action);
                }
            }

            this.setActivity();
            this.addPerson();
            this.update();

            // animations
            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);

            resolve(this);
        }.bind(this));
    }

    addPerson() {
        setLayer(this.person, this.stage.layer.persons);
        this.scene.add(this.person);
    }

    addAction(action) {
        const clip = action.getClip();
        const settings = this.activityMapping[clip.name];
        this.setWeight(action, settings.weight);
        this.actions.push(action);
        action.play();
    }

    crossFade(startActivity, endActivity, duration) {
        const startActivityName = startActivity ? startActivity.name : this.activityMapping['idle'].name;
        const endActivityName = endActivity.name;

        const startAction = this.activityMapping[startActivityName].action;
        const endAction = this.activityMapping[endActivityName].action;

        // reset time
        this.mixer.setTime(0.0);

        // set current position
        this.setPosition(this.person.position.clone(), this.lastDirection);

        // execute cross fade
        if (!startActivity || startActivityName !== endActivityName) {
            this.setWeight(endAction, 1.0);
            endAction.time = 0;
            startAction.crossFadeTo(endAction, startActivity ? duration : 0, true);
        }

        // set current activity
        this.currentActivity = endActivity;
    }

    getActivity() {
        let activeSeed = `${this.index}-${this.config.forest.persons.count}`;

        // get active activities
        let activeActivities = [];
        Object.entries(this.config.forest.persons.activities).forEach(([activity, active]) => {
            if (active) {
                activeSeed += `-${activity}`;
                activeActivities.push(this.activityMapping[activity]);
            }
        });

        // choose random activity from active activities
        const randomIndex = randomInt(0, activeActivities.length - 1, activeSeed);
        const randomActivity = activeActivities[randomIndex];

        return randomActivity || this.activityMapping['idle'];
    }

    setActivity() {
        this.crossFade(this.currentActivity, this.getActivity(), 0.2);
    }

    setWeight(action, weight) {
        action.enabled = true;
        action.setEffectiveTimeScale(1.0);
        action.setEffectiveWeight(weight);
    }

    setTime(time) {
        this.mixer.timeScale = time;
    }

    setPosition(position, direction) {
        // update last position and direction
        this.lastPosition = position;
        this.lastDirection = direction;

        // set position with offset
        this.person.position.set(
            this.lastPosition.x,
            this.lastPosition.y,
            this.lastPosition.z
        );

        // set direction rotation
        const rotation = new THREE.Euler(0, rad(this.lastDirection ), 0);
        this.person.setRotationFromEuler(rotation);
    }

    async animate() {
        for (let i = 0; i < this.animations; ++i) {
            const action = this.actions[i];
            const clip = action.getClip();
            const settings = this.activityMapping[clip.name];
            settings.weight = action.getEffectiveWeight();
        }

        // update person position
        await this.update();

        // next animation
        requestAnimationFrame(this.animate);
    }

    async update() {
        // update action mixer time
        this.mixer.update(this.clock.getDelta());

        // update height offset based on activity
        const height = (this.currentActivity ? this.currentActivity.height : 0) + this.offset;
        this.person.position.x = this.config.forest.persons.posx;
        this.person.position.z = this.config.forest.persons.posy;
        const rotation = new THREE.Euler(0, rad(this.config.forest.persons.rotation ), 0);
        this.person.setRotationFromEuler(rotation);
        this.person.position.y = height;
        this.lastPosition = this.person.position.clone();
        // trajectory coordinates
        this.lastDirection = this.config.forest.persons.rotation;
        const start = this.lastPosition;
        const dir = new THREE.Vector3(Math.cos(rad(this.lastDirection)), 0, -Math.sin(rad(this.lastDirection)));
        const end = start.clone().add(dir);

        // move duration
        const speed = this.currentActivity.speed;
        const moveDuration = speed ? start.distanceTo(end) / speed : 0;
        if (moveDuration <= 0) {
            return;
        }

        // calculate time
        const elapsedTime = this.mixer.time;
        const trajectoryTime = elapsedTime / moveDuration;

        // calculate trajectory
        const current = new THREE.Vector3();
        const trajectory = new THREE.Line3(start, end);
        trajectory.at(trajectoryTime, current);

        // update person position
        current.y = height;
        this.person.position.set(current.x, current.y, current.z);

        // boundary check
        if (elapsedTime > 0.1) {

            // ground position constraints
            const personMargin = 1;
            const personPositionMin = -this.config.forest.ground / 2 + personMargin;
            const personPositionMax = this.config.forest.ground / 2 - personMargin;

            // boundary check
            const top = current.z <= personPositionMin;
            const bottom = current.z >= personPositionMax;
            const left = current.x <= personPositionMin;
            const right = current.x >= personPositionMax;

            // boundary detection
            const boundaryReached = top ? 'top' : (bottom ? 'bottom' : (left ? 'left' : (right ? 'right' : '')));
            if (boundaryReached) {
                const oppositeDirections = {
                    top: randomInt(185, 355, this.lastDirection),
                    bottom: randomInt(5, 175, this.lastDirection),
                    left: randomInt(85, -85, this.lastDirection),
                    right: randomInt(95, 265, this.lastDirection)
                };

                // reset time
                this.mixer.setTime(0.0);

                // move to opposite direction using a random angle
                this.setPosition(current, oppositeDirections[boundaryReached]);
                this.track.push({ position: current, direction: oppositeDirections[boundaryReached] });
            }
        }
    }

    async clear() {
        // reset time
        this.mixer.setTime(0.0);

        // set initial position
        this.setPosition(this.initialPosition, this.initialDirection);
        this.track = [{ position: this.initialPosition, direction: this.initialDirection }];
    }

    async remove() {
        this.scene.remove(this.person);
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}

class Person1 {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.loader = forest.loader;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const personMargin = 1;
        const personPositionMin = -this.config.forest.ground / 2 + personMargin;
        const personPositionMax = this.config.forest.ground / 2 - personMargin;

        this.initialPosition = new THREE.Vector3(
            0, //randomFloat(personPositionMin, personPositionMax),
            0,
            0 //randomFloat(personPositionMin, personPositionMax)
        );
        this.initialDirection = 0 //randomInt(0, 360, index);
        //this.lastPosition = this.initialPosition.clone();
        this.lastDirection = this.initialDirection;

        this.track = [];
        this.actions = [];

        this.currentActivity;
        this.activityMapping = {
            laying: {
                name: 'laying',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            sitting: {
                name: 'sitting',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            standing: {
                name: 'standing',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            waving: {
                name: 'waving',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            injured: {
                name: 'injured',
                weight: 0.0,
                height: 1.8,
                speed: 1.7
            },
            walking: {
                name: 'walking',
                weight: 0.0,
                height: 1.8,
                speed: 1
            },
            running: {
                name: 'running',
                weight: 0.0,
                height: 1.8,
                speed: 3.9
            },
            idle: {
                name: 'idle',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            }
        };

        this.gender = parseInt(this.index % 2, 10);
        this.offset = [0.0, 0.04][this.gender];

        this.surfaceMaterial = new THREE.MeshStandardMaterial({
            color: this.config.material.color.person,
            roughness: 0.7,
            metalness: 0.7,
            
        });

        this.jointsMaterial = new THREE.MeshStandardMaterial({
            color: shadeColor(this.config.material.color.person, 0.4),
            roughness: 0.7,
            metalness: 0.7,
            SVGFEPointLightElement:100
        });

        this.clock = new THREE.Clock();

        this.loaded = new Promise(async function (resolve) {
            const path = ['model/male.glb', 'model/female.glb'][this.gender];
            const gltf = await this.loader.load('gltf', path);

            // init person
            this.person = THREE.SkeletonUtils.clone(gltf.scene);
            this.person.traverse((o) => {
                if (o.isMesh) {
                    const joints = o.name.includes('Joints');
                    o.material = joints ? this.jointsMaterial : this.surfaceMaterial;
                }
            });
            this.person.scale.multiplyScalar(20 / 1000);
            this.setPosition(this.initialPosition, this.initialDirection);
            
            this.track.push({ position: this.initialPosition, direction: this.initialDirection });

            // init animation mixer
            this.animations = gltf.animations.length;
            this.mixer = new THREE.AnimationMixer(this.person);
            this.setTime(1.0);

            // init actions
            for (let i = 0; i < this.animations; ++i) {
                let clip = gltf.animations[i].clone();
                let name = clip.name;

                // add actions
                if (this.activityMapping[name]) {
                    const action = this.mixer.clipAction(clip);
                    this.activityMapping[name].action = action;
                    this.addAction(action);
                }
            }

            this.setActivity();
            this.addPerson();
            this.update();

            // animations
            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);

            resolve(this);
        }.bind(this));
    }

    addPerson() {
        setLayer(this.person, this.stage.layer.persons);
        this.scene.add(this.person);
    }

    addAction(action) {
        const clip = action.getClip();
        const settings = this.activityMapping[clip.name];
        this.setWeight(action, settings.weight);
        this.actions.push(action);
        action.play();
    }

    crossFade(startActivity, endActivity, duration) {
        const startActivityName = startActivity ? startActivity.name : this.activityMapping['idle'].name;
        const endActivityName = endActivity.name;

        const startAction = this.activityMapping[startActivityName].action;
        const endAction = this.activityMapping[endActivityName].action;

        // reset time
        this.mixer.setTime(0.0);

        // set current position
        this.setPosition(this.person.position.clone(), this.lastDirection);

        // execute cross fade
        if (!startActivity || startActivityName !== endActivityName) {
            this.setWeight(endAction, 1.0);
            endAction.time = 0;
            startAction.crossFadeTo(endAction, startActivity ? duration : 0, true);
        }

        // set current activity
        this.currentActivity = endActivity;
    }

    getActivity() {
        let activeSeed = `${this.index}-${this.config.forest.persons.count}`;

        // get active activities
        let activeActivities = [];
        Object.entries(this.config.forest.persons.activities).forEach(([activity, active]) => {
            if (active) {
                activeSeed += `-${activity}`;
                activeActivities.push(this.activityMapping[activity]);
            }
        });

        // choose random activity from active activities
        const randomIndex = randomInt(0, activeActivities.length - 1, activeSeed);
        const randomActivity = activeActivities[randomIndex];

        return randomActivity || this.activityMapping['idle'];
    }

    setActivity() {
        this.crossFade(this.currentActivity, this.getActivity(), 0.2);
    }

    setWeight(action, weight) {
        action.enabled = true;
        action.setEffectiveTimeScale(1.0);
        action.setEffectiveWeight(weight);
    }

    setTime(time) {
        this.mixer.timeScale = time;
    }

    setPosition(position, direction) {
        // update last position and direction
        this.lastPosition = position;
        this.lastDirection = direction;

        // set position with offset
        this.person.position.set(
            this.lastPosition.x,
            this.lastPosition.y,
            this.lastPosition.z
        );

        // set direction rotation
        const rotation = new THREE.Euler(0, rad(this.lastDirection ), 0);
        this.person.setRotationFromEuler(rotation);
    }

    async animate() {
        for (let i = 0; i < this.animations; ++i) {
            const action = this.actions[i];
            const clip = action.getClip();
            const settings = this.activityMapping[clip.name];
            settings.weight = action.getEffectiveWeight();
        }

        // update person position
        await this.update();

        // next animation
        requestAnimationFrame(this.animate);
    }

    async update() {
        // update action mixer time
        this.mixer.update(this.clock.getDelta());

        // update height offset based on activity
        const height = (this.currentActivity ? this.currentActivity.height : 0) + this.offset;
        this.person.position.x = this.config.forest.persons1.posx;
        this.person.position.z = this.config.forest.persons1.posy;
        const rotation = new THREE.Euler(0, rad(this.config.forest.persons1.rotation ), 0);
        this.person.setRotationFromEuler(rotation);
        this.person.position.y = height;
        this.lastPosition = this.person.position.clone();
        // trajectory coordinates
        this.lastDirection = this.config.forest.persons1.rotation;
        const start = this.lastPosition;
        const dir = new THREE.Vector3(Math.cos(rad(this.lastDirection)), 0, -Math.sin(rad(this.lastDirection)));
        const end = start.clone().add(dir);

        // move duration
        const speed = this.currentActivity.speed;
        const moveDuration = speed ? start.distanceTo(end) / speed : 0;
        if (moveDuration <= 0) {
            return;
        }

        // calculate time
        const elapsedTime = this.mixer.time;
        const trajectoryTime = elapsedTime / moveDuration;

        // calculate trajectory
        const current = new THREE.Vector3();
        const trajectory = new THREE.Line3(start, end);
        trajectory.at(trajectoryTime, current);

        // update person position
        current.y = height;
        this.person.position.set(current.x, current.y, current.z);

        // boundary check
        if (elapsedTime > 0.1) {

            // ground position constraints
            const personMargin = 1;
            const personPositionMin = -this.config.forest.ground / 2 + personMargin;
            const personPositionMax = this.config.forest.ground / 2 - personMargin;

            // boundary check
            const top = current.z <= personPositionMin;
            const bottom = current.z >= personPositionMax;
            const left = current.x <= personPositionMin;
            const right = current.x >= personPositionMax;

            // boundary detection
            const boundaryReached = top ? 'top' : (bottom ? 'bottom' : (left ? 'left' : (right ? 'right' : '')));
            if (boundaryReached) {
                const oppositeDirections = {
                    top: randomInt(185, 355, this.lastDirection),
                    bottom: randomInt(5, 175, this.lastDirection),
                    left: randomInt(85, -85, this.lastDirection),
                    right: randomInt(95, 265, this.lastDirection)
                };

                // reset time
                this.mixer.setTime(0.0);

                // move to opposite direction using a random angle
                this.setPosition(current, oppositeDirections[boundaryReached]);
                this.track.push({ position: current, direction: oppositeDirections[boundaryReached] });
            }
        }
    }

    async clear() {
        // reset time
        this.mixer.setTime(0.0);

        // set initial position
        this.setPosition(this.initialPosition, this.initialDirection);
        this.track = [{ position: this.initialPosition, direction: this.initialDirection }];
    }

    async remove() {
        this.scene.remove(this.person);
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}


class Person2 {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.loader = forest.loader;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const personMargin = 1;
        const personPositionMin = -this.config.forest.ground / 2 + personMargin;
        const personPositionMax = this.config.forest.ground / 2 - personMargin;

        this.initialPosition = new THREE.Vector3(
            0, //randomFloat(personPositionMin, personPositionMax),
            0,
            10 //randomFloat(personPositionMin, personPositionMax)
        );
        this.initialDirection = 0 //randomInt(0, 360, index);
        //this.lastPosition = this.initialPosition.clone();
        this.lastDirection = this.initialDirection;

        this.track = [];
        this.actions = [];

        this.currentActivity;
        this.activityMapping = {
            laying: {
                name: 'laying',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            sitting: {
                name: 'sitting',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            standing: {
                name: 'standing',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            waving: {
                name: 'waving',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            },
            injured: {
                name: 'injured',
                weight: 0.0,
                height: 1.8,
                speed: 1.7
            },
            walking: {
                name: 'walking',
                weight: 0.0,
                height: 1.8,
                speed: 1.8
            },
            running: {
                name: 'running',
                weight: 0.0,
                height: 1.8,
                speed: 3.9
            },
            idle: {
                name: 'idle',
                weight: 0.0,
                height: 1.8,
                speed: 0.0
            }
        };

        this.gender = parseInt(this.index % 2, 10);
        this.offset = [0.0, 0.04][this.gender];

        this.surfaceMaterial = new THREE.MeshStandardMaterial({
            color: this.config.material.color.person,
            roughness: 0.7,
            metalness: 0.7
        });

        this.jointsMaterial = new THREE.MeshStandardMaterial({
            color: shadeColor(this.config.material.color.person, 0.4),
            roughness: 0.7,
            metalness: 0.7
        });

        this.clock = new THREE.Clock();

        this.loaded = new Promise(async function (resolve) {
            const path = ['model/male.glb', 'model/female.glb'][this.gender];
            const gltf = await this.loader.load('gltf', path);

            // init person
            this.person2 = THREE.SkeletonUtils.clone(gltf.scene);
            this.person2.traverse((o) => {
                if (o.isMesh) {
                    const joints = o.name.includes('Joints');
                    o.material = joints ? this.jointsMaterial : this.surfaceMaterial;
                }
            });
            this.person2.scale.multiplyScalar(20 / 1000);
            this.setPosition(this.initialPosition, this.initialDirection);
            this.track.push({ position: this.initialPosition, direction: this.initialDirection });

            // init animation mixer
            this.animations = gltf.animations.length;
            this.mixer = new THREE.AnimationMixer(this.person2);
            this.setTime(1.0);

            // init actions
            for (let i = 0; i < this.animations; ++i) {
                let clip = gltf.animations[i].clone();
                let name = clip.name;

                // add actions
                if (this.activityMapping[name]) {
                    const action = this.mixer.clipAction(clip);
                    this.activityMapping[name].action = action;
                    this.addAction(action);
                }
            }

            this.setActivity();
            this.addPerson2();
            this.update();

            // animations
            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);

            resolve(this);
        }.bind(this));
    }

    addPerson2() {
        setLayer(this.person2, this.stage.layer.persons2);
        this.scene.add(this.person2);
    }

    addAction(action) {
        const clip = action.getClip();
        const settings = this.activityMapping[clip.name];
        this.setWeight(action, settings.weight);
        this.actions.push(action);
        action.play();
    }

    crossFade(startActivity, endActivity, duration) {
        const startActivityName = startActivity ? startActivity.name : this.activityMapping['idle'].name;
        const endActivityName = endActivity.name;

        const startAction = this.activityMapping[startActivityName].action;
        const endAction = this.activityMapping[endActivityName].action;

        // reset time
        this.mixer.setTime(0.0);

        // set current position
        this.setPosition(this.person2.position.clone(), this.lastDirection);

        // execute cross fade
        if (!startActivity || startActivityName !== endActivityName) {
            this.setWeight(endAction, 1.0);
            endAction.time = 0;
            startAction.crossFadeTo(endAction, startActivity ? duration : 0, true);
        }

        // set current activity
        this.currentActivity = endActivity;
    }

    getActivity() {
        let activeSeed = `${this.index}-${this.config.forest.persons2.count2}`;

        // get active activities
        let activeActivities = [];
        Object.entries(this.config.forest.persons2.activities).forEach(([activity, active]) => {
            if (active) {
                activeSeed += `-${activity}`;
                activeActivities.push(this.activityMapping[activity]);
            }
        });

        // choose random activity from active activities
        const randomIndex = randomInt(0, activeActivities.length - 1, activeSeed);
        const randomActivity = activeActivities[randomIndex];

        return randomActivity || this.activityMapping['idle'];
    }

    setActivity() {
        this.crossFade(this.currentActivity, this.getActivity(), 0.2);
    }

    setWeight(action, weight) {
        action.enabled = true;
        action.setEffectiveTimeScale(1.0);
        action.setEffectiveWeight(weight);
    }

    setTime(time) {
        this.mixer.timeScale = time;
    }

    setPosition(position, direction) {
        // update last position and direction
        this.lastPosition = position;
        this.lastDirection = direction;

        // set position with offset
        this.person2.position.set(
            this.lastPosition.x,
            this.lastPosition.y,
            this.lastPosition.z
        );

        // set direction rotation
        const rotation = new THREE.Euler(0, rad(this.lastDirection), 0);
        this.person2.setRotationFromEuler(rotation);
    }

    async animate() {
        for (let i = 0; i < this.animations; ++i) {
            const action = this.actions[i];
            const clip = action.getClip();
            const settings = this.activityMapping[clip.name];
            settings.weight = action.getEffectiveWeight();
        }

        // update person position
        await this.update();

        // next animation
        requestAnimationFrame(this.animate);
    }

    async update() {
        // update action mixer time
        this.mixer.update(this.clock.getDelta());

        // update height offset based on activity
        const height = (this.currentActivity ? this.currentActivity.height : 0) + this.offset;
        this.person2.position.x = this.config.forest.persons1.posx;
        this.person2.position.z = this.config.forest.persons1.posy;
        const rotation = new THREE.Euler(0, rad(this.config.forest.persons1.rotation ), 0);
        this.person2.setRotationFromEuler(rotation);
        this.person2.position.y = height;
        this.lastPosition = this.person2.position.clone();

        // trajectory coordinates
        this.lastDirection = this.config.forest.persons1.rotation;
        const start = this.lastPosition;
        const dir = new THREE.Vector3(Math.cos(rad(this.lastDirection)), 0, -Math.sin(rad(this.lastDirection)));
        const end = start.clone().add(dir);

        // move duration
        const speed = this.currentActivity.speed;
        const moveDuration = speed ? start.distanceTo(end) / speed : 0;
        if (moveDuration <= 0) {
            return;
        }

        // calculate time
        const elapsedTime = this.mixer.time;
        const trajectoryTime = elapsedTime / moveDuration;

        // calculate trajectory
        const current = new THREE.Vector3();
        const trajectory = new THREE.Line3(start, end);
        trajectory.at(trajectoryTime, current);

        // update person position
        current.y = height;
        this.person2.position.set(current.x, current.y, current.z);

        // boundary check
        if (elapsedTime > 0.1) {

            // ground position constraints
            const personMargin = 1;
            const personPositionMin = -this.config.forest.ground / 2 + personMargin;
            const personPositionMax = this.config.forest.ground / 2 - personMargin;

            // boundary check
            const top = current.z <= personPositionMin;
            const bottom = current.z >= personPositionMax;
            const left = current.x <= personPositionMin;
            const right = current.x >= personPositionMax;

            // boundary detection
            const boundaryReached = top ? 'top' : (bottom ? 'bottom' : (left ? 'left' : (right ? 'right' : '')));
            if (boundaryReached) {
                const oppositeDirections = {
                    top: randomInt(185, 355, this.lastDirection),
                    bottom: randomInt(5, 175, this.lastDirection),
                    left: randomInt(85, -85, this.lastDirection),
                    right: randomInt(95, 265, this.lastDirection)
                };

                // reset time
                this.mixer.setTime(0.0);

                // move to opposite direction using a random angle
                this.setPosition(current, oppositeDirections[boundaryReached]);
                this.track.push({ position: current, direction: oppositeDirections[boundaryReached] });
            }
        }
    }

    async clear() {
        // reset time
        this.mixer.setTime(0.0);

        // set initial position
        this.setPosition(this.initialPosition, this.initialDirection);
        this.track = [{ position: this.initialPosition, direction: this.initialDirection }];
    }

    async remove() {
        this.scene.remove(this.person2);
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}


class Block1 {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const width = 0.75;
        const height = 0.75;
        const alpha = this.config.forest.blockOrientation;
        const beta = (alpha * 0.0174533);

        const segments = 4;
        
        const widthSegments = width * segments;
        const heightSegments = height * segments;

        const planeGeometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments);
        planeGeometry.rotateX(-Math.PI / 2).rotateY(beta).translate(0, 0.1, 0);
        const planeMaterial = new THREE.MeshStandardMaterial({ color: this.config.material.color.block1 });

        const wireGeometry = new THREE.WireframeGeometry(planeGeometry);
        const wireMaterial = new THREE.LineBasicMaterial({ color: this.config.material.color.block1 });

        this.wire = new THREE.LineSegments(wireGeometry, wireMaterial);
        this.mesh = new THREE.Mesh(planeGeometry, planeMaterial);
        this.mesh.add(this.wire);
    }
}

class Block2 {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const width = 1;
        const height = 2;
        const alpha = this.config.forest.blockOrientation;
        const beta = (alpha * 0.0174533);

        const segments = 4;
        
        const widthSegments = width * segments;
        const heightSegments = height * segments;

        const planeGeometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments);
        planeGeometry.rotateX(-Math.PI / 2).rotateY(beta).translate(0, 0.1, 0);
        const planeMaterial = new THREE.MeshStandardMaterial({ color: this.config.material.color.block2 });

        const wireGeometry = new THREE.WireframeGeometry(planeGeometry);
        const wireMaterial = new THREE.LineBasicMaterial({ color: this.config.material.color.block2 });

        this.wire = new THREE.LineSegments(wireGeometry, wireMaterial);
        this.mesh = new THREE.Mesh(planeGeometry, planeMaterial);
        this.mesh.add(this.wire);
    }
}

class Block3 {
    constructor(forest, index) {
        this.root = forest.root;
        this.config = forest.config;
        this.scene = forest.scene;
        this.stage = forest.stage;
        this.forest = forest;
        this.index = index;

        const width = 1;
        const height = 2;
        const alpha = this.config.forest.blockOrientation;
        const beta = (alpha * 0.0174533);

        const segments = 4;
        
        const widthSegments = width * segments;
        const heightSegments = height * segments;

        const planeGeometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments);
        planeGeometry.rotateX(-Math.PI / 2).rotateY(beta).translate(0, 0.1, 0);
        const planeMaterial = new THREE.MeshStandardMaterial({ color: this.config.material.color.block3 });

        const wireGeometry = new THREE.WireframeGeometry(planeGeometry);
        const wireMaterial = new THREE.LineBasicMaterial({ color: this.config.material.color.block3 });

        this.wire = new THREE.LineSegments(wireGeometry, wireMaterial);
        this.mesh = new THREE.Mesh(planeGeometry, planeMaterial);
        this.mesh.add(this.wire);
    }
}