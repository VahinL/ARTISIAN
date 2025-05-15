from .models import User, Artwork, Comment, Report, Follow, Like, Share
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count


## ADMIN MODULE --->

@login_required(login_url='login')
def admin_dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'pending_approvals': User.objects.filter(is_active=False).count(),
        'total_artworks': Artwork.objects.count(),
        'recent_reports': Report.objects.filter(is_resolved=False).count(),
        'active_artists': User.objects.filter(user_type='artist', is_active=True).count(),
        'active_viewers': User.objects.filter(user_type='viewer', is_active=True).count()
    }
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_reports = Report.objects.filter(is_resolved=False).order_by('-created_at')[:5]
    
    return render(request, 'adminT/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_reports': recent_reports
    })

@login_required(login_url='login')
def all_users(request):
    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 25)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'adminT/all_users.html', {
        'page_obj': page_obj,
        'total_users': users.count()
    })

@login_required(login_url='login')
def user_management(request):
    pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
    paginator = Paginator(pending_users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'adminT/user_management.html', {
        'page_obj': page_obj,
        'pending_count': pending_users.count()
    })

@login_required(login_url='login')
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved!')
    return redirect(request.META.get('HTTP_REFERER', 'admin_user_management'))

@login_required(login_url='login')
def reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been rejected and removed.')
    return redirect('admin_user_management')


@login_required(login_url='login')
def content_monitoring(request):
    artworks = Artwork.objects.all().order_by('-upload_date')
    comments = Comment.objects.all().order_by('-created_at')
    reports = Report.objects.all().order_by('-created_at')
    shares = Share.objects.all().order_by('-shared_at')  


    return render(request, 'adminT/content_monitoring.html', {
        'artworks': artworks[:20],  
        'comments': comments[:20],
        'reports': reports,
        'shares': shares[:50],  

    })


@login_required(login_url='login')
def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        report.is_resolved = True
        report.resolved_by = request.user
        report.save()
        messages.success(request, 'Report marked as resolved!')
    return redirect('admin_content_monitoring')


## ARTIST MODULE -->

@login_required(login_url='login')
def artist_dashboard(request):    
    artworks = Artwork.objects.filter(artist=request.user).order_by('-upload_date')
    reports = Report.objects.filter(artwork__artist=request.user).order_by('-created_at')
    shares = Share.objects.filter(artwork__artist=request.user).order_by('-shared_at')[:10]
    share_count = Share.objects.filter(artwork__artist=request.user).count()

    return render(request, 'artist/dashboard.html', {
        'artworks': artworks,
        'artworks_count': artworks.count(),
        'reports': reports,
        'shares': shares,
        'share_count': share_count,

    })

@login_required(login_url='login')
def upload_art(request):    
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        description = request.POST.get('description', '')
        tags = request.POST.get('tags', '')
        
        if not all([title, image]):
            messages.error(request, 'Title and image are required')
        else:
            Artwork.objects.create(
                artist=request.user,
                title=title,
                image=image,
                description=description,
                tags=tags
            )
            messages.success(request, 'Artwork uploaded successfully!')
            return redirect('artist_dashboard')
    
    return render(request, 'artist/upload_art.html')


@login_required(login_url='login')
def edit_art(request, art_id):
    artwork = get_object_or_404(Artwork, id=art_id, artist=request.user)
    
    if request.method == 'POST':
        artwork.title = request.POST.get('title', artwork.title)
        artwork.description = request.POST.get('description', artwork.description)
        artwork.tags = request.POST.get('tags', artwork.tags)
        
        if 'image' in request.FILES:
            artwork.image = request.FILES['image']
        
        artwork.save()
        messages.success(request, 'Artwork updated successfully!')
        return redirect('artist_dashboard')
    
    return render(request, 'artist/edit_art.html', {'artwork': artwork})


@login_required(login_url='login')
def delete_art(request, art_id):
    artwork = get_object_or_404(Artwork, id=art_id, artist=request.user)
    
    if request.method == 'POST':
        artwork.delete()
        messages.success(request, 'Artwork deleted successfully!')
    
    return redirect('artist_dashboard')

@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        user.website = request.POST.get('website', user.website)
        
        if 'profile_pic' in request.FILES:
            user.profile_picture = request.FILES['profile_pic']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('artist_dashboard')
    
    return render(request, 'artist/edit_profile.html')


# Viewer -->

def home(request):
    artworks = Artwork.objects.annotate(
        num_likes=Count('likes'),
        num_comments=Count('comments'),
        num_shares=Count('shares')  
    ).order_by('-upload_date')
    
    suggested_artists = User.objects.filter(
        user_type='artist',
        is_active=True,
    ).annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]
    
    following_ids = []
    if request.user.is_authenticated:
        following_ids = request.user.following.values_list('artist', flat=True)
    
    context = {
        'artworks': artworks,
        'suggested_artists': suggested_artists,
        'following_ids': following_ids
    }

    return render(request, 'viewer/home.html', context)

