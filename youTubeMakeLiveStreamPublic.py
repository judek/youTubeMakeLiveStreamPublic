import os
import pickle
import json  
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

credentials = None
videoID = None

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube'
            ]
        )

        flow.run_local_server(port=8080, prompt='consent',
                              authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')

            # Should write the pickled data with a lower protocol number in Python 3. 
            # Python 3 introduced a new protocol with the number 3 (and uses it as default)
            # so switch back to a value of 2 which can be read by Python 2.
            pickle.dump(credentials, f, protocol=2)

youtube = build('youtube', 'v3', credentials=credentials)


print('Searching for live streams...')
list_broadcasts_request = youtube.liveBroadcasts().list(broadcastStatus='active', part='id,status', maxResults=1)

broadcastResponse = list_broadcasts_request.execute()

if not broadcastResponse['items']:
    print ('No live steams found')
    quit()

print('Live stream found id:')
videoID = broadcastResponse['items'][0]['id']
print(videoID)

#quit()

#listResponse = youtube.videos().list(part='status', id=videoID).execute()
listResponse = broadcastResponse

if not listResponse['items']:
    print ('Video was not found.')
    quit()


video_status = listResponse['items'][0]['status']

print('Current status.privacyStatus is', video_status['privacyStatus'])

if video_status['privacyStatus'] == 'public':
    print ('No work to do.')
    quit()


print('Setting status.privacyStatus = public')
video_status['privacyStatus'] = 'public'

print('Updating video status...')
updateResponse = youtube.videos().update(part='status',
    
    body=dict(
      status=video_status,
     id=videoID)
 
 ).execute()

print(updateResponse)