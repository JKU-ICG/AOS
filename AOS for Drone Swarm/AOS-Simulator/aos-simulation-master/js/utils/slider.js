class Slider {
    constructor(root, config, loader) {
        this.root = root;
        this.config = config;
        this.loader = loader;

        this.images = root.querySelector('#images');
        this.previews = root.querySelector('#previews');

        this.image = this.images.querySelectorAll('.image');
        this.preview = this.previews.querySelectorAll('.image');

        this.width = { slider: 0, images: 0, image: 0 };
        this.scroll = { start: 0, next: 0, x: 0 };
        this.touch = { start: 0, x: 0 };

        // animations
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);

        // events
        this.images.addEventListener('wheel', this.scrollWheel.bind(this));
        this.images.addEventListener('touchstart', this.touchStart.bind(this));
        this.images.addEventListener('touchmove', this.touchMove.bind(this));
        this.images.addEventListener('touchend', this.touchEnd.bind(this));
        this.images.addEventListener('mousedown', this.touchStart.bind(this));
        this.images.addEventListener('mousemove', this.touchMove.bind(this));
        this.images.addEventListener('mouseleave', this.touchEnd.bind(this));
        this.images.addEventListener('mouseup', this.touchEnd.bind(this));

        window.addEventListener('resize', this.update.bind(this));
    }

    scrollWheel(e) {
        this.scroll.x -= e.deltaY * 5.0;
    }

    touchStart(e) {
        this.touch.start = e.clientX || e.touches && e.touches[0].clientX || this.touch.start;
        this.images.classList.add('dragging');
    }

    touchMove(e) {
        if (!this.images.classList.contains('dragging')) {
            return;
        }

        this.touch.x = e.clientX || e.touches && e.touches[0].clientX || this.touch.x;
        this.scroll.x += (this.touch.x - this.touch.start) * 2.5;
        this.touch.start = this.touch.x;
    }

    touchEnd() {
        this.images.classList.remove('dragging');
    }

    addImage(image) {
        // remove first children, ignore up to number of used images
        for (let i = 0; i <= this.count - this.config.drone.camera.images; i++) {
            const img = this.image[i];
            img.classList.add('removed');
            sleep().then(() => {
                if (this.images.contains(img)) {
                    this.images.removeChild(img);
                }
            });
        }

        // append child
        this.images.append(image);

        // update width and scroll to last child
        this.update().then((empty) => {
            if (!empty) {
                this.scroll.x = this.width.slider - this.width.images;
            }
        });
    }

    addPreview(preview) {
        // remove first children, ignore last live preview image
        for (let i = 0; i < this.preview.length - 1; i++) {
            const img = this.preview[i];
            img.classList.add('removed');
            sleep().then(() => {
                if (this.images.contains(img)) {
                    this.images.removeChild(img);
                }
            });
        }

        // prepend child
        this.previews.prepend(preview);
    }

    async animate() {
        // calculate scroll
        this.scroll.x = Math.min(0, Math.max(this.width.slider - this.width.images, this.scroll.x));
        this.scroll.next = interpolate(this.scroll.next, this.scroll.x, 0.2);

        // update slider
        this.update().then((empty) => {
            if (!empty) {
                const delta = this.scroll.next - this.scroll.start;

                // set positions
                gsap.set(this.image, {
                    x: (i) => { return i * this.width.image + this.scroll.next; },
                    modifiers: { x: (x) => { return gsap.utils.clamp(-this.width.slider, this.width.images, parseInt(x, 10)) + 'px'; } }
                });

                // animate transitions
                gsap.to(this.image, {
                    skewX: -delta * 0.1,
                    rotate: delta * 0.01,
                    scale: 1 - Math.min(100, Math.abs(delta)) * 0.003
                });

                // scroll start position
                this.scroll.start = this.scroll.next;

                // image visibility
                for (let i = 1; i < this.count; i++) {
                    this.image[i].style.zIndex = 1;
                }
                this.image[this.count - 1].style.zIndex = 1;
            }
            else {
                // reset positions
                this.scroll = { start: 0, next: 0, x: 0 };
            }

            requestAnimationFrame(this.animate);
        });
    }

    async update() {
        this.image = this.images.querySelectorAll('.image:not(.removed)');
        this.preview = this.previews.querySelectorAll('.image:not(.removed)');

        // count images
        this.count = this.image.length;

        // update width
        if (this.count) {
            this.width = {
                slider: this.images.clientWidth - this.previews.clientWidth - 8,
                images: this.count * (this.image[0].firstChild.clientWidth + 4),
                image: this.image[0].firstChild.clientWidth + 4
            };
            return false;
        }
        return true;
    }

    async clear() {
        // clear images, all of them
        for (let i = 0; i < this.image.length; i++) {
            this.images.removeChild(this.image[i]);
        }

        // clear previews, ignore last live preview
        for (let i = 0; i < this.preview.length; i++) {
            this.previews.removeChild(this.preview[i]);
        }
    }

    async reset() {
        await this.clear();
        await this.update();

        await sleep(100);
    }
}