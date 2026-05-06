import boto3
import json
import os
from pathlib import Path
from botocore.exceptions import ClientError


BUCKET_NAME = 'cloud-computing-a2-tejum'   
AWS_REGION  = 'us-east-1'                 
EC2_IP      = 'YOUR_EC2_IP_HERE'           
EC2_PORT    = '5000'


project_root = Path(__file__).parent

FRONTEND_FILES = {
    'index.html': {
        'path':         project_root / 'templates' / 'index.html',
        'content_type': 'text/html'
    },
    'styles.css': {
        'path':         project_root / 'static' / 'styles.css',
        'content_type': 'text/css'
    },
    'app.js': {
        'path':         project_root / 'static' / 'app.js',
        'content_type': 'application/javascript'
    },
}

s3 = boto3.client('s3', region_name=AWS_REGION)



def create_bucket():
    try:
        if AWS_REGION == 'us-east-1':
            s3.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
        print(f' Bucket {BUCKET_NAME} created')
    except ClientError as e:
        code = e.response['Error']['Code']
        if code in ('BucketAlreadyOwnedByYou', 'BucketAlreadyExists'):
            print(f' Bucket {BUCKET_NAME} already exists')
        else:
            raise



def disable_block_public_access():
    try:
        s3.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls':       False,
                'IgnorePublicAcls':      False,
                'BlockPublicPolicy':     False,
                'RestrictPublicBuckets': False
            }
        )
        print('Public access block disabled')
    except ClientError as e:
        print(f'  Warning: Could not disable block public access: {e}')



def set_bucket_policy():
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid":       "PublicReadGetObject",
                "Effect":    "Allow",
                "Principal": "*",
                "Action":    "s3:GetObject",
                "Resource":  f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }
    try:
        s3.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(policy)
        )
        print(' Bucket policy set (public read)')
    except ClientError as e:
        print(f'  Warning: Could not set bucket policy: {e}')



def enable_static_hosting():
    try:
        s3.put_bucket_website(
            Bucket=BUCKET_NAME,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key':    'index.html'}
            }
        )
        print(' Static website hosting enabled')
    except ClientError as e:
        print(f'  Warning: Could not enable static hosting: {e}')



def patch_app_js():
    js_path = FRONTEND_FILES['app.js']['path']

    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    ec2_base = f'http://{EC2_IP}:{EC2_PORT}'

    api_routes = [
        '/login',
        '/logout',
        '/register',
        '/songs',
        '/subscriptions',
        '/play',
        '/image/',
    ]

    patched = content
    for route in api_routes:
        patched = patched.replace(
            f"fetch('{route}",
            f"fetch('{ec2_base}{route}"
        ).replace(
            f'fetch("{route}',
            f'fetch("{ec2_base}{route}'
        ).replace(
            f'fetch(`{route}',
            f'fetch(`{ec2_base}{route}'
        )

    # Write patched version to a temp file for upload
    temp_path = project_root / 'static' / 'app_s3.js'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(patched)

    print(f' app.js patched with EC2 URL: {ec2_base}')
    return temp_path



def print_cors_instructions():
    s3_url = f'http://{BUCKET_NAME}.s3-website-{AWS_REGION}.amazonaws.com'
    print()
    print('=' * 60)
    print('IMPORTANT: Update CORS in ECS/appFlask.py')
    print('=' * 60)
    print()
    print('Change this line in appFlask.py:')
    print()
    print('  CORS(app, supports_credentials=True)')
    print()
    print('To this:')
    print()
    print(f'  CORS(app, origins=["{s3_url}"], supports_credentials=True)')
    print()
    print('This allows the S3-hosted frontend to call the EC2 API.')
    print()



def upload_files(patched_js_path):
    print()
    print('Uploading frontend files to S3...')

    for key, info in FRONTEND_FILES.items():
        # Use patched app.js for upload, not the original
        if key == 'app.js' and patched_js_path:
            file_path = patched_js_path
        else:
            file_path = info['path']

        if not file_path.exists():
            print(f'   File not found: {file_path}')
            continue

        try:
            s3.upload_file(
                Filename=str(file_path),
                Bucket=BUCKET_NAME,
                Key=key,
                ExtraArgs={'ContentType': info['content_type']}
            )
            size = file_path.stat().st_size
            print(f'   Uploaded {key} ({size:,} bytes)')
        except ClientError as e:
            print(f'   Failed to upload {key}: {e}')

    # Clean up temp patched file
    if patched_js_path and patched_js_path.exists():
        patched_js_path.unlink()



def verify_uploads():
    print()
    print('Verifying uploads...')
    try:
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=''
        )
        objects = [o for o in response.get('Contents', [])
                   if o['Key'] in ('index.html', 'styles.css', 'app.js')]

        for obj in objects:
            print(f'   {obj["Key"]} — {obj["Size"]:,} bytes')

        if len(objects) < 3:
            missing = {'index.html','styles.css','app.js'} - {o['Key'] for o in objects}
            for m in missing:
                print(f'   {m} — NOT FOUND')

    except ClientError as e:
        print(f'  Could not verify: {e}')



def main():
    print('=' * 60)
    print('Soundwave — Upload Frontend to S3 Static Website')
    print('=' * 60)
    print(f'Bucket : {BUCKET_NAME}')
    print(f'Region : {AWS_REGION}')
    print(f'EC2 IP : {EC2_IP}:{EC2_PORT}')
    print()

    if EC2_IP == 'YOUR_EC2_IP_HERE':
        print('  WARNING: EC2_IP is not set!')
        print('   Edit this file and set EC2_IP to your EC2 public IP.')
        print('   e.g. EC2_IP = "54.123.45.67"')
        print()
        cont = input('Continue anyway? (y/n): ').strip().lower()
        if cont != 'y':
            print('Aborted.')
            return

    create_bucket()
    disable_block_public_access()
    set_bucket_policy()
    enable_static_hosting()

    # Patch app.js with EC2 URL before uploading
    patched_js = None
    if EC2_IP != 'YOUR_EC2_IP_HERE':
        patched_js = patch_app_js()
    else:
        print('  Skipping app.js patch (EC2_IP not set)')

    upload_files(patched_js)
    verify_uploads()
    print_cors_instructions()

    s3_url = f'http://{BUCKET_NAME}.s3-website-{AWS_REGION}.amazonaws.com'
    print('=' * 60)
    print('DONE!')
    print()
    print(f'Frontend URL: {s3_url}')
    print()
    print('Next steps:')
    print('  1. Update CORS in appFlask.py (see above)')
    print(f'  2. Run Flask on EC2: python -m ECS.appFlask')
    print(f'  3. Open in browser: {s3_url}')
    print('=' * 60)


if __name__ == '__main__':
    main()
