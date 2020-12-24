from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard),
    path('<int:page>/', views.page),
    path('login/', auth_views.LoginView.as_view()),
    path('register/', views.register),
    path('logout/', views.logout_view),
    path('documents/my', views.my_documents),
    path('documents/my/json', views.my_documents_json),
    path('documents/public', views.public_documents),
    path('documents/public/json', views.public_documents_json),
    path('documents/all', views.all_documents),
    path('documents/all/json', views.all_documents_json),
    path('edit_doc/<int:doc_id>', views.edit_doc),
    path('view_doc/<int:doc_id>', views.view_doc),
    path('doc/<int:doc_id>', views.edit_doc_live),
]