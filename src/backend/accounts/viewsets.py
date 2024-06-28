import logging
from urllib.parse import urlencode
from datetime import datetime, date, timedelta
from functools import partial

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action

from .oauth import AuthOAuth
from .filters import UserBasicFilter
from .models import PasswordResetCode, OTPLogin, User
from .permissions import UserPermissions
from .serializers import UserSerializer, PasswordResetSerializer, UserBasicDataSerializer, UserRegistrationSerializer, \
    UserRegisterSerializer
from .services import auth_login, auth_password_change, _parse_data, \
    get_user_from_email_or_mobile_or_employee_code, generate_auth_data, user_clone_api

from ..base import response
from ..base.api.pagination import StandardResultsSetPagination
from ..base.api.viewsets import ModelViewSet
from ..base.serializers import SawaggerResponseSerializer
from ..base.services import create_update_record
from ..base.utils.sms import send_sms_without_save

logger = logging.getLogger(__name__)

parse_password_reset_data = partial(_parse_data, cls=PasswordResetSerializer)


class UserViewSet(ModelViewSet):
    """
    Here we have user login, logout, endpoints.
    """
    queryset = get_user_model().objects.all()
    permission_classes = (UserPermissions,)
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = None

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset

    @swagger_auto_schema(
        method="post",
        operation_summary='Login',
        operation_description='Post login credential to log in and get a login session token.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        responses={
            307: SawaggerResponseSerializer(partial=True)
        }
    )
    @action(detail=False, methods=['POST'])
    def oauth_start(self, request):
        authorize_url = AuthOAuth.make_authorize_url()
        return redirect(authorize_url)

    @swagger_auto_schema(
        method="get",
        operation_summary='OAuth Callback',
        operation_description='Handle the OAuth callback from Google.',
        manual_parameters=[
            openapi.Parameter('code', openapi.IN_QUERY, description="code for verifying the oauth login",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('state', openapi.IN_QUERY, description="state containing provider information",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            302: 'Redirect with token',
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error',
        }
    )
    @action(detail=False, methods=['GET'], url_path='oauth-callback')
    def oauth_callback(self, request):
        code = request.GET.get("code")
        if not code or code.strip() == "":
            return self.prepare_response(status_code=status.HTTP_400_BAD_REQUEST,
                                         error_msg="missing or empty authorization code")

        user_info = AuthOAuth.validate_code(code)
        email = user_info.get('email')
        user_obj = User.objects.filter(email=email, is_active=True).first()
        if not user_obj:
            user_obj = User.objects.create(email=email)

        header_data = generate_auth_data(request, user_obj)
        header_data["id"] = user_obj.id
        header_data["email_id"] = user_obj.email
        return self.prepare_response(status_code=status.HTTP_200_OK, params_data=header_data)

    @staticmethod
    def prepare_response(status_code, error_msg=None, params_data=None):
        frontend_url = settings.FRONTEND_CALLBACK_URL  # Make sure to set this in your Django settings

        # Initialize query parameters with status_code
        query_params = {'status_code': status_code}

        # Add error_msg to query parameters if provided
        if error_msg:
            query_params['error'] = error_msg

        # Add additional parameters from params_data if provided
        if params_data:
            query_params.update(params_data)

        # Create the query string from query_params
        query_string = urlencode(query_params)

        # Append the query string to the frontend URL
        redirect_url = f"{frontend_url}?{query_string}"

        # Create the HttpResponseRedirect with the modified URL
        response = HttpResponseRedirect(redirect_url)

        return response

    @action(methods=['GET'], detail=False)
    def user_clone(self, request):
        if not request.user.is_authenticated:
            content = {'detail': 'user is not authenticated'}
            return response.Unauthorized(content)
        if request.user.is_separated:
            content = {'detail': 'user is separated from the system'}
            return response.Unauthorized(content)
        return response.Ok(user_clone_api(request.user))

    @swagger_auto_schema(
        method="post",
        operation_summary='Change Password',
        operation_description='Post old and new password while logged in session.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description=""),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description=""),
            }),
        responses={
            200: SawaggerResponseSerializer(data={'message': 'Password changed Successfully.'}, partial=True)
        }
    )
    @action(detail=False, methods=['POST'])
    def password_change(self, request):
        data = auth_password_change(request)
        user, new_password = request.user, data.get('new_password')
        if new_password:
            if len(new_password) < 6:
                return response.BadRequest({"detail": "Password too short."})
        if user.check_password(data.get('old_password')):
            user.set_password(new_password)
            user.save()
            content = {'success': 'Password changed successfully.'}
            return response.Ok(content)
        else:
            content = {'detail': 'Old password is incorrect.'}
            return response.BadRequest(content)

    @swagger_auto_schema(
        method="post",
        operation_summary='Send Password Reset Mail',
        operation_description='Post username to get a code on mail to make new password using reset_password API. '
                              'Used in case of forget password',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="mobile/email/employee_code"),
            }),
        responses={
            200: SawaggerResponseSerializer(data={'message': 'Password changed Successfully.'}, partial=True)
        }
    )
    @action(detail=False, methods=['POST'])
    def user_reset_mail(self, request):
        data = parse_password_reset_data(request.data)
        username = data.get('username')
        domain = None
        user, email_user, mobile_user, username_user = get_user_from_email_or_mobile_or_employee_code(username)
        if not email_user and not mobile_user and not username_user:
            return response.BadRequest({'detail': 'User does not exists.'})
        if user:
            try:
                email = user.email
                password_reset_code = PasswordResetCode.objects.create_reset_code(user)
                password_reset_code.send_password_reset_email(domain)
                message = "We have sent a password reset link to the {}. Use that link to set your new password".format(
                    email)
                return response.Ok({"detail": message})
            except get_user_model().DoesNotExist:
                message = "Email '{}' is not registered with us. Please provide a valid email id".format(email)
                message_dict = {'detail': message}
                return response.BadRequest(message_dict)
            except Exception:
                message = "Unable to send password reset link to email-id- {}".format(email)
                message_dict = {'detail': message}
                logger.exception(message)
                return response.BadRequest(message_dict)
        else:
            message = {'detail': 'User for this staff does not exist'}
            return response.BadRequest(message)

    @swagger_auto_schema(
        method="post",
        operation_summary='Reset Password',
        operation_description='Use the code got in mail by using reset_password_mail API to make new password',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="code received on mail"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description=""),
            }),
        responses={
            200: SawaggerResponseSerializer(data={'message': 'Password changed Successfully.'}, partial=True)
        }
    )
    @action(detail=False, methods=['POST'])
    def reset_password(self, request):
        code = request.data.get('code')
        password = request.data.get('password')
        if code:
            try:
                password_reset_code = PasswordResetCode.objects.get(code=code.encode('utf8'))
                uid = force_str(urlsafe_base64_decode(password_reset_code.uid))
                password_reset_code.user = get_user_model().objects.get(id=uid)
            except:
                message = 'Unable to verify user.'
                message_dict = {'detail': message}
                return response.BadRequest(message_dict)
            # verify signature with the help of timestamp and previous password for one secret urls of password reset.
            else:
                signer = signing.TimestampSigner()
                max_age = settings.PASSWORD_RESET_TIME
                l = (password_reset_code.user.password, password_reset_code.timestamp, password_reset_code.signature)
                try:
                    signer.unsign(':'.join(l), max_age=max_age)
                except (signing.BadSignature, signing.SignatureExpired):
                    logger.info('Session Expired')
                    message = 'Password reset link expired. Please re-generate password reset link. '
                    message_dict = {'detail': message}
                    return response.BadRequest(message_dict)
            password_reset_code.user.set_password(password)
            password_reset_code.user.save()
            message = "Password Created successfully"
            message_dict = {'detail': message}
            return response.Ok({"success": message_dict})
        else:
            message = {'detail': 'Password reset link expired. Please re-generate password reset link. '}
            return response.BadRequest(message)

    @action(detail=False, methods=['POST'])
    def resend_otp(self, request):
        import datetime
        mobile = request.data.get("mobile")
        user_model = get_user_model()
        user = user_model.objects.filter(is_active=True, mobile=mobile).first()
        if user:
            timestamp = datetime.datetime.now() - datetime.timedelta(minutes=15)
            login_obj = OTPLogin.objects.filter(mobile=mobile, is_active=True, modified_at__gte=timestamp,
                                                resend_counter__gt=0).first()
            if login_obj:
                send_sms_without_save(mobile, "Your OTP for My Fitnezz Login is " + str(
                    login_obj.otp) + ". It is valid for next 10 minutes.")
                login_obj.resend_counter = login_obj.resend_counter - 1
                login_obj.save()
                return response.Ok({"detail": "OTP resent successfully"})
            else:
                return response.BadRequest(
                    {"detail": "Maximum retries have been exceeded. Please retry after 15 minutes."})
        else:
            return response.BadRequest({"detail": "No User exists with mobile no: " + str(mobile)})

    @action(detail=False, methods=['POST'])
    def send_otp(self, request):
        mobile = request.data.get("mobile")
        user_model = get_user_model()
        user = user_model.objects.filter(is_active=True, mobile=mobile).first()
        if user:
            otp = self.get_random_number(6)
            OTPLogin.objects.filter(mobile=mobile, modified_at__lt=date.today(), is_active=True).delete()
            login_obj = OTPLogin.objects.filter(mobile=mobile, is_active=True, modified_at__gte=date.today()).first()
            if login_obj:
                counter = login_obj.counter - 1
                if counter > 0:
                    OTPLogin.objects.filter(mobile=mobile, is_active=True, modified_at__gte=date.today()).update(
                        otp=otp, is_active=True, counter=counter, resend_counter=25, modified_at=datetime.now())
            else:
                counter = 25
                OTPLogin.objects.create(mobile=mobile, otp=otp)
            if counter > 0:
                send_sms_without_save(mobile, "Your OTP for My Fitnezz Login is " + str(
                    otp) + ". It is valid for next 10 minutes.")
                return response.Ok({"detail": "OTP sent successfully"})
            else:
                return response.BadRequest(
                    {"detail": "Max tries for OTP exceeded. Kindly try again tommorow or login with password"})
        else:
            return response.BadRequest({"detail": "No User exists with mobile no: " + str(mobile)})

    @action(detail=False, methods=['POST'])
    def verify_otp(self, request):
        mobile = request.data.get("mobile")
        otp = request.data.get("otp")
        user_model = get_user_model()
        user = user_model.objects.filter(is_active=True, mobile=mobile).first()
        if user:
            timestamp = datetime.now() - timedelta(minutes=15)
            login_obj = OTPLogin.objects.filter(mobile=mobile, otp=otp, is_active=True,
                                                modified_at__gte=timestamp).first()
            if login_obj:
                login_obj.is_active = False
                login_obj.save()
                auth_data = generate_auth_data(request, user)
                return response.Ok(auth_data)
            else:
                return response.BadRequest({"detail": "Invalid OTP used. Please Check!!"})
        else:
            return response.BadRequest({"detail": "No Such User with mobile no: " + str(mobile) + " exists."})
