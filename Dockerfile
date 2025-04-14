# Use Miniconda base image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Create Conda virtual environment and install dependencies
RUN conda create -n tailortrip python=3.9.12 --yes && \
    conda install -n tailortrip -c conda-forge --yes faiss-gpu && \
    # conda install -n tailortrip -c conda-forge --yes faiss-cpu && \
    conda run -n tailortrip pip install -r requirements.txt && \
    conda run -n tailortrip pip install torch torchvision torchaudio

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]