from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import get_user_model
from django.contrib import messages
from complaints.models import Comment, Complaint, Ward, Category, Status, Municipality 
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q



User = get_user_model()

@login_required(login_url='login')
def municipality_dashboard(request):
    user = request.user
    if user.is_authenticated and user.user_type == 'municipality':
        
        # Get complaints where complaint's ward municipality matches user's municipality
        complaints_list = Complaint.objects.filter(ward=user.ward ,is_hidden=False).order_by('-created_at')
        total_count=complaints_list.count()
        
        #Count complaints by status
        pending_count = complaints_list.filter(status__name='Pending').count()
        in_progress_count = complaints_list.filter(status__name='In Progress').count()
        resolved_count = complaints_list.filter(status__name='Resolved').count()

        paginator = Paginator(complaints_list, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        post_count = paginator.count 
        
        context = {
            'complaints': page_obj, 
            'wards': Ward.objects.filter(municipality=user.municipality),
            'statuses': Status.objects.all(),
            'links': Category.objects.all(),
            'total_count': total_count,
            'post_count': post_count,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'resolved_count': resolved_count,
        }
        return render(request, 'dashboard/municipality_dashboard.html', context)
    
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login')



@login_required(login_url='login')
def dashboard_my_search_complaints(request):

    keyword = request.GET.get('q', '').strip()
    category = request.GET.get('category')
    municipality = request.GET.get('municipality')
    status = request.GET.get('status')
    ward_number = request.GET.get('ward_number')
    
    
    user = request.user
    if user.is_authenticated and user.user_type == 'municipality':
        complaints = Complaint.objects.filter(ward=user.ward ,is_hidden=False).order_by('-created_at')
        total_count=complaints.count()
   
        #Count complaints by status
        pending_count = complaints.filter(status__name='Pending').count()
        in_progress_count = complaints.filter(status__name='In Progress').count()
        resolved_count = complaints.filter(status__name='Resolved').count()

    
    if keyword:
        complaints = complaints.filter(title__icontains=keyword)

    if category:
        complaints = complaints.filter(category__id=category)
        
    if municipality and ward_number:
        complaints = complaints.filter(ward__ward_number=ward_number, ward__municipality_id=municipality)

    if status:
        complaints = complaints.filter(status=status)

    post_count = complaints.count()

    context = {
        'complaints': complaints,
        'total_count':total_count,
        'post_count': post_count,
        'links': Category.objects.all(),
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
    }

    return render(request, 'dashboard/municipality_dashboard.html', context)


@login_required(login_url='login')
def dashboard_search(request):
    user = request.user
    if user.is_authenticated and user.user_type == 'municipality':
        complaints = Complaint.objects.filter(ward=user.ward, is_hidden=False ).order_by('-created_at')
        total_count=complaints.count()

        # Count complaints by status 
        pending_count = complaints.filter(status__name='Pending').count()
        in_progress_count = complaints.filter(status__name='In Progress').count()
        resolved_count = complaints.filter(status__name='Resolved').count()

        # Search
        keyword = request.GET.get('q', '').strip().lower()
        if keyword:
            complaints = complaints.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(category__category_name__icontains=keyword) |
                Q(ward__ward_number__icontains=keyword) |
                Q(ward__municipality__name__icontains=keyword)
            ).distinct()

        post_count = complaints.count()

        # Pagination
        paginator = Paginator(complaints, 6)
        page = request.GET.get('page')
        complaints = paginator.get_page(page)

        context = {
            'complaints': complaints,
            'post_count': post_count,
            'total_count': total_count,
            'links': Category.objects.all(),
            'wards': Ward.objects.all(),
            'statuses': Status.objects.all(),
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'resolved_count': resolved_count,
        }
        return render(request, 'dashboard/municipality_dashboard.html', context)

    # Not authorized
    messages.error(request, 'You are not authorized to view this page.')
    return redirect('login')


