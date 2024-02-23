import subprocess
import time
from datetime import datetime

command = "curl -H 'Cache-Control: no-cache' -s https://clinical.optum.com/microproduct/user-management-cds-ui-service.core.svc.cluster.local/main.0273d9eb80849df2.js -O 2>&1"

while True:
    start_time = time.time()

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, _ = process.communicate()

    end_time = time.time()

    elapsed_time = end_time - start_time

    current_time = datetime.now().strftime("%H:%M:%S")

    print(f"{current_time},{elapsed_time}")

    time.sleep(1)
