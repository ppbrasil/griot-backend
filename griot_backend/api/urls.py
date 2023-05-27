from django.urls import path
from . import views

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='create_user'),
    path('user/auth/', views.AuthenticateUserView.as_view(), name='authenticate_user'),
    path('user/logout/', views.LogoutView.as_view(), name='logout_user'),
    path('profile/update/<int:pk>/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('account/create/', views.CreateAccountView.as_view(), name='create_account'),
    path('account/update/<int:pk>/', views.UpdateAccountView.as_view(), name='update_account'),
    path('account/add-beloved-one/<int:pk>/<int:beloved_one_id>/', views.AddBelovedOneToAccountView.as_view(), name='add_beloved_one'),
    path('account/remove-beloved-one/<int:pk>/<int:beloved_one_id>/', views.RemoveBelovedOneFromAccountView.as_view(), name='remove_beloved_one'),
]


