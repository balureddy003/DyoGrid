# pip install fastmcp
from mcp.server.fastmcp import FastMCP
import os
import json
import logging
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Initialize the server
mcp = FastMCP("Math")


# MCP tool for sending email using a local SMTP server
@mcp.tool()
def mailer(
    to_address: str = "",
    subject: str = "",
    plain_text: str = "",
    html_content: str = ""
) -> str:
    """Send an email via SMTP."""
    logger = logging.getLogger("mailer")

    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", "25"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    sender_address = os.environ.get("SMTP_SENDER", "noreply@example.com")

    logger.info("Mailer tool started.")
    logger.info(f"SMTP host: {smtp_host}:{smtp_port}")
    logger.info(f"Sender address: {sender_address}")
    logger.info(f"Recipient address: {to_address}")
    logger.info(f"Subject: {subject}")  
    logger.info(f"Plain text: {plain_text}")
    logger.info(f"HTML content: {html_content}")
    logger.info(f"Environment variables: {os.environ}")

    if not to_address:
        logger.error("No recipient address provided")
        return "Recipient address is required"
    if not subject:
        subject = "Message from local agent"
    logger.info(f"Sending email to {to_address}...")
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(plain_text, "plain")
        msg["Subject"] = subject
        msg["From"] = sender_address
        msg["To"] = to_address

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(sender_address, [to_address], msg.as_string())
        logger.info("Email sent.")
        return "Email sent. \n\nTERMINATE."
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return f"Failed to send email: {e} \n\nTERMINATE."

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b

# @mcp.tool()
# def data_provider() -> str:
#     """A tool that provides some data."""
#     # This is a placeholder for the actual data provider logic
#     data = "This is some data."
#     # read from a file
#     with open("data/pred_maint/sensor.csv", "r") as file:
#         data = file.read()
    
#     return data


@mcp.tool()
def data_provider(tablename: str) -> str:
    """A tool that provides data from database based on given table name as parameter.
    
    Args:
        tablename (str): The table to read data from.
        
    Returns:
        str: The content of the file.

    """
    logger = logging.getLogger("file_provider")
    # This is a placeholder for the actual data provider logic
    data = "This is some data."
    logger.warning(f"Table '{tablename}' requested.")

    try:
        tablename = tablename.strip() + ".csv"
        # locate the file in .data folder recursively
        _file_json = find_file(tablename)
        _file_info = json.loads(_file_json)
        _file_path = _file_info["path"]
        if not _file_path:
            logger.error(f"File '{tablename}' not found.")
            return f"File '{tablename}' not found."
        logger.warning(f"File '{tablename}' found at '{_file_path}'.")
        # read from a file
        with open(_file_path, "r") as file:
            data = file.read()
    
        return data
    except Exception as e:
        logger.error(f"Error reading file '{tablename}': {e}")
        return None

def find_file(filename: str) -> str:
    """
    Searches recursively within the ./data folder for an exact filename match.
    Returns a JSON string with the full relative path and the original filename.
    """
    logger = logging.getLogger("find_file")
    for root, _, files in os.walk("./data"):
        if filename in files:
            full_path = os.path.join(root, filename)
            logger.warning(f"Found file: {full_path}")
            return json.dumps({
                "path": full_path,
                "filename": filename
            })
    logging.warning(f"File '{filename}' not found in './data' directory.")
    return json.dumps({
        "path": None,
        "filename": filename
    })

if __name__ == "__main__":
    mcp.run(transport="stdio")
    # data = file_provider("maintenance.csv")
    # print(data)