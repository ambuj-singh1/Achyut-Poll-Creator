import subprocess
import time

while True:
    print("बोट चालू हो रही है...")
    process = subprocess.Popen(["python", "bot.py"])
    process.wait()
    print("बोट बंद हो गई। 5 सेकंड में रीस्टार्ट हो रही है...")
    time.sleep(5)