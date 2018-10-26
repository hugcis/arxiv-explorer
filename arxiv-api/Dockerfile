FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN \ 
    pip3 install --no-cache-dir Cython
RUN \ 
    pip3 install --no-cache-dir numpy
RUN python3 -c "import Cython; print(Cython.__version__)"

RUN pip3 install -r requirements.txt
RUN python -m nltk.downloader stopwords
ADD . /app/