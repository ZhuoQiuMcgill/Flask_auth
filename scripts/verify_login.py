#!/usr/bin/env python3
"""
Login verification script.
This script tests login functionality by making HTTP requests to the Auth API.
"""

import os
import sys
import argparse
import logging
import requests
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_api_config(env_file='.env'):
    """Get API host and port from environment or .env file."""
    # Check environment variables first
    host = os.environ.get('API_HOST', 'localhost')
    port = os.environ.get('API_PORT', '5000')

    # If not in environment, try to read from .env file
    if (host == 'localhost' or port == '5000') and os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('API_HOST='):
                    host = line.strip().split('=', 1)[1].strip("'\"")
                elif line.startswith('API_PORT='):
                    port = line.strip().split('=', 1)[1].strip("'\"")

    return host, int(port)


def verify_login(host, port, identifier, password):
    """Verify login credentials by calling the Auth API."""
    url = f"http://{host}:{port}/api/user/login"
    headers = {"Content-Type": "application/json"}
    payload = {
        "identifier": identifier,
        "password": password
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


def get_user_profile(host, port, access_token):
    """Get user profile information using the access token."""
    url = f"http://{host}:{port}/api/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Profile request failed: {e}")
        return None


def main():
    """Main function to parse arguments and verify login."""
    parser = argparse.ArgumentParser(description='Verify login credentials against the Auth API.')

    # API connection options
    parser.add_argument(
        '--host',
        help='Host address of the Auth API (default: from .env or localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        help='Port number of the Auth API (default: from .env or 5000)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to the environment file (default: .env)'
    )

    # Login credentials
    parser.add_argument(
        '-u', '--username',
        help='Username for login'
    )
    parser.add_argument(
        '-e', '--email',
        help='Email for login'
    )
    parser.add_argument(
        '-p', '--password',
        required=True,
        help='Password for login'
    )

    # Additional options
    parser.add_argument(
        '--profile',
        action='store_true',
        help='Fetch user profile after successful login'
    )

    args = parser.parse_args()

    # Get API configuration
    default_host, default_port = get_api_config(args.env_file)
    host = args.host or default_host
    port = args.port or default_port

    # Determine identifier (username or email)
    identifier = args.username or args.email
    if not identifier:
        logger.error("Either username (-u) or email (-e) is required.")
        sys.exit(1)

    # Verify login
    logger.info(f"Verifying login for {identifier} at {host}:{port}...")
    response = verify_login(host, port, identifier, args.password)

    if not response:
        logger.error("Failed to connect to the Auth API.")
        sys.exit(1)

    # Display results
    status_code = response.status_code
    response_data = response.json() if response.text else {}

    print("\n--- Login Verification Results ---")
    print(f"Status: {status_code}")

    if status_code == 200:
        print(f"Result: SUCCESS")
        print(f"Access Token: {response_data.get('access_token', 'N/A')}")
        print(f"Token Type: {response_data.get('token_type', 'N/A')}")

        # Fetch profile if requested
        if args.profile:
            print("\n--- User Profile ---")
            access_token = response_data.get('access_token')
            if access_token:
                profile_response = get_user_profile(host, port, access_token)
                if profile_response and profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(json.dumps(profile_data, indent=2))
                else:
                    profile_status = profile_response.status_code if profile_response else "Failed"
                    profile_error = profile_response.json().get('error',
                                                                'Unknown error') if profile_response and profile_response.text else "Connection failed"
                    print(f"Failed to fetch profile: {profile_status} - {profile_error}")
            else:
                print("No access token available for profile request.")
            print("------------------")
    else:
        print(f"Result: FAILED")
        print(f"Error: {response_data.get('error', 'Unknown error')}")
        if 'details' in response_data:
            print(f"Details: {json.dumps(response_data['details'], indent=2)}")

    print(f"Message: {response_data.get('message', 'N/A')}")
    print("--------------------------------\n")


if __name__ == "__main__":
    main()
