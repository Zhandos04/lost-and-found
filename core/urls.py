from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('items/', views.ItemListView.as_view(), name='item-list'),
    path('items/<str:status>/', views.ItemListView.as_view(), name='item-list-filtered'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),
    path('item/new/', views.ItemCreateView.as_view(), name='item-create'),
    path('item/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item-update'),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
    path('item/<int:pk>/claim/', views.create_claim, name='create-claim'),
    path('search/', views.search_items, name='search'),
    path('my-items/', views.my_items, name='my-items'),
    path('item/<int:pk>/claims/', views.manage_claims, name='manage-claims'),
    path('claim/<int:claim_id>/approve/', views.approve_claim, name='approve-claim'),
    path('claim/<int:claim_id>/reject/', views.reject_claim, name='reject-claim'),
]