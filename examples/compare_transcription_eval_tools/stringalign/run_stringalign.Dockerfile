FROM python:3.13-trixie

RUN pip install stringalign==0.1.4

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY run_stringalign.py .

CMD ["python", "run_stringalign.py"]
