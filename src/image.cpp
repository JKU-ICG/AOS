#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include "image.h"
#include "utils.h"
#include <stdio.h>
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <math.h>

#ifndef STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#endif
#ifndef STB_IMAGE_WRITE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#endif


float colors[6][3] = { {1,0,1}, {0,0,1},{0,1,1},{0,1,0},{1,1,0},{1,0,0} };

float get_color(int c, int x, int max)
{
    float ratio = ((float)x/max)*5;
    int i = floor(ratio);
    int j = ceil(ratio);
    ratio -= i;
    float r = (1-ratio) * colors[i][c] + ratio*colors[j][c];
    //printf("%f\n", r);
    return r;
}

static float get_pixel(Image m, int x, int y, int c)
{
    assert(x < m.w && y < m.h && c < m.c);
    return m.data[c*m.h*m.w + y*m.w + x];
}
static float get_pixel_extend(Image m, int x, int y, int c)
{
    if (x < 0 || x >= m.w || y < 0 || y >= m.h) return 0;
    /*
    if(x < 0) x = 0;
    if(x >= m.w) x = m.w-1;
    if(y < 0) y = 0;
    if(y >= m.h) y = m.h-1;
    */
    if (c < 0 || c >= m.c) return 0;
    return get_pixel(m, x, y, c);
}
static void set_pixel(Image m, int x, int y, int c, float val)
{
    if (x < 0 || y < 0 || c < 0 || x >= m.w || y >= m.h || c >= m.c) return;
    assert(x < m.w && y < m.h && c < m.c);
    m.data[c*m.h*m.w + y*m.w + x] = val;
}
static void add_pixel(Image m, int x, int y, int c, float val)
{
    assert(x < m.w && y < m.h && c < m.c);
    m.data[c*m.h*m.w + y*m.w + x] += val;
}

void composite_image(Image source, Image dest, int dx, int dy)
{
    int x,y,k;
    for(k = 0; k < source.c; ++k){
        for(y = 0; y < source.h; ++y){
            for(x = 0; x < source.w; ++x){
                float val = get_pixel(source, x, y, k);
                float val2 = get_pixel_extend(dest, dx+x, dy+y, k);
                set_pixel(dest, dx+x, dy+y, k, val * val2);
            }
        }
    }
}

Image border_image(Image a, int border)
{
    Image b = make_image(a.w + 2*border, a.h + 2*border, a.c);
    int x,y,k;
    for(k = 0; k < b.c; ++k){
        for(y = 0; y < b.h; ++y){
            for(x = 0; x < b.w; ++x){
                float val = get_pixel_extend(a, x - border, y - border, k);
                if(x - border < 0 || x - border >= a.w || y - border < 0 || y - border >= a.h) val = 1;
                set_pixel(b, x, y, k, val);
            }
        }
    }
    return b;
}

Image tile_images(Image a, Image b, int dx)
{
    if(a.w == 0) return copy_image(b);
    Image c = make_image(a.w + b.w + dx, (a.h > b.h) ? a.h : b.h, (a.c > b.c) ? a.c : b.c);
    //fill_cpu(c.w*c.h*c.c, 1, c.data, 1);
    embed_image(a, c, 0, 0);
    composite_image(b, c, a.w + dx, 0);
    return c;
}

Image get_label(Image **characters, char *string, int size)
{
    if(size > 7) size = 7;
    Image label = make_empty_image(0,0,0);
    while(*string){
        Image l = characters[size][(int)*string];
        Image n = tile_images(label, l, -size - 1 + (size+1)/2);
        free_image(label);
        label = n;
        ++string;
    }
    Image b = border_image(label, label.h*.25);
    free_image(label);
    return b;
}

Image get_label_v3(Image **characters, char *string, int size)
{
    size = size / 10;
    if (size > 7) size = 7;
    Image label = make_empty_image(0, 0, 0);
    while (*string) {
        Image l = characters[size][(int)*string];
        Image n = tile_images(label, l, -size - 1 + (size + 1) / 2);
        free_image(label);
        label = n;
        ++string;
    }
    Image b = border_image(label, label.h*.05);
    free_image(label);
    return b;
}

void draw_label(Image a, int r, int c, Image label, const float *rgb)
{
    int w = label.w;
    int h = label.h;
    if (r - h >= 0) r = r - h;

    int i, j, k;
    for(j = 0; j < h && j + r < a.h; ++j){
        for(i = 0; i < w && i + c < a.w; ++i){
            for(k = 0; k < label.c; ++k){
                float val = get_pixel(label, i, j, k);
                set_pixel(a, i+c, j+r, k, rgb[k] * val);
            }
        }
    }
}

void draw_weighted_label(Image a, int r, int c, Image label, const float *rgb, const float alpha)
{
    int w = label.w;
    int h = label.h;
    if (r - h >= 0) r = r - h;

    int i, j, k;
    for (j = 0; j < h && j + r < a.h; ++j) {
        for (i = 0; i < w && i + c < a.w; ++i) {
            for (k = 0; k < label.c; ++k) {
                float val1 = get_pixel(label, i, j, k);
                float val2 = get_pixel(a, i + c, j + r, k);
                float val_dst = val1 * rgb[k] * alpha + val2 * (1 - alpha);
                set_pixel(a, i + c, j + r, k, val_dst);
            }
        }
    }
}

