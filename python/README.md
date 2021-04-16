
## Python Bindings

To compile the Python bindings make `python` your current working directory and run
```
python setup_Win.py build_ext --inplace
```

## ToDos

- [ ] support for masking / alpha channels (e.g., to remove FLIR watermark)
- [ ] render with RGB
- [ ] display the satelite image on the ground
- [ ] check if float32 ifdef is working
