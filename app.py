import os
import time
import threading
import gitlab
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask

# ==========================
# CONFIG (use env vars)
# ==========================
GITLAB_URL = "https://gitlab.com"
PRIVATE_TOKEN = os.environ.get("TOKEN")
MAX_WORKERS = 10

app = Flask(__name__)

# ==========================
# CONNECT
# ==========================
gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)


# ==========================
# WORKER FUNCTION
# ==========================
def process_project(proj):
    try:
        project = gl.projects.get(proj.id)
        print(f"\nRepo: {project.name}")

        original_desc = project.description or ""

        project.description = original_desc + "√"
        project.save()

        project.description = original_desc
        project.save()

        print("✅ Activity triggered")

    except Exception as e:
        print("⚠ Error:", e)


# ==========================
# BACKGROUND LOOP
# ==========================
def background_worker():
    while True:
        print("\nFetching repositories...")
        projects = gl.projects.list(membership=True, all=True)
        print(f"Total repos: {len(projects)}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_project, proj) for proj in projects]
            for _ in as_completed(futures):
                pass

        print("Sleeping 30 seconds...\n")
        time.sleep(0)


# ==========================
# START BACKGROUND THREAD
# ==========================
threading.Thread(target=background_worker, daemon=True).start()


# ==========================
# HEALTH ROUTE (required)
# ==========================
@app.route("/")
def home():
    return "GitLab activity bot running!"


# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
