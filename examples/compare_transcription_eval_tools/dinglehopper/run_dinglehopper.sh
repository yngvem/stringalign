#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_dinglehopper.Dockerfile -t stringalign_run_dinglehopper .
rm -rf ./ocr_results/
mkdir -p dinglehopper_results


docker run --rm --volume $(pwd)/dinglehopper_results:/analysis/output stringalign_run_dinglehopper
docker image rm stringalign_run_dinglehopper