void draw_box_bw(Image a, int x1, int y1, int x2, int y2, float brightness)
{
    //normalize_image(a);
    int i;
    if (x1 < 0) x1 = 0;
    if (x1 >= a.w) x1 = a.w - 1;
    if (x2 < 0) x2 = 0;
    if (x2 >= a.w) x2 = a.w - 1;

    if (y1 < 0) y1 = 0;
    if (y1 >= a.h) y1 = a.h - 1;
    if (y2 < 0) y2 = 0;
    if (y2 >= a.h) y2 = a.h - 1;

    for (i = x1; i <= x2; ++i) {
        a.data[i + y1*a.w + 0 * a.w*a.h] = brightness;
        a.data[i + y2*a.w + 0 * a.w*a.h] = brightness;
    }
    for (i = y1; i <= y2; ++i) {
        a.data[x1 + i*a.w + 0 * a.w*a.h] = brightness;
        a.data[x2 + i*a.w + 0 * a.w*a.h] = brightness;
    }
}

void draw_box_width_bw(Image a, int x1, int y1, int x2, int y2, int w, float brightness)
{
    int i;
    for (i = 0; i < w; ++i) {
        float alternate_color = (w % 2) ? (brightness) : (1.0 - brightness);
        draw_box_bw(a, x1 + i, y1 + i, x2 - i, y2 - i, alternate_color);
    }
}

void draw_box(Image a, int x1, int y1, int x2, int y2, float r, float g, float b)
{
    //normalize_image(a);
    int i;
    if(x1 < 0) x1 = 0;
    if(x1 >= a.w) x1 = a.w-1;
    if(x2 < 0) x2 = 0;
    if(x2 >= a.w) x2 = a.w-1;

    if(y1 < 0) y1 = 0;
    if(y1 >= a.h) y1 = a.h-1;
    if(y2 < 0) y2 = 0;
    if(y2 >= a.h) y2 = a.h-1;

    for(i = x1; i <= x2; ++i){
        a.data[i + y1*a.w + 0*a.w*a.h] = r;
        a.data[i + y2*a.w + 0*a.w*a.h] = r;

        a.data[i + y1*a.w + 1*a.w*a.h] = g;
        a.data[i + y2*a.w + 1*a.w*a.h] = g;

        a.data[i + y1*a.w + 2*a.w*a.h] = b;
        a.data[i + y2*a.w + 2*a.w*a.h] = b;
    }
    for(i = y1; i <= y2; ++i){
        a.data[x1 + i*a.w + 0*a.w*a.h] = r;
        a.data[x2 + i*a.w + 0*a.w*a.h] = r;

        a.data[x1 + i*a.w + 1*a.w*a.h] = g;
        a.data[x2 + i*a.w + 1*a.w*a.h] = g;

        a.data[x1 + i*a.w + 2*a.w*a.h] = b;
        a.data[x2 + i*a.w + 2*a.w*a.h] = b;
    }
}


void transpose_image(Image im)
{
    assert(im.w == im.h);
    int n, m;
    int c;
    for(c = 0; c < im.c; ++c){
        for(n = 0; n < im.w-1; ++n){
            for(m = n + 1; m < im.w; ++m){
                float swap = im.data[m + im.w*(n + im.h*c)];
                im.data[m + im.w*(n + im.h*c)] = im.data[n + im.w*(m + im.h*c)];
                im.data[n + im.w*(m + im.h*c)] = swap;
            }
        }
    }
}

void rotate_image_cw(Image im, int times)
{
    assert(im.w == im.h);
    times = (times + 400) % 4;
    int i, x, y, c;
    int n = im.w;
    for(i = 0; i < times; ++i){
        for(c = 0; c < im.c; ++c){
            for(x = 0; x < n/2; ++x){
                for(y = 0; y < (n-1)/2 + 1; ++y){
                    float temp = im.data[y + im.w*(x + im.h*c)];
                    im.data[y + im.w*(x + im.h*c)] = im.data[n-1-x + im.w*(y + im.h*c)];
                    im.data[n-1-x + im.w*(y + im.h*c)] = im.data[n-1-y + im.w*(n-1-x + im.h*c)];
                    im.data[n-1-y + im.w*(n-1-x + im.h*c)] = im.data[x + im.w*(n-1-y + im.h*c)];
                    im.data[x + im.w*(n-1-y + im.h*c)] = temp;
                }
            }
        }
    }
}

void flip_image(Image a)
{
    int i,j,k;
    for(k = 0; k < a.c; ++k){
        for(i = 0; i < a.h; ++i){
            for(j = 0; j < a.w/2; ++j){
                int index = j + a.w*(i + a.h*(k));
                int flip = (a.w - j - 1) + a.w*(i + a.h*(k));
                float swap = a.data[flip];
                a.data[flip] = a.data[index];
                a.data[index] = swap;
            }
        }
    }
}

Image image_distance(Image a, Image b)
{
    int i,j;
    Image dist = make_image(a.w, a.h, 1);
    for(i = 0; i < a.c; ++i){
        for(j = 0; j < a.h*a.w; ++j){
            dist.data[j] += pow(a.data[i*a.h*a.w+j]-b.data[i*a.h*a.w+j],2);
        }
    }
    for(j = 0; j < a.h*a.w; ++j){
        dist.data[j] = sqrt(dist.data[j]);
    }
    return dist;
}

void embed_image(Image source, Image dest, int dx, int dy)
{
    int x,y,k;
    for(k = 0; k < source.c; ++k){
        for(y = 0; y < source.h; ++y){
            for(x = 0; x < source.w; ++x){
                float val = get_pixel(source, x,y,k);
                set_pixel(dest, dx+x, dy+y, k, val);
            }
        }
    }
}

Image collapse_image_layers(Image source, int border)
{
    int h = source.h;
    h = (h+border)*source.c - border;
    Image dest = make_image(source.w, h, 1);
    int i;
    for(i = 0; i < source.c; ++i){
        Image layer = get_image_layer(source, i);
        int h_offset = i*(source.h+border);
        embed_image(layer, dest, 0, h_offset);
        free_image(layer);
    }
    return dest;
}

