from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
import json
from google import genai
from PIL import Image
import os
from datetime import datetime
from datetime import date

from .models import Place, PlaceRating, ForumPost, ForumComment, UserProfile

def landing_page(request):
    return render(request, 'landing/index.html')

def analyze_page(request):
    return render(request, 'landing/analyze.html')

def translate_page(request):
    return render(request, 'landing/translate.html')

def forum_page(request):
    return render(request, 'landing/forum.html')

def places_page(request):
    places = Place.objects.all()
    return render(request, 'landing/places.html', {'places': places})


class IconInput(forms.TextInput):
    template_name = 'landing/widgets/icon_input.html'

    def __init__(self, attrs=None, icon_class=None):
        super().__init__(attrs)
        self.icon_class = icon_class

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['icon_class'] = self.icon_class
        return context

class IconPasswordInput(IconInput, forms.PasswordInput):
    pass
class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super(CustomRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = '' # Remove default help text
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username atau Email",
        widget=IconInput(attrs={
            'placeholder': 'Masukkan username atau email',
            'autocomplete': 'username'
        }, icon_class='fa-user')
    )
    password = forms.CharField(
        label="Password",
        widget=IconPasswordInput(attrs={
            'placeholder': 'Masukkan password',
            'autocomplete': 'current-password'
        }, icon_class='fa-lock')
    )


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the 'next' page if it exists, otherwise to the landing page
                next_url = request.POST.get('next', 'landing_page')
                return redirect(next_url)
        else:
            # If form is not valid, the error is automatically added to form.non_field_errors
            # which will be displayed in your template.
            messages.error(request, "Username atau password salah. Silakan coba lagi.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'landing/login.html', {'form': form})

def register_page(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optional: Log the user in directly after registration
            # login(request, user)
            messages.success(request, 'Registrasi berhasil! Silakan login dengan akun baru Anda.')
            return redirect('login_view')
    else:
        form = CustomRegisterForm()
        
    return render(request, 'landing/register.html', {'form': form})
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('landing_page')

@csrf_exempt
def api_login(request):
    """API endpoint for user login"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({
                    'success': False, 
                    'error': 'Username and password are required'
                })
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': f'Selamat datang, {user.username}!',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Username atau password salah!'
                })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def api_register(request):
    """API endpoint for user registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            
            # Validation
            if not username or not email or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Username, email, and password are required'
                })
            if password != password_confirm:
                return JsonResponse({
                    'success': False,
                    'error': 'Password tidak sama!'
                })
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Username sudah digunakan!'
                })
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email sudah digunakan!'
                })
            
            # Create new user
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            
            return JsonResponse({
                'success': True,
                'message': 'Akun berhasil dibuat! Silakan login.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def api_logout(request):
    """API endpoint for user logout"""
    if request.method == 'POST':
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Anda telah logout.'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def validate_file(file):
    try:
        api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
        if not api_key:
            raise ValueError("Google AI API key not configured")
            
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=['''(jawab menggunakan bahasa indonesia) (kamu adalah sebuah ai yang dirancang untuk mengenali budaya indonesia) can you recognize this picture what is that and return the value with this format only{
            'item_type': 'nama jenis barang',
            'confidence': 'seberapa yakin akan barang yang dipindai 1-100%',
            'details': {
                'origin': 'kota asal barang',
                'pattern': 'pola barang (opsional)',
                'description': 'deskripsi barang',
                'created' : 'ditemukan pada ',
                'history': 'sejarah barang',
                'how_to_create': 'cara membuat barang tersebut (opsional)',
                'link_video': 'tautan video (opsional)'
            }
            }''', Image.open(file)]
        )
        json_start = response.text.find('{')
        json_end = response.text.rfind('}') + 1
        clean_json_str = response.text[json_start:json_end]

        data = json.loads(clean_json_str)
        return data
    except Exception as e:
        print(f"Error processing file: {e}")
        return {
            'item_type': 'Error',
            'confidence': 0,
            'details': {
                'origin': 'Unknown',
                'pattern': 'N/A',
                'description': 'Terjadi kesalahan saat menganalisis gambar',
                'created': 'N/A',
                'history': 'N/A',
                'how_to_create': 'N/A',
                'link_video': 'N/A'
            }
        }

@csrf_exempt
def upload_cultural_item(request):
    if request.method == 'POST' and request.FILES.get('cultural_image'):
        uploaded_file = request.FILES['cultural_image']
        predictions = validate_file(uploaded_file)
        return JsonResponse({
            'success': True,
            'filename': uploaded_file.name,
            'predictions': predictions
        })
    
    return JsonResponse({'success': False, 'error': 'No file uploaded'})

@csrf_exempt
def translate_audio(request):
    if request.method == 'POST':
        try:
            api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
            if not api_key:
                raise ValueError("Google AI API key not configured")
            text = request.POST.get('text', '')
            source_lang = request.POST.get('source_lang', 'id')
            target_lang = request.POST.get('target_lang', 'en')
            client = genai.Client(api_key=api_key)
            print(f"Translating text: {text} from {source_lang} to {target_lang}")
            prompt = ""
            if source_lang == 'auto':
                prompt = f"""
                Tugas:
                1. Pertama, deteksi bahasa dari teks berikut.
                2. Kedua, terjemahkan teks tersebut ke dalam Bahasa {target_lang}.
                3. Kembalikan HANYA sebuah objek JSON tunggal dengan format berikut: {{"translated_text": "hasil terjemahan di sini"}}. Jangan tambahkan teks atau penjelasan lain.

                Teks untuk diterjemahkan: "{text}"
                """
            else:
                prompt = f"""
                Tugas:
                Terjemahkan teks berikut dari Bahasa {source_lang} ke Bahasa {target_lang}.
                Kembalikan HANYA sebuah objek JSON tunggal dengan format berikut: {{"translated_text": "hasil terjemahan di sini"}}. Jangan tambahkan teks atau penjelasan lain.

                Teks untuk diterjemahkan: "{text}"
                """
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt ]
            )
            translated_text = response.text
            json_start = translated_text.find('{')
            json_end = translated_text.rfind('}') + 1
            clean_json_str = translated_text[json_start:json_end]
            translated_data = json.loads(clean_json_str)
            translated_text = translated_data.get('translated_text', '')
            if not translated_text:
                translated_text = "Translation failed or not available"
            return JsonResponse({
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': target_lang
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_forum_posts(request):
    try:
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        
        posts = ForumPost.objects.all()
        
        if search:
            posts = posts.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search)
            )
        
        if category:
            posts = posts.filter(category=category)
        
        posts = posts.order_by('-created_at')
        
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'date': post.created_at.strftime('%Y-%m-%d %H:%M'),
                'category': post.category,
                'tags': post.tags,
                'views': post.views,
                'likes': post.like_count(),
                'comments': post.comment_count()
            })
        
        return JsonResponse({'success': True, 'posts': posts_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def create_forum_post(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Anda harus login terlebih dahulu untuk membuat diskusi'
            })
        try:
            # Handle JSON data
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            category = data.get('category')
            tags = data.get('tags', '')  # Default to empty string if not provided
            
            post = ForumPost.objects.create(
                title=title,
                content=content,
                category=category,
                tags=tags,
                author=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Diskusi berhasil dibuat!',
                'post_id': post.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def forum_discussions_api(request):
    if request.method == 'GET':
        try:
            search = request.GET.get('search', '')
            category = request.GET.get('category', '')
            
            posts = ForumPost.objects.all()
            
            if search:
                posts = posts.filter(
                    Q(title__icontains=search) | 
                    Q(content__icontains=search)
                )
            
            if category:
                posts = posts.filter(category=category)
            
            posts = posts.order_by('-created_at')
            
            posts_data = []
            for post in posts:
                posts_data.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'author': post.author.username,
                    'date': post.created_at.strftime('%Y-%m-%d'),
                    'category': post.category,
                    'likes': post.like_count(),
                    'comments': post.comment_count()
                })
            
            stats = {
                'total_posts': ForumPost.objects.count(),
                'total_users': User.objects.count(),
                'today_posts': ForumPost.objects.filter(created_at__date=date.today()).count()
            }
            
            return JsonResponse({
                'success': True, 
                'posts': posts_data,
                'stats': stats
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
        try:
            data = json.loads(request.body)
            
            title = data.get('title')
            content = data.get('content')
            category = data.get('category')
            
            if not title or not content:
                return JsonResponse({'success': False, 'error': 'Title and content are required'})
            
            post = ForumPost.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Diskusi berhasil dibuat!',
                'post_id': post.id
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_forum_post_detail(request, post_id):
    try:
        post = get_object_or_404(ForumPost, id=post_id)
        comments = ForumComment.objects.filter(post=post).order_by('created_at')
        comments_data = []
        for comment in comments:
            user_has_liked = False
            like_count = 0
            try:
                if request.user.is_authenticated:
                    user_has_liked = request.user in comment.likes.all()
                like_count = comment.like_count()
            except Exception as db_error:
                print(f"Database error getting comment likes: {db_error}")
                user_has_liked = False
                like_count = 0
            
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'date': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'likes': like_count,
                'user_has_liked': user_has_liked
            })
        
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'category': post.category,
            'tags': post.tags,
            'views': post.views,
            'likes': post.like_count(),
            'comments': comments_data,
            'comment_count': len(comments_data)
        }
        
        return JsonResponse({'success': True, 'post': post_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        try:
            post = get_object_or_404(ForumPost, id=post_id)
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'success': False, 'error': 'Content is required'})
            
            comment = ForumComment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Komentar berhasil ditambahkan!',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'date': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'likes': 0 
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def like_comment(request, comment_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Anda harus login terlebih dahulu untuk menyukai komentar'
            })
        try:
            comment = get_object_or_404(ForumComment, id=comment_id)
            try:
                if request.user in comment.likes.all():
                    comment.likes.remove(request.user)
                    liked = False
                    message = 'Batal menyukai komentar'
                else:
                    comment.likes.add(request.user)
                    liked = True
                    message = 'Menyukai komentar'
                like_count = comment.like_count()
            except Exception as e:
                print(f"like comments {e}")
                return JsonResponse({
                    'success': True,
                    'liked': True,
                    'like_count': 0,
                    'message': 'Error occured'
                })
            return JsonResponse({
                'success': True,
                'liked': liked,
                'like_count': like_count,
                'message': message
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def rate_place(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Anda harus login terlebih dahulu untuk menyukai diskusi'
            })
        try:
            place_id = request.POST.get('place_id')
            rating = int(request.POST.get('rating', 0))
            comment = request.POST.get('comment', '')
            
            place = get_object_or_404(Place, id=place_id)
            place_rating, created = PlaceRating.objects.update_or_create(
                place=place,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            action = 'dibuat' if created else 'diperbarui'
            return JsonResponse({
                'success': True,
                'message': f'Rating berhasil {action}!',
                'place_id': place_id,
                'rating': rating,
                'average_rating': place.average_rating(),
                'rating_count': place.rating_count()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_place_ratings(request, place_id):
    try:
        place = get_object_or_404(Place, id=place_id)
        ratings = PlaceRating.objects.filter(place=place).order_by('-created_at')
        
        ratings_data = []
        for rating in ratings:
            ratings_data.append({
                'id': rating.id,
                'user': rating.user.username,
                'rating': rating.rating,
                'comment': rating.comment,
                'date': rating.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'ratings': ratings_data,
            'average_rating': place.average_rating(),
            'rating_count': place.rating_count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def like_post(request, post_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Anda harus login terlebih dahulu untuk menyukai diskusi'
            })
        try:
            post = get_object_or_404(ForumPost, id=post_id)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                liked = False
                message = 'Batal menyukai diskusi'
            else:
                post.likes.add(request.user)
                liked = True
                message = 'Menyukai diskusi'
            return JsonResponse({
                'success': True,
                'liked': liked,
                'like_count': post.like_count(),
                'message': message
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_places_api(request):
    try:
        if request.method == "GET":
            search = request.GET.get("search", "")
            category = request.GET.get("category", "")
            province = request.GET.get("province", "")
            places = Place.objects.all()
            if search:
                places = places.filter(
                    Q(name__icontains=search) | 
                    Q(description__icontains=search) |
                    Q(location__icontains=search)
                )
                print(f"Search filter applied: {places}")
            if category:
                places = places.filter(category=category)
            if province:
                places = places.filter(province__icontains=province)
            places = places.order_by("name")
            places_data = []
            for place in places:
                try:
                    image_url = place.get_image_url() if hasattr(place, 'get_image_url') else (place.image_url or '')
                except:
                    image_url = place.image_url if hasattr(place, 'image_url') else ''
                
                places_data.append({
                    "id": place.id,
                    "name": place.name,
                    "description": place.description,
                    "location": place.location,
                    "province": place.province,
                    "category": place.category,
                    "image_url": image_url,
                    "average_rating": place.average_rating(),
                    "rating_count": place.rating_count(),
                    "created_at": place.created_at.strftime("%Y-%m-%d")
                })
            
            # Calculate stats
            all_places = Place.objects.all()
            total_ratings = sum(place.rating_count() for place in all_places)
            total_rating_sum = sum(place.average_rating() * place.rating_count() for place in all_places if place.rating_count() > 0)
            average_rating = total_rating_sum / total_ratings if total_ratings > 0 else 0
            
            stats = {
                'total_places': all_places.count(),
                'average_rating': average_rating,
                'total_reviews': total_ratings,
                'total_provinces': all_places.values('province').distinct().count()
            }
            
            return JsonResponse({
                "success": True, 
                "places": places_data,
                "total_count": len(places_data),
                "stats": stats
            })
            
        elif request.method == "POST":
            # Create new place (admin only - you might want to add permission checks)
            print(f"DEBUG: Raw request body: {request.body}")
            print(f"DEBUG: Request content type: {request.content_type}")
            print(f"DEBUG: Request headers: {dict(request.headers)}")
            
            data = json.loads(request.body)
            
            print(f"DEBUG: get_places_api POST data: {data}")  # Debug log
            print(f"DEBUG: Data type: {type(data)}")
            print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            image_url = data.get("image_url", "")
            print(f"DEBUG: Original image_url from data: '{image_url}' (type: {type(image_url)})")
            
            if image_url and image_url.strip():
                image_url = image_url.strip()
                print(f"DEBUG: Cleaned image_url: '{image_url}'")
                # Basic URL validation
                if not (image_url.startswith('http://') or image_url.startswith('https://')):
                    print(f"DEBUG: URL validation failed for: '{image_url}'")
                    return JsonResponse({
                        "success": False, 
                        "error": "URL gambar harus dimulai dengan http:// atau https://"
                    })
                print(f"DEBUG: URL validation passed for: '{image_url}'")
            else:
                image_url = None
                print(f"DEBUG: image_url set to None (was empty or None)")
            
            print(f"DEBUG: Final image_url value before creating place: '{image_url}'")
            
            place = Place.objects.create(
                name=data.get("name"),
                description=data.get("description"),
                location=data.get("location"),
                province=data.get("province"),
                category=data.get("category"),
                image_url=image_url
            )
            
            print(f"DEBUG: Place created with ID: {place.id}")
            print(f"DEBUG: Place.image_url in database: '{place.image_url}'")
            print(f"DEBUG: Place.get_image_url() result: '{place.get_image_url()}'")
            
            return JsonResponse({
                "success": True,
                "message": "Place created successfully!",
                "place_id": place.id,
                "debug_image_url": place.image_url,
                "debug_get_image_url": place.get_image_url()
            })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_places_api: {e}")
        print(f"Full traceback: {error_details}")
        return JsonResponse({
            "success": False, 
            "error": str(e),
            "details": error_details
        })
    
    return JsonResponse({"success": False, "error": "Invalid request method"})

@csrf_exempt
def get_place_detail(request, place_id):
    """API endpoint to get a specific place by ID"""
    try:
        place = get_object_or_404(Place, id=place_id)
        # Get reviews for this place
        reviews = PlaceRating.objects.filter(place=place).order_by('-created_at')
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'author': review.user.username,
                'rating': review.rating,
                'content': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
            })
        place_data = {
            "id": place.id,
            "name": place.name,
            "description": place.description,
            "location": place.location,
            "province": place.province,
            "category": place.category,
            "image_url": place.get_image_url(),
            "average_rating": place.average_rating(),
            "rating_count": place.rating_count(),
            "created_at": place.created_at.strftime("%Y-%m-%d %H:%M"),
            "reviews": reviews_data
        }
        
        return JsonResponse({
            "success": True,
            "place": place_data
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def create_place(request):
    """API endpoint to create a new place with image upload"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Invalid request method"})
    # print(f"DEBUG: create_place request body: {request.body}")  # Debug log
    try:
        # Handle both form data (with file) and JSON data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            name = request.POST.get('name')
            description = request.POST.get('description')
            location = request.POST.get('location')
            province = request.POST.get('province')
            category = request.POST.get('category')
            image_url = request.POST.get('image_url', '')
            image = request.FILES.get('image')
            
        else:
            # JSON data (no file upload)
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description')
            location = data.get('location')
            province = data.get('province')
            category = data.get('category')
            image_url = data.get('image_url', '')
            image = None
        
        # Validate required fields
        if not all([name, description, location, province, category]):
            return JsonResponse({
                "success": False, 
                "error": "Semua field wajib harus diisi"
            })
        
        # Clean up image_url - set to None if empty string
        if image_url and image_url.strip():
            image_url = image_url.strip()
        else:
            image_url = None
            
        print(f"DEBUG: Creating place with image_url: '{image_url}'")  # Debug log
        
        # Create the place
        place = Place.objects.create(
            name=name,
            description=description,
            location=location,
            province=province,
            category=category,
            image_url=image_url,
            image=image
        )
        
        return JsonResponse({
            "success": True,
            "message": "Tempat berhasil ditambahkan!",
            "place_id": place.id,
            "place": {
                "id": place.id,
                "name": place.name,
                "description": place.description,
                "location": place.location,
                "province": place.province,
                "category": place.category,
                "image_url": place.get_image_url(),
                "average_rating": place.average_rating(),
                "rating_count": place.rating_count()
            }
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def update_place(request, place_id):
    """API endpoint to update a place with image upload"""
    if request.method not in ['PUT', 'POST']:
        return JsonResponse({"success": False, "error": "Invalid request method"})
    
    try:
        place = get_object_or_404(Place, id=place_id)
        
        # Handle both form data (with file) and JSON data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            name = request.POST.get('name', place.name)
            description = request.POST.get('description', place.description)
            location = request.POST.get('location', place.location)
            province = request.POST.get('province', place.province)
            category = request.POST.get('category', place.category)
            image_url = request.POST.get('image_url', place.image_url or '')
            image = request.FILES.get('image')
            
        else:
            # JSON data (no file upload)
            data = json.loads(request.body)
            name = data.get('name', place.name)
            description = data.get('description', place.description)
            location = data.get('location', place.location)
            province = data.get('province', place.province)
            category = data.get('category', place.category)
            image_url = data.get('image_url', place.image_url or '')
            image = None
        
        # Update the place
        place.name = name
        place.description = description
        place.location = location
        place.province = province
        place.category = category
        place.image_url = image_url
        
        if image:
            place.image = image
        
        place.save()
        
        return JsonResponse({
            "success": True,
            "message": "Tempat berhasil diperbarui!",
            "place": {
                "id": place.id,
                "name": place.name,
                "description": place.description,
                "location": place.location,
                "province": place.province,
                "category": place.category,
                "image_url": place.get_image_url(),
                "average_rating": place.average_rating(),
                "rating_count": place.rating_count()
            }
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
@login_required
def submit_place_review(request):
    """API endpoint for submitting place reviews"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Anda harus login terlebih dahulu untuk memberikan rating'
            })
        try:
            data = json.loads(request.body)
            place_id = data.get('place_id')
            rating = int(data.get('rating', 0))
            comment = data.get('content', '')  # Changed from 'comment' to 'content' to match frontend
            
            print(f"DEBUG: Raw request body: {request.body}")  # Debug
            print(f"DEBUG: Parsed data: {data}")  # Debug
            print(f"DEBUG: Received data - place_id: {place_id}, rating: {rating}, comment: '{comment}' (length: {len(comment)})")  # Debug
            
            if not place_id or not rating:
                return JsonResponse({
                    'success': False,
                    'error': 'Place ID and rating are required'
                })
            
            if rating < 1 or rating > 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                })
            
            place = get_object_or_404(Place, id=place_id)
            place_rating, created = PlaceRating.objects.update_or_create(
                place=place,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            
            print(f"DEBUG: PlaceRating created/updated - created: {created}, id: {place_rating.id}")  # Debug
            print(f"DEBUG: Saved PlaceRating - rating: {place_rating.rating}, comment: '{place_rating.comment}' (length: {len(place_rating.comment)})")  # Debug
            
            action = 'dibuat' if created else 'diperbarui'
            return JsonResponse({
                'success': True,
                'message': f'Rating berhasil {action}!',
                'place_id': place_id,
                'rating': rating,
                'average_rating': place.average_rating(),
                'rating_count': place.rating_count()
            })
        except Exception as e:
            print(f"DEBUG: Error in submit_place_review - {str(e)}")  # Debug
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})