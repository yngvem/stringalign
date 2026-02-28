FROM python:3.14-trixie

RUN pip install meeteval==0.4.3

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY run_meeteval.py .

CMD ["python", "run_meeteval.py"]