void constrain_image(Image im)
{
    int i;
    for(i = 0; i < im.w*im.h*im.c; ++i){
        if(im.data[i] < 0) im.data[i] = 0;
        if(im.data[i] > 1) im.data[i] = 1;
    }
}

void normalize_image(Image p)
{
    int i;
    float min = 9999999;
    float max = -999999;

    for(i = 0; i < p.h*p.w*p.c; ++i){
        float v = p.data[i];
        if(v < min) min = v;
        if(v > max) max = v;
    }
    if(max - min < .000000001){
        min = 0;
        max = 1;
    }
    for(i = 0; i < p.c*p.w*p.h; ++i){
        p.data[i] = (p.data[i] - min)/(max-min);
    }
}

void normalize_image2(Image p)
{
    float* min = (float*)xcalloc(p.c, sizeof(float));
    float* max = (float*)xcalloc(p.c, sizeof(float));
    int i,j;
    for(i = 0; i < p.c; ++i) min[i] = max[i] = p.data[i*p.h*p.w];

    for(j = 0; j < p.c; ++j){
        for(i = 0; i < p.h*p.w; ++i){
            float v = p.data[i+j*p.h*p.w];
            if(v < min[j]) min[j] = v;
            if(v > max[j]) max[j] = v;
        }
    }
    for(i = 0; i < p.c; ++i){
        if(max[i] - min[i] < .000000001){
            min[i] = 0;
            max[i] = 1;
        }
    }
    for(j = 0; j < p.c; ++j){
        for(i = 0; i < p.w*p.h; ++i){
            p.data[i+j*p.h*p.w] = (p.data[i+j*p.h*p.w] - min[j])/(max[j]-min[j]);
        }
    }
    free(min);
    free(max);
}

void copy_image_inplace(Image src, Image dst)
{
    memcpy(dst.data, src.data, src.h*src.w*src.c * sizeof(float));
}

Image copy_image(Image p)
{
    Image copy = p;
    copy.data = (float*)xcalloc(p.h * p.w * p.c, sizeof(float));
    memcpy(copy.data, p.data, p.h*p.w*p.c*sizeof(float));
    return copy;
}

void rgbgr_image(Image im)
{
    int i;
    for(i = 0; i < im.w*im.h; ++i){
        float swap = im.data[i];
        im.data[i] = im.data[i+im.w*im.h*2];
        im.data[i+im.w*im.h*2] = swap;
    }
}

void show_image(Image p, const char *name)
{
#ifdef OPENCV
    show_image_cv(p, name);
#else
    fprintf(stderr, "Not compiled with OpenCV, saving to %s.png instead\n", name);
    save_image(p, name);
#endif  // OPENCV
}

void save_image_png(Image im, const char *name)
{
    const unsigned int buff_size = 256;
    char buff[buff_size];
    //sprintf(buff, "%s (%d)", name, windows);
    sprintf_s(buff, buff_size, "%s.png", name);
    unsigned char* data = (unsigned char*)xcalloc(im.w * im.h * im.c, sizeof(unsigned char));
    int i,k;
    for(k = 0; k < im.c; ++k){
        for(i = 0; i < im.w*im.h; ++i){
            data[i*im.c+k] = (unsigned char) (255*im.data[i + k*im.w*im.h]);
        }
    }
    int success = stbi_write_png(buff, im.w, im.h, im.c, data, im.w*im.c);
    free(data);
    if(!success) fprintf(stderr, "Failed to write Image %s\n", buff);
}

void save_image_options(Image im, const char *name, IMTYPE f, int quality)
{
    const unsigned int buff_size = 256;
    char buff[buff_size];
    //sprintf(buff, "%s (%d)", name, windows);
    if (f == PNG)      sprintf_s(buff, buff_size, "%s.png", name);
    else if (f == BMP) sprintf_s(buff, buff_size, "%s.bmp", name);
    else if (f == TGA) sprintf_s(buff, buff_size, "%s.tga", name);
    else if (f == JPG) sprintf_s(buff, buff_size, "%s.jpg", name);
    else               sprintf_s(buff, buff_size, "%s.png", name);
    unsigned char* data = (unsigned char*)xcalloc(im.w * im.h * im.c, sizeof(unsigned char));
    int i, k;
    for (k = 0; k < im.c; ++k) {
        for (i = 0; i < im.w*im.h; ++i) {
            data[i*im.c + k] = (unsigned char)(255 * im.data[i + k*im.w*im.h]);
        }
    }
    int success = 0;
    if (f == PNG)       success = stbi_write_png(buff, im.w, im.h, im.c, data, im.w*im.c);
    else if (f == BMP) success = stbi_write_bmp(buff, im.w, im.h, im.c, data);
    else if (f == TGA) success = stbi_write_tga(buff, im.w, im.h, im.c, data);
    else if (f == JPG) success = stbi_write_jpg(buff, im.w, im.h, im.c, data, quality);
    free(data);
    if (!success) fprintf(stderr, "Failed to write Image %s\n", buff);
}

void save_image(Image im, const char *name)
{
    save_image_options(im, name, JPG, 80);
}

void save_image_jpg(Image p, const char *name)
{
    save_image_options(p, name, JPG, 80);
}

void show_image_layers(Image p, char *name)
{
    int i;
    char buff[256];
    for(i = 0; i < p.c; ++i){
        sprintf_s(buff,256, "%s - Layer %d", name, i);
        Image layer = get_image_layer(p, i);
        show_image(layer, buff);
        free_image(layer);
    }
}

