from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('create/', views.create_post, name='create_post'),
    path('profile/<slug:user_name>', views.profile, name='profile')
]
