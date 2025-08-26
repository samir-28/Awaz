from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Complaint, Ward, Category, Status ,Like, Comment, Report
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q



User = get_user_model()

@login_required(login_url='login')
def post_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_name = request.POST.get('category', '').strip()
        ward_id = request.POST.get('ward_id')
        image = request.FILES.get('image')

        # Validation
        if not all([title, description, category_name, ward_id]):
            messages.error(request, "Please fill all required fields.")
            return redirect('post_complaint')

        try:
            ward = Ward.objects.get(id=ward_id)
        except Ward.DoesNotExist:
            messages.error(request, "Invalid ward selected.")
            return redirect('post_complaint')

        try:
            category = Category.objects.get(category_name=category_name)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return redirect('post_complaint')

        try:
            status = Status.objects.get(name='Pending')  # Default status
        except Status.DoesNotExist:
            messages.error(request, "Default status not set in database.")
            return redirect('post_complaint')

        # Save complaint
        Complaint.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category,
            municipality=ward.municipality, 
            ward=ward,  
            status=status,
            image=image if image else None,
        )

        messages.success(request, "Complaint submitted successfully.")
        return redirect('my_complaints')
    
  
    # GET method: render form
    wards = Ward.objects.select_related('municipality').all()
    categories = Category.objects.all()

    return render(request, 'complaints/create_complaint.html', {
        'wards': wards,
        'categories': categories
    })


@login_required(login_url='login')
def all_complaint(request):
    complaints_list = Complaint.objects.all().order_by('-created_at') 
    paginator = Paginator(complaints_list, 6)  # 6 complaints per page 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count= paginator.count 

    context = {
        'complaints': page_obj, 
        'wards':Ward.objects.all(),
        'statuses': Status.objects.all(),
        'links': Category.objects.all(),
        'post_count': post_count
    }

    return render(request, 'complaints/all_complaints.html',context )


@login_required(login_url='login')
def post_detail(request, id):
    user = request.user
    
    if user.is_authenticated and user.user_type == 'admin':
        
        complaint = get_object_or_404(Complaint, id=id)
    else:
        complaint = get_object_or_404(Complaint, id=id, is_hidden=False)

    statuses = Status.objects.all()   
    return render(request, 'complaints/post_detail.html', {'complaint': complaint, 'statuses': statuses})


@login_required(login_url='login')
def search(request):
    
    complaints = Complaint.objects.filter(is_hidden=False).order_by('-created_at')
    post_count = 0
    keyword = request.GET.get('q', '').strip().lower()
    
    if keyword:
        complaints = complaints.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(category__category_name__icontains=keyword) |
            Q(ward__ward_number__icontains=keyword) |
            Q(municipality__name__icontains=keyword)
        ).order_by('-created_at').distinct()

    post_count = complaints.count()

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
    }
    return render(request, 'complaints/all_complaints.html', context)

@login_required(login_url='login')
def my_complaints(request):
    complaints_list = Complaint.objects.filter(user=request.user).order_by('-created_at') 
    paginator = Paginator(complaints_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count= paginator.count 
    
    context = {
        'complaints': page_obj, 
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
        'links': Category.objects.all(),
        'post_count': post_count
    }
    return render(request, 'complaints/my_complaints.html', context)


@login_required(login_url='login')
def my_profile(request):
    user = request.user
    post_count = Complaint.objects.filter(user=user).count()
    total_count = Complaint.objects.filter(ward=user.ward ,is_hidden=False).count()
     
    
    context = {
        'profile': user,
        'post_count': post_count,
        'total_count':total_count
    }
    return render(request, 'accounts/my_profile.html', context)


@login_required(login_url='login')
def like_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.user == complaint.user:
        messages.error(request, "You cannot like your own post.")
    else:
        like_obj = Like.objects.filter(user=request.user, complaint=complaint).first()
        if like_obj:
            like_obj.delete()
            messages.success(request, "You unliked the post.")
        else:
            Like.objects.create(user=request.user, complaint=complaint)
            messages.success(request, "You liked the post.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))



@login_required(login_url='login')
def report_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.user == complaint.user:
        messages.error(request, "You cannot report your own post.")
    else:
        report_obj = Report.objects.filter(user=request.user, complaint=complaint).first()
        if report_obj:
            report_obj.delete()
            messages.success(request, "You have unreported this post.")
            
            # unhide if reports drop below 
            if complaint.report_count() < 3 and complaint.is_hidden:
                complaint.is_hidden = False
                complaint.save()
        else:
            Report.objects.create(user=request.user, complaint=complaint)
            messages.success(request, "You reported the post.")

            if complaint.report_count() >= 3 and not complaint.is_hidden:
                complaint.is_hidden = True
                complaint.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))



