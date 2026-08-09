from google_auth_oauthlib.flow import InstalledAppFlow

# Scope for reading Gmail - read-only is enough for pulling invoices
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',  # the file you downloaded from GCP console
    SCOPES
)

# This spins up a local server, opens your browser automatically
creds = flow.run_local_server(port=0)

# Save the token for future use
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("Auth successful. token.json created.")