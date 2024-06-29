import io
import re
import boto3
import zipfile
import logging
import random, string

from django.conf import settings
from botocore.exceptions import ClientError
from decouple import config


def delete_child(parent_id, model_class):
    children = []
    if model_class.objects.filter(parent=parent_id, is_active=True).exists():
        query = model_class.objects.filter(parent=parent_id)
        for one in query:
            children.append(one.pk)
            delete_child(one.pk, model_class)
            one.is_active = False
            one.save()
        return children
    else:
        return children


def dropdown_tree(settings_list, serializer_class, model_class, parent_id=None, path=""):
    separator = "$#$"
    if len(settings_list) == 0:
        return []
    else:
        data = []
        for i in range(len(settings_list)):
            child = {
                **settings_list[i],
                'parent': parent_id,
                'path': path + separator + settings_list[i]['title'] if path else settings_list[i]['title'],
                'value': settings_list[i]['title'] + "-" + str(parent_id) if 'title' in settings_list[i] else ""
            }
            if len(child['children']) > 0:
                children = child['children']
                child['children'] = []
                queryset = model_class.objects.filter(name=child['title'], is_active=True)
                if parent_id:
                    queryset = queryset.filter(parent=parent_id)
                for item in queryset:
                    item_path = path + separator + child['path'] + separator + item.value if path else \
                        child['path'] + separator + item.value
                    child['children'].append({
                        'id': item.id,
                        'title': item.value,
                        'value': item.value + "-" + str(parent_id),
                        'path': item_path.split(separator),
                        'disabled': True,
                        'children': dropdown_tree(children, serializer_class, model_class, item.id, item_path)
                    })
            child['path'] = child['path'].split(separator)
            data.append(child)
        data.sort(key=lambda x: x.get('title'))
        return data


def generate_password():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def remove_special_characters(sting):
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, '', sting)


def generate_username(first_name=None, middle_name=None, last_name=None):
    first_name = first_name.replace(" ", "").replace(".", "") if first_name else first_name
    middle_name = middle_name.replace(" ", "").replace(".", "") if middle_name else middle_name
    last_name = last_name.replace(" ", "").replace(".", "") if last_name else last_name
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    if first_name:
        first_name = remove_special_characters(first_name)
        if len(first_name) > 4:
            return first_name[0:4].upper() + random_string
        if middle_name:
            middle_name = first_name + remove_special_characters(middle_name)
            if len(middle_name) > 4:
                return middle_name[0:4].upper() + random_string
        else:
            middle_name = ''
        if last_name:
            last_name = first_name + middle_name + remove_special_characters(last_name)
            if len(last_name) > 4:
                return last_name[0:4].upper() + random_string
        return first_name.upper() + random_string
    return None


