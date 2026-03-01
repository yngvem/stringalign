#!/bin/bash

cp -r ../ocr_results ./ocr_results
docker build -f run_ocrevalUAtion.Dockerfile -t stringalign_run_ocrevaluation .
rm -rf ocr_results
mkdir -p ocrevalUAtion_results

docker run --rm --volume $(pwd)/../ocr_results:/analysis/ocr_results --volume $(pwd)/ocrevalUAtion_results:/analysis/output stringalign_run_ocrevaluation
docker image rm stringalign_run_ocrevaluation
