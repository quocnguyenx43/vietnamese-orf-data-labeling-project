import os
# from apscheduler.schedulers.background import BackgroundScheduler
from onedrivesdk import AuthProvider, OneDriveClient


# Replace with your OneDrive API credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'your_redirect_uri'
SCOPES = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

auth_provider = AuthProvider(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scopes=SCOPES
)
client = OneDriveClient(auth_provider, None)
client.auth_provider.authenticate()

# Replace 'YourOneDriveFolder' with the actual path in your OneDrive where you want to store the backups
file_path = '/instance/database.db'
target_folder = "/test/database.db"

with open(file_path, "rb") as file:
    client.item(drive='me', path=target_folder + os.path.basename(file_path)).upload(file)