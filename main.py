import boto3
from botocore.exceptions import NoCredentialsError
import requests
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play
import requests


# Define the audio settings
CHUNK = 1024  # Size of each audio chunk
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 2  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sample rate (samples per second)
RECORD_SECONDS = 10  # Duration of the recording
OUTPUT_FILENAME = "put.wav"  # Output audio file

# Record audio
p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Recording...")

frames = []

for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording done.")

stream.stop_stream()
stream.close()
p.terminate()

# Create a WAV file to save the recorded audio
wf = wave.open(OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

def upload_to_s3(local_file_path, bucket_name, s3_file_key, aws_access_key_id, aws_secret_access_key):
    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Upload the file with public-read ACL (Access Control List)
        s3.upload_file(
            local_file_path,
            bucket_name,
            s3_file_key,
            ExtraArgs={'ACL': 'public-read'}
        )

        # Generate direct URL
        direct_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_file_key}'
        return direct_url

    except FileNotFoundError:
        print("The file was not found")
        return None

    except NoCredentialsError:
        print("Credentials not available")
        return None

# Example usage
local_file_path = 'put.wav'
bucket_name = ''
s3_file_key = ''
aws_access_key_id = ''
aws_secret_access_key = ''

direct_url = upload_to_s3(local_file_path, bucket_name, s3_file_key, aws_access_key_id, aws_secret_access_key)

if direct_url:
    print(f'Direct URL: {direct_url}')
    # Now you can use this direct URL in your API call
    shazam_api_url = "https://shazam-api-new1.p.rapidapi.com/"
    shazam_querystring = {"url": direct_url}

    shazam_headers = {
            "X-RapidAPI-Key": "",
            "X-RapidAPI-Host": ""
        }

    shazam_response = requests.get(shazam_api_url, headers=shazam_headers, params=shazam_querystring)

        # Process the Shazam API response as needed
    shazam_result = shazam_response.json()
    print("Shazam API Response:", shazam_result)

    track_info = shazam_result.get('track', {}) or shazam_result.get('result', {}).get('track', {})
    title = track_info.get('title')
    subtitle = track_info.get('subtitle')
    images = track_info.get('images', {})
    background_image_url = images.get('background')

    # Print the extracted information
    print(f'Title: {title}')
    print(f'Artist: {subtitle}')
    print(f'Background Image URL: {background_image_url}')

import boto3
from botocore.exceptions import NoCredentialsError

def delete_from_s3(bucket_name, s3_file_key, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Delete the object from S3
        s3.delete_object(Bucket=bucket_name, Key=s3_file_key)

        print(f'File {s3_file_key} deleted successfully from {bucket_name}')

    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"An error occurred: {e}")

# this will delete the just uploaded file so you can re upload a new file later
bucket_name = ''
s3_file_key = ''
aws_access_key_id = ''
aws_secret_access_key = ''


delete_from_s3(bucket_name, s3_file_key, aws_access_key_id, aws_secret_access_key)
