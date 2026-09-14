import judge0api as api

client = api.Client("http://localhost:2358")
client.wait = True

submission = api.submission.submit(
    client,
    source_code=b"print('Hello from local Judge0!')",
    language=71,  # 71 = Python 3
)

print("Status ID:", submission.status.get("id"))
print("Status Description:", submission.status.get("description"))

if submission.message:
    print("Execution Message:", submission.message)

stdout = submission.stdout.decode("utf-8") if submission.stdout else ""
stderr = submission.stderr.decode("utf-8") if submission.stderr else ""

if stdout:
    print("STDOUT:", stdout)

if stderr:
    print("STDERR:", stderr)