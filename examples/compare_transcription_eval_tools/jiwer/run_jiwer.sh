#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_jiwer.Dockerfile -t stringalign_run_jiwer .
rm -rf ./ocr_results/
mkdir -p jiwer_results


docker run --rm --volume $(pwd)/jiwer_results:/analysis/output stringalign_run_jiwer
docker image rm stringalign_run_jiwer