@login_required(login_url='login')
def artists_list(request):
    artists = User.objects.filter(user_type='artist', is_active=True).order_by('-date_joined')
    context = {
        'artists': artists,
    }
    return render(request, 'viewer/artists_list.html', context)

def about(request):
    return render(request, 'viewer/about.html')

def contact(request):
    return render(request, 'viewer/contact.html')


@require_POST
@login_required(login_url='login')
def toggle_like(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    like, created = Like.objects.get_or_create(
        artwork=artwork,
        user=request.user
    )
    
    if not created:
        like.delete()
        action = 'unliked'
    else:
        action = 'liked'
    
    return JsonResponse({
        'status': 'ok',
        'action': action,
        'likes_count': artwork.likes.count()
    })

@require_POST
@login_required(login_url='login')
def add_comment(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    content = request.POST.get('content', '').strip()
    
    if content:
        comment = Comment.objects.create(
            artwork=artwork,
            user=request.user,
            content=content
        )
        return JsonResponse({
            'status': 'ok',
            'comment': {
                'content': comment.content,
                'username': comment.user.username,
                'profile_pic': comment.user.profile_picture.url if comment.user.profile_picture else '/static/images/default-profile.png',
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
            }
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Comment cannot be empty'
        }, status=400)

@login_required(login_url='login')
def follow_artist(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, user_type='artist')
    
    if request.user == artist:
        messages.error(request, "You can't follow yourself")
    else:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            artist=artist
        )
        
        if created:
            messages.success(request, f'Now following {artist.username}')
        else:
            follow.delete()
            messages.success(request, f'Unfollowed {artist.username}')
    
    return redirect('home')


@login_required(login_url='login')
def report_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)

    if artwork.artist == request.user:
        messages.error(request, "You can't report your own artwork.")
        return redirect('home')  

    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        details = request.POST.get('details', '')

        Report.objects.create(
            reporter=request.user,
            artwork=artwork,
            report_type=report_type,
            details=details
        )

        messages.success(request, 'Thank you for your report. We will review it shortly.')

    return redirect('home')


@login_required(login_url='login')
def edit_user_profile(request):
    user = request.user
    
    if request.method == 'POST':
       
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.bio = request.POST.get('bio', user.bio)
        
       
        if 'profile_picture' in request.FILES:
            
            if user.profile_picture:
                user.profile_picture.delete(save=False)
            user.profile_picture = request.FILES['profile_picture']
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_user_profile')  
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    
    context = {
        'user': user,
        'following_count': user.following.count(),
    }
    return render(request, 'viewer/profile.html', context)

@login_required(login_url='login')
def artist_profile(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, user_type='artist')
    artworks = Artwork.objects.filter(artist=artist).order_by('-upload_date')
    
    following_ids = []
    if request.user.is_authenticated:
        following_ids = request.user.following.values_list('artist_id', flat=True)
    
    context = {
        'artist': artist,
        'artworks': artworks, 
        'following_ids': following_ids,
    }
    return render(request, 'viewer/artist_profile.html', context)

@login_required(login_url='login')
def artwork_detail(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    context = {
        'artwork': artwork,
    }
    return render(request, 'viewer/artwork_detail.html', context)


@login_required(login_url='login')
def share_artwork(request, artwork_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Please login to share artwork'}, status=403)
        
        share_to = request.POST.get('share_to')
        
        try:
            artwork = Artwork.objects.get(id=artwork_id)
            Share.objects.create(
                artwork=artwork,
                shared_by=request.user,
                shared_to=share_to
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Artwork shared to {share_to} successfully!'
            })
        except Artwork.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Artwork not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



# Accounts

def register(request):
    user_type = request.GET.get('type', 'viewer').lower()
        
    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        bio = request.POST.get('bio', '')
        profile_pic = request.FILES.get('profile_pic')
        
        website = request.POST.get('website', '') if user_type == 'artist' else ''
         
        errors = []
        if not all([first_name, last_name, username, email, password]):
            errors.append('All required fields must be filled')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
            
        if not errors:
            try:
                user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=make_password(password),
                    user_type=user_type,
                    bio=bio,
                    website=website,
                    is_active=0,
                )
                
                if profile_pic:
                    user.profile_picture = profile_pic
                    user.save()
                
                messages.success(request, 
                    f'Account created! {"Pending approval" if user_type == "artist" else "You can now login"}')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            for error in errors:
                messages.error(request, error)
    
    return render(request, 'accounts/register.html', {
        'user_type': user_type,
        'type_display': 'Artist' if user_type == 'artist' else 'Viewer'
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None :
            if user.is_superuser == 1:
                login(request, user)
                return redirect('admin_dashboard')
            elif user.user_type == 'artist':
                if user.is_active==1:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, "Waiting for Approval")
                    return render(request, 'accounts/login.html')
            elif user.user_type == 'viewer':
                if user.is_active==1:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, "Waiting for Approval")
                    return render(request, 'accounts/login.html')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
            return render(request, 'accounts/login.html')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


