# Synthetic boundary-point classification example

This is an invented calibration scenario, not data from the author's original
application or a specification for a real device. A light-triggered relay is ON
when `0.65*x1 + 0.90*x2 - 0.75 > 0`, and OFF otherwise. Each lamp setting is
normalized to [0, 1]. Eighteen switching-point measurements have independent
Gaussian noise with standard deviation 0.018 in each recorded coordinate.
Four known ON/OFF controls determine the orientation of the fitted plane.

## Run

Use Python 3.12 or later. In this directory:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python boundary_classifier.py
python generate_example.py
```

`boundary_classifier.py` reads the supplied input CSVs and prints the fitted
model and the first three predictions. It does not read evaluation labels or
simulator coefficients. Positive signed distance predicts ON (+1); an exactly
zero or negative distance predicts OFF (-1). Distances use the normalized
feature coordinates, not physical light-intensity units or probabilities.

`generate_example.py` regenerates all data, predictions, diagnostics, PNG/SVG
plots, and the ZIP bundle. Its default seed is 20171006. Paths are resolved
relative to the script, so both commands also work from another directory.
Use `--output-dir /path/to/new-folder` to generate an independent complete copy,
or `--seed 123` to try another sample. It overwrites its named output files.
The numbers in the article refer to the default seed and supplied requirements.
Plot bytes can differ with another font/rendering environment or dependency set.

## Files and schemas

- `boundary_classifier.py`: reusable `fit_hyperplane` and `orient_hyperplane`
  functions, plus the CSV example. The fit supports n-dimensional points.
- `generate_example.py`: synthetic data generation, evaluation, plotting, and ZIP
  creation. The two-dimensional scenario is separate from the general fitter.
- `requirements.txt`: direct dependency versions used to create the example.
- `boundary_points.csv`: `x1,x2`; noisy boundary estimates used for fitting.
- `orientation_points.csv`: `x1,x2,label`; four controls used only to choose the
  normal's sign, with `label` equal to -1 (OFF) or +1 (ON).
- `unlabeled_points.csv`: `log_id,x1,x2`; three illustrative queries followed by
  237 uniformly sampled settings. Their labels are not inputs to the fitter.
- `evaluation_truth.csv`: `log_id,true_label,true_signed_distance`; simulation
  truth for evaluating the logged settings, produced after predictions.
- `predictions.csv`: `log_id,signed_distance,predicted_label`; join to the logs or
  evaluation truth by `log_id`.
- `results.json`: seed, noise, generator parameters, fitted coefficients,
  diagnostics, software versions, and the first three predictions.
- `calibration-and-predictions.png`: figure used in the article.
- `calibration-and-predictions.svg`: vector version of that figure.
- `boundary-example.zip`: all of the files above plus this README, under a
  `boundary-points/` directory. The ZIP does not contain itself or the blog post.

The hidden true line is drawn only as an evaluation reference. It is not used
to choose the fitted normal or its sign. Four labeled controls resolve the sign;
evaluation labels are separate. This one synthetic run demonstrates the workflow
and is not evidence of performance on real data or superiority to other methods.

The fitter rejects insufficient affine rank and numerically tied smallest
singular values. These checks do not guarantee stability under arbitrary noise;
feature scaling, calibration coverage, outliers, and the singular-value gap still
matter. Its reduced SVD is valid because the centered input has m >= n rows.

## Moving the example to another repository

Copy this entire directory to `assets/code/2026-09-23-linear-classifier-boundary-points/`
in the new repository. The article links every file, including the ZIP, using
this path and `site.baseurl`. If you choose another path, update those links.
The pre-existing figures elsewhere in the article must also be copied; they are
not included in this supplementary example bundle. The environment directory
and Python cache files are not needed.
