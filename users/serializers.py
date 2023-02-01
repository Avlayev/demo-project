from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from demo_project.utility import check_email_or_phone
from shared.utils import phone_parser, send_phone_notification, send_email
from .models import User, VIA_EMAIL, VIA_PHONE

class SignUpSerializer(serializers.Serializer):
    guid = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'guid', 'auth_type', 'auth_status'
        )

        extra_kwargs = {
            'auth_type':{'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(user.auth_type)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(user.auth_type)
            send_phone_notification(user.email, code)
        user.save()
        return user

    def validate(self, attrs):
        super(SignUpSerializer, self).validate(attrs)
        data = self.auth_validator(attrs)
        return data


    @staticmethod
    def auth_validator(attrs):
        user_input = str(attrs.get('email_phone_number'))
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email': attrs.get('email_phone_number'),
                'auth_type': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': attrs.get('email_phone_number'),
                'auth_type': VIA_PHONE,
            }

        elif input_type is None:
            data = {
                'success': False,
                'message':"Email yoki telefon raqamingiz noto'g'ri"
            }
            raise ValidationError(data)

        else:
            data = {
                'success': False,
                'message': 'Must send email or number'
            }
            raise ValidationError(data)
        return data

    def validate_email_phone_number(self, value):
        value = value.lower()

        if value and User.objects.filter(email=value).exist():
            data = {
                'success': False,
                'message': 'This phone email is already being used'
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exist():
            data = {
                'success': False,
                'message': 'This phone number is already being used'
            }
            raise ValidationError(data)
        elif check_email_or_phone(value) == "phone":
            phone_parser(value, self.initial_data.get('country_code'))
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.tokens())
        return data

