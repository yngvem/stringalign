#!/bin/bash

run_analysis() {
    cd calamari
    rm -rf calamari_results
    bash run_calamari.sh
    cd ..


    cd dinglehopper
    rm -rf dinglehopper_results
    bash run_dinglehopper.sh
    cd ..


    cd isri
    rm -rf isri_results
    bash run_isri.sh
    cd ..

    cd jiwer
    rm -rf jiwer_results
    bash run_jiwer.sh
    cd ..

    cd meeteval
    rm -rf meeteval_results
    bash run_meeteval.sh
    cd ..

    cd ocrevalUAtion
    rm -rf ocrevalUAtion_results
    bash run_ocrevalUAtion.sh
    cd ..

    cd stringalign
    rm -rf stringalign_results
    bash run_stringalign.sh
    cd ..
}

bash synthetic_emoji_make_data.sh
run_analysis
pipx synthetic_emoji_get_results.py
