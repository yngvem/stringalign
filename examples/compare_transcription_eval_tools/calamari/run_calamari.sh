#!/bin/bash

cp -r ../ocr_results ./ocr_results/
docker build -f run_calamari.Dockerfile -t stringalign_run_calamari .
rm -rf ./ocr_results/
mkdir -p calamari_results


docker run --rm --volume $(pwd)/calamari_results:/analysis/output stringalign_run_calamari
docker image rm stringalign_run_calamari
