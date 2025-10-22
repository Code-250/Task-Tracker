"""
QR Code Service - FastAPI Application
"""
import os
import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from app.qr_encoder import encode_message
from app.qr_decoder import decode_qr
from app.auth_client import AuthClient, AuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QR Code Service",
    description="QR Code Encoding and Decoding Service with Authentication",
    version="1.0.0"
)

# Configuration from environment variables
TEAM_NAME = os.getenv("TEAM_NAME", "Cumulonimbus")
TEAM_AWS_ID = os.getenv("TEAM_AWS_ID", "587764054854")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:9000")

# Initialize authentication client
auth_client = AuthClient(AUTH_SERVICE_URL, TEAM_NAME)

logger.info(f"QR Code Service started")
logger.info(f"Team: {TEAM_NAME}, AWS ID: {TEAM_AWS_ID}")
logger.info(f"Auth Service URL: {AUTH_SERVICE_URL}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "QR Code Service",
        "team": TEAM_NAME,
        "aws_id": TEAM_AWS_ID,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check for Kubernetes liveness/readiness probes"""
    return {"status": "healthy"}


@app.get("/qrcode", response_class=PlainTextResponse)
async def qrcode_handler(
    type: str = Query(..., description="Operation type: 'encode' or 'decode'"),
    data: str = Query(..., description="Data to encode or decode"),
    timestamp: int = Query(None, description="Unix timestamp (required for decode)")
):
    """
    QR Code Service Endpoint

    Encoding:
        GET /qrcode?type=encode&data=<message>
        Returns: <TEAM_NAME>,<TEAM_AWS_ID>\\n<Encoded_Hex_String>

    Decoding:
        GET /qrcode?type=decode&data=<hex_string>&timestamp=<unix_timestamp>
        Returns: <TEAM_NAME>,<TEAM_AWS_ID>\\n<Encrypted_Token>
    """
    try:
        if type.lower() == "encode":
            logger.info(f"Encoding request: message='{data}'")

            # Encode the message
            hex_string = encode_message(data)

            # Format response
            response = f"{TEAM_NAME},{TEAM_AWS_ID}\n{hex_string}"

            logger.info(f"Encoding successful: {len(hex_string)} characters")
            return response

        elif type.lower() == "decode":
            logger.info(f"Decoding request: data length={len(data)}, timestamp={timestamp}")

            # Validate timestamp
            if timestamp is None:
                raise HTTPException(
                    status_code=400,
                    detail="timestamp parameter is required for decode operation"
                )

            # Decode the QR code
            decoded_message = decode_qr(data)
            logger.info(f"Decoded message: '{decoded_message}'")

            # Authenticate and get token
            try:
                token = auth_client.authenticate(decoded_message, timestamp)
                logger.info(f"Authentication successful, token received")
            except AuthenticationError as e:
                logger.error(f"Authentication failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Authentication failed: {str(e)}"
                )

            # Format response
            response = f"{TEAM_NAME},{TEAM_AWS_ID}\n{token}"

            logger.info("Decoding and authentication successful")
            return response

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type parameter: '{type}'. Must be 'encode' or 'decode'"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
