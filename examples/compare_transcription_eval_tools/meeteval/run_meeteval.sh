#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_meeteval.Dockerfile -t stringalign_run_meeteval .
rm -rf ./ocr_results/
mkdir -p meeteval_results


docker run --rm --volume $(pwd)/meeteval_results:/analysis/output stringalign_run_meeteval
docker image rm stringalign_run_meeteval
