import io
import os

from flask import jsonify, request, send_file


def format_response(username, service, image_data, image_url, cache_metadata=None, raw=False):
    """
    Format the response based on the raw parameter.
    If raw is True, return JSON data, otherwise return the image.
    """
    if raw:
        return format_json_response(username, service, image_url, cache_metadata)
    else:
        return format_image_response(image_data, image_url, username)


def format_image_response(image_data, image_url=None, username=None):
    """
    Return the image data as a response.
    """
    if image_data:
        # Return the image data
        return send_file(io.BytesIO(image_data), mimetype="image/jpeg")

    return format_default_avatar_response()


def format_json_response(username, service, image_url, cache_metadata=None):
    """
    Return JSON data with metadata.
    """
    response_data = {
        "username": username,
        "service": service,
        "image_url": image_url,
    }

    if cache_metadata:
        response_data["cache"] = {
            "status": "hit",
            "created_at": cache_metadata.get("created_at"),
            "expires_at": cache_metadata.get("expires_at"),
            "ttl": cache_metadata.get("ttl"),
        }
    else:
        response_data["cache"] = {"status": "miss"}

    return jsonify(response_data)


def format_default_avatar_response():
    """
    Return the default avatar from the utils folder.
    """
    default_avatar_path = os.path.join(os.path.dirname(__file__), "default_avatar.png")

    try:
        return send_file(default_avatar_path, mimetype="image/png")
    except Exception as e:
        return format_error_response(404, f"Default avatar not found: {str(e)}")


def format_error_response(error_code, message):
    """
    Return an error response.
    """
    if request.args.get("raw", "false").lower() in ["true", "1", "yes"]:
        return jsonify({"error": message}), error_code
    else:
        return format_default_avatar_response()
