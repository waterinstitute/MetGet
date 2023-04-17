#!/usr/bin/env python3

from flask import Flask, redirect, jsonify, request
import logging
from metget_api.access_control import AccessControl

application = Flask(__name__)


def check_authorization_token(headers) -> bool:
    user_token = headers.get("x-api-key")
    gatekeeper = AccessControl()
    if gatekeeper.is_authorized(user_token):
        return True
    else:
        return False


@application.route("/")
def index():
    """
    When the user hits the root path, redirect them to the MetGet homepage
    """
    return redirect(location="http://metget.org", code=302)


@application.route("/status")
def metget_status():
    authorized = check_authorization_token(request.headers)
    if authorized:
        return metget_return_status()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@application.route("/build", methods=["POST"])
def metget_build():
    authorized = check_authorization_token(request.headers)
    if authorized:
        return metget_generate_build(request)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


def metget_return_status():
    return jsonify({"message": "Success"}), 200


def metget_generate_build(request_data):
    import uuid
    #import pika
    from metget_api.request import Request, RequestEnum

    request_uuid = str(uuid.uuid4())
    request_api_key = request_data.headers.get("x-api-key")
    request_source_ip = request_data.remote_addr
    request_json = request_data.get_json()

    request_json["source-ip"] = request_source_ip

    request_obj = Request()
    request_obj.add_request(
        request_uuid,
        RequestEnum.queued,
        0,
        request_api_key,
        request_source_ip,
        request_json,
    )

    return jsonify({"message": "Success", "request-id": request_uuid})
