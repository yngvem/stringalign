FROM python:3.14-trixie

RUN pip install dinglehopper==0.11.0

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
RUN mkdir pred ref && \
    bash -c 'for f in ocr_results/*ref.txt; do cp "$f" "ref/$(basename "$f" .ref.txt).txt"; done' && \
    bash -c 'for f in ocr_results/*pred.txt; do cp "$f" "pred/$(basename "$f" .pred.txt).txt"; done'

CMD ["bash", "-c", "dinglehopper ref/ pred/ report output/  --plain-encoding utf-8 && dinglehopper-summarize output/"]
