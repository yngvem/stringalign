#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_isri.Dockerfile -t stringalign_run_isri .
rm -rf ./ocr_results/
mkdir -p isri_results


docker run --rm  --volume $(pwd)/isri_results:/analysis/output stringalign_run_isri
docker image rm stringalign_run_isri