void show_image_collapsed(Image p, char *name)
{
    Image c = collapse_image_layers(p, 1);
    show_image(c, name);
    free_image(c);
}

Image make_empty_image(int w, int h, int c)
{
    Image out;
    out.data = 0;
    out.h = h;
    out.w = w;
    out.c = c;
    return out;
}

Image make_image(int w, int h, int c)
{
    Image out = make_empty_image(w,h,c);
    out.data = (float*)xcalloc(h * w * c, sizeof(float));
    return out;
}

Image make_random_image(int w, int h, int c)
{
    Image out = make_empty_image(w,h,c);
    out.data = (float*)xcalloc(h * w * c, sizeof(float));
    int i;
    for(i = 0; i < w*h*c; ++i){
        out.data[i] = (rand_normal() * .25) + .5;
    }
    return out;
}

Image float_to_image_scaled(int w, int h, int c, float *data)
{
    Image out = make_image(w, h, c);
    int abs_max = 0;
    int i = 0;
    for (i = 0; i < w*h*c; ++i) {
        if (fabs(data[i]) > abs_max) abs_max = fabs(data[i]);
    }
    for (i = 0; i < w*h*c; ++i) {
        out.data[i] = data[i] / abs_max;
    }
    return out;
}

Image float_to_image(int w, int h, int c, float *data)
{
    Image out = make_empty_image(w,h,c);
    out.data = data;
    return out;
}


Image rotate_crop_image(Image im, float rad, float s, int w, int h, float dx, float dy, float aspect)
{
    int x, y, c;
    float cx = im.w/2.;
    float cy = im.h/2.;
    Image rot = make_image(w, h, im.c);
    for(c = 0; c < im.c; ++c){
        for(y = 0; y < h; ++y){
            for(x = 0; x < w; ++x){
                float rx = cos(rad)*((x - w/2.)/s*aspect + dx/s*aspect) - sin(rad)*((y - h/2.)/s + dy/s) + cx;
                float ry = sin(rad)*((x - w/2.)/s*aspect + dx/s*aspect) + cos(rad)*((y - h/2.)/s + dy/s) + cy;
                float val = bilinear_interpolate(im, rx, ry, c);
                set_pixel(rot, x, y, c, val);
            }
        }
    }
    return rot;
}

Image rotate_image(Image im, float rad)
{
    int x, y, c;
    float cx = im.w/2.;
    float cy = im.h/2.;
    Image rot = make_image(im.w, im.h, im.c);
    for(c = 0; c < im.c; ++c){
        for(y = 0; y < im.h; ++y){
            for(x = 0; x < im.w; ++x){
                float rx = cos(rad)*(x-cx) - sin(rad)*(y-cy) + cx;
                float ry = sin(rad)*(x-cx) + cos(rad)*(y-cy) + cy;
                float val = bilinear_interpolate(im, rx, ry, c);
                set_pixel(rot, x, y, c, val);
            }
        }
    }
    return rot;
}

void translate_image(Image m, float s)
{
    int i;
    for(i = 0; i < m.h*m.w*m.c; ++i) m.data[i] += s;
}

void scale_image(Image m, float s)
{
    int i;
    for(i = 0; i < m.h*m.w*m.c; ++i) m.data[i] *= s;
}

Image crop_image(Image im, int dx, int dy, int w, int h)
{
    Image cropped = make_image(w, h, im.c);
    int i, j, k;
    for(k = 0; k < im.c; ++k){
        for(j = 0; j < h; ++j){
            for(i = 0; i < w; ++i){
                int r = j + dy;
                int c = i + dx;
                float val = 0;
                r = constrain_int(r, 0, im.h-1);
                c = constrain_int(c, 0, im.w-1);
                if (r >= 0 && r < im.h && c >= 0 && c < im.w) {
                    val = get_pixel(im, c, r, k);
                }
                set_pixel(cropped, i, j, k, val);
            }
        }
    }
    return cropped;
}

int best_3d_shift_r(Image a, Image b, int min, int max)
{
    if(min == max) return min;
    int mid = floor((min + max) / 2.);
    Image c1 = crop_image(b, 0, mid, b.w, b.h);
    Image c2 = crop_image(b, 0, mid+1, b.w, b.h);
    float d1 = dist_array(c1.data, a.data, a.w*a.h*a.c, 10);
    float d2 = dist_array(c2.data, a.data, a.w*a.h*a.c, 10);
    free_image(c1);
    free_image(c2);
    if(d1 < d2) return best_3d_shift_r(a, b, min, mid);
    else return best_3d_shift_r(a, b, mid+1, max);
}

int best_3d_shift(Image a, Image b, int min, int max)
{
    int i;
    int best = 0;
    float best_distance = FLT_MAX;
    for(i = min; i <= max; i += 2){
        Image c = crop_image(b, 0, i, b.w, b.h);
        float d = dist_array(c.data, a.data, a.w*a.h*a.c, 100);
        if(d < best_distance){
            best_distance = d;
            best = i;
        }
        printf("%d %f\n", i, d);
        free_image(c);
    }
    return best;
}

void composite_3d(char *f1, char *f2, const char *out, int delta)
{
    if(!out) out = "out";
    Image a = load_image(f1, 0,0,0);
    Image b = load_image(f2, 0,0,0);
    int shift = best_3d_shift_r(a, b, -a.h/100, a.h/100);

    Image c1 = crop_image(b, 10, shift, b.w, b.h);
    float d1 = dist_array(c1.data, a.data, a.w*a.h*a.c, 100);
    Image c2 = crop_image(b, -10, shift, b.w, b.h);
    float d2 = dist_array(c2.data, a.data, a.w*a.h*a.c, 100);

    if(d2 < d1 && 0){
        Image swap = a;
        a = b;
        b = swap;
        shift = -shift;
        printf("swapped, %d\n", shift);
    }
    else{
        printf("%d\n", shift);
    }

    Image c = crop_image(b, delta, shift, a.w, a.h);
    int i;
    for(i = 0; i < c.w*c.h; ++i){
        c.data[i] = a.data[i];
    }
#ifdef OPENCV
    save_image_jpg(c, out);
#else
    save_image(c, out);
#endif
}

