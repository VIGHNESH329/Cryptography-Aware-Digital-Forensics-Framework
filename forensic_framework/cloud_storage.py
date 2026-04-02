import os

# Simulated S3 storage
CLOUD_BUCKET = "cloud_evidence_simulation"

def push_to_cloud(file_path):
    if not os.path.exists(CLOUD_BUCKET):
        os.makedirs(CLOUD_BUCKET)
    
    filename = os.path.basename(file_path)
    cloud_path = os.path.join(CLOUD_BUCKET, filename)
    
    # Simulate upload by copying
    with open(file_path, 'rb') as src, open(cloud_path, 'wb') as dst:
        dst.write(src.read())
    
    return f"s3://forensic-bucket/{filename}"

def check_cloud_status(filename):
    cloud_path = os.path.join(CLOUD_BUCKET, filename)
    return os.path.exists(cloud_path)
