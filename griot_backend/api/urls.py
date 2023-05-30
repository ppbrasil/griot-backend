from django.urls import path
from . import views

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='create_user'),
    path('user/auth/', views.AuthenticateUserView.as_view(), name='authenticate_user'),
    path('user/logout/', views.LogoutView.as_view(), name='logout_user'),
    path('user/list-accounts/', views.ListUserAccountsViews.as_view(), name='list_accounts'),
    path('profile/update/<int:pk>/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('account/create/', views.CreateAccountView.as_view(), name='create_account'),
    path('account/update/<int:pk>/', views.UpdateAccountView.as_view(), name='update_account'),
    path('account/delete/<int:pk>/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('account/add-beloved-one/<int:pk>/<int:beloved_one_id>/', views.AddBelovedOneToAccountView.as_view(), name='add_beloved_one'),
    path('account/remove-beloved-one/<int:pk>/<int:beloved_one_id>/', views.RemoveBelovedOneFromAccountView.as_view(), name='remove_beloved_one'),
    path('account/list-beloved-ones/<int:pk>/', views.ListBelovedOneFromAccountView.as_view(), name='list_beloved_ones'),
    path('character/create/', views.CreateCharacterView.as_view(), name='create_character'),
    path('character/update/<int:pk>/', views.UpdateCharacterView.as_view(), name='update_character'),
    path('character/delete/<int:pk>/', views.DeleteCharacterView.as_view(), name='delete_character'),
    path('memory/create/', views.CreateMemoryView.as_view(), name='create_memory'),
    path('memory/retrieve/<int:pk>/', views.RetrieveMemoryView.as_view(), name='retrieve_memory'),
    path('memory/update/<int:pk>/', views.UpdateMemoryView.as_view(), name='update_memory'),
    path('memory/list/', views.ListMemoriesView.as_view(), name='list_memories'),
    path('memory/delete/<int:pk>/', views.DeleteMemoryView.as_view(), name='delete_memory'),
    path('memory/video/upload/', views.CreateVideoMemoryView.as_view(), name='upload_memory_video'),
    path('memory/video/retrieve/<int:pk>/', views.RetrieveVideoMemoryView.as_view(), name='retrieve_memory_video'),
    path('memory/add_character/<int:pk>/', views.AddCharacterToMemoryView.as_view(), name='add_character_to_memory'),
    path('memory/remove_character/<int:pk>/', views.RemoveCharacterToMemoryView.as_view(), name='remove_character_from_memory'),
]

