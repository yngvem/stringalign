#!/bin/bash
# shellcheck disable=all
run_analysis() {


    cd isri
    rm -rf isri_results
    time bash run_isri.sh
    cd ..

    cd jiwer
    rm -rf jiwer_results
    time bash run_jiwer.sh
    cd ..

    cd meeteval
    rm -rf meeteval_results
    time bash run_meeteval.sh
    cd ..

    cd ocrevalUAtion
    rm -rf ocrevalUAtion_results
    time bash run_ocrevalUAtion.sh
    cd ..

    cd stringalign
    rm -rf stringalign_results
    time bash run_stringalign.sh
    cd ..

    cd dinglehopper
    rm -rf dinglehopper_results
    time bash run_dinglehopper.sh
    cd ..

    cd calamari
    rm -rf calamari_results
    time bash run_calamari.sh
    cd ..
}

rm -rf ocr_results

git clone https://github.com/cneud/hip21_ocrevaluation.git
cd hip21_ocrevaluation
git checkout 9979dacfeebef65b419a44ea3f12a0bcba153c6f
cd ..

pipx run hip21_get_data.py
run_analysis
pipx run hip21_get_results.py
