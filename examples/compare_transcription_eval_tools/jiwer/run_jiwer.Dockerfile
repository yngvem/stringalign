FROM python:3.14-trixie

RUN pip install jiwer==4.0.0

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY run_jiwer.py .

CMD ["python", "run_jiwer.py"]