void fill_image(Image m, float s)
{
    int i;
    for (i = 0; i < m.h*m.w*m.c; ++i) m.data[i] = s;
}

void letterbox_image_into(Image im, int w, int h, Image boxed)
{
    int new_w = im.w;
    int new_h = im.h;
    if (((float)w / im.w) < ((float)h / im.h)) {
        new_w = w;
        new_h = (im.h * w) / im.w;
    }
    else {
        new_h = h;
        new_w = (im.w * h) / im.h;
    }
    Image resized = resize_image(im, new_w, new_h);
    embed_image(resized, boxed, (w - new_w) / 2, (h - new_h) / 2);
    free_image(resized);
}

Image letterbox_image(Image im, int w, int h)
{
    int new_w = im.w;
    int new_h = im.h;
    if (((float)w / im.w) < ((float)h / im.h)) {
        new_w = w;
        new_h = (im.h * w) / im.w;
    }
    else {
        new_h = h;
        new_w = (im.w * h) / im.h;
    }
    Image resized = resize_image(im, new_w, new_h);
    Image boxed = make_image(w, h, im.c);
    fill_image(boxed, .5);
    //int i;
    //for(i = 0; i < boxed.w*boxed.h*boxed.c; ++i) boxed.data[i] = 0;
    embed_image(resized, boxed, (w - new_w) / 2, (h - new_h) / 2);
    free_image(resized);
    return boxed;
}

Image resize_max(Image im, int max)
{
    int w = im.w;
    int h = im.h;
    if(w > h){
        h = (h * max) / w;
        w = max;
    } else {
        w = (w * max) / h;
        h = max;
    }
    if(w == im.w && h == im.h) return im;
    Image resized = resize_image(im, w, h);
    return resized;
}

Image resize_min(Image im, int min)
{
    int w = im.w;
    int h = im.h;
    if(w < h){
        h = (h * min) / w;
        w = min;
    } else {
        w = (w * min) / h;
        h = min;
    }
    if(w == im.w && h == im.h) return im;
    Image resized = resize_image(im, w, h);
    return resized;
}

Image random_crop_image(Image im, int w, int h)
{
    int dx = rand_int(0, im.w - w);
    int dy = rand_int(0, im.h - h);
    Image crop = crop_image(im, dx, dy, w, h);
    return crop;
}

Image random_augment_image(Image im, float angle, float aspect, int low, int high, int size)
{
    aspect = rand_scale(aspect);
    int r = rand_int(low, high);
    int min = (im.h < im.w*aspect) ? im.h : im.w*aspect;
    float scale = (float)r / min;

    float rad = rand_uniform(-angle, angle) * 2.0 * M_PI / 360.;

    float dx = (im.w*scale/aspect - size) / 2.;
    float dy = (im.h*scale - size) / 2.;
    if(dx < 0) dx = 0;
    if(dy < 0) dy = 0;
    dx = rand_uniform(-dx, dx);
    dy = rand_uniform(-dy, dy);

    Image crop = rotate_crop_image(im, rad, scale, size, size, dx, dy, aspect);

    return crop;
}

float three_way_max(float a, float b, float c)
{
    return (a > b) ? ( (a > c) ? a : c) : ( (b > c) ? b : c) ;
}

float three_way_min(float a, float b, float c)
{
    return (a < b) ? ( (a < c) ? a : c) : ( (b < c) ? b : c) ;
}

// http://www.cs.rit.edu/~ncs/color/t_convert.html
void rgb_to_hsv(Image im)
{
    assert(im.c == 3);
    int i, j;
    float r, g, b;
    float h, s, v;
    for(j = 0; j < im.h; ++j){
        for(i = 0; i < im.w; ++i){
            r = get_pixel(im, i , j, 0);
            g = get_pixel(im, i , j, 1);
            b = get_pixel(im, i , j, 2);
            float max = three_way_max(r,g,b);
            float min = three_way_min(r,g,b);
            float delta = max - min;
            v = max;
            if(max == 0){
                s = 0;
                h = 0;
            }else{
                s = delta/max;
                if(r == max){
                    h = (g - b) / delta;
                } else if (g == max) {
                    h = 2 + (b - r) / delta;
                } else {
                    h = 4 + (r - g) / delta;
                }
                if (h < 0) h += 6;
                h = h/6.;
            }
            set_pixel(im, i, j, 0, h);
            set_pixel(im, i, j, 1, s);
            set_pixel(im, i, j, 2, v);
        }
    }
}

void hsv_to_rgb(Image im)
{
    assert(im.c == 3);
    int i, j;
    float r, g, b;
    float h, s, v;
    float f, p, q, t;
    for(j = 0; j < im.h; ++j){
        for(i = 0; i < im.w; ++i){
            h = 6 * get_pixel(im, i , j, 0);
            s = get_pixel(im, i , j, 1);
            v = get_pixel(im, i , j, 2);
            if (s == 0) {
                r = g = b = v;
            } else {
                int index = floor(h);
                f = h - index;
                p = v*(1-s);
                q = v*(1-s*f);
                t = v*(1-s*(1-f));
                if(index == 0){
                    r = v; g = t; b = p;
                } else if(index == 1){
                    r = q; g = v; b = p;
                } else if(index == 2){
                    r = p; g = v; b = t;
                } else if(index == 3){
                    r = p; g = q; b = v;
                } else if(index == 4){
                    r = t; g = p; b = v;
                } else {
                    r = v; g = p; b = q;
                }
            }
            set_pixel(im, i, j, 0, r);
            set_pixel(im, i, j, 1, g);
            set_pixel(im, i, j, 2, b);
        }
    }
}

