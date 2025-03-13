import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from cache import cache
from config import Config
from services import get_service, get_unique_services
from utils.response import format_error_response, format_response
from utils.validation import get_request_params, validate_username

# Create a default avatar image directory
os.makedirs("utils", exist_ok=True)

app = Flask(__name__, template_folder="templates")
CORS(app)


@app.route("/")
def index():
    """
    Index page with documentation.

    Returns:
        HTML page with documentation
    """
    services = get_unique_services()

    return render_template("index.html", services=services)


@app.route("/docs")
def docs():
    """
    Documentation page with detailed API information.

    Returns:
        HTML page with detailed API documentation
    """
    services = get_unique_services()

    return render_template("docs.html", services=services)


@app.route("/<service>/<username>")
def get_profile_picture(service, username):
    """
    Get a profile picture from the specified service.

    Args:
        service (str): The service name (github, twitter, etc.)
        username (str): The username to get the profile picture for

    Query Parameters:
        raw (bool): If true, return JSON data instead of the image
        ttl (int): Custom TTL in seconds

    Returns:
        Image or JSON response
    """
    service_adapter = get_service(service)
    if not service_adapter:
        return format_error_response(400, f"Unsupported service: {service}")

    is_valid, error_message = validate_username(username, service)
    if not is_valid:
        return format_error_response(400, error_message)

    raw, ttl, error_response = get_request_params()
    if error_response:
        return error_response

    cache_key = f"{service}:{username}"
    cached_data = cache.get(cache_key)
    cache_metadata = None

    if cached_data:
        cache_metadata = cache.get_metadata(cache_key)
        return format_response(
            username,
            service,
            cached_data.get("image_data"),
            cached_data.get("image_url"),
            cache_metadata,
            raw,
        )

    image_data, image_url, error = service_adapter.get_profile_picture(username)

    if error:
        return format_error_response(404, error)

    cache.set(cache_key, {"image_data": image_data, "image_url": image_url}, ttl)

    return format_response(username, service, image_data, image_url, None, raw)


@app.route("/batch")
def batch_profile_pictures():
    """
    Get multiple profile pictures in one request.

    Query Parameters:
        <service>=<username>: Multiple service-username pairs
        raw (bool): If true, return JSON data

    Returns:
        JSON response with all requested profile pictures
    """
    _, ttl, error_response = get_request_params()
    if error_response:
        return error_response

    service_usernames = {}
    for param, value in request.args.items():
        if param not in ["raw", "ttl"]:
            service = param
            username = value
            service_usernames[service] = username

    if not service_usernames:
        return format_error_response(400, "No service-username pairs provided")

    results = {}
    for service, username in service_usernames.items():
        service_adapter = get_service(service)
        if not service_adapter:
            results[service] = {"error": f"Unsupported service: {service}"}
            continue

        is_valid, error_message = validate_username(username, service)
        if not is_valid:
            results[service] = {"error": error_message}
            continue

        cache_key = f"{service}:{username}"
        cached_data = cache.get(cache_key)
        cache_metadata = None

        if cached_data:
            cache_metadata = cache.get_metadata(cache_key)
            image_url = cached_data.get("image_url")
            if not image_url:
                results[service] = {"error": f"Avatar not found for {username} on {service}"}
                continue

            results[service] = {
                "username": username,
                "service": service,
                "image_url": image_url,
                "cache": cache_metadata,
            }
            continue

        image_data, image_url, error = service_adapter.get_profile_picture(username)

        if error:
            results[service] = {"error": error}
            continue

        if not image_url:
            results[service] = {"error": f"Avatar not found for {username} on {service}"}
            continue

        cache.set(cache_key, {"image_data": image_data, "image_url": image_url}, ttl)

        results[service] = {
            "username": username,
            "service": service,
            "image_url": image_url,
            "cache": {"status": "miss"},
        }

    return jsonify(results)


@app.route("/health")
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with service status
    """
    return jsonify({"status": "ok", "version": "1.0.0"})


@app.route("/stats")
def get_stats():
    """
    Get cache statistics.

    Returns:
        JSON response with cache statistics
    """
    stats = cache.get_stats()

    return jsonify({"cache": {"type": Config.CACHE_TYPE, "stats": stats}})


@app.route("/invalidate-cache/<service>/<username>")
def invalidate_cache(service, username):
    """
    Invalidate cache for a specific service and username.

    Args:
        service (str): The service name (github, twitter, etc.)
        username (str): The username to invalidate cache for

    Returns:
        JSON response with operation status
    """
    service_adapter = get_service(service)
    if not service_adapter:
        return format_error_response(400, f"Unsupported service: {service}")

    is_valid, error_message = validate_username(username, service)
    if not is_valid:
        return format_error_response(400, error_message)

    cache_key = f"{service}:{username}"
    success = cache.delete(cache_key)

    if success:
        return jsonify({"status": "ok", "message": f"Cache invalidated for {service}:{username}"})
    else:
        return format_error_response(404, f"No cache entry found for {service}:{username}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port)
