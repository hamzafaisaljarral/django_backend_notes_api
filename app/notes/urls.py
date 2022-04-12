from django.urls import path
from . import views
from . import urls_name
from . import registration_views


urlpatterns = [
    path(r'',
         views.ListNotes.as_view(),
         name=urls_name.NOTES_LIST_NAME),

    path(r'admin/notes/',
         views.CreateAdminNotes.as_view(),
         name=urls_name.ME_NOTES),

    path('delete/<int:pk>',
         views.DestroyAPIView.as_view(),
         name=urls_name.NOTES_DELETE),

    path('update/<int:pk>',
         views.UpdateAPIView.as_view(),
         name=urls_name.NOTES_UPDATE),

    path('notes/filter/',
         views.FilterAPIView.as_view(),
         name=urls_name.FILTER_TAGS),

    path('users/(?P<pk>\d+)/',
         views.DetailUser.as_view(),
         name=urls_name.USER_DETAIL_NAME),

    path('users/',
         views.ListUser.as_view(),
         name=urls_name.USER_LIST_NAME),

    path('users/auth/login/',
         registration_views.UserAuthenticationView.as_view(),
         name=urls_name.LOGIN_NAME),

    path('users/auth/logout/',
         registration_views.LogoutView.as_view(),
         name=urls_name.LOGOUT_NAME),

    path('users/auth/register/',
         registration_views.UserRegistrationView.as_view(),
         name=urls_name.REGISTER_NAME),
]