Image grayscale_image(Image im)
{
    assert(im.c == 3);
    int i, j, k;
    Image gray = make_image(im.w, im.h, 1);
    float scale[] = {0.587, 0.299, 0.114};
    for(k = 0; k < im.c; ++k){
        for(j = 0; j < im.h; ++j){
            for(i = 0; i < im.w; ++i){
                gray.data[i+im.w*j] += scale[k]*get_pixel(im, i, j, k);
            }
        }
    }
    return gray;
}

Image threshold_image(Image im, float thresh)
{
    int i;
    Image t = make_image(im.w, im.h, im.c);
    for(i = 0; i < im.w*im.h*im.c; ++i){
        t.data[i] = im.data[i]>thresh ? 1 : 0;
    }
    return t;
}

Image blend_image(Image fore, Image back, float alpha)
{
    assert(fore.w == back.w && fore.h == back.h && fore.c == back.c);
    Image blend = make_image(fore.w, fore.h, fore.c);
    int i, j, k;
    for(k = 0; k < fore.c; ++k){
        for(j = 0; j < fore.h; ++j){
            for(i = 0; i < fore.w; ++i){
                float val = alpha * get_pixel(fore, i, j, k) +
                    (1 - alpha)* get_pixel(back, i, j, k);
                set_pixel(blend, i, j, k, val);
            }
        }
    }
    return blend;
}

void scale_image_channel(Image im, int c, float v)
{
    int i, j;
    for(j = 0; j < im.h; ++j){
        for(i = 0; i < im.w; ++i){
            float pix = get_pixel(im, i, j, c);
            pix = pix*v;
            set_pixel(im, i, j, c, pix);
        }
    }
}

void translate_image_channel(Image im, int c, float v)
{
    int i, j;
    for(j = 0; j < im.h; ++j){
        for(i = 0; i < im.w; ++i){
            float pix = get_pixel(im, i, j, c);
            pix = pix+v;
            set_pixel(im, i, j, c, pix);
        }
    }
}

Image binarize_image(Image im)
{
    Image c = copy_image(im);
    int i;
    for(i = 0; i < im.w * im.h * im.c; ++i){
        if(c.data[i] > .5) c.data[i] = 1;
        else c.data[i] = 0;
    }
    return c;
}

void saturate_image(Image im, float sat)
{
    rgb_to_hsv(im);
    scale_image_channel(im, 1, sat);
    hsv_to_rgb(im);
    constrain_image(im);
}

void hue_image(Image im, float hue)
{
    rgb_to_hsv(im);
    int i;
    for(i = 0; i < im.w*im.h; ++i){
        im.data[i] = im.data[i] + hue;
        if (im.data[i] > 1) im.data[i] -= 1;
        if (im.data[i] < 0) im.data[i] += 1;
    }
    hsv_to_rgb(im);
    constrain_image(im);
}

void exposure_image(Image im, float sat)
{
    rgb_to_hsv(im);
    scale_image_channel(im, 2, sat);
    hsv_to_rgb(im);
    constrain_image(im);
}

void distort_image(Image im, float hue, float sat, float val)
{
    if (im.c >= 3)
    {
        rgb_to_hsv(im);
        scale_image_channel(im, 1, sat);
        scale_image_channel(im, 2, val);
        int i;
        for(i = 0; i < im.w*im.h; ++i){
            im.data[i] = im.data[i] + hue;
            if (im.data[i] > 1) im.data[i] -= 1;
            if (im.data[i] < 0) im.data[i] += 1;
        }
        hsv_to_rgb(im);
    }
    else
    {
        scale_image_channel(im, 0, val);
    }
    constrain_image(im);
}

void random_distort_image(Image im, float hue, float saturation, float exposure)
{
    float dhue = rand_uniform_strong(-hue, hue);
    float dsat = rand_scale(saturation);
    float dexp = rand_scale(exposure);
    distort_image(im, dhue, dsat, dexp);
}

void saturate_exposure_image(Image im, float sat, float exposure)
{
    rgb_to_hsv(im);
    scale_image_channel(im, 1, sat);
    scale_image_channel(im, 2, exposure);
    hsv_to_rgb(im);
    constrain_image(im);
}

float bilinear_interpolate(Image im, float x, float y, int c)
{
    int ix = (int) floorf(x);
    int iy = (int) floorf(y);

    float dx = x - ix;
    float dy = y - iy;

    float val = (1-dy) * (1-dx) * get_pixel_extend(im, ix, iy, c) +
        dy     * (1-dx) * get_pixel_extend(im, ix, iy+1, c) +
        (1-dy) *   dx   * get_pixel_extend(im, ix+1, iy, c) +
        dy     *   dx   * get_pixel_extend(im, ix+1, iy+1, c);
    return val;
}

void quantize_image(Image im)
{
    int size = im.c * im.w * im.h;
    int i;
    for (i = 0; i < size; ++i) im.data[i] = (int)(im.data[i] * 255) / 255. + (0.5/255);
}

