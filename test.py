import subprocess

process = subprocess.Popen(
    ["dirh.exe"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=1,
    text=True
)

print("Waiting for output...")

for line in process.stdout:
    print("Output from C program:", line.strip())  # Debugging output
