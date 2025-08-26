from django.shortcuts import render, redirect
from complaints.models import Complaint

def home(request):
    # Check if logged in and session indicates frontend login
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect('admin_dashboard')
        
        elif request.user.user_type == 'municipality':
            return redirect('municipality_dashboard')
        
        elif request.user.user_type == 'user':
            complaints = Complaint.objects.select_related('ward', 'user', 'municipality', 'category').order_by('-created_at')[:4]
            return render(request, 'home.html', {'complaints': complaints})
        else:
            # Fallback: unknown user type
            return render(request, 'home.html')

    complaints = Complaint.objects.select_related('ward', 'user', 'municipality', 'category', 'status').order_by('-created_at')[:4]
    return render(request, 'home.html', {'complaints': complaints}) 