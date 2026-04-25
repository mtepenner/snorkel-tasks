FROM python:3.10-slim
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*
RUN pip install numpy==1.26.4 pandas==2.0.3 graphviz==0.20.1

WORKDIR /app/workspace
RUN mkdir -p data src output

RUN printf 'region_id,year,temperature\n1,2020,14.5\n1,2021,15.0\n2,2020,22.1\n2,2021,22.5\n' > data/climate.csv
RUN echo '{"1": "North America", "2": "Europe"}' > data/metadata.json

CMD ["/bin/bash"]
