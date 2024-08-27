# Reddit Notes Exporter

This script exports your saved Reddit posts and comments to a text file.

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Create a Reddit app at https://www.reddit.com/prefs/apps
   - Choose 'script' for the app type
   - Set the redirect URI to http://localhost:8080

3. Copy the `.env.example` file to `.env` and fill in your Reddit app credentials.

## Usage

Run the script:

```
python src/exporter.py
```

Follow the prompts to authorize the app. Your saved notes will be exported to `data/reddit_saved_notes.txt`.
```