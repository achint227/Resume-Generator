FROM python:3.7

RUN git clone https://github.com/achint227/Resume-Generator.git \
    && cd Resume-Generator \
    && pip install --no-cache-dir -r requirements.txt

WORKDIR /Resume-Generator

EXPOSE 5001

ENTRYPOINT [ "waitress-serve" ]

CMD ["--listen=*:5001","server:app"]
