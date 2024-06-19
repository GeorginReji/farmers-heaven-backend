#! /usr/bin/env python
#
# Author: jyothis@edgebricks.com
# (c) 2023 Edgebricks Inc
"""This module implements OAuth functionality."""

import json
from urllib.parse import unquote

import requests
from flask_oauthlib.client import _encode

import constants.auth as a_econst
from db.extensions import oauth, cfg
from utils.logger import elog


class AuthOAuth:
    """
    Utility class for handling Oauth.
    """

    _google_client = None
    _microsoft_client = None

    @classmethod
    def make_client_google(cls):
        """
        This class method retrieves or creates a Google OAuth client instance

        Returns:
        The Google OAuth client instance (either retrieved or newly created).
        """

        try:
            elog.debug("[auth-oauth]: received make client google request")
            if cls._google_client:
                return cls._google_client

            elog.debug("[auth-oauth]: creating a new google client")
            cls._google_client = oauth.remote_app(
                name=a_econst.AUTH_TYPE_GOOGLE,
                consumer_key=cfg.get_oauth_client_id(idp=a_econst.AUTH_TYPE_GOOGLE),
                consumer_secret=cfg.get_oauth_client_secret(idp=a_econst.AUTH_TYPE_GOOGLE),
                request_token_params={"scope": "email profile"},
                base_url=a_econst.GOOGLE_BASE_URL,
                authorize_url=a_econst.GOOGLE_AUTHORIZE_URL,
                access_token_url=a_econst.GOOGLE_ACCESS_TOKEN_URL,
            )
            elog.debug("[auth-oauth]: successfully created a google client")
            return cls._google_client
        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to generate google client. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @classmethod
    def make_client_microsoft(cls):
        """
        This class method retrieves or creates a Microsoft OAuth client instance

        Returns:
        The Microsoft OAuth client instance (either retrieved or newly created).
        """

        try:
            elog.debug("[auth-oauth]: received make client microsoft request")
            if cls._microsoft_client:
                return cls._microsoft_client

            elog.debug("[auth-oauth]: creating a new microsoft client")
            cls._microsoft_client = oauth.remote_app(
                name=a_econst.AUTH_TYPE_MICROSOFT,
                consumer_key=cfg.get_oauth_client_id(idp=a_econst.AUTH_TYPE_MICROSOFT),
                consumer_secret=cfg.get_oauth_client_secret(idp=a_econst.AUTH_TYPE_MICROSOFT),
                request_token_params={"scope": ["user.read"]},
                base_url=a_econst.MICROSOFT_BASE_URL,
                authorize_url=a_econst.MICROSOFT_AUTHORIZE_URL,
                access_token_url=a_econst.MICROSOFT_TOKEN_ENDPOINT,
            )
            elog.debug("[auth-oauth]: successfully created a microsoft client")
            return cls._microsoft_client

        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to generate microsoft client. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @classmethod
    def make_client(cls, provider):
        """
        This class method retrieves or creates a OAuth client instance

        Returns:
        The OAuth client instance.
        """
        try:
            elog.debug("[auth-oauth]: received make client request with provider:%s", provider)
            if provider == a_econst.AUTH_TYPE_GOOGLE:
                return AuthOAuth.make_client_google()
            if provider == a_econst.AUTH_TYPE_MICROSOFT:
                return AuthOAuth.make_client_microsoft()
            raise ValueError(f"unsupported provider: {provider}")
        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to generate oauth client. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @classmethod
    def make_authorize_url(cls, provider):
        """
        This class method creates a oauth authorize url based on the provider

        Returns:
        The Microsoft OAuth client instance (either retrieved or newly created).
        """
        try:
            elog.debug(
                "[auth-oauth]: received make authorize url request with provider:%s", provider
            )

            # make scope
            o_client = AuthOAuth.make_client(provider)
            scope = dict(o_client.request_token_params).pop("scope")
            scope = _encode(scope, o_client.encoding)

            # make authorize URL
            r_url = o_client.make_client().prepare_request_uri(
                o_client.expand_url(o_client.authorize_url),
                redirect_uri=cfg.get_idp_callback_url(),
                scope=scope,
                state=json.dumps({"provider": provider}),
            )

            elog.info("[auth-oauth]: %s oauth authorize url is %s", provider, r_url)
            return r_url
        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to generate authorize url. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @classmethod
    def oauth_common_response(cls, provider, user_info):
        """
        This class method prepares common response for oauth providers
        """

        if provider == a_econst.AUTH_TYPE_GOOGLE:
            data = {"email": user_info.get("email", None)}
            return data

        if provider == a_econst.AUTH_TYPE_MICROSOFT:
            data = {"email": user_info.get("mail", None)}
            return data

        raise ValueError(f"unsupported provider: {provider}")

    @classmethod
    def validate_code(cls, provider, code):
        """
        This class method validates given provider code

        Returns:
        User details.
        """
        try:
            elog.debug(
                "[auth-oauth]: received validate code request. code:%s provider:%s",
                code,
                provider,
            )
            code = unquote(code)

            config = AuthOAuth.get_client_config(provider)
            data = {
                "code": code,
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "redirect_uri": config["redirect_uri"],
                "grant_type": "authorization_code",
            }

            # validating the token and getting the access token using the
            # code given by the provider
            access_token = AuthOAuth.get_access_token(data, config["token_url"])

            # fetching the user details from the provider
            user_info = AuthOAuth.get_user_info(access_token, config["user_info_url"])

            # making a common response for all the provider
            user_info = AuthOAuth.oauth_common_response(provider, user_info)

            elog.debug("[auth-oauth]: successfully validated code. user_info:%s", user_info)
            return user_info

        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to validate oauth token. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @staticmethod
    def get_client_config(provider):
        """
        This class method returns provider credentials and config

        Returns:
        Config details.
        """

        if provider == a_econst.AUTH_TYPE_GOOGLE:
            return {
                "client_id": cfg.get_oauth_client_id(idp=a_econst.AUTH_TYPE_GOOGLE),
                "client_secret": cfg.get_oauth_client_secret(idp=a_econst.AUTH_TYPE_GOOGLE),
                "redirect_uri": cfg.get_idp_callback_url(),
                "token_url": a_econst.GOOGLE_ACCESS_TOKEN_URL,
                "user_info_url": a_econst.GOOGLE_USER_INFO_URL,
            }

        if provider == a_econst.AUTH_TYPE_MICROSOFT:
            return {
                "client_id": cfg.get_oauth_client_id(idp=a_econst.AUTH_TYPE_MICROSOFT),
                "client_secret": cfg.get_oauth_client_secret(idp=a_econst.AUTH_TYPE_MICROSOFT),
                "redirect_uri": cfg.get_idp_callback_url(),
                "token_url": a_econst.MICROSOFT_TOKEN_ENDPOINT,
                "user_info_url": a_econst.MICROSOFT_USER_INFO_URL,
            }

        raise ValueError(f"unsupported provider: {provider}")

    @staticmethod
    def get_access_token(data, token_url):
        """
        This class method queries token details from the oauth provider
        """

        try:
            elog.info("[auth-oauth]: sending token request to %s with data:%s", token_url, data)
            o_response = requests.post(
                token_url,
                data=data,
                timeout=a_econst.OAUTH_TIMEOUT,
            )
            o_resp_data = o_response.json()
            o_resp_code = o_response.status_code
            elog.debug(
                "[auth-oauth]: received access token response with code:%s, data:%s",
                o_resp_code,
                o_resp_data,
            )
            return o_resp_data.get("access_token")
        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to fetch access token. reason=%s", errMsg)
            raise OAuthError(errMsg) from e

    @staticmethod
    def get_user_info(access_token, user_info_url):
        """
        This class method queries user details from the oauth provider
        """

        try:
            elog.info(
                "[auth-oauth]: sending user info request to %s with token:%s",
                user_info_url,
                access_token,
            )
            o_response = requests.get(
                user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=a_econst.OAUTH_TIMEOUT,
            )
            o_resp_data = o_response.json()
            o_resp_code = o_response.status_code
            elog.debug(
                "[auth-oauth]: received user info response with code:%s, data:%s",
                o_resp_code,
                o_resp_data,
            )
            return o_resp_data
        except Exception as e:
            errMsg = str(e).lower()
            elog.error("[auth-oauth]: failed to fetch user info. reason=%s", errMsg)
            raise OAuthError(errMsg) from e


class OAuthError(Exception):
    """
    Class returning OAuth error
    """

    def __init__(self, reason):
        self.message = f"oauth failed. reason={reason}"
        super().__init__(self.message)
