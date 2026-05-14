# Quickstart: Veg Restaurant Finder

## Prerequisites
- Python 3.11 or later
- Streamlit installed or available on Streamlit Community Cloud
- Valid environment variables:
  - `GOOGLE_API_KEY`
  - `OPENAI_API_KEY`

## Google Cloud Setup (Required)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the **Places API**:
   - Navigate to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
   - Search for "Places API"
   - Click on "Places API" and press **Enable**
4. Create an API key:
   - Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
   - Click **Create Credentials** > **API Key**
   - Copy the API key and save it for the `GOOGLE_API_KEY` environment variable

## OpenAI Setup (Required)

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign in or create an account
3. Navigate to [API Keys](https://platform.openai.com/account/api-keys)
4. Create a new secret key
5. Copy the key and save it for the `OPENAI_API_KEY` environment variable

## Local Setup
1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Create `.env` file from the template:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Edit `.env` and add your API keys:
   ```
   GOOGLE_API_KEY=your-google-api-key-here
   OPENAI_API_KEY=your-openai-api-key-here
   ```
5. Run the app locally:
   ```powershell
   streamlit run app.py
   ```

## Streamlit Community Cloud Deployment
1. Push the repository to GitHub
2. Create a new Streamlit Community Cloud app at [https://share.streamlit.io](https://share.streamlit.io)
3. Connect it to your GitHub repository
4. In the app settings, add your environment secrets:
   - `GOOGLE_API_KEY`: Your Google Places API key
   - `OPENAI_API_KEY`: Your OpenAI API key
5. Deploy the app

## Troubleshooting

### REQUEST_DENIED error
If you see "REQUEST_DENIED: The Places API is not enabled", follow the Google Cloud Setup section above to enable the Places API.

### No results found
- Verify the location name is valid (e.g., "San Francisco, CA")
- Check that your Google API key has the Places API enabled
- Ensure there are restaurants near the location

## Notes
- No user input or output is stored beyond the current session
- The app uses lightweight CSS only for styling and readability
- Each search request consumes API calls; be mindful of your Google and OpenAI usage quotas
