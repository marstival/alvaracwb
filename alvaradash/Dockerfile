FROM continuumio/miniconda3 AS builder

COPY requirements.txt /tmp/

#RUN conda create -n base --yes

RUN /bin/bash -c "echo Hello from bash"

SHELL ["/bin/bash", "-c"]

RUN echo "$PATH"

RUN conda init bash 

RUN conda install python==3.12.7
RUN conda upgrade --all --yes

#RUN conda install -n base conda libarchive -c main --force-reinstall --solver classic --yes

RUN python --version
#-c conda-forge --yes
RUN conda install --file /tmp/requirements.txt  --yes


RUN pip install redlock-py "dash-bootstrap-components<1" "dash_html_components" turfpy

ENV LANGUAGE="pt_BR.ISO-8859-1"
ENV LC_ALL="pt_BR.ISO-8859-1"

COPY ./src /app
WORKDIR "/app"
EXPOSE 8051

#ENV CACHE_TYPE='redis'
#ENV CACHE_DIR='redis://redis:6379'
#ENV HOME_BUCKET='s3://cwbalvaras/'

ENV PATH=/root/.local:$PATH
#ENTRYPOINT [ "python3" ]
#CMD [ "python", "./application.py" ]

#RUN pip install gunicorn
CMD ["gunicorn", "--preload", "-t" ,"330",  "--bind", ":8051", "--workers", "2", "application:server"]
