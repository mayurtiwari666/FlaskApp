# from flask import Flask, render_template, request, redirect, url_for, send_file
# import boto3
# import os
# from config import AWS_REGION
# from werkzeug.utils import secure_filename
# import tempfile

# app = Flask(__name__)

# s3 = boto3.client("s3", region_name=AWS_REGION)


# @app.route("/")
# def index():
#     buckets = s3.list_buckets()["Buckets"]
#     return render_template("index.html", buckets=buckets, current_bucket=None, objects=[])


# @app.route("/create_bucket", methods=["POST"])
# def create_bucket():
#     bucket_name = request.form["bucket_name"]
#     s3.create_bucket(
#         Bucket=bucket_name,
#         CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
#     )
#     return redirect(url_for("index"))


# @app.route("/delete_bucket/<bucket_name>")
# def delete_bucket(bucket_name):
#     s3.delete_bucket(Bucket=bucket_name)
#     return redirect(url_for("index"))


# @app.route("/bucket/<bucket_name>")
# def view_bucket(bucket_name):
#     response = s3.list_objects_v2(Bucket=bucket_name)
#     objects = response.get("Contents", [])
#     return render_template(
#         "index.html",
#         buckets=s3.list_buckets()["Buckets"],
#         current_bucket=bucket_name,
#         objects=objects,
#     )


# @app.route("/upload/<bucket_name>", methods=["POST"])
# def upload_file(bucket_name):
#     file = request.files["file"]
#     folder = request.form.get("folder", "").strip()
#     key = secure_filename(file.filename)
#     if folder:
#         key = folder.rstrip("/") + "/" + key

#     s3.upload_fileobj(file, bucket_name, key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# @app.route("/download/<bucket_name>/<path:key>")
# def download_file(bucket_name, key):
#     tmp = tempfile.NamedTemporaryFile(delete=False)
#     s3.download_file(bucket_name, key, tmp.name)
#     tmp.close()
#     return send_file(tmp.name, as_attachment=True, download_name=os.path.basename(key))


# @app.route("/delete_file/<bucket_name>/<path:key>")
# def delete_file(bucket_name, key):
#     s3.delete_object(Bucket=bucket_name, Key=key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# @app.route("/copy_move/<bucket_name>", methods=["POST"])
# def copy_move(bucket_name):
#     src_key = request.form["src_key"]
#     dest_key = request.form["dest_key"]
#     action = request.form["action"]

#     copy_source = {"Bucket": bucket_name, "Key": src_key}
#     s3.copy_object(CopySource=copy_source, Bucket=bucket_name, Key=dest_key)

#     if action == "move":
#         s3.delete_object(Bucket=bucket_name, Key=src_key)

#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# if __name__ == "__main__":
#     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, send_file
# import boto3
# import os
# from io import BytesIO

# app = Flask(__name__)

# # Boto3 S3 client (uses your env/credentials config)
# s3 = boto3.client("s3")


# @app.route("/")
# def index():
#     """List all buckets"""
#     buckets = s3.list_buckets().get("Buckets", [])
#     return render_template("index.html", buckets=buckets, current_bucket=None, objects=None)


# @app.route("/create_bucket", methods=["POST"])
# def create_bucket():
#     """Create a new bucket"""
#     bucket_name = request.form["bucket_name"].strip()
#     if bucket_name:
#         s3.create_bucket(Bucket=bucket_name)
#     return redirect(url_for("index"))


# @app.route("/delete_bucket/<bucket_name>")
# def delete_bucket(bucket_name):
#     """Delete a bucket (must be empty)"""
#     s3.delete_bucket(Bucket=bucket_name)
#     return redirect(url_for("index"))


# @app.route("/bucket/<bucket_name>")
# def view_bucket(bucket_name):
#     """View contents of a bucket"""
#     objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", []) or []
#     buckets = s3.list_buckets().get("Buckets", [])
#     return render_template(
#         "index.html",
#         buckets=buckets,
#         current_bucket=bucket_name,
#         objects=objects,
#         all_buckets=buckets,   # for the destination bucket dropdown
#     )


