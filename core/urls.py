from core.views import *
from django.urls import path,include
from .views import set_password_page
from .views import save_password, check_password_status

app_name = 'core'

urlpatterns = [
    path('', Index, name='index'),
    path('set/', SaveData, name='set-data'),
    path('assign/<slug:slug>/', AssignTag, name='assign-data'),
    path('view/<slug:slug>/', ViewData, name='view-data'),
    path('set/<slug:slug>/', SetAssignedFlag.as_view(), name='set-flag'),
    path('output/<slug:slug>/', OutputData, name='output-data'),
    path('writeNfc/', WriteNfc, name='write-nfc'),
    path('setpasswordnfc/', set_password_page, name='set_password_page'),
    path("savepasswordnfc/", save_password, name="save_password"),
    path("checkpasswordstatus/", check_password_status, name="check_password_status"),
]