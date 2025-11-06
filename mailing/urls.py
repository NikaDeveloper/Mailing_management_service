from django.urls import path

from . import views
from .views import (HomePageView, MailingAttemptListView, MailingCreateView,
                    MailingDeleteView, MailingDetailView, MailingListView,
                    MailingUpdateView, MessageCreateView, MessageDeleteView,
                    MessageDetailView, MessageListView, MessageUpdateView,
                    RecipientCreateView, RecipientDeleteView,
                    RecipientDetailView, RecipientListView,
                    RecipientUpdateView)

app_name = "mailing"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/send/", views.manual_send, name="manual_send"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("recipient/", RecipientListView.as_view(), name="recipient_list"),
    path("recipient/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipient/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipient/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("reports/", MailingAttemptListView.as_view(), name="attempt_list"),
]
