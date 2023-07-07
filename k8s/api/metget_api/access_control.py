#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################
from metbuild.database import Database

CREDIT_MULTIPLIER = 100000.0


class AccessControl:
    """
    This class is used to check if the user is authorized to use the API
    """

    def __init__(self):
        pass

    @staticmethod
    def hash_access_token(token: str) -> str:
        """
        This method is used to hash the access token before comparison
        """
        from hashlib import sha256

        return sha256(token.encode()).hexdigest()

    @staticmethod
    def is_authorized(api_key: str) -> bool:
        """
        This method is used to check if the user is authorized to use the API
        The method returns True if the user is authorized and False if not
        Keys are hashed before being compared to the database to prevent
        accidental exposure of the keys and/or sql injection
        """
        from metbuild.tables import AuthTable
        from datetime import datetime

        api_key_hash = AccessControl.hash_access_token(str(api_key))
        with Database() as db, db.session() as session:
            api_key_db = (
                session.query(
                    AuthTable.id,
                    AuthTable.key,
                )
                .filter(AuthTable.key == api_key)
                .filter(AuthTable.enabled == True)
                .filter(AuthTable.expiration >= datetime.utcnow())
                .first()
            )

        if api_key_db is None:
            return False

        api_key_db_hash = AccessControl.hash_access_token(api_key_db.key.strip())

        if api_key_db_hash != api_key_hash:
            return False
        else:
            return True

    @staticmethod
    def check_authorization_token(headers) -> bool:
        """
        This method is used to check if the user is authorized to use the API
        The method returns True if the user is authorized and False if not
        """
        user_token = headers.get("x-api-key")
        gatekeeper = AccessControl()
        if gatekeeper.is_authorized(user_token):
            return True
        else:
            return False

    @staticmethod
    def unauthorized_response():
        status = 401
        return {
            "statusCode": status,
            "body": {"message": "ERROR: Unauthorized"},
        }, status

    @staticmethod
    def get_credit_balance(api_key: str) -> dict:
        """
        This method is used to get the credit balance for the user

        Args:
            api_key (str): The API key used to authenticate the request

        Returns:
            dict: A dictionary containing the credit limit, credits used, and credit balance
        """
        from metbuild.tables import RequestTable
        from metbuild.tables import AuthTable
        from metbuild.database import Database
        from datetime import datetime, timedelta
        from sqlalchemy import func, or_

        with Database() as db, db.session() as session:
            # ...Queries the database for the credit limit for the user
            credit_limit = (
                session.query(AuthTable.credit_limit).filter_by(key=api_key).first()[0]
            )
            credit_limit = float(credit_limit) / CREDIT_MULTIPLIER

            # ...Queries the database for the credit used for the user over the last 30 days
            start_date = datetime.utcnow() - timedelta(days=30)
            credit_used = (
                session.query(func.sum(RequestTable.credit_usage))
                .filter(RequestTable.last_date >= start_date)
                .filter(RequestTable.api_key == api_key)
                .filter(
                    or_(
                        RequestTable.status == "completed",
                        RequestTable.status == "running",
                    )
                )
                .first()[0]
            )

        if credit_used is None:
            credit_used = 0.0
        else:
            credit_used = float(credit_used) / CREDIT_MULTIPLIER

        credit_balance = credit_limit - credit_used

        return {
            "credit_limit": credit_limit,
            "credits_used": credit_used,
            "credit_balance": credit_balance,
        }
