from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfile, Project, Bug, Notification
from django.http import HttpResponseForbidden



def edit_bug(request, bug_id):

    if not request.user.is_authenticated:
        return redirect('login')

    bug = get_object_or_404(Bug, pk=bug_id)

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    if not request.user.is_superuser and bug.tester.user != request.user and bug.selected_project.project_leader.user != request.user:
            return redirect('dashboard')

    if request.method == 'POST':
        notification_message = None
        if request.user.is_superuser or bug.tester.user == request.user:
            bug_name = request.POST.get('bug_name')
            bug_description = request.POST.get('bug_description')
            selected_project_id = request.POST.get('selected_project')
            tester_id = request.POST.get('tester')
            bug_category = request.POST.get('bug_category')
            total_time_spent = request.POST.get('total_time_spent')
            bug_priority = request.POST.get('bug_priority')
            cvss_score = request.POST.get('cvss_score')

            bug.bug_name = bug_name
            bug.bug_description = bug_description
            bug.selected_project_id = selected_project_id
            bug.tester_id = tester_id
            bug.bug_category = bug_category
            bug.total_time_spend = total_time_spent
            bug.bug_priority = bug_priority
            bug.cvss_score = cvss_score

        if request.user.is_superuser or bug.tester.user == request.user or bug.selected_project.project_leader.user == request.user:
            status = request.POST.get('status')
            if bug.status != status:
                notification_message = f"The  bug '{bug.bug_name}' has been '{status}'."
            bug.status = status

        bug.save()

        # Send notification if the project leader changed the status
        if notification_message:
            Notification.objects.create(
                sender=request.user,
                user=bug.tester.user,
                notification_type='info',
                message=notification_message
            )

        return redirect('all_bug')

    projects = Project.objects.all()
    testers = UserProfile.objects.filter(userrole='Tester')

    if request.user == bug.selected_project.project_leader.user:
        return render(request, 'edit_bug2.html', {'bug': bug, 'projects': projects, 'testers': testers, 'notifications':notifications,})
    
    else:
        return render(request, 'edit_bug.html', {'bug': bug, 'projects': projects, 'testers': testers, 'notifications':notifications,})


def delete_bug(request, bug_id):

    if not request.user.is_authenticated:
        return redirect('login')

    bug = get_object_or_404(Bug, pk=bug_id)

    if not request.user.is_superuser and bug.tester.user != request.user:
        return redirect('dashboard')
    
    user2 = User.objects.get(username=request.user)
    notification = Notification.objects.create(
    user = user2,
    notification_type='success',
    message=f'Bug {bug.bug_name} Deleted Successfully.'
    )

    bug.delete()
    return redirect('all_bug')


def bug_view(request, bug_id):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    bug = get_object_or_404(Bug, pk=bug_id)
    
    # Check if user is allowed to view this bug
    if not request.user.is_superuser and request.user != bug.tester.user and request.user != bug.selected_project.project_leader.user:
        return redirect('dashboard')  # Or any other appropriate redirection
    
    return render(request, 'view_bug.html', {'bug': bug, 'notifications':notifications,})

