# nice light version of Python 3.10.12
FROM python:3.10.12-slim-buster

WORKDIR /hamiltoniansports

# Copy the dependencies file to the working directory, then install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# create a volume so that data created is persisted beyond container life cycle
VOLUME /hamiltoniansports

# copy across the code directory
COPY hamiltoniansports/ .
