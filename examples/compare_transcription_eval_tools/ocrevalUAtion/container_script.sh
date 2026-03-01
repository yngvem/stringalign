for reference_file in ocr_results/*.ref.txt
do
    name=$(basename "$reference_file" .ref.txt)
    predicted_file="ocr_results/$name.pred.txt"
    output_file="output/$name.report.html"

    java -cp ocrevalUAtion-1.3.4-jar-with-dependencies.jar \
        eu.digitisation.Main \
        -gt "$reference_file" \
        -ocr "$predicted_file" \
        -e utf-8 \
        -o "$output_file"
done
