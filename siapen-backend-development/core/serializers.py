import re
from core.models import BaseModel
from django.forms.models import model_to_dict
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from .models import Log


class LogSerializer(FlexFieldsModelSerializer):
    status_code_nome = SerializerMethodField()
    method_nome = SerializerMethodField()

    class Meta:
        model = Log
        fields = "__all__"

    def get_status_code_nome(self, obj):
        return obj.get_status_code_display()

    def get_method_nome(self, obj):
        return obj.get_method_display()
