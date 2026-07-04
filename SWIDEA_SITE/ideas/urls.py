from django.urls import path
from . import views

app_name = 'ideas'

urlpatterns = [
    path('', views.idea_list, name='idea-list'),
    path('ideas/create/', views.idea_create, name='idea-create'),
    path('ideas/<int:pk>/', views.idea_detail, name='idea-detail'),
    path('ideas/<int:pk>/update/', views.idea_update, name='idea-update'),
    path('ideas/<int:pk>/delete/', views.idea_delete, name='idea-delete'),

    path('ideas/<int:pk>/star/', views.idea_star_toggle, name='idea-star-toggle'),
    path('ideas/<int:pk>/interest/<str:action>/', views.idea_interest_update, name='idea-interest-update'),

    path('devtools/', views.devtool_list, name='devtool-list'),
    path('devtools/create/', views.devtool_create, name='devtool-create'),
    path('devtools/<int:pk>/', views.devtool_detail, name='devtool-detail'),
    path('devtools/<int:pk>/update/', views.devtool_update, name='devtool-update'),
    path('devtools/<int:pk>/delete/', views.devtool_delete, name='devtool-delete'),
]