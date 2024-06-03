from flask import Flask, request, jsonify
import ftplib
from io import BytesIO
import json
import os

app = Flask(__name__)

# Define your API key
API_KEY = 'your_api_key'

# Path to the JSON file with FTP credentials
CREDENTIALS_FILE = 'ftp_credentials.json'

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check for API key in headers
        api_key = request.headers.get('API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Unauthorized access'}), 401

        # Get filename and platename from headers
        filename = request.headers.get('Filename')
        platename = request.headers.get('Platename')

        if not filename or not platename:
            return jsonify({'error': 'Missing Filename or Platename in headers'}), 400
        
        # Load and parse the FTP credentials JSON file
        if not os.path.exists(CREDENTIALS_FILE):
            return jsonify({'error': 'Credentials file not found'}), 500

        with open(CREDENTIALS_FILE, 'r') as file:
            ftp_credentials = json.load(file)
        
        # Look up FTP credentials based on platename
        if platename not in ftp_credentials:
            return jsonify({'error': 'Invalid platename'}), 400
        
        ftp_info = ftp_credentials[platename]
        ftp_host = ftp_info['host']
        ftp_user = ftp_info['user']
        ftp_pass = ftp_info['pass']
        ftp_dir = ftp_info['dir']
        
        # Read binary data from the request body
        file_data = request.get_data()
        print('upload '+filename +' to '+ftp_host)
        # Establish FTP connection
        ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
        ftp.cwd(ftp_dir)
        
        # Convert binary data to a BytesIO object
        file_obj = BytesIO(file_data)
        
        # Upload the file
        ftp.storbinary(f'STOR {filename}', file_obj)
        
        # Close the FTP connection
        ftp.quit()
        
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
