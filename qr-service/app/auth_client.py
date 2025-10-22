"""
REST Authentication Client
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


class AuthClient:
    """
    REST client for QR code authentication service
    """

    def __init__(self, auth_service_url: str, team_name: str):
        """
        Initialize authentication client

        Args:
            auth_service_url: URL of authentication service (e.g., http://auth-service:9000)
            team_name: Team name for authentication
        """
        self.auth_service_url = auth_service_url.rstrip('/')
        self.team_name = team_name

    def authenticate(self, decoded_qrcode: str, timestamp: int) -> str:
        """
        Authenticate using decoded QR code data

        Args:
            decoded_qrcode: The decoded QR code message
            timestamp: Unix timestamp (int64)

        Returns:
            Encrypted token string

        Raises:
            AuthenticationError: If authentication fails
        """
        # Prepare request payload
        payload = {
            "team_name": self.team_name,
            "timestamp": timestamp,
            "decoded_qrcode": decoded_qrcode
        }

        # Send POST request to /rest_auth endpoint
        url = f"{self.auth_service_url}/rest_auth"

        try:
            logger.info(f"Sending authentication request to {url}")
            logger.debug(f"Payload: {payload}")

            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )

            # Check response status
            if response.status_code != 200:
                error_msg = f"Authentication failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            # Parse response
            response_data = response.json()
            logger.debug(f"Response: {response_data}")

            # Check message field
            if response_data.get("message") != "SUCCESS":
                error_msg = f"Authentication failed: {response_data.get('message', 'Unknown error')}"
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            # Extract token
            token = response_data.get("token")
            if not token:
                error_msg = "No token in authentication response"
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            logger.info("Authentication successful")
            return token

        except requests.exceptions.Timeout:
            error_msg = "Authentication request timed out"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Could not connect to authentication service: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Authentication request failed: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
        except ValueError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
