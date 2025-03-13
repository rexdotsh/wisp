import re

from flask import request

from utils.response import format_error_response


def validate_username(username, service=None):
    """
    Validate the username based on the service.
    Return (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    if len(username) > 100:
        return False, "Username is too long"

    if service:
        if service == "gravatar" and not is_valid_email(username):
            return False, "Invalid email format for Gravatar"

        if service in ["google", "duckduckgo"] and not is_valid_domain(username):
            return False, "Invalid domain format"

        if re.search(r'[<>"\']', username):
            return False, f"Username contains invalid characters for {service}"

    return True, None


def is_valid_email(email):
    """
    Basic email validation.
    """
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_pattern.match(email))


def is_valid_domain(domain):
    """
    Basic domain validation.
    """
    domain_pattern = re.compile(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
    return bool(domain_pattern.match(domain))


def validate_ttl(ttl):
    """
    Validate the TTL value.
    Return (is_valid, ttl_value, error_message)
    """
    if ttl is None:
        return True, None, None

    try:
        ttl_value = int(ttl)
        if ttl_value < 60:  # Minimum 1 minute
            return False, None, "TTL must be at least 60 seconds"
        if ttl_value > 2592000:  # Maximum 30 days
            return False, None, "TTL cannot exceed 30 days (2592000 seconds)"
        return True, ttl_value, None
    except ValueError:
        return False, None, "TTL must be a valid integer"


def get_request_params():
    """
    Get and validate common request parameters.
    Return (raw, ttl, error_response)
    """
    raw = request.args.get("raw", "false").lower() in ["true", "1", "yes"]

    ttl = request.args.get("ttl")
    is_valid, ttl_value, error_message = validate_ttl(ttl)

    if not is_valid:
        return None, None, format_error_response(400, error_message)

    return raw, ttl_value, None
