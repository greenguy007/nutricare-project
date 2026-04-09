from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
from django.contrib.auth import authenticate
import random
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'index.html')

# def adm(request):
#     adm=Login.objects.create_superuser(username='admin',email='admin@gmail.com',viewpassword='admin',password='admin',usertype='admin')
#     adm.save()
#     return redirect('/')


def customer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        image = request.FILES.get('image')

        if Login.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('customer_register')

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone already exists')
            return redirect('customer_register')

        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('customer_register')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email')
            return redirect('customer_register')

        otp = str(random.randint(100000, 999999))

        login = Login.objects.create_user(
            username=username,
            email=email,
            usertype='customer',
            otp=otp,
            is_verified=False,
            is_active=False
        )

        Customer.objects.create(
            login=login,
            full_name=full_name,
            phone=phone,
            address=address,
            email=email,
            image=image
        )

        send_mail(
            subject='Your OTP for Registration',
            message=f'Your OTP is {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        request.session['otp_user_id'] = login.id
        messages.success(request, 'OTP sent to your email')
        return redirect('otp_verify')

    return render(request, 'customer_register.html')


import string

def otp_verify(request):
    user_id = request.session.get('otp_user_id')

    if not user_id:
        return redirect('customer_register')

    user = Login.objects.get(id=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'resend':
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()
            
            try:
                send_mail(
                    subject='Your OTP for Registration',
                    message=f'Your OTP is {otp}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                )
                messages.success(request, 'New OTP sent to your email')
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
        else:
            otp = request.POST.get('otp')

            if user.otp == otp:
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                user.set_password(password)
                user.viewpassword = password
                user.otp = None
                user.is_verified = True
                user.is_active = True
                user.save()

                try:
                    send_mail(
                        subject='Your Login Password',
                        message=f'Your account is verified.\nUsername: {user.username}\nPassword: {password}',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                    )
                except Exception as e:
                    user.save()
                    print(f"Email send failed: {e}")

                del request.session['otp_user_id']
                messages.success(request, 'Account verified. Password sent to email')
                return redirect('login')

            else:
                messages.error(request, 'Invalid OTP')

    return render(request, 'otp.html')


def dietician_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        license_file = request.FILES.get('license_file')   # ✅ NEW

        if Login.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('dietician_register')

        if Dietician.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists')
            return redirect('dietician_register')

        if Dietician.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('dietician_register')

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Phone must be 10 digits')
            return redirect('dietician_register')

        if not (email.endswith('@gmail.com') or email.endswith('@gmail.in')):
            messages.error(request, 'Email must be gmail.com or gmail.in')
            return redirect('dietician_register')
        
        # if license_file and not license_file.name.endswith('.pdf'):
        #     messages.error(request, 'License must be a PDF file')
        #     return redirect('dietician_register')
        

        login = Login.objects.create_user(
            username=username,
            password=password,
            email=email,
            usertype='dietician',
            viewpassword=password,
            is_active=False
        )

        Dietician.objects.create(
            login=login,
            full_name=full_name,
            phone=phone,
            address=address,
            email=email,
            image=image,
            license_file=license_file   # ✅ NEW
        )

        messages.success(request, 'Registration successful. Await admin approval.')
        return redirect('dietician_register')

    return render(request, 'dietician_register.html')



def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

def dietician_dashboard(request):
    return render(request,'dietician/dietician_dashboard.html')

def customer_dashboard(request):
    return render(request,'customer/customer_dashboard.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active is False:
                messages.error(request, 'Your account is not approved yet')
                return redirect('login')

            request.session['login_id'] = user.id
            request.session['usertype'] = user.usertype

            if user.usertype == 'admin':
                messages.success(request, 'Login as Admin successful')
                return redirect('admin_dashboard')

            elif user.usertype == 'dietician':
                messages.success(request, 'Login as Dietician successful')
                return redirect('dietician_dashboard')

            elif user.usertype == 'customer':
                messages.success(request, 'Login as Customer successful')
                return redirect('customer_dashboard')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



def view_all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'admin/view_all_customers.html', {'customers': customers})


def verify_customer(request, id):
    customer = Customer.objects.get(id=id)
    login = customer.login
    import string
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    login.set_password(password)
    login.viewpassword = password
    login.is_verified = True
    login.is_active = True
    login.otp = None
    login.save()
    try:
        send_mail(
            subject='Your Login Password',
            message=f'Your account is verified.\nUsername: {login.username}\nPassword: {password}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[login.email],
        )
    except:
        pass
    messages.success(request, 'Customer verified. Password sent to email')
    return redirect('view_all_customers')


def delete_customer(request, id):
    from django.db import connection
    try:
        customer = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer not found')
        return redirect('view_all_customers')
    
    login = customer.login
    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        Chat.objects.filter(sender=login).delete()
        Chat.objects.filter(receiver=login).delete()
        CustomerDietPlan.objects.filter(customer=customer).delete()
        CustomerDietStep.objects.filter(customer_diet_plan__customer=customer).delete()
        CustomerBMI.objects.filter(customer=customer).delete()
        CustomerBMR.objects.filter(customer=customer).delete()
        CustomerMeal.objects.filter(customer=customer).delete()
        DietFeedback.objects.filter(customer=customer).delete()
        DietCustomizationRequest.objects.filter(customer=customer).delete()
        CustomDietPlan.objects.filter(customer=customer).delete()
        CustomDietStep.objects.filter(custom_plan__customer=customer).delete()
        WorkoutFeedback.objects.filter(customer=customer).delete()
        WorkoutPurchase.objects.filter(customer=customer).delete()
        
        diet_plans = DietPlan.objects.filter(dietician=login)
        for dp in diet_plans:
            DietStep.objects.filter(diet_plan=dp).delete()
            CustomerDietPlan.objects.filter(diet_plan=dp).delete()
            DietFeedback.objects.filter(diet_plan=dp).delete()
            DietCustomizationRequest.objects.filter(diet_plan=dp).delete()
            dp.delete()
        
        DietPlanPDF.objects.filter(dietician=login).delete()
        Food.objects.filter(dietician=login).delete()
        
        customer.delete()
        login.delete()
        
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()
        
        messages.success(request, 'Customer deleted successfully')
    except Exception as e:
        try:
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()
        except:
            pass
        messages.error(request, f'Error deleting customer: {str(e)}')
    return redirect('view_all_customers')


def view_all_dieticians(request):
    dieticians = Dietician.objects.all()
    return render(request, 'admin/view_all_dieticians.html', {'dieticians': dieticians})

def view_dietician_profile(request, id):
    dietician = Dietician.objects.get(id=id)
    return render(request, 'admin/view_dietician_profile.html', {'d': dietician})


def approve_dietician(request, id):
    dietician = Dietician.objects.get(id=id)
    dietician.login.is_active = True
    dietician.login.save()
    messages.success(request, 'Dietician approved successfully')
    return redirect('view_all_dieticians')


def reject_dietician(request, id):
    dietician = Dietician.objects.get(id=id)
    dietician.login.is_active = False
    dietician.login.save()
    messages.success(request, 'Dietician rejected (deactivated)')
    return redirect('view_all_dieticians')


def delete_dietician(request, id):
    dietician = Dietician.objects.get(id=id)
    login = dietician.login
    dietician.delete()
    login.delete()
    messages.success(request, 'Dietician permanently deleted')
    return redirect('view_all_dieticians')


def add_dietplans(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    if request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        steps = request.POST.getlist('steps[]')

        plan_type = request.POST.get('plan_type')
        price = request.POST.get('price')

        if plan_type == 'free':
            price = 0

        dietician = Login.objects.get(id=request.session['login_id'])

        diet_plan = DietPlan.objects.create(
            dietician=dietician,
            plan_name=plan_name,
            description=description,
            image=image,
            plan_type=plan_type,
            price=price
        )

        for step in steps:
            if step.strip():
                DietStep.objects.create(
                    diet_plan=diet_plan,
                    step_text=step
                )

        messages.success(request, 'Diet plan added successfully')
        return redirect('add_dietplans')

    return render(request, 'dietician/add_dietplans.html')


def view_diet_plans(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    dietician = Login.objects.get(id=request.session['login_id'])
    plans = DietPlan.objects.filter(dietician=dietician)

    return render(request, 'dietician/view_diet_plans.html', {'plans': plans})


def edit_diet_plan(request, plan_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    diet_plan = DietPlan.objects.get(id=plan_id)
    steps = diet_plan.steps.all()

    if request.method == 'POST':
        diet_plan.plan_name = request.POST.get('plan_name')
        diet_plan.description = request.POST.get('description')

        if request.FILES.get('image'):
            diet_plan.image = request.FILES.get('image')

        diet_plan.save()

        DietStep.objects.filter(diet_plan=diet_plan).delete()

        step_list = request.POST.getlist('steps[]')
        for step in step_list:
            if step.strip():
                DietStep.objects.create(
                    diet_plan=diet_plan,
                    step_text=step
                )
        messages.success(request, 'Diet plan updated successfully')
        return redirect('view_diet_plans')

    return render(request, 'dietician/edit_diet_plan.html', {
        'diet_plan': diet_plan,
        'steps': steps
    })


def delete_diet_plan(request, plan_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    diet_plan = DietPlan.objects.get(id=plan_id)
    diet_plan.delete()
    messages.success(request, 'Diet plan deleted successfully')
    return redirect('view_diet_plans')


def view_all_diets(request):
    if request.session.get('usertype') != 'admin':
        return redirect('login')

    plans = DietPlan.objects.all()  # Admin can see all diet plans
    return render(request, 'admin/view_all_diets.html', {'plans': plans})


def view_customer_diets(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    plans = DietPlan.objects.all()

    search = request.GET.get('search')
    dietician = request.GET.get('dietician')

    if search:
        plans = plans.filter(plan_name__icontains=search)

    if dietician:
        plans = plans.filter(dietician__id=dietician)

    dieticians = Login.objects.filter(usertype='dietician')

    return render(request, 'customer/view_customer_diets.html', {
        'plans': plans,
        'dieticians': dieticians
    })


def request_custom_diet(request, plan_id):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    plan = DietPlan.objects.get(id=plan_id)

    # If Paid → payment first
    if plan.plan_type == 'paid':
        return redirect('payment_page', plan_id=plan.id, action='request')

    return render(request, 'customer/request_custom_diet.html', {'plan': plan})

def payment_page(request, plan_id, action):
    plan = DietPlan.objects.get(id=plan_id)
    customer = Customer.objects.get(login_id=request.session['login_id'])

    if request.method == 'POST':
        # After payment success
        if action == 'join':
            customer_diet = CustomerDietPlan.objects.create(
                customer=customer,
                diet_plan=plan
            )

            for step in plan.steps.all():
                CustomerDietStep.objects.create(
                    customer_diet_plan=customer_diet,
                    diet_step=step
                )

            messages.success(request, 'Payment successful & joined plan')
            return redirect('view_joined_diets')

        elif action == 'request':
            notes = request.POST.get('notes')

            DietCustomizationRequest.objects.create(
                customer=customer,
                dietician=plan.dietician,
                diet_plan=plan,
                notes=notes
            )

            messages.success(request, 'Payment successful & request sent')
            return redirect('view_customer_diets')

    return render(request, 'customer/payment.html', {
        'plan': plan,
        'action': action
    })


def view_custom_diet_requests(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    dietician = Login.objects.get(id=request.session['login_id'])

    requests = DietCustomizationRequest.objects.filter(
        dietician=dietician
    ).order_by('-created_at')

    return render(
        request,
        'dietician/view_custom_diet_requests.html',
        {'requests': requests}
    )


def create_custom_diet_plan(request, request_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    diet_request = DietCustomizationRequest.objects.get(id=request_id)

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        steps = request.POST.getlist('steps')

        custom_plan = CustomDietPlan.objects.create(
            customer=diet_request.customer,
            dietician=diet_request.dietician,
            request=diet_request,
            title=title,
            description=description
        )

        for step in steps:
            if step.strip():
                CustomDietStep.objects.create(
                    custom_plan=custom_plan,
                    step_text=step
                )

        diet_request.status = 'approved'
        diet_request.save()

        return redirect('view_custom_diet_requests')

    return render(
        request,
        'dietician/create_custom_diet_plan.html',
        {'diet_request': diet_request}
    )


def view_customer_custom_diet_plans(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])

    custom_plans = CustomDietPlan.objects.filter(
        customer=customer
    ).order_by('-created_at')

    return render(
        request,
        'customer/view_custom_diet_plans.html',
        {'custom_plans': custom_plans}
    )

def toggle_custom_diet_step(request, step_id):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])

    step = CustomDietStep.objects.get(id=step_id)

    if step.custom_plan.customer != customer:
        return redirect('view_customer_custom_diet_plans')

    step.is_completed = not step.is_completed
    step.save()

    return redirect('view_customer_custom_diet_plans')


def join_diet_plan(request, plan_id):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    plan = DietPlan.objects.get(id=plan_id)

    # Already joined
    if CustomerDietPlan.objects.filter(customer=customer, diet_plan=plan).exists():
        return redirect('view_joined_diets')

    # If Paid → go to payment
    if plan.plan_type == 'paid':
        return redirect('payment_page', plan_id=plan.id, action='join')

    # Free → direct join
    customer_diet = CustomerDietPlan.objects.create(
        customer=customer,
        diet_plan=plan
    )

    for step in plan.steps.all():
        CustomerDietStep.objects.create(
            customer_diet_plan=customer_diet,
            diet_step=step
        )

    return redirect('view_joined_diets')



def view_joined_diets(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    joined_plans = CustomerDietPlan.objects.filter(customer=customer)

    data = []

    for jp in joined_plans:
        steps = jp.customerdietstep_set.all()
        all_done = all(step.is_completed for step in steps)

        feedback_exists = DietFeedback.objects.filter(
            customer=customer,
            diet_plan=jp.diet_plan
        ).exists()

        data.append({
            'jp': jp,
            'all_done': all_done,
            'feedback_given': feedback_exists
        })

    return render(request, 'customer/view_joined_diets.html', {
        'data': data
    })


def add_feedback(request, plan_id):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    plan = DietPlan.objects.get(id=plan_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')

        DietFeedback.objects.create(
            customer=customer,
            diet_plan=plan,
            rating=rating,
            feedback=feedback
        )

        return redirect('view_joined_diets')

    return render(request, 'customer/add_feedback.html', {'plan': plan})

def update_diet_steps(request, customer_diet_id):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer_diet = CustomerDietPlan.objects.get(id=customer_diet_id)
    selected_steps = request.POST.getlist('steps')

    for step in customer_diet.customerdietstep_set.all():
        step.is_completed = str(step.id) in selected_steps
        step.save()

    return redirect('view_joined_diets')


def joined_customers_diet_plans(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    dietician_id = request.session['login_id']

    plans = DietPlan.objects.filter(dietician_id=dietician_id)

    data = []

    for plan in plans:
        joined_customers = CustomerDietPlan.objects.filter(diet_plan=plan)

        for jc in joined_customers:
            total_steps = plan.steps.count()
            completed_steps = CustomerDietStep.objects.filter(
                customer_diet_plan=jc,
                is_completed=True
            ).count()

            percentage = 0
            if total_steps > 0:
                percentage = int((completed_steps / total_steps) * 100)

            data.append({
                'plan_name': plan.plan_name,
                'customer': jc.customer.full_name,
                'completed': completed_steps,
                'total': total_steps,
                'percentage': percentage
            })

    return render(request, 'dietician/joined_customers_diet_plans.html', {'data': data})


def all_joined_diet_plans(request):
    if request.session.get('usertype') != 'admin':
        return redirect('login')

    joined = CustomerDietPlan.objects.select_related('customer', 'diet_plan')

    data = []

    for j in joined:
        total_steps = j.diet_plan.steps.count()
        completed_steps = CustomerDietStep.objects.filter(
            customer_diet_plan=j,
            is_completed=True
        ).count()

        percentage = 0
        if total_steps > 0:
            percentage = int((completed_steps / total_steps) * 100)

        data.append({
            'dietician': j.diet_plan.dietician.username,
            'customer': j.customer.full_name,
            'plan': j.diet_plan.plan_name,
            'completed': completed_steps,
            'total': total_steps,
            'percentage': percentage
        })

    return render(request, 'admin/all_joined_diet_plans.html', {'data': data})


def customer_profile(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    login_id = request.session['login_id']
    customer = Customer.objects.get(login_id=login_id)

    return render(request, 'customer/customer_profile.html', {'customer': customer})

def dietician_profile(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    login_id = request.session['login_id']
    dietician = Dietician.objects.get(login_id=login_id)

    return render(request, 'dietician/dietician_profile.html', {'dietician': dietician})


def edit_customer_profile(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])

    if request.method == 'POST':
        customer.full_name = request.POST.get('full_name')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')

        if request.FILES.get('image'):
            customer.image = request.FILES.get('image')

        customer.save()
        return redirect('customer_profile')

    return render(request, 'customer/edit_customer_profile.html', {
        'customer': customer
    })



def edit_dietician_profile(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    dietician = Dietician.objects.get(login_id=request.session['login_id'])

    if request.method == 'POST':
        dietician.full_name = request.POST.get('full_name')
        dietician.phone = request.POST.get('phone')
        dietician.address = request.POST.get('address')

        if request.FILES.get('image'):
            dietician.image = request.FILES.get('image')

        dietician.save()
        return redirect('dietician_profile')

    return render(request, 'dietician/edit_dietician_profile.html', {
        'dietician': dietician
    })


def add_bmi(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    bmi_status = None
    bmi_value = None

    if request.method == 'POST':
        height_cm = float(request.POST.get('height_cm'))
        weight_kg = float(request.POST.get('weight_kg'))

        height_m = height_cm / 100
        bmi_value = round(weight_kg / (height_m ** 2), 2)

        # Determine status
        if bmi_value < 18.5:
            bmi_status = "Underweight"
        elif bmi_value < 24.9:
            bmi_status = "Healthy"
        elif bmi_value < 29.9:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese"

        # Save to DB
        CustomerBMI.objects.create(
            customer=customer,
            height_cm=height_cm,
            weight_kg=weight_kg,
            bmi=bmi_value
        )

    return render(request, 'customer/add_bmi.html', {'bmi_status': bmi_status, 'bmi_value': bmi_value})


def upload_diet_plan_pdf(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    dietician = Login.objects.get(id=request.session['login_id'])

    if request.method == 'POST':
        title = request.POST.get('title')
        pdf_file = request.FILES.get('pdf_file')

        DietPlanPDF.objects.create(
            dietician=dietician,
            title=title,
            pdf_file=pdf_file
        )
        messages.success(request, 'Diet plan PDF uploaded successfully')
        return redirect('view_diet_plan_pdfs')

    return render(request, 'dietician/upload_diet_plan_pdf.html')


def view_diet_plan_pdfs(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    pdfs = DietPlanPDF.objects.filter(dietician_id=request.session['login_id'])
    return render(request, 'dietician/view_diet_plan_pdfs.html', {'pdfs': pdfs})


def customer_view_diet_plan_pdfs(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    pdfs = DietPlanPDF.objects.all()
    return render(request, 'customer/view_diet_plan_pdfs.html', {'pdfs': pdfs})

def admin_view_diet_plan_pdfs(request):
    if request.session.get('usertype') != 'admin':
        return redirect('login')

    pdfs = DietPlanPDF.objects.all()
    return render(request, 'admin/view_all_diet_plan_pdfs.html', {'pdfs': pdfs})


def dietician_edit_pdf(request, pdf_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    pdf = get_object_or_404(DietPlanPDF, id=pdf_id)

    if request.method == 'POST':
        pdf.title = request.POST.get('title')

        if request.FILES.get('pdf_file'):
            pdf.pdf_file = request.FILES.get('pdf_file')

        pdf.save()
        return redirect('view_diet_plan_pdfs')

    return render(request, 'dietician/edit_diet_plan_pdf.html', {'pdf': pdf})


def dietician_delete_pdf(request, pdf_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    pdf = get_object_or_404(DietPlanPDF, id=pdf_id)
    pdf.delete()
    return redirect('view_diet_plan_pdfs')



def ChatBot(request):
    import os
    os.system("python chatgui.py")  # Runs the Python file
    print("hello world hiiii")
    return redirect("customer_dashboard")


def add_food(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    if request.method == 'POST':
        Food.objects.create(
            dietician_id=request.session['login_id'],
            name=request.POST['name'],
            meal_type=request.POST['meal_type'],
            calories=request.POST['calories'],
            carbs=request.POST['carbs'],
            protein=request.POST['protein'],
            fat=request.POST['fat'],
            zinc=request.POST['zinc'],
        )
        messages.success(request, 'Food added successfully')
        return redirect('add_food')

    return render(request, 'dietician/add_food.html')

def view_foods(request):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    foods = Food.objects.filter(dietician_id=request.session['login_id'])
    return render(request, 'dietician/view_foods.html', {'foods': foods})


def edit_food(request, food_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    food = get_object_or_404(Food, id=food_id, dietician_id=request.session['login_id'])

    if request.method == 'POST':
        food.name = request.POST['name']
        food.meal_type = request.POST['meal_type']
        food.calories = request.POST['calories']
        food.carbs = request.POST['carbs']
        food.protein = request.POST['protein']
        food.fat = request.POST['fat']
        food.zinc = request.POST['zinc']
        food.save()
        messages.success(request, 'Food updated successfully')
        return redirect('view_foods')

    return render(request, 'dietician/edit_food.html', {'food': food})


def delete_food(request, food_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    food = get_object_or_404(Food, id=food_id, dietician_id=request.session['login_id'])
    food.delete()
    messages.success(request, 'Food deleted successfully')
    return redirect('view_foods')

from datetime import date


def select_food_today(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    foods = Food.objects.all()

    meal_categories = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    ]

    if request.method == 'POST':
        food_ids = request.POST.getlist('food')
        for fid in food_ids:
            CustomerMeal.objects.create(
                customer=customer,
                food_id=fid
            )
        messages.success(request, 'Food added for today')
        return redirect('today_report')

    return render(request, 'customer/select_food.html', {
        'foods': foods,
        'meal_categories': meal_categories
    })



def today_report(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    meals = CustomerMeal.objects.filter(customer=customer, date=date.today())

    total = {
        'calories': 0,
        'carbs': 0,
        'protein': 0,
        'fat': 0,
        'zinc': 0
    }

    for meal in meals:
        total['calories'] += meal.food.calories
        total['carbs'] += meal.food.carbs
        total['protein'] += meal.food.protein
        total['fat'] += meal.food.fat
        total['zinc'] += meal.food.zinc

    if total['calories'] >= 2000 and total['protein'] >= 50:
        status = "Good"
    elif total['calories'] >= 1500:
        status = "Average"
    else:
        status = "Bad"

    return render(request, 'customer/today_report.html', {
        'total': total,
        'status': status
    })

def display_all_food(request):
    if request.session.get('usertype') != 'admin':
        return redirect('login')

    foods = Food.objects.all().order_by('meal_type')  # you can also order by dietician or date
    return render(request, 'admin/display_all_food.html', {'foods': foods})

# import requests
# from django.shortcuts import render

# def system_ip_location(request):

#     # Get PUBLIC IP of system
#     public_ip = requests.get('https://api.ipify.org').text

#     response = requests.get(f"http://ip-api.com/json/{public_ip}")
#     data = response.json()

#     context = {
#         'ip': public_ip,
#         'country': data.get('country'),
#         'region': data.get('regionName'),
#         'city': data.get('city'),
#         'isp': data.get('isp'),
#     }

#     return render(request, 'ip_location.html', context)



def customer_dietician_list(request):
    dieticians = Dietician.objects.all()
    return render(request, 'customer/dietician_list.html', {'dieticians': dieticians})


def dietician_customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'dietician/customer_list.html', {'customers': customers})


def customer_chat(request, did):
    if 'login_id' not in request.session:
        return redirect('login')

    sender = Login.objects.get(id=request.session['login_id'])

    dietician = Dietician.objects.filter(id=did).first()
    if not dietician:
        return redirect('customer_dietician_list')

    receiver = dietician.login

    if request.method == 'POST':
        msg = request.POST.get('message')
        Chat.objects.create(
            sender=sender,
            receiver=receiver,
            message=msg
        )

    chats = Chat.objects.filter(
        sender__in=[sender, receiver],
        receiver__in=[sender, receiver]
    ).order_by('date')

    return render(request, 'customer/chat.html', {
        'receiver': receiver,
        'chats': chats,
        'login_id': request.session['login_id']
    })



def dietician_chat(request, cid):
    if 'login_id' not in request.session:
        return redirect('login')

    sender = Login.objects.get(id=request.session['login_id'])

    customer = Customer.objects.filter(id=cid).first()
    if not customer:
        return redirect('dietician_customer_list')

    receiver = customer.login

    if request.method == 'POST':
        msg = request.POST.get('message')
        Chat.objects.create(
            sender=sender,
            receiver=receiver,
            message=msg
        )

    chats = Chat.objects.filter(
        sender__in=[sender, receiver],
        receiver__in=[sender, receiver]
    ).order_by('date')

    return render(request, 'dietician/chat.html', {
        'receiver': receiver,
        'chats': chats,
        'login_id': request.session['login_id']
    })



def add_workout_plan(request):
    if 'login_id' not in request.session:
        return redirect('login')

    dietician = Dietician.objects.get(login_id=request.session['login_id'])

    if request.method == "POST":
        title = request.POST.get('title').strip()
        description = request.POST.get('description').strip()
        plan_image = request.FILES.get('plan_image')
        plan_video = request.FILES.get('plan_video')

        plan_type = request.POST.get('plan_type')
        price = request.POST.get('price')

        is_free = True if plan_type == 'free' else False

        plan = WorkoutPlan.objects.create(
            dietician=dietician,
            title=title,
            description=description,
            image=plan_image,
            video=plan_video,
            is_free=is_free,
            price=price if not is_free else None
        )

        step_numbers = request.POST.getlist('step_number')
        step_titles = request.POST.getlist('step_title')
        step_descriptions = request.POST.getlist('step_description')
        step_images = request.FILES.getlist('step_image')

        for i in range(len(step_numbers)):
            WorkoutStep.objects.create(
                plan=plan,
                step_number=int(step_numbers[i]),
                title=step_titles[i],
                description=step_descriptions[i],
                image=step_images[i]
            )

        messages.success(request, 'Workout plan added successfully')
        return redirect('workout_plan_list')

    return render(request, 'dietician/add_workout_plans.html')


def workout_plan_list(request):
    login_id = request.session.get('login_id')
    dietician = Dietician.objects.get(login_id=login_id)
    plans = WorkoutPlan.objects.filter(dietician=dietician)
    return render(request,'dietician/workout_plan_list.html',{'plans':plans})


def edit_workout_plan(request, plan_id):
    if request.session.get('usertype') != 'dietician':
        return redirect('login')

    plan = WorkoutPlan.objects.get(id=plan_id)
    steps = WorkoutStep.objects.filter(plan=plan).order_by('step_number')

    if request.method == 'POST':

        # -------- PLAN UPDATE --------
        plan.title = request.POST.get('title')
        plan.description = request.POST.get('description')

        plan_type = request.POST.get('plan_type')
        price = request.POST.get('price')

        plan.is_free = True if plan_type == 'free' else False
        plan.price = None if plan.is_free else price

        if request.FILES.get('image'):
            plan.image = request.FILES.get('image')

        if request.FILES.get('video'):
            plan.video = request.FILES.get('video')

        plan.save()

        # -------- UPDATE EXISTING STEPS --------
        step_ids = request.POST.getlist('step_id')

        for step_id in step_ids:
            step = WorkoutStep.objects.get(id=step_id)

            step.step_number = request.POST.get(f'step_number_{step_id}')
            step.title = request.POST.get(f'step_title_{step_id}')
            step.description = request.POST.get(f'step_description_{step_id}')

            if request.FILES.get(f'step_image_{step_id}'):
                step.image = request.FILES.get(f'step_image_{step_id}')

            step.save()

        # -------- ADD NEW STEPS --------
        new_numbers = request.POST.getlist('new_step_number')
        new_titles = request.POST.getlist('new_step_title')
        new_descs = request.POST.getlist('new_step_description')
        new_images = request.FILES.getlist('new_step_image')

        for i in range(len(new_numbers)):
            if new_numbers[i] and new_titles[i] and new_descs[i]:
                WorkoutStep.objects.create(
                    plan=plan,
                    step_number=new_numbers[i],
                    title=new_titles[i],
                    description=new_descs[i],
                    image=new_images[i] if i < len(new_images) else None
                )

        return redirect('workout_plan_list')

    return render(request, 'dietician/edit_workout_plans.html', {
        'plan': plan,
        'steps': steps
    })


def delete_workout_step(request, step_id):
    step = WorkoutStep.objects.get(id=step_id)
    plan_id = step.plan.id
    step.delete()
    messages.success(request, 'Workout step deleted successfully')
    return redirect('edit_workout_plan', plan_id=plan_id)

def delete_workout_plan(request, plan_id):
    plan = WorkoutPlan.objects.get(id=plan_id)
    plan.delete()
    messages.success(request, 'Workout plan deleted successfully')
    return redirect('workout_plan_list')


def workout_detail(request, plan_id):
    if 'login_id' not in request.session:
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    plan = WorkoutPlan.objects.get(id=plan_id)

    if not plan.is_free:
        if not WorkoutPurchase.objects.filter(customer=customer, plan=plan).exists():
            return redirect('workout_payment', plan_id=plan.id)

    steps = WorkoutStep.objects.filter(plan=plan)

    return render(request, 'customer/workout_detail.html', {
        'plan': plan,
        'steps': steps
    })

def workout_detail(request, plan_id):
    if 'login_id' not in request.session:
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    plan = WorkoutPlan.objects.get(id=plan_id)

    # check purchase
    if not plan.is_free:
        if not WorkoutPurchase.objects.filter(customer=customer, plan=plan).exists():
            return redirect('workout_payment', plan_id=plan.id)

    steps = WorkoutStep.objects.filter(plan=plan)

    # SAVE FEEDBACK
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        WorkoutFeedback.objects.create(
            customer=customer,
            plan=plan,
            rating=rating,
            comment=comment
        )

    feedbacks = WorkoutFeedback.objects.filter(plan=plan).order_by('-id')

    return render(request, 'customer/workout_detail.html', {
        'plan': plan,
        'steps': steps,
        'feedbacks': feedbacks
    })



def workout_payment(request, plan_id):
    if 'login_id' not in request.session:
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])
    plan = WorkoutPlan.objects.get(id=plan_id)

    # already purchased
    if WorkoutPurchase.objects.filter(customer=customer, plan=plan).exists():
        return redirect('workout_detail', plan_id=plan.id)

    if request.method == "POST":
        WorkoutPurchase.objects.create(
            customer=customer,
            plan=plan
        )
        return redirect('workout_detail', plan_id=plan.id)

    return render(request, 'customer/workout_payment.html', {'plan': plan})

def view_workout_customer(request):
    login_id = request.session.get('login_id')

    if not login_id:
        return redirect('login')

    customer = Customer.objects.get(login_id=login_id)

    plans = WorkoutPlan.objects.all()

    # 🔍 SEARCH
    search = request.GET.get('search')
    if search:
        plans = plans.filter(title__icontains=search)

    # 🎯 FILTER
    filter_type = request.GET.get('filter')

    if filter_type == 'free':
        plans = plans.filter(is_free=True)

    elif filter_type == 'paid':
        plans = plans.filter(is_free=False)

    elif filter_type == 'purchased':
        purchased = WorkoutPurchase.objects.filter(customer=customer)
        plans = plans.filter(id__in=purchased.values_list('plan_id', flat=True))

    plans = plans.prefetch_related('workoutstep_set')

    purchased = WorkoutPurchase.objects.filter(customer=customer)
    purchased_plan_ids = purchased.values_list('plan_id', flat=True)

    return render(request, 'customer/view_workout_customer.html', {
        'plans': plans,
        'customer': customer,
        'purchased_plan_ids': purchased_plan_ids
    })

    
def view_all_workouts(request):
    workouts = WorkoutPlan.objects.all().order_by('-id')
    return render(request, 'admin/view_all_workouts.html', {'workouts': workouts})


def view_workout_details(request, id):
    workout = WorkoutPlan.objects.get(id=id)
    steps = WorkoutStep.objects.filter(plan=workout).order_by('step_number')
    return render(request, 'admin/view_workout_details.html', {
        'workout': workout,
        'steps': steps
    })


def calculate_bmr(request):
    if request.session.get('usertype') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(login_id=request.session['login_id'])

    bmr_value = None

    if request.method == 'POST':
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        height = float(request.POST.get('height'))
        weight = float(request.POST.get('weight'))

        if gender == 'male':
            bmr_value = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr_value = 10 * weight + 6.25 * height - 5 * age - 161

        CustomerBMR.objects.create(
            customer=customer,
            age=age,
            gender=gender,
            height_cm=height,
            weight_kg=weight,
            bmr=bmr_value
        )

    history = CustomerBMR.objects.filter(customer=customer).order_by('-id')

    return render(request, 'customer/calculate_bmr.html', {
        'bmr': bmr_value,
        'history': history
    })


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('EMAIL', '')
        if email:
            try:
                send_mail(
                    subject='Welcome to NutriScan Newsletter!',
                    message=(
                        f'Hi,\n\n'
                        f'Thank you for subscribing to NutriScan Newsletter!\n\n'
                        f'This email confirms that your subscription has been activated. '
                        f'You\'ll receive the latest health tips, diet plans, workout guides, '
                        f'and exclusive offers right in your inbox.\n\n'
                        f'Here\'s what you can expect:\n'
                        f'  • Weekly nutrition & diet tips\n'
                        f'  • Healthy recipe ideas\n'
                        f'  • Exclusive discounts on diet plans\n'
                        f'  • Motivational fitness content\n\n'
                        f'Stay healthy and keep eating smart!\n\n'
                        f'Best regards,\n'
                        f'The NutriScan Team'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                )
                messages.success(request, f'Subscription confirmed! A welcome email has been sent to {email}.')
            except Exception as e:
                messages.error(request, 'Failed to send email. Please try again later.')
        else:
            messages.error(request, 'Please provide a valid email address.')

    return redirect('index')


def admin_feedbacks(request):
    if request.session.get('usertype') != 'admin':
        return redirect('login')

    workout_feedbacks = WorkoutFeedback.objects.select_related('customer', 'plan').order_by('-id')
    diet_feedbacks = DietFeedback.objects.select_related('customer', 'diet_plan').order_by('-id')

    return render(request, 'admin/admin_feedbacks.html', {
        'workout_feedbacks': workout_feedbacks,
        'diet_feedbacks': diet_feedbacks
    })


def error_404(request, exception):
    return render(request, '404.html', status=404)