# @app.route("/upload/<bucket_name>", methods=["POST"])
# def upload_file(bucket_name):
#     """Upload a file to a bucket (optional folder prefix)"""
#     file = request.files["file"]
#     folder = (request.form.get("folder", "") or "").strip()
#     key = file.filename
#     if folder:
#         folder = folder.rstrip("/") + "/"
#         key = folder + file.filename
#     s3.upload_fileobj(file, bucket_name, key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# @app.route("/download/<bucket_name>/<path:key>")
# def download_file(bucket_name, key):
#     """Download a file from a bucket"""
#     buf = BytesIO()
#     s3.download_fileobj(bucket_name, key, buf)
#     buf.seek(0)
#     return send_file(buf, as_attachment=True, download_name=os.path.basename(key))


# @app.route("/delete_file/<bucket_name>/<path:key>")
# def delete_file(bucket_name, key):
#     """Delete a file from a bucket"""
#     s3.delete_object(Bucket=bucket_name, Key=key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# # Backward-compatible endpoint name AND the new one:
# @app.route("/copy_move/<bucket_name>", methods=["POST"], endpoint="copy_move")
# @app.route("/copy_move_file/<bucket_name>", methods=["POST"])
# def copy_move_file(bucket_name):
#     """
#     Copy/Move a file within the same bucket or to another bucket.
#     Form fields:
#       - src_key (existing key)
#       - dest_key (new key)
#       - dest_bucket (optional; defaults to current bucket)
#       - action: "copy" or "move"
#     """
#     src_key = request.form["src_key"]
#     dest_key = request.form["dest_key"]
#     dest_bucket = (request.form.get("dest_bucket") or "").strip() or bucket_name
#     action = (request.form.get("action") or "copy").lower()

#     # Copy
#     s3.copy_object(
#         Bucket=dest_bucket,
#         CopySource={"Bucket": bucket_name, "Key": src_key},
#         Key=dest_key,
#     )

#     # If move, delete original
#     if action == "move":
#         s3.delete_object(Bucket=bucket_name, Key=src_key)

#     # After operation, show the destination bucket contents
#     return redirect(url_for("view_bucket", bucket_name=dest_bucket))


# if __name__ == "__main__":
#     app.run(debug=True, port=5001)  # 5001 to avoid conflicts on 5000

# from flask import Flask, render_template, request, redirect, url_for, send_file
# import boto3
# import os
# from io import BytesIO

# app = Flask(__name__)

# # Pick credentials from Render Environment Variables
# s3 = boto3.client(
#     "s3",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
#     region_name=os.getenv("AWS_REGION", "ap-south-1")
# )


# @app.route("/")
# def index():
#     buckets = s3.list_buckets().get("Buckets", [])
#     return render_template("index.html", buckets=buckets, current_bucket=None, objects=None)


# @app.route("/create_bucket", methods=["POST"])
# def create_bucket():
#     bucket_name = request.form["bucket_name"].strip()
#     if bucket_name:
#         s3.create_bucket(
#             Bucket=bucket_name,
#             CreateBucketConfiguration={"LocationConstraint": os.getenv("AWS_REGION", "ap-south-1")}
#         )
#     return redirect(url_for("index"))


# @app.route("/delete_bucket/<bucket_name>")
# def delete_bucket(bucket_name):
#     s3.delete_bucket(Bucket=bucket_name)
#     return redirect(url_for("index"))


# @app.route("/bucket/<bucket_name>")
# def view_bucket(bucket_name):
#     objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", []) or []
#     buckets = s3.list_buckets().get("Buckets", [])
#     return render_template("index.html",
#                            buckets=buckets,
#                            current_bucket=bucket_name,
#                            objects=objects,
#                            all_buckets=buckets)


# @app.route("/upload/<bucket_name>", methods=["POST"])
# def upload_file(bucket_name):
#     file = request.files["file"]
#     folder = (request.form.get("folder", "") or "").strip()
#     key = file.filename
#     if folder:
#         key = folder.rstrip("/") + "/" + file.filename
#     s3.upload_fileobj(file, bucket_name, key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# @app.route("/download/<bucket_name>/<path:key>")
# def download_file(bucket_name, key):
#     buf = BytesIO()
#     s3.download_fileobj(bucket_name, key, buf)
#     buf.seek(0)
#     return send_file(buf, as_attachment=True, download_name=os.path.basename(key))