def closed_bug(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.user.is_superuser:
        bugs = Bug.objects.filter(status__iexact='closed').select_related('selected_project')
    elif request.user.userprofile.userrole == 'Tester':
        bugs = Bug.objects.filter(status__iexact='closed', tester=request.user.userprofile).select_related('selected_project')
    elif request.user.userprofile.userrole == 'Developer':  # Assuming project leader is considered as Developer
        projects_managed = Project.objects.filter(project_leader=request.user.userprofile)
        bugs = Bug.objects.filter(status__iexact='closed', selected_project__in=projects_managed).select_related('selected_project')
    else:
        # Redirect or handle case for other user roles (optional)
        return redirect('dashboard')  # Redirect to dashboard or any relevant page
    
    breadcrumb = "Closed Bug Reports"
    return render(request, 'bug_list.html', {'bugs': bugs, 'breadcrumb': breadcrumb, 'notifications':notifications,})

def open_bug(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.user.is_superuser:
        bugs = Bug.objects.filter(status__iexact='open').select_related('selected_project')
    elif request.user.userprofile.userrole == 'Tester':
        bugs = Bug.objects.filter(status__iexact='open', tester=request.user.userprofile).select_related('selected_project')
    elif request.user.userprofile.userrole == 'Developer':  # Assuming project leader is considered as Developer
        projects_managed = Project.objects.filter(project_leader=request.user.userprofile)
        bugs = Bug.objects.filter(status__iexact='open', selected_project__in=projects_managed).select_related('selected_project')
    else:
        # Redirect or handle case for other user roles (optional)
        return redirect('dashboard')  # Redirect to dashboard or any relevant page
    
    breadcrumb = "Open Bug Reports"
    return render(request, 'bug_list.html', {'bugs': bugs, 'breadcrumb': breadcrumb, 'notifications':notifications,})


def all_bug(request):

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.user.is_superuser:
        bugs = Bug.objects.all().select_related('selected_project')
    elif request.user.userprofile.userrole == 'Tester':
        bugs = Bug.objects.filter(tester=request.user.userprofile).select_related('selected_project')
    elif request.user.userprofile.userrole == 'Developer': 
        projects_managed = Project.objects.filter(project_leader=request.user.userprofile)
        bugs = Bug.objects.filter(selected_project__in=projects_managed).select_related('selected_project')
    else:
        return redirect('dashboard')  

    breadcrumb = "Bug Reports"
    return render(request, 'bug_list.html', {'bugs': bugs, 'breadcrumb': breadcrumb, 'notifications':notifications,})

def add_bug(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_superuser and user_profile.userrole != 'Tester':
        return redirect('dashboard')

    if request.method == "POST":
        bug_name = request.POST.get('bug_name')
        bug_description = request.POST.get('bug_description')
        selected_project_id = request.POST.get('selected_project')
        status = request.POST.get('status')
        tester_id = request.POST.get('tester')
        bug_category = request.POST.get('bug_category')
        total_time_spent = request.POST.get('total_time_spent')
        bug_priority = request.POST.get('bug_priority')
        cvss_score = request.POST.get('cvss_score')

        selected_project = Project.objects.get(id=selected_project_id)
        tester = UserProfile.objects.get(id=tester_id)

        Bug.objects.create(
            bug_name=bug_name,
            bug_description=bug_description,
            selected_project=selected_project,
            status=status,
            tester=tester,
            bug_category=bug_category,
            total_time_spend=total_time_spent,
            bug_priority=bug_priority,
            cvss_score=cvss_score
        )

        user2 = User.objects.get(username=tester)
        notification = Notification.objects.create(
        user = user2,
        notification_type='success',
        message=f'Bug {bug_name} Reported To {selected_project}'
        )

        user2 = User.objects.get(username=selected_project.project_leader)
        notification2 = Notification.objects.create(
        user = user2,
        notification_type='success',
        message=f'Bug {bug_name} Reported To {selected_project}'
        )

        return redirect('all_bug')

    projects = Project.objects.all()
    testers = UserProfile.objects.filter(userrole='Tester')
    return render(request, 'add_bug.html', {'projects': projects, 'testers': testers, 'notifications':notifications,})

def edit_project(request, project_id):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    project = get_object_or_404(Project, pk=project_id)

    if not request.user.is_superuser and project.project_leader.user != request.user:
        return redirect('dashboard')

    # Get all developers
    devs = User.objects.filter(userprofile__userrole='Developer').select_related('userprofile')

    if request.method == "POST":
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        client_company = request.POST.get('client_company')
        project_leader = request.POST.get('project_leader')
        estimated_project_duration = request.POST.get('estimated_project_duration')
        project_location = request.POST.get('project_location')
        status = request.POST.get('status')

        try:
            project_leader_profile = UserProfile.objects.get(user__username=project_leader)
        except UserProfile.DoesNotExist:
            project_leader_profile = None

        # Update the project instance with new data
        project.project_name = project_name
        project.project_description = project_description
        project.client_company = client_company
        project.project_leader = project_leader_profile
        project.estimated_project_duration = estimated_project_duration
        project.project_location = project_location
        project.status = status

        project.save()

        return redirect('all_project')
    context = {
        'project': project,
        'devs': devs,
        'notifications':notifications,
    }

    return render(request, 'edit_project.html', context)


def delete_project(request, project_id):

    if not request.user.is_authenticated:
        return redirect('login')

    project = get_object_or_404(Project, pk=project_id)

    if not request.user.is_superuser and project.project_leader.user != request.user:
        return redirect('dashboard')
    
    user2 = User.objects.get(username=request.user)
    notification = Notification.objects.create(
    user = user2,
    notification_type='success',
    message=f'Project {project.project_name} is Deleted Successfully'
    )
    
    project.delete()
    return redirect('all_project')

def project_view(request, project_id):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'view_project.html', {'project': project, 'notifications':notifications,})

def closed_project(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    closed_project = Project.objects.filter(status__in=['closed', 'Closed'])
    breadcrumb = "Closed Projects"
    return render(request, 'project_list.html', {'projects': closed_project, 'breadcrumb': breadcrumb, 'notifications':notifications,})

def open_project(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    open_projects = Project.objects.filter(status__in=['open', 'Open'])
    breadcrumb = "Open Projects"
    return render(request, 'project_list.html', {'projects': open_projects, 'breadcrumb': breadcrumb, 'notifications':notifications,})

def all_project(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    projects = Project.objects.all()
    breadcrumb = "Projects"
    for project in projects:
        num_of_bugs = Bug.objects.filter(selected_project=project).count()
        project.num_of_bugs = num_of_bugs 
    
    context = {
        'projects': projects,
        'breadcrumb':breadcrumb,
        'notifications':notifications,
    }
    return render(request, 'project_list.html', context)

def add_project(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_superuser and user_profile.userrole != 'Developer':
        return redirect('dashboard')
    
    devs = User.objects.filter(userprofile__userrole='Developer').select_related('userprofile')
    
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        #status = request.POST.get('status')
        client_company = request.POST.get('client_company')
        project_leader = request.POST.get('project_leader')
        estimated_project_duration = request.POST.get('estimated_project_duration')
        project_location = request.POST.get('project_location')

        try:
            project_leader_profile = UserProfile.objects.get(user__username=project_leader)
        except UserProfile.DoesNotExist:
            project_leader_profile = None


        Project.objects.create(
            project_name=project_name,
            project_description=project_description,
            #status=status,
            client_company=client_company,
            project_leader=project_leader_profile,
            estimated_project_duration=estimated_project_duration,
            project_location = project_location
        )

        if request.user.is_superuser:
            user2 = User.objects.get(username='admin')
            notification = Notification.objects.create(
            user = user2,
            notification_type='success',
            message=f'Project {project_name} is Added Successfully'
            )

        else: 
            user2 = User.objects.get(username=request.user)
            notification = Notification.objects.create(
            user = user2,
            notification_type='success',
            message=f'Project {project_name} is Added Successfully'
            )

        user2 = User.objects.get(username=project_leader)
        notification = Notification.objects.create(
        user = user2,
        notification_type='info',
        message=f'You are Leader of {project_name} Project'
        )

        return redirect('all_project')

    return render(request, 'add_project.html', {'devs':devs, 'notifications':notifications,})

def edit_user_profile(request, profile_id):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    profile = get_object_or_404(UserProfile, id=profile_id)

    if request.method == 'POST' and (request.user.is_superuser or request.user == profile.user):
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        profile_pic = request.FILES.get('profile_pic')  # Handle file upload
        
        # Update profile instance with new data
        profile.full_name = full_name
        profile.email = email  # Ensure email field is updated
        profile.mobile = mobile
        profile.address = address
        
        # Allow changing user role only if the user is a superuser
        if request.user.is_superuser:
            userrole = request.POST.get('userrole')
            profile.userrole = userrole

        if profile_pic:
            profile.profile_pic = profile_pic
        
        profile.save()

        return redirect('/')  # Redirect to homepage or profile view
    
    elif request.user.is_superuser or request.user == profile.user:
        context = {'profile': profile, 'is_superuser': request.user.is_superuser, 'notifications':notifications,}
        return render(request, 'edit_profile.html', context)
    
    else:
        return redirect('dashboard')

def delete_user(request, user_id):

    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_superuser:
        redirect(dashboard)

    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        logout(request)
        user.delete()
        return redirect('login')
    else:
        user2 = User.objects.get(username='admin')
        notification = Notification.objects.create(
        user = user2,
        notification_type='success',
        message=f'User {user} is Deleted Successfully'
        )

        user.delete()
        return redirect('user_list')

def tester_list(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    users = User.objects.filter(userprofile__userrole='Tester').select_related('userprofile')
    breadcrumb = "Testers"
    return render(request, 'users_list.html', {'users': users, 'breadcrumb':breadcrumb,'notifications':notifications,})

def dev_list(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    users = User.objects.filter(userprofile__userrole='Developer').select_related('userprofile')
    breadcrumb = "Developers"
    return render(request, 'users_list.html', {'users': users, 'breadcrumb':breadcrumb, 'notifications':notifications,})


def user_list(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    users = User.objects.all().select_related('userprofile')
    breadcrumb = "All Users"
    return render(request, 'users_list.html', {'users': users, 'breadcrumb':breadcrumb, 'notifications':notifications,})


def profile_view(request, user_id):

    if not request.user.is_authenticated:
        return redirect('login')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    profile = get_object_or_404(UserProfile, pk=user_id)
    return render(request, 'profile.html', {'profile': profile, 'notifications':notifications,})


#@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def add_user(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    if not request.user.is_superuser:
        return redirect('/')

    errors = []

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        full_name = request.POST.get('fullname')
        userrole = request.POST.get('userrole')

        if User.objects.filter(username=username).exists():
            errors.append('Username is already taken. Please choose a different username.')

        if User.objects.filter(email=email).exists():
            errors.append('Email is already in use. Please choose a different email.')

        try:
            validate_password(password)
        except ValidationError as e:
            errors.extend(e.messages)

        if errors:
            return render(request, 'register.html', {'errors': errors})

        user = User.objects.create_user(username=username, password=password, email=email)

        if userrole == 'admin':
            user.is_staff = True

        user.save()

        profile = UserProfile(user=user, email=email, full_name=full_name, userrole=userrole)
        profile.save()

        admin_user = User.objects.get(username='admin')
        notification = Notification.objects.create(
            user=admin_user,
            notification_type='success',
            message='New User Added'
        )

        return redirect('/')

    return render(request, 'register.html')

def logout_user(request):

    if not request.user.is_authenticated:
        return redirect('login')

    logout(request)
    return redirect('login')

#@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        #try:
        user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
        
        #except ratelimit.exceptions.Ratelimited as e:
            # Handle rate limit exceeded scenario
            #return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
    
    return render(request, 'login.html')

def delete_notification(request, notification_id):

    if not request.user.is_authenticated:
        return redirect('login')

    notification = get_object_or_404(Notification, pk=notification_id)

    if request.user == notification.user:
        notification.delete()
        return redirect('view_notifications') 
    
    else:
        return redirect('dashboard') 


def view_notifications(request):

    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications
    }
    
    return render(request, 'notifications.html', context)


def contact(request):
    return render(request, 'contact.html')


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = UserProfile.objects.get(user=request.user)

    total_projects = Project.objects.count()
    total_bugs = Bug.objects.count()
    total_users = UserProfile.objects.count()
    total_active_bugs = Bug.objects.filter(status__iexact='open').count()

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'total_projects': total_projects,
        'total_bugs': total_bugs,
        'total_users': total_users,
        'total_active_bugs': total_active_bugs,
        'user_profile':user_profile,
        'notifications':notifications,
    }
    
    return render(request, 'dashboard.html', context)