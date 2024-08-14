import os
import subprocess
from quart import Blueprint, request, render_template, current_app

upload_service = Blueprint('upload_service', __name__)
upload_service.config = {
    'UPLOAD_FOLDER': 'uploads/'
}

# Ensure the upload folder exists
os.makedirs(upload_service.config['UPLOAD_FOLDER'], exist_ok=True)

@upload_service.route('/upload', methods=['GET'])
async def upload_form():
    return await render_template('upload.html')

@upload_service.route('/process', methods=['POST'])
async def process_files():
    files = await request.files
    inference_code = files.get('inference_code')
    weights = files.get('weights')
    requirements = files.get('requirements')

    if inference_code is None or weights is None or requirements is None:
        return 'Missing file(s).', 400

    # Save files
    inference_code_path = os.path.join(upload_service.config['UPLOAD_FOLDER'], inference_code.filename)
    weights_path = os.path.join(upload_service.config['UPLOAD_FOLDER'], weights.filename)
    requirements_path = os.path.join(upload_service.config['UPLOAD_FOLDER'], requirements.filename)

    await inference_code.save(inference_code_path)
    await weights.save(weights_path)
    await requirements.save(requirements_path)

    # Create Dockerfile
    dockerfile_content = f"""
FROM python:3.9-slim-bullseye

WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libssl-dev \
    libffi-dev \
    libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY lightgbm_model.txt /app/lightgbm_model.txt
COPY inference_code.py /app/inference_code.py
COPY tickers.py /app/tickers.py

CMD ["python", "inference_code.py"]


    """

    dockerfile_path = os.path.join(upload_service.config['UPLOAD_FOLDER'], 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    # Remove any existing container
    try:
        subprocess.run(["docker", "rm", "-f", "model_inference"], check=True)
    except subprocess.CalledProcessError:
        pass  # Ignore error if the container doesn't exist

    # Build Docker image
    try:
        subprocess.run(["docker", "build", "-t", "model_inference:latest", upload_service.config['UPLOAD_FOLDER']], check=True)
    except subprocess.CalledProcessError as e:
        return await render_template('upload.html', result=f'Docker build failed: {e}')

    # Run Docker container
    try:
        container_id = subprocess.check_output([
            "docker", "run", "--name", "model_inference", "model_inference:latest"
        ]).strip().decode()
    except subprocess.CalledProcessError as e:
        return await render_template('upload.html', result=f'Docker run failed: {e}')

    return await render_template('upload.html', result=f'Docker container started successfully with ID: {container_id}')