void make_image_red(Image im)
{
    int r, c, k;
    for (r = 0; r < im.h; ++r) {
        for (c = 0; c < im.w; ++c) {
            float val = 0;
            for (k = 0; k < im.c; ++k) {
                val += get_pixel(im, c, r, k);
                set_pixel(im, c, r, k, 0);
            }
            for (k = 0; k < im.c; ++k) {
                //set_pixel(im, c, r, k, val);
            }
            set_pixel(im, c, r, 0, val);
        }
    }
}

Image make_attention_image(int img_size, float *original_delta_cpu, float *original_input_cpu, int w, int h, int c)
{
    Image attention_img;
    attention_img.w = w;
    attention_img.h = h;
    attention_img.c = c;
    attention_img.data = original_delta_cpu;
    make_image_red(attention_img);

    int k;
    float min_val = 999999, mean_val = 0, max_val = -999999;
    for (k = 0; k < img_size; ++k) {
        if (original_delta_cpu[k] < min_val) min_val = original_delta_cpu[k];
        if (original_delta_cpu[k] > max_val) max_val = original_delta_cpu[k];
        mean_val += original_delta_cpu[k];
    }
    mean_val = mean_val / img_size;
    float range = max_val - min_val;

    for (k = 0; k < img_size; ++k) {
        float val = original_delta_cpu[k];
        val = fabs(mean_val - val) / range;
        original_delta_cpu[k] = val * 4;
    }

    Image resized = resize_image(attention_img, w / 4, h / 4);
    attention_img = resize_image(resized, w, h);
    free_image(resized);
    for (k = 0; k < img_size; ++k) attention_img.data[k] += original_input_cpu[k];

    //normalize_image(attention_img);
    //show_image(attention_img, "delta");
    return attention_img;
}

Image resize_image(Image im, int w, int h)
{
    if (im.w == w && im.h == h) return copy_image(im);

    Image resized = make_image(w, h, im.c);
    Image part = make_image(w, im.h, im.c);
    int r, c, k;
    float w_scale = (float)(im.w - 1) / (w - 1);
    float h_scale = (float)(im.h - 1) / (h - 1);
    for(k = 0; k < im.c; ++k){
        for(r = 0; r < im.h; ++r){
            for(c = 0; c < w; ++c){
                float val = 0;
                if(c == w-1 || im.w == 1){
                    val = get_pixel(im, im.w-1, r, k);
                } else {
                    float sx = c*w_scale;
                    int ix = (int) sx;
                    float dx = sx - ix;
                    val = (1 - dx) * get_pixel(im, ix, r, k) + dx * get_pixel(im, ix+1, r, k);
                }
                set_pixel(part, c, r, k, val);
            }
        }
    }
    for(k = 0; k < im.c; ++k){
        for(r = 0; r < h; ++r){
            float sy = r*h_scale;
            int iy = (int) sy;
            float dy = sy - iy;
            for(c = 0; c < w; ++c){
                float val = (1-dy) * get_pixel(part, c, iy, k);
                set_pixel(resized, c, r, k, val);
            }
            if(r == h-1 || im.h == 1) continue;
            for(c = 0; c < w; ++c){
                float val = dy * get_pixel(part, c, iy+1, k);
                add_pixel(resized, c, r, k, val);
            }
        }
    }

    free_image(part);
    return resized;
}


void test_resize(char *filename)
{
    Image im = load_image(filename, 0,0, 3);
    float mag = mag_array(im.data, im.w*im.h*im.c);
    printf("L2 Norm: %f\n", mag);
    Image gray = grayscale_image(im);

    Image c1 = copy_image(im);
    Image c2 = copy_image(im);
    Image c3 = copy_image(im);
    Image c4 = copy_image(im);
    distort_image(c1, .1, 1.5, 1.5);
    distort_image(c2, -.1, .66666, .66666);
    distort_image(c3, .1, 1.5, .66666);
    distort_image(c4, .1, .66666, 1.5);


    show_image(im,   "Original");
    show_image(gray, "Gray");
    show_image(c1, "C1");
    show_image(c2, "C2");
    show_image(c3, "C3");
    show_image(c4, "C4");

#ifdef OPENCV
    while(1){
        Image aug = random_augment_image(im, 0, .75, 320, 448, 320);
        show_image(aug, "aug");
        free_image(aug);


        float exposure = 1.15;
        float saturation = 1.15;
        float hue = .05;

        Image c = copy_image(im);

        float dexp = rand_scale(exposure);
        float dsat = rand_scale(saturation);
        float dhue = rand_uniform(-hue, hue);

        distort_image(c, dhue, dsat, dexp);
        show_image(c, "rand");
        printf("%f %f %f\n", dhue, dsat, dexp);
        free_image(c);
        wait_until_press_key_cv();
    }
#endif
}


Image load_image_stb(const char *filename, int channels)
{
    int w, h, c;
    unsigned char *data = stbi_load(filename, &w, &h, &c, channels);
    if (!data) {
        char shrinked_filename[1024];
        if (strlen(filename) >= 1024) sprintf_s(shrinked_filename,1024, "name is too long");
        else sprintf_s(shrinked_filename, 1024, "%s", filename);
        fprintf(stderr, "Cannot load Image \"%s\"\nSTB Reason: %s\n", shrinked_filename, stbi_failure_reason());
        FILE* fw; fopen_s(&fw, "bad.list", "a");
        fwrite(shrinked_filename, sizeof(char), strlen(shrinked_filename), fw);
        const char *new_line = "\n";
        fwrite(new_line, sizeof(char), strlen(new_line), fw);
        fclose(fw);
        printf("\n Error in load_image_stb() \n");

        return make_image(0, 0, 0);
        //exit(EXIT_FAILURE);
    }
    if(channels) c = channels;
    int i,j,k;
    Image im = make_image(w, h, c);
    for(k = 0; k < c; ++k){
        for(j = 0; j < h; ++j){
            for(i = 0; i < w; ++i){
                int dst_index = i + w*j + w*h*k;
                int src_index = k + c*i + c*w*j;
                im.data[dst_index] = (float)data[src_index]/255.;
            }
        }
    }
    free(data);
    return im;
}

