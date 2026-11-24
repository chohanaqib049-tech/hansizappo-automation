import argparse
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    parser = argparse.ArgumentParser(
        description="Authorize HansiZappo to upload videos to the selected YouTube channel."
    )
    parser.add_argument(
        "--client-secrets",
        default="client_secret.json",
        help="Path to the downloaded Google Desktop OAuth client JSON file.",
    )
    parser.add_argument(
        "--output",
        default="youtube-token.json",
        help="Local token output path. Keep this file private; never commit or share it.",
    )
    args = parser.parse_args()

    client_file = Path(args.client_secrets)
    if not client_file.is_file():
        raise SystemExit(
            f"OAuth client JSON not found: {client_file}\n"
            "Save the downloaded Desktop OAuth JSON as client_secret.json "
            "in the repository root, or pass --client-secrets with its path."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_file), SCOPES
    )
    credentials = flow.run_local_server(
        host="localhost",
        port=0,
        authorization_prompt_message=(
            "Open this URL in your browser to authorize HansiZappo: {url}"
        ),
        success_message=(
            "Authorization received. You can close this browser tab and return "
            "to the terminal."
        ),
        open_browser=True,
    )

    token_file = Path(args.output)
    token_file.write_text(
        json.dumps(
            {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"AUTHORIZATION_SUCCESS. Token saved locally to: {token_file}")
    print("Do not upload this file to GitHub, commit it, or send it in chat.")
    if not credentials.refresh_token:
        print(
            "WARNING: Google did not return a refresh token. Do not continue "
            "to configure GitHub Actions until a refresh token is obtained."
        )


if __name__ == "__main__":
    main()
