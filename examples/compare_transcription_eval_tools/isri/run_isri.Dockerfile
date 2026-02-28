FROM python:3.14-trixie

RUN apt-get update && \
    apt-get install -y build-essential libutf8proc-dev git && \
    git clone https://github.com/eddieantonio/ocreval && \
    cd ocreval && \
    git checkout 873a0de5796c0b9ccf07a549afdd30159a9e0b3e && \
    make && make install

WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY run_isri_analysis.py .

CMD ["python3", "run_isri_analysis.py"]
