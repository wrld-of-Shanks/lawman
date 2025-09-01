import os
import requests

UPLOAD_URL = 'http://localhost:8000/upload'
FOLDER = 'data/processed/'

# Supported file extensions
EXTENSIONS = ['.txt', '.pdf', '.docx']

def batch_upload():
    files = [f for f in os.listdir(FOLDER) if os.path.splitext(f)[1].lower() in EXTENSIONS]
    if not files:
        print('No files found for upload.')
        return
    for fname in files:
        path = os.path.join(FOLDER, fname)
        print(f'Uploading: {fname} ...', end=' ')
        with open(path, 'rb') as f:
            files_data = {'file': (fname, f)}
            try:
                resp = requests.post(UPLOAD_URL, files=files_data)
                if resp.status_code == 200:
                    print('Success!')
                else:
                    print(f'Failed ({resp.status_code})')
            except Exception as e:
                print(f'Error: {e}')

if __name__ == '__main__':
    batch_upload() 