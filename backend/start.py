import subprocess
import sys
import time

def main():
    print("Starting migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migrations complete!")

    print("Starting background ingestion worker...")
    worker_process = subprocess.Popen(
        ["python", "-u", "-m", "app.workers.ingestion_worker"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    try:
        worker_process.wait()
        server_process.wait()
    except KeyboardInterrupt:
        print("Shutting down processes...")
        worker_process.terminate()
        server_process.terminate()

if __name__ == "__main__":
    main()
