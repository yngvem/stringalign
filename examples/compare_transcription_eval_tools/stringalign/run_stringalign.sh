#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_stringalign.Dockerfile -t stringalign_run_stringalign .
rm -rf ./ocr_results/
mkdir -p stringalign_results


docker run --rm --volume $(pwd)/stringalign_results:/analysis/output stringalign_run_stringalign
docker image rm stringalign_run_stringalign