def create_presigned_url(object_name, file_type):
    s3_client = boto3.client('s3', settings.AWS_S3_REGION_NAME,
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    try:
        response = s3_client.generate_presigned_url('put_object', Params={
            'Bucket': settings.AWS_STORAGE_TEMP_BUCKET_NAME,
            'Key': object_name,
            'ContentType': file_type})
    except ClientError as e:
        logging.error(e)
        return None
    return response


def s3_upload_file_from_local(file_path, destination):
    import mimetypes

    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Default MIME type if unable to guess
            mime_type = 'application/octet-stream'

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        file_name = file_path.split('/')[-1]
        s3_client.upload_file(Filename=file_path, Bucket=settings.AWS_STORAGE_TEMP_BUCKET_NAME,
                              Key=destination,
                              ExtraArgs={
                                  'ContentType': mime_type,
                                  'ContentDisposition': f'inline; filename="{file_name}"'
                              })
        return True
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False


def create_update_s3_record(from_path=None, to_path=None, path='common', is_onboard=False):
    buket_name = settings.AWS_STORAGE_ONBOARD_BUCKET_NAME if is_onboard else settings.AWS_STORAGE_BUCKET_NAME
    s3_client = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    s3 = s3_client.resource('s3')
    if from_path == to_path:
        return None, from_path
    if from_path:
        try:
            s3.Object(buket_name, from_path).delete()
        except:
            pass
    if to_path:
        try:
            copy_source = {'Bucket': settings.AWS_STORAGE_TEMP_BUCKET_NAME, 'Key': 'temp/' + to_path}
            target_bucket = s3.Bucket(buket_name)
            file_name = to_path.split('/')[-1]
            destination_path = '{path}{image}'.format(path=path, image=file_name)
            target_bucket.copy(copy_source, destination_path)
            file_path = destination_path
            s3.Object(settings.AWS_STORAGE_TEMP_BUCKET_NAME, 'temp/' + to_path).delete()
            size_response = s3.Object(buket_name, destination_path)
            file_size = size_response.content_length
            return file_size, file_path
        except Exception as e:
            print(e)
            pass
        return None, to_path
    return None, None


def s3_move_files(from_path, to_path):
    s3_client = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    s3 = s3_client.client('s3')
    source_bucket = settings.AWS_STORAGE_BUCKET_NAME
    # List objects with the specified prefix
    source_objects = s3.list_objects_v2(Bucket=source_bucket, Prefix=from_path)
    for obj in source_objects.get('Contents', []):
        source_key = obj['Key']
        target_key = source_key.replace(from_path, to_path, 1)  # Replace the prefix
        # Copy each object to the new destination
        s3.copy_object(
            CopySource={'Bucket': source_bucket, 'Key': source_key},
            Bucket=source_bucket,
            Key=target_key
        )
        # Delete the original object
        s3.delete_object(Bucket=source_bucket, Key=source_key)
    return None


def create_update_s3_directory(from_path=None, to_path=None, is_temp=False, path='common'):
    s3_client = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    s3 = s3_client.resource('s3')
    bucket_name = settings.AWS_STORAGE_TEMP_BUCKET_NAME if is_temp else settings.AWS_STORAGE_BUCKET_NAME
    if from_path:
        try:
            bucket = s3.Bucket(bucket_name)
            bucket.objects.filter(Prefix=from_path).delete()
        except:
            pass
    if to_path:
        try:
            final_path = path + to_path + "/"
            s3.Bucket(bucket_name).put_object(Key=(final_path))
            return final_path
        except:
            pass
    return None


def get_presigned_url(object_name, expiration=config('PRESIGNED_EXPIRY_SECONDS', cast=int)):
    s3_client = boto3.client('s3', settings.AWS_S3_REGION_NAME,
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    try:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        response = s3_client.generate_presigned_url('get_object', ExpiresIn=expiration,
                                                    Params={'Bucket': bucket_name, 'Key': object_name})
    except ClientError as e:
        logging.error(e)
        return None
    # print(response)
    response = response.split('.com/') if response else None
    return response[1] if response else ""


def check_s3_file_exists(object_name, is_onboard=False):
    s3_client = boto3.client('s3', settings.AWS_S3_REGION_NAME,
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    bucket_name = settings.AWS_STORAGE_ONBOARD_BUCKET_NAME if is_onboard else settings.AWS_STORAGE_BUCKET_NAME
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        return True
    except Exception as e:
        # The object does not exist or other error
        print(e)
    return False


def order_folder_path(organization, customer):
    if organization and customer:
        return "ORGANIZATION_" + str(organization) + '/CUSTOMER_' + str(customer) + "/"
    raise ValueError('invalid order_folder_path')


def order_path(data):
    organization = data.get('organization', None)
    customer = data.get('customer', None)
    order = data.get('order', None)
    temp_order = data.get('temp_order', None)
    if organization and customer and order:
        return "ORGANIZATION_" + str(organization.id) + '/CUSTOMER_' + str(customer.id) + '/ORDER_' + str(
            order.id) + '/'
    elif organization and customer and temp_order:
        return "ORGANIZATION_" + str(organization.id) + '/CUSTOMER_' + str(customer.id) + '/TEMP_ORDER_' + str(
            temp_order.id) + '/'
    raise ValueError('invalid order_path')


def temp_order_path(data):
    organization = data.get('organization', None)
    customer = data.get('customer', None)
    temp_order = data.get('temp_order', None)
    if organization and customer and temp_order:
        return "ORGANIZATION_" + str(organization.id) + '/CUSTOMER_' + str(customer.id) + '/TEMP_ORDER_' + str(
            temp_order.id) + '/'
    raise ValueError('invalid temp_order_path')


def partner_kyc_path():
    return "kyc_documents/"


def onboard_path():
    return "on-boarding/"


def organization_logo_path():
    return "organization_logos/"


def chat_group_path(group_obj):
    return "CHAT_GROUP/CHAT_" + str(group_obj.id) + "/"


def employee_photo_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'partner_photos/'
    raise ValueError('invalid employee_photo_path')


def customer_photo_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'customer_photos/'
    raise ValueError('invalid customer_photo_path')


def customer_invoice_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'invoices/'
    raise ValueError('invalid customer_invoice_path')


def customer_proforma_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'proforma/'
    raise ValueError('invalid customer_proforma_path')


def customer_ledger_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'ledger/'
    raise ValueError('invalid customer_ledger_path')


def customer_payment_path(organization_id):
    if organization_id:
        return "ORGANIZATION_" + str(organization_id) + '/' + 'payment/'
    raise ValueError('invalid customer_payment_path')


def order_final_document_path(order_obj):
    return "ORGANIZATION_" + str(order_obj.organization.id) + '/CUSTOMER_' + str(
        order_obj.customer.id) + '/ORDER_' + str(order_obj.id) + '/final_documents/'


def support_path():
    return "SUPPORT/"


def ticket_path():
    return "TICKET_MEDIA/"


def qr_code_path():
    return "QR_CODES/"


def zip_s3_folder(file_name, file_path, zip_path='downloads/'):
    s3_client = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    s3 = s3_client.client('s3')
    buffer = io.BytesIO()
    try:
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            infile_object = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=file_path)['Contents']
            for file_path in infile_object:
                response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path['Key'])
                file_content = response['Body'].read()
                zip_file.writestr(file_path['Key'].split('/')[-1], file_content)
        buffer.seek(0)
        s3.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME, zip_path + file_name)
        return get_presigned_url(zip_path + file_name)
    except Exception as e:
        print(e)
        return None


def s3_copy_record(source=None, folder_path='temp/ORDER/'):
    s3_client = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, )
    s3 = s3_client.resource('s3')
    try:
        copy_source = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': source}
        target_bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        file_name = source.split('/')[-1]
        destination_path = '{path}{image}'.format(path=folder_path, image=file_name)
        target_bucket.copy(copy_source, destination_path)
    except:
        pass
