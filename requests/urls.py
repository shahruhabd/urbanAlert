from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomLoginForm
from .views import *

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html', 
        authentication_form=CustomLoginForm), 
        name='login'),
    path('profile/', profile_view, name='profile'),
    path('', dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('application/<int:pk>/', application_detail, name='application_detail'),
    path('categories/create/', create_or_edit_category, name='create_category'),
    path('categories/edit/<int:category_id>/', create_or_edit_category, name='edit_category'),
    path('application-status/<int:application_id>/', application_status, name='application_status'),
]
