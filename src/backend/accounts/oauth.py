import json
from urllib.parse import unquote

import requests
from .constants import GOOGLE_AUTHORIZE_URL, GOOGLE_ACCESS_TOKEN_URL, GOOGLE_USER_INFO_URL
from django.conf import settings
from django.urls import reverse


class AuthOAuth:
    """
    Utility class for handling Google OAuth.
    """

    @classmethod
    def make_authorize_url(cls):
        """
        This class method creates a Google OAuth authorize URL.

        Returns:
        The Google OAuth authorize URL.
        """
        try:
            scope = "email profile"
            redirect_uri = settings.FRONTEND_CALLBACK_URL
            authorize_url = (
                f"{GOOGLE_AUTHORIZE_URL}"
                f"?client_id={settings.GOOGLE_CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={redirect_uri}"
                f"&scope={scope}"
                f"&state={json.dumps({'provider': 'google'})}"
            )
            return authorize_url
        except Exception as e:
            raise OAuthError(str(e).lower()) from e

    @classmethod
    def validate_code(cls, code):
        """
        This class method validates the given Google OAuth code.

        Returns:
        User details.
        """
        try:
            code = unquote(code)

            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.FRONTEND_CALLBACK_URL,
                "grant_type": "authorization_code",
            }

            access_token = cls.get_access_token(data, GOOGLE_ACCESS_TOKEN_URL)
            user_info = cls.get_user_info(access_token, GOOGLE_USER_INFO_URL)
            return True, {"email": user_info.get("email", None), "name": user_info.get("name", "")}
        except Exception as e:
            print(e)
            return False, "invalid request"

    @staticmethod
    def get_access_token(data, token_url):
        """
        This method queries token details from Google OAuth provider.
        """
        try:
            response = requests.post(token_url, data=data, timeout=10)
            response_data = response.json()
            return response_data.get("access_token")
        except Exception as e:
            raise OAuthError(str(e).lower()) from e

    @staticmethod
    def get_user_info(access_token, user_info_url):
        """
        This method queries user details from Google OAuth provider.
        """
        try:
            response = requests.get(
                user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            raise OAuthError(str(e).lower()) from e


class OAuthError(Exception):
    """
    Class returning OAuth error
    """

    def __init__(self, reason):
        self.message = f"oauth failed. reason={reason}"
        super().__init__(self.message)
