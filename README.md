# HTTP load-testing

### How to run

```
$ python3 loadtest.py -h
usage: loadtest.py [-h] [-qps QPS] [-d D] url

positional arguments:
  url         HTTP address

options:
  -h, --help  show this help message and exit
  -qps QPS    Queries per second
  -d D        Duration to run test
```

Example:
```
$ python3 loadtest.py https://www.google.com -qps 10 -d 10
Querying www.google.com 10 time(s) a second for 10 seconds
Done Querying
100/100 successes
0/100 errors
0.011187484100810252s Avg. Latency of Successful requests
```

### Using Docker
Build the docker container
```
docker compose up -d
```
Run the command 
```
docker exec loadtest-src-1 python3 loadtest.py https://www.google.com -qps 10 -d 10
```
