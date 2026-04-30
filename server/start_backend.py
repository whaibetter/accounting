import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=r"c:\Users\whaif\Downloads\android\accounting\server",
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)
