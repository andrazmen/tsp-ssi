import time
import asyncio
import aiohttp
import matplotlib.pyplot as plt

# JSON body for the POST request
payload = {
    "id": "828b559d-7710-4816-ac9a-e22668c567d9",
    "topic": "/cem/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/rm/96439751-b2ad-496b-b80e-a3cb4e79b0db/devices"
}

# Function to send one POST request and measure time
async def post(session, url, timings, i):
    start = time.perf_counter()
    async with session.post(url, json=payload) as response:
        await response.text()
    end = time.perf_counter()
    timings.append((i, (end - start) * 1000)) # Convert to milliseconds

# Main test function
async def test_post_requests_serial(url, total_requests=100):
    timings = []
    async with aiohttp.ClientSession() as session:
        for i in range(total_requests):
            try:
                await post(session, url, timings, i)
            except Exception as e:
                print(f"Request {i + 1} failed: {e}")
            await asyncio.sleep(0.1)  # Optional delay to avoid overwhelming the server
    return timings

# Replace this with your actual server endpoint
url_to_test = "http://localhost:5200/api/acs"
total_requests = 100

# Run the test
timings = asyncio.run(test_post_requests_serial(url_to_test, total_requests))

# Plot results
x_vals = [(x + 1) for x, _ in timings]
y_vals = [y for _, y in timings]
y_vals_avg = sum(y_vals) / len(y_vals)

plt.figure(figsize=(12, 6))
plt.plot(x_vals, y_vals, marker='o', linestyle='-', color='blue', label='Odzivni čas')

plt.axhline(y=y_vals_avg, color='red', linestyle='--', label=f'Povprečni odzivni čas')

plt.title(f"Odzivni čas {total_requests} zaporednih zahtev HTTP POST")
plt.xlabel("Zaporedno število POST zahtevka [n]")
plt.ylabel("Odzivni čas [ms]")
plt.grid(True)

plt.legend()

plt.tight_layout()

# Save instead of show
plt.savefig("response_times_cached-v2.png")
print("Plot saved as response_times_cached-v2.png")
print(f"Average response time: {y_vals_avg:.3f} ms")