@login_required(login_url='login')
def comment_complaint(request, pk):
    
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.user == complaint.user:
        messages.error(request, "You cannot comment on your own post.")
        return redirect('post_detail', id=pk)

    if Comment.objects.filter(user=request.user, complaint=complaint).exists():
        messages.info(request, "You have already commented on this post.")
        return redirect('post_detail', id=pk)  # Important: redirect here to avoid adding duplicate comment

    if request.method == "POST":
        content = request.POST.get('comment', '').strip()
        if content:
            Comment.objects.create(user=request.user, complaint=complaint, content=content)
            messages.success(request, "You commented on the post.")
        else:
            messages.warning(request, "Comment cannot be empty.")

    return redirect('post_detail', id=pk)


# Catagory search for all complaints
@login_required(login_url='login')
def search_complaints(request):

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

    post_count = complaints.count()

    context = {
        'complaints': complaints,
        'post_count': post_count,
        'links': Category.objects.all(),
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
    }

    return render(request, 'complaints/all_complaints.html', context)


# category search for My compalints
@login_required(login_url='login')
def my_search_complaints(request):

    keyword = request.GET.get('q', '').strip()
    category = request.GET.get('category')
    municipality = request.GET.get('municipality')
    status = request.GET.get('status')
    ward_number = request.GET.get('ward_number')

    complaints=Complaint.objects.filter(user=request.user).order_by('-created_at') 
    

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
        'post_count': post_count,
        'links': Category.objects.all(),
        'wards': Ward.objects.all(),
        'statuses': Status.objects.all(),
    }

    return render(request, 'complaints/my_complaints.html', context)

@login_required
def delete_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    # Check if current user is the creator
    if complaint.user != request.user:
        messages.error(request, "You are not allowed to delete this complaint.")
        return redirect(request.META.get('HTTP_REFERER', 'my_complaints'))  

    complaint.delete()
    messages.success(request, "Complaint deleted successfully.")
    return redirect('my_complaints') 


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    complaint = comment.complaint

    if request.user == comment.user or request.user == complaint.user:
        if request.method == 'POST':
            comment.delete()
            messages.success(request, "Comment deleted successfully.")
            return redirect('post_detail', complaint.id)
    else:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('post_detail', complaint.id)

    return redirect('post_detail', complaint.id)


@login_required
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    wards = Ward.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        ward_id = request.POST.get('ward_id')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Update fields
        complaint.title = title
        complaint.description = description
        complaint.ward = Ward.objects.get(id=ward_id) if ward_id else None
        complaint.category = Category.objects.get(id=category_id) if category_id else None
        
        # Update image if new image is uploaded
        if image:
            complaint.image = image

        complaint.save()
        messages.success(request, "Complaint Updated Successfully.")
        return redirect('my_complaints')

    context = {
        'complaint': complaint,
        'wards': wards,
        'categories': categories,
    }
    return render(request, 'complaints/edit_complaint.html', context)


@login_required(login_url='login')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "You are not authorized to edit this comment.")
        return redirect('post_detail', id=comment.complaint.id)

    if request.method == 'POST':
        content = request.POST.get('comment', '').strip()
        if content:
            comment.content = content
            comment.save()
            messages.success(request, "Comment updated successfully.")
            return redirect('post_detail', id=comment.complaint.id)

    return render(request, 'complaints/edit_comment.html', {'comment': comment, 'complaint': comment.complaint})
