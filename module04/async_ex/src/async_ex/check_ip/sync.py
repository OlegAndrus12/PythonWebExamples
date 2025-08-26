import requests
import time

url = "https://api.ipify.org/?format=json"

def fetch_ip(n=100):
    start = time.perf_counter()
    for i in range(n):
        response = requests.get(url, timeout=2)
        ip = response.json().get("ip")
        print(f"Request #{i}: ip: {ip}")
    end = time.perf_counter()
    print(f"Sync total time: {end - start:.2f} seconds")

fetch_ip(n=100)
