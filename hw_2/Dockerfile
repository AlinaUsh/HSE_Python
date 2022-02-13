FROM python:3
WORKDIR /workspace

COPY . .
RUN apt-get update
RUN python3 -m pip install --upgrade pip
RUN apt-get install -y graphviz
RUN apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
RUN python3 -m pip install hse-python-hw-1-avushakova==0.0.5

CMD ["python3", "make_tex.py"]