FROM python:3.14-trixie

WORKDIR /analysis
RUN apt-get update && \
    apt-get install -y openjdk-25-jre-headless wget && \
    wget https://github.com/impactcentre/ocrevalUAtion/releases/download/v1.3.4/ocrevalUAtion-1.3.4-jar-with-dependencies.jar


WORKDIR /analysis
COPY ocr_results/ ./ocr_results/
COPY container_script.sh run_eval.sh

CMD ["bash", "run_eval.sh"]
