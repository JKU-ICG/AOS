importScripts('../utils/helper.js', '../objects/tree.js');

class Task {
    constructor(chunks) {
        this.chunks = chunks;
    }

    getTrees(configs) {
        const trees = [];

        configs.forEach((config, i) => {
            trees.push(new Tree(config));

            // chunk message
            if (!((i + 1) % this.chunks)) {
                self.postMessage({ trees: trees });
                trees.splice(0, trees.length);
            }
        });

        // final message
        self.postMessage({ trees: trees });
    }
}

self.onmessage = (e) => {
    const params = e.data.params;
    const method = e.data.method;

    // init task
    const task = new Task(params.chunks);

    // execute task
    switch (method) {
        case 'getTrees':
            task.getTrees(params.configs || []);
            break;
        default:
            self.postMessage();
    }
};