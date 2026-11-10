# Legacy prototype (2018/19)

This is the original VIDEO-ANALYZER code, kept unchanged for reference. It does not run on current systems: it depends on `pafy`, which is dead, and on the pre-0.6 PySceneDetect API.

| File | Purpose |
|---|---|
| `omimages/analyzeVideo.py` | Main script: scene detection, slit-scan stripes (`ist_*.jpg`), OM images (`a_*.jpg`) |
| `omimages/makeOMimage.py` | Earlier standalone OM image generator (syntax error on line 1) |
| `omimages/analyzeScenes.py` | Earlier standalone scene detection |
| `omimages/test-edgededection.py` | Experiment: detecting cuts in stripe images with Canny/Hough |
| `omimages/readFromYoutube.py`, `ty.py` | YouTube streaming tests (pafy) |
| `omimages/scenes.csv` | Example scene list (start frame, end frame) |
| `omimages/omimagetest.jpg` | Example OM image |
