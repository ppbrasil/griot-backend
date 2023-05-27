from django.urls import path
from . import views

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='create_user'),
    path('user/auth/', views.AuthenticateUserView.as_view(), name='authenticate_user'),
    path('user/logout/', views.LogoutView.as_view(), name='logout_user'),
    path('profile/update/<int:pk>/', views.UpdateProfileView.as_view(), name='update_profile'),
]