@login_required
def update_complaint_status(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    
    if request.method == "POST":
        status_id = request.POST.get("status")
        if status_id:
            try:
                status_obj = Status.objects.get(id=status_id)
                complaint.status = status_obj
                complaint.save()
                messages.success(request, "Complaint status updated successfully.")
            except Status.DoesNotExist:
                messages.error(request, "Invalid status selected.")
        else:
            messages.error(request, "Please select a status.")

    return redirect('post_detail', id=id)



@login_required(login_url='login')
def admin_dashboard(request):
    
    if request.user.is_authenticated and request.user.user_type == 'admin':
        complaints_list = Complaint.objects.filter(is_hidden=False).order_by('-created_at')
        total_count=complaints_list.count()
        paginator = Paginator(complaints_list, 6) # 6 complaints per page
    
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        post_count = paginator.count

        # Extra counts for admin overview
        total_users = User.objects.exclude(user_type='admin').count()
        total_admin = User.objects.filter(user_type='admin').count()
        total_municipalities = Municipality.objects.count()
        total_reported_posts = Complaint.objects.filter(is_hidden=True).count()
        total_categories = Category.objects.count()
        total_wards = Ward.objects.count()

        context = {
            'complaints': page_obj,
            'wards': Ward.objects.all(),
            'statuses': Status.objects.all(),
            'links': Category.objects.all(),
            'post_count': post_count,

            # New data for dashboard overview
            'total_count':total_count,
            'total_users': total_users,
            'total_municipalities': total_municipalities,
            'total_reported_posts': total_reported_posts,
            'total_categories': total_categories,
            'total_wards': total_wards,
            'total_admin':total_admin

        }

        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login')
    
    
@login_required(login_url='login')
def admin_search(request):
    
    complaints = Complaint.objects.filter(is_hidden=False).order_by('-created_at')
    total_count=complaints.count()
    post_count = 0
    
    #Extra counts for admin overview
    total_users = User.objects.exclude(user_type='admin').count()
    total_admin = User.objects.filter(user_type='admin').count()
    total_municipalities = Municipality.objects.count()
    total_reported_posts = Complaint.objects.filter(is_hidden=True).count()
    total_categories = Category.objects.count()
    total_wards = Ward.objects.count()
    
    
    
    
    keyword = request.GET.get('q', '').strip().lower()
    
    if keyword:
        complaints = complaints.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(category__category_name__icontains=keyword) |
            Q(ward__ward_number__icontains=keyword) |
            Q(municipality__name__icontains=keyword)
        ).order_by('-created_at').distinct()

    post_count = complaints.filter(is_hidden=False).count()

    # Pagination
    paginator = Paginator(complaints, 6)
    page = request.GET.get('page')
    complaints = paginator.get_page(page)

    context = {
        'complaints': complaints,
        'post_count': post_count,
        'links': Category.objects.all(),
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
        # New data for dashboard overview
        'total_count':total_count,
        'total_users': total_users,
        'total_municipalities': total_municipalities,
        'total_reported_posts': total_reported_posts,
        'total_categories': total_categories,
        'total_wards': total_wards,
        'total_admin':total_admin
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# Catagory search for all complaints
@login_required(login_url='login')
def admin_search_complaints(request):
    
    complaints_list = Complaint.objects.filter(is_hidden=False).order_by('-created_at')
    total_count=complaints_list.count()
    
    
    #Extra counts for admin overview
    total_users = User.objects.exclude(user_type='admin').count()
    total_admin = User.objects.filter(user_type='admin').count()
    total_municipalities = Municipality.objects.count()
    total_reported_posts = Complaint.objects.filter(is_hidden=True).count()
    total_categories = Category.objects.count()
    total_wards = Ward.objects.count()
    

    keyword = request.GET.get('q', '').strip()
    category = request.GET.get('category')
    municipality = request.GET.get('municipality')
    status = request.GET.get('status')
    ward_number = request.GET.get('ward_number')

    complaints = Complaint.objects.all()
     
    if keyword:
        complaints = complaints.filter(title__icontains=keyword)

    if category:
        complaints = complaints.filter(category__id=category)
        
    if municipality and ward_number:
        complaints = complaints.filter(ward__ward_number=ward_number, ward__municipality_id=municipality)

    if status:
        complaints = complaints.filter(status=status)

    post_count = complaints.filter(is_hidden=False).count()

    context = {
        'complaints': complaints,
        'post_count': post_count,
        'links': Category.objects.all(),
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
        # New data for dashboard overview
        'total_count':total_count,
        'total_users': total_users,
        'total_municipalities': total_municipalities,
        'total_reported_posts': total_reported_posts,
        'total_categories': total_categories,
        'total_wards': total_wards,
        'total_admin':total_admin
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_delete_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.is_authenticated or request.user.user_type != 'admin':
        messages.error(request, "You are not allowed to delete this complaint.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

    if request.method == 'POST':
        complaint.delete()
        messages.success(request, "Complaint deleted successfully.")
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')


@login_required
def admin_delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    complaint = comment.complaint

    if not request.user.is_authenticated or request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('post_detail', complaint.id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('post_detail', complaint.id)

    return redirect('post_detail', complaint.id)



@login_required(login_url='login')
def reported_complaints(request): 
    if request.user.is_authenticated and request.user.user_type == 'admin':
        complaints_list = Complaint.objects.filter(is_hidden=True).order_by('-created_at')
        total_count=Complaint.objects.filter(is_hidden=False).count()
        paginator = Paginator(complaints_list, 6) # 6 complaints per page
    
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        post_count = paginator.count

        # Extra counts for admin overview
        total_users = User.objects.exclude(user_type='admin').count()
        total_admin = User.objects.filter(user_type='admin').count()
        total_municipalities = Municipality.objects.count()
        total_reported_posts = Complaint.objects.filter(is_hidden=True).count()
        total_categories = Category.objects.count()
        total_wards = Ward.objects.count()

        context = {
            'complaints': page_obj,
            'wards': Ward.objects.all(),
            'statuses': Status.objects.all(),
            'links': Category.objects.all(),
            'post_count': post_count,

            # New data for dashboard overview
            'total_count':total_count,
            'total_users': total_users,
            'total_municipalities': total_municipalities,
            'total_reported_posts': total_reported_posts,
            'total_categories': total_categories,
            'total_wards': total_wards,
            'total_admin':total_admin

        }

        return render(request, 'dashboard/reported.html', context)
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login')
    
    
@login_required
def delete_user(request, user_id):
    if request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete users.")
        return redirect('user_details')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('user_details')
  
@login_required(login_url='login')
def user_details(request):
    users = User.objects.exclude(user_type='admin')
    user_count=users.count()
    
    total_users = User.objects.exclude(user_type='admin').count()
    total_admin = User.objects.filter(user_type='admin').count()
    total_municipalities = Municipality.objects.count()
    total_reported_posts = Complaint.objects.filter(is_hidden=True).count()
    total_categories = Category.objects.count()
    total_wards = Ward.objects.count()
    
    context = {
        'users': users,
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
        'links': Category.objects.all(),
        'user_count': user_count,
        'total_users': total_users,
        'total_municipalities': total_municipalities,
        'total_reported_posts': total_reported_posts,
        'total_categories': total_categories,
        'total_wards': total_wards,
        'total_admin':total_admin

        }
    
    return render(request, 'dashboard/user_details.html', context)


@login_required
def update_complaint_visibility(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.user.user_type != 'admin':
        messages.error(request, "You are not authorized to change visibility.")
        return redirect('post_detail', id=id)

    if request.method == "POST":
        is_hidden_value = request.POST.get("is_hidden")
        complaint.is_hidden = (is_hidden_value == "true")
        complaint.save()

        action = "hidden" if complaint.is_hidden else "unhidden"
        messages.success(request, f"Post successfully {action}.")

    return redirect('post_detail', id=id)