# @app.route("/delete_file/<bucket_name>/<path:key>")
# def delete_file(bucket_name, key):
#     s3.delete_object(Bucket=bucket_name, Key=key)
#     return redirect(url_for("view_bucket", bucket_name=bucket_name))


# @app.route("/copy_move/<bucket_name>", methods=["POST"])
# def copy_move(bucket_name):
#     src_key = request.form["src_key"]
#     dest_key = request.form["dest_key"]
#     dest_bucket = (request.form.get("dest_bucket") or "").strip() or bucket_name
#     action = (request.form.get("action") or "copy").lower()

#     s3.copy_object(
#         Bucket=dest_bucket,
#         CopySource={"Bucket": bucket_name, "Key": src_key},
#         Key=dest_key,
#     )

#     if action == "move":
#         s3.delete_object(Bucket=bucket_name, Key=src_key)

#     return redirect(url_for("view_bucket", bucket_name=dest_bucket))


# if __name__ == "__main__":
#     # In Render, Gunicorn will run it, not Flask dev server
#     app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
import os
from io import BytesIO

app = Flask(__name__)

# Pick credentials from Render Environment Variables
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION", "ap-south-1")
)

# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    """List all buckets"""
    buckets = s3.list_buckets().get("Buckets", [])
    return render_template("index.html", buckets=buckets, current_bucket=None, objects=None)


@app.route("/create_bucket", methods=["POST"])
def create_bucket():
    """Create a new bucket"""
    bucket_name = request.form["bucket_name"].strip()
    if bucket_name:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": os.getenv("AWS_REGION", "ap-south-1")}
        )
    return redirect(url_for("index"))


@app.route("/delete_bucket/<bucket_name>")
def delete_bucket(bucket_name):
    """Delete a bucket (must be empty)"""
    s3.delete_bucket(Bucket=bucket_name)
    return redirect(url_for("index"))


@app.route("/bucket/<bucket_name>")
def view_bucket(bucket_name):
    """View bucket contents"""
    objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", []) or []
    buckets = s3.list_buckets().get("Buckets", [])
    return render_template(
        "index.html",
        buckets=buckets,
        current_bucket=bucket_name,
        objects=objects,
        all_buckets=buckets
    )


@app.route("/upload/<bucket_name>", methods=["POST"])
def upload_file(bucket_name):
    """Upload file to bucket (optional folder prefix)"""
    file = request.files["file"]
    folder = (request.form.get("folder", "") or "").strip()
    key = file.filename
    if folder:
        key = folder.rstrip("/") + "/" + file.filename
    s3.upload_fileobj(file, bucket_name, key)
    return redirect(url_for("view_bucket", bucket_name=bucket_name))


@app.route("/download/<bucket_name>/<path:key>")
def download_file(bucket_name, key):
    """Download a file"""
    buf = BytesIO()
    s3.download_fileobj(bucket_name, key, buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=os.path.basename(key))


@app.route("/delete_file/<bucket_name>/<path:key>")
def delete_file(bucket_name, key):
    """Delete a file"""
    s3.delete_object(Bucket=bucket_name, Key=key)
    return redirect(url_for("view_bucket", bucket_name=bucket_name))


@app.route("/copy_move/<bucket_name>", methods=["POST"])
def copy_move(bucket_name):
    """Copy or Move a file within/between buckets"""
    src_key = request.form["src_key"]
    dest_key = request.form["dest_key"]
    dest_bucket = (request.form.get("dest_bucket") or "").strip() or bucket_name
    action = (request.form.get("action") or "copy").lower()

    # Copy
    s3.copy_object(
        Bucket=dest_bucket,
        CopySource={"Bucket": bucket_name, "Key": src_key},
        Key=dest_key,
    )

    # If move, delete original
    if action == "move":
        s3.delete_object(Bucket=bucket_name, Key=src_key)

    return redirect(url_for("view_bucket", bucket_name=dest_bucket))


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    # Locally you can run with Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
