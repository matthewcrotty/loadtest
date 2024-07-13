import argparse
import threading
import time
import socket
from urllib.parse import urlparse

# Wrapper around thread class to allow for return values to be collected after execution
class retThread(threading.Thread):
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.target = target
        self.result = None

    def run(self):
        self.result = self.target()

# simple request funciton to measure latency or errors of a request to a http address
def request(host, timeout):
    start = time.monotonic()
    try: 
        s = socket.create_connection((host,443), timeout=timeout)
        s.shutdown(socket.SHUT_RD)
    except socket.timeout:
        return 0, 1, 0.0
    except OSError:
        return 0, 1, 0.0
    return 1, 0, float((time.monotonic() - start))

# Function to be passed into a thread, which allows us to start a thread at specified split-second intervals
def req_timed(timer_flag, rate, host, duration):
        
        # Create a child thread every 1s / qps until timer flag is set to false
        allthreads = []
        while timer_flag.is_set():
            start = time.perf_counter_ns()
            child = retThread(target=lambda: request(host, 1))
            child.start()
            allthreads.append(child)
            time.sleep(rate - (time.perf_counter_ns() - start) / 1000000000)

        print("Done Querying")
        
        # Obtain results from all threads post execution
        successes, errors, latency = 0, 0, 0.0
        for t2 in allthreads:
            while t2.result is None:
                time.sleep(0.1)
            s, e, l = t2.result
            successes += s
            errors += e
            latency += l

        print("{}/{} successes".format(successes, successes+errors))
        print("{}/{} errors".format(errors, successes+errors))
        if successes != 0:
            print("{}s Avg. Latency of Successful requests".format(latency/successes))
        else:
            print("No Latency to measure")

        # One limitation of python is inaccuracy of clock cycles due to being an interpreted language
        if successes+errors < 1.0/rate * duration:
            print("{} requests missed from clock latency".format(1.0/rate * duration) - (successes + errors))

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="HTTP address")
    parser.add_argument("-qps", type=int, help="Queries per second", default=10)
    parser.add_argument('-d', type=int, help="Duration to run test", default=30)
    # Parse Arguments
    args = parser.parse_args()
    parsed_uri = urlparse(args.url)
    host = parsed_uri.netloc
    
    # Create flag that stops the thread execution
    timer_flag = threading.Event()
    timer_flag.set()

    print("Querying {} {} time(s) a second for {} seconds".format(args.uri, args.qps, args.d))

    # Create timing thread that will loop requests according to the qps flag
    timer_thread = threading.Thread(target=req_timed, args=(timer_flag, 1.0/args.qps, host, args.d))
    timer_thread.start()

    # The thread will loop for a set duration before stopping
    time.sleep(args.d)
    timer_flag.clear()

