import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from myhouse_admin.forms.forms import MeterReadingForm
from myhouse_admin.models import Message
from myhouse_admin.utils import db_utils
from myhouse_admin.utils.utils import permission_required, PermissionRequiredMixin


logger = logging.getLogger(__name__)


class MessageListView(PermissionRequiredMixin, ListView):
    model = Message
    template_name = 'messages/message_list.html'
    permission_required = '8'