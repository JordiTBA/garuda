from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('analyze/', views.analyze_page, name='analyze_page'),
    path('translate/', views.translate_page, name='translate_page'),
    path('forum/', views.forum_page, name='forum_page'),
    path('places/', views.places_page, name='places_page'),
    
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('logout/', views.logout_view, name='logout_view'),
    
    # API Authentication endpoints
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    
    path('upload/', views.upload_cultural_item, name='upload_cultural_item'),
    path('api/translate/', views.translate_audio, name='translate_audio'),
    path('api/forum/posts/', views.get_forum_posts, name='get_forum_posts'),
    path('api/forum/create/', views.create_forum_post, name='create_forum_post'),
    # Forum discussions endpoints (aliases for posts)
    path('api/forum/discussions/', views.forum_discussions_api, name='forum_discussions_api'),
    path('api/forum/discussions/<int:post_id>/', views.get_forum_post_detail, name='get_forum_discussion_detail'),
    path('api/forum/discussions/<int:post_id>/like/', views.like_post, name='like_forum_discussion'),
    path('api/forum/discussions/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('api/forum/comments/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('api/places/', views.get_places_api, name='get_places_api'),
    path('api/places/rate/', views.rate_place, name='rate_place'),
    path('api/places/ratings/<int:place_id>/', views.get_place_ratings, name='get_place_ratings'),
    path('api/posts/like/<int:post_id>/', views.like_post, name='like_post'),
]