Image load_image_stb_resize(char *filename, int w, int h, int c)
{
    Image out = load_image_stb(filename, c);    // without OpenCV

    if ((h && w) && (h != out.h || w != out.w)) {
        Image resized = resize_image(out, w, h);
        free_image(out);
        out = resized;
    }
    return out;
}

Image load_image(const char *filename, int w, int h, int c)
{
#ifdef OPENCV
    //Image out = load_image_stb(filename, c);
    Image out = load_image_cv(filename, c);
#else
    Image out = load_image_stb(filename, c);    // without OpenCV
#endif  // OPENCV

    if((h && w) && (h != out.h || w != out.w)){
        Image resized = resize_image(out, w, h);
        free_image(out);
        out = resized;
    }
    return out;
}

Image load_image_color(char *filename, int w, int h)
{
    return load_image(filename, w, h, 3);
}

Image get_image_layer(Image m, int l)
{
    Image out = make_image(m.w, m.h, 1);
    int i;
    for(i = 0; i < m.h*m.w; ++i){
        out.data[i] = m.data[i+l*m.h*m.w];
    }
    return out;
}

void print_image(Image m)
{
    int i, j, k;
    for(i =0 ; i < m.c; ++i){
        for(j =0 ; j < m.h; ++j){
            for(k = 0; k < m.w; ++k){
                printf("%.2lf, ", m.data[i*m.h*m.w + j*m.w + k]);
                if(k > 30) break;
            }
            printf("\n");
            if(j > 30) break;
        }
        printf("\n");
    }
    printf("\n");
}

Image collapse_images_vert(Image *ims, int n)
{
    int color = 1;
    int border = 1;
    int h,w,c;
    w = ims[0].w;
    h = (ims[0].h + border) * n - border;
    c = ims[0].c;
    if(c != 3 || !color){
        w = (w+border)*c - border;
        c = 1;
    }

    Image filters = make_image(w, h, c);
    int i,j;
    for(i = 0; i < n; ++i){
        int h_offset = i*(ims[0].h+border);
        Image copy = copy_image(ims[i]);
        //normalize_image(copy);
        if(c == 3 && color){
            embed_image(copy, filters, 0, h_offset);
        }
        else{
            for(j = 0; j < copy.c; ++j){
                int w_offset = j*(ims[0].w+border);
                Image layer = get_image_layer(copy, j);
                embed_image(layer, filters, w_offset, h_offset);
                free_image(layer);
            }
        }
        free_image(copy);
    }
    return filters;
}

Image collapse_images_horz(Image *ims, int n)
{
    int color = 1;
    int border = 1;
    int h,w,c;
    int size = ims[0].h;
    h = size;
    w = (ims[0].w + border) * n - border;
    c = ims[0].c;
    if(c != 3 || !color){
        h = (h+border)*c - border;
        c = 1;
    }

    Image filters = make_image(w, h, c);
    int i,j;
    for(i = 0; i < n; ++i){
        int w_offset = i*(size+border);
        Image copy = copy_image(ims[i]);
        //normalize_image(copy);
        if(c == 3 && color){
            embed_image(copy, filters, w_offset, 0);
        }
        else{
            for(j = 0; j < copy.c; ++j){
                int h_offset = j*(size+border);
                Image layer = get_image_layer(copy, j);
                embed_image(layer, filters, w_offset, h_offset);
                free_image(layer);
            }
        }
        free_image(copy);
    }
    return filters;
}

void show_image_normalized(Image im, const char *name)
{
    Image c = copy_image(im);
    normalize_image(c);
    show_image(c, name);
    free_image(c);
}

void show_images(Image *ims, int n, char *window)
{
    Image m = collapse_images_vert(ims, n);
    /*
       int w = 448;
       int h = ((float)m.h/m.w) * 448;
       if(h > 896){
       h = 896;
       w = ((float)m.w/m.h) * 896;
       }
       Image sized = resize_image(m, w, h);
     */
    normalize_image(m);
    save_image(m, window);
    show_image(m, window);
    free_image(m);
}

void free_image(Image m)
{
    if(m.data){
        free(m.data);
    }
}

// Fast copy data from a contiguous byte array into the Image.
void copy_image_from_bytes(Image im, char *pdata)
{
    unsigned char *data = (unsigned char*)pdata;
    int i, k, j;
    int w = im.w;
    int h = im.h;
    int c = im.c;
    for (k = 0; k < c; ++k) {
        for (j = 0; j < h; ++j) {
            for (i = 0; i < w; ++i) {
                int dst_index = i + w * j + w * h*k;
                int src_index = k + c * i + c * w*j;
                im.data[dst_index] = (float)data[src_index] / 255.;
            }
        }
    }
}

// Fast copy data from a contiguous byte array into the Image.
void copy_image_from_float(Image im, char *pdata)
{
    float *data = (float *)pdata;
    int i, k, j;
    int w = im.w;
    int h = im.h;
    int c = im.c;
    for (k = 0; k < c; ++k) {
        for (j = 0; j < h; ++j) {
            for (i = 0; i < w; ++i) {
                int dst_index = i + w * j + w * h*k;
                int src_index = k + c * i + c * w*j;
                im.data[dst_index] = (float)data[src_index];
            }
        }
    }
}


bool is_empty_image(Image img) 
{ 
    return img.c == 0 || img.w == 0 || img.h == 0 || img.data == NULL; 
}
