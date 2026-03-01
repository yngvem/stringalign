FROM python:3.14-trixie

RUN pip install edit_distance==1.0.7 numpy==2.4.2

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY evaluate.py textprocessors.py run_calamari.py .

CMD ["python", "run_calamari.py"]
