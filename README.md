# FTP API Gateway

This project provides an API gateway to transfer files to an FTP server using FastAPI. It allows you to send binary file content along with metadata like filename and platename, and handles FTP connections based on a lookup table defined in an external JSON file.

## Features

- Upload files to an FTP server via a REST API.
- Dynamically look up FTP server credentials from an external JSON file.
- Cancel ongoing uploads using `AbortController`.

## Requirements

- Python 3.7+
- FastAPI
- `aiofiles` for asynchronous file handling
- `python-multipart` for handling file uploads
- `uvicorn` for running the FastAPI server

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/your-repo/ftp-api-gateway.git
    cd ftp-api-gateway
    ```

2. **Create a virtual environment and activate it:**

    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Create config JSON file:**

    Create a file named `config.json` in the project root directory with the following format:

    ```json
    {
        "http_port": 5000,
        "https_port": 5001,
        "api_key": "your_api_key",
        "cors_origins": [
            "http://localhost:5173"
        ],
        "ftp_credentials": {
            "wallplate2": {
                "host": "wallplate2.local",
                "user": "ftpuser",
                "pass": "ftpuser"
            }
        }
    }
    ```
5. **Create certificate files**

    Create the certificate files in the cert directory. When the directory does not exist you should create on:

    ```bash
    mkdir certs
    cd certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
    ```

    After running the command and providing the information, you will have two files in your certs directory:

    - key.pem: The private key file.
    - cert.pem: The self-signed certificate file.

## Usage

1. **Run the FastAPI server:**

    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2. **Upload a file using the API:**

    Use a tool like `curl` or Postman to send a POST request to the API endpoint:

    ```sh
    curl -X POST "http://localhost:8000/upload" \
    -H "API-Key: your_api_key" \
    -H "Filename: your_filename" \
    -H "Platename: platename1" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @path_to_your_file
    ```

3. **Cancel an ongoing upload:**

    If you are using the JavaScript client, you can call the `cancelUpload` method on the `FileUploader` class instance to cancel an ongoing upload.

## API Documentation

Once the server is running, you can access the automatically generated API documentation by navigating to:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## JavaScript Client

### FileUploader Class

The `FileUploader` class is used to interact with the API from a JavaScript client. Here's an example:

```javascript
class FileUploader {
  constructor(apiUrl, apiKey) {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
    this.controller = new AbortController();
  }

  async uploadFile(file, filename, platename, username, password) {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/octet-stream',
          'API-Key': this.apiKey,
          'Filename': filename,
          'Platename': platename,
          'Username': username,
          'Password': password
        },
        body: file,
        signal: this.controller.signal
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      return responseData;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Upload canceled');
      } else {
        console.error('Error uploading file:', error);
      }
      throw error;
    }
  }

  cancelUpload() {
    this.controller.abort();
  }
}
