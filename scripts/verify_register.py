#!/usr/bin/env python3
"""
Registration verification script.
This script tests registration functionality by making HTTP requests to the Auth API.
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


def verify_register(host, port, username, password, email=None):
    """Register a new user by calling the Auth API."""
    url = f"http://{host}:{port}/api/user/register"
    headers = {"Content-Type": "application/json"}
    payload = {
        "username": username,
        "password": password
    }

    # Add email if provided
    if email:
        payload["email"] = email

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


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
        logger.error(f"Login request failed: {e}")
        return None


def main():
    """Main function to parse arguments and verify registration."""
    parser = argparse.ArgumentParser(description='Verify user registration against the Auth API.')

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

    # Registration details
    parser.add_argument(
        '-u', '--username',
        required=True,
        help='Username for registration'
    )
    parser.add_argument(
        '-p', '--password',
        required=True,
        help='Password for registration'
    )
    parser.add_argument(
        '-e', '--email',
        help='Email for registration (optional)'
    )

    # Additional options
    parser.add_argument(
        '--verify-login',
        action='store_true',
        help='Verify login after successful registration'
    )

    args = parser.parse_args()

    # Get API configuration
    default_host, default_port = get_api_config(args.env_file)
    host = args.host or default_host
    port = args.port or default_port

    # Register user
    logger.info(f"Registering user {args.username} at {host}:{port}...")
    response = verify_register(host, port, args.username, args.password, args.email)

    if not response:
        logger.error("Failed to connect to the Auth API.")
        sys.exit(1)

    # Display results
    status_code = response.status_code
    response_data = response.json() if response.text else {}

    print("\n--- Registration Verification Results ---")
    print(f"Status: {status_code}")

    if status_code == 201:
        print(f"Result: SUCCESS")
        print(f"Message: {response_data.get('message', 'N/A')}")

        # Print user details if available
        if 'user' in response_data:
            print("\nUser Details:")
            print(json.dumps(response_data['user'], indent=2))

        # Verify login if requested
        if args.verify_login:
            print("\n--- Verifying Login with New Credentials ---")
            identifier = args.username
            password = args.password

            login_response = verify_login(host, port, identifier, password)

            if login_response:
                login_status = login_response.status_code
                login_data = login_response.json() if login_response.text else {}

                print(f"Login Status: {login_status}")

                if login_status == 200:
                    print(f"Login Result: SUCCESS")
                    print(f"Access Token: {login_data.get('access_token', 'N/A')}")
                    print(f"Token Type: {login_data.get('token_type', 'N/A')}")
                else:
                    print(f"Login Result: FAILED")
                    print(f"Error: {login_data.get('error', 'Unknown error')}")
                    if 'details' in login_data:
                        print(f"Details: {json.dumps(login_data['details'], indent=2)}")
            else:
                print("Login verification failed: Unable to connect to the Auth API.")
    else:
        print(f"Result: FAILED")
        print(f"Error: {response_data.get('error', 'Unknown error')}")
        if 'details' in response_data:
            print(f"Details: {json.dumps(response_data['details'], indent=2)}")

    print("--------------------------------\n")


if __name__ == "__main__":
    main()
