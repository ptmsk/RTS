# Connected Component Labeling

This repo is based on the pseudo code of [A Run-Based Two-Scan Labeling Algorithm (RTS)](https://ieeexplore.ieee.org/document/4472694) proposed by He et al.

---

## Keywords

- As in most labeling algorithms, the authors assume that all pixels on the edges of an image are background pixels, and only consider **eight-connectivity**.
- **Run**: A run is a block of contiguous object pixels in a row.
- **Label equivalence**
- **Run-length encoding**
- **Raster scan**

## Algorithm phases

- **First pass**:
  - Traverse the pixel one by one in the order of raster scanning direction. If the pixel is the object pixel, do the labeling task and resolve equivalence. After this step, this pixel holds the provisional label, the equivalent label sets are updated.
  - Discard all of the unusable run data $\hat r$, which satisfy $i_{end}(\hat r) \leq i_{start}(r) - N$, provided that $i$ is the index of the pixel and $r$ is the current run. After processing the current run $r$, $\hat r$ become useless because the incoming run can't connect with them anymore.
- Second pass: Scan the image pixel by pixel in the raster scanning direction and map the provisional label of the current pixel with the corresponding representative label (Background pixel is scanned again).

## Run

### Requirements

```text
opencv-python
numpy
imutils
```

```bash
pip install -r requirements.txt
```

### Run IRCL algorithm and save the result

```bash
#!/bin/bash
python run.py --image_path images/ \
              --save_dir results/
```

### Export the visualization step by step of the algorithm

```bash
#!/bin/bash
python run.py --image_path images/granularity.jpg \
              --save_dir results/ \
              --save_vis
```
