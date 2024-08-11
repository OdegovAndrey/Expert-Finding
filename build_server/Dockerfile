#FROM mashasha/pylucene:latest
FROM python:3.12-bookworm

RUN mkdir -p /app || true
WORKDIR /app

COPY requirements-torch.txt /app/requirements-torch.txt
RUN pip install -r /app/requirements-torch.txt

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY ./index/ /app/index/
COPY ./semantic_vs_unigrams_search/ /app/semantic_vs_unigrams_search/

EXPOSE 7860

ENV ISDOCKER=1
ENV PATH_TO_DATA=/data_with_embeddings.pqt

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python3", "semantic_vs_unigrams_search/gradio_interface.py"]
