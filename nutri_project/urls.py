"""
URL configuration for nutri_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from nutri_app import views
from django.conf import settings

handler404 = views.error_404

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('adm/', views.adm, name='adm'),

    path('', views.index, name='index'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),
    path('dietician_register/', views.dietician_register, name='dietician_register'),
    path('login/', views.login_view, name='login'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('dietician_dashboard/', views.dietician_dashboard, name='dietician_dashboard'),

    path('view_customers/', views.view_all_customers, name='view_all_customers'),
    path('verify_customer/<int:id>/', views.verify_customer, name='verify_customer'),
    path('delete_customer/<int:id>/', views.delete_customer, name='delete_customer'),

    path('view_all_dieticians/', views.view_all_dieticians, name='view_all_dieticians'),
    path('approve_dietician/<int:id>/', views.approve_dietician, name='approve_dietician'),
    path('reject_dietician/<int:id>/', views.reject_dietician, name='reject_dietician'),
    path('delete_dietician/<int:id>/', views.delete_dietician, name='delete_dietician'),
    path('view_dietician_profile/<int:id>/', views.view_dietician_profile, name='view_dietician_profile'),

    path('add_dietplans/', views.add_dietplans, name='add_dietplans'),

    path('view_diet_plans/', views.view_diet_plans, name='view_diet_plans'),
    path('edit_diet_plan/<int:plan_id>/', views.edit_diet_plan, name='edit_diet_plan'),
    path('delete_diet_plan/<int:plan_id>/', views.delete_diet_plan, name='delete_diet_plan'),

    path('view_all_diets/', views.view_all_diets, name='view_all_diets'),
    path('view_customer_diets/', views.view_customer_diets, name='view_customer_diets'),

  
    path('join_diet/<int:plan_id>/', views.join_diet_plan, name='join_diet_plan'),
    path('joined_diets/', views.view_joined_diets, name='view_joined_diets'),
    path('update_steps/<int:customer_diet_id>/', views.update_diet_steps, name='update_diet_steps'),

    path('joined_customers_diet_plans/', views.joined_customers_diet_plans, name='joined_customers_diet_plans'),
    path('all_joined_diet_plans/', views.all_joined_diet_plans, name='all_joined_diet_plans'),

    path('customer_profile/', views.customer_profile, name='customer_profile'),
    path('dietician_profile/', views.dietician_profile, name='dietician_profile'),

    path('edit_customer_profile/', views.edit_customer_profile, name='edit_customer_profile'),
    path('edit_dietician_profile/', views.edit_dietician_profile, name='edit_dietician_profile'),

    path('add_bmi/', views.add_bmi, name='add_bmi'),
    path('calculate_bmr/', views.calculate_bmr, name='calculate_bmr'),
    path('upload_diet_plan_pdf/', views.upload_diet_plan_pdf, name='upload_diet_plan_pdf'),
    path('view_diet_plan_pdfs/', views.view_diet_plan_pdfs, name='view_diet_plan_pdfs'),
    path('customer_view_diet_plan_pdfs/', views.customer_view_diet_plan_pdfs, name='customer_view_diet_plan_pdfs'),
    path('admin_view_diet_plan_pdfs/', views.admin_view_diet_plan_pdfs, name='admin_view_diet_plan_pdfs'),
    path('dietician_edit_pdf/<int:pdf_id>/', views.dietician_edit_pdf, name='dietician_edit_pdf'),
    path('dietician_delete_pdf/<int:pdf_id>/', views.dietician_delete_pdf, name='dietician_delete_pdf'),

    path('ChatBot/',views.ChatBot,name='ChatBot'),

    path('add_food/', views.add_food, name='add_food'),
    path('view_foods/', views.view_foods, name='view_foods'),
    path('edit_food/<int:food_id>/', views.edit_food, name='edit_food'),
    path('delete_food/<int:food_id>/', views.delete_food, name='delete_food'),

    path('select_food/', views.select_food_today, name='select_food'),
    path('today_report/', views.today_report, name='today_report'),
    path('display_all_food/', views.display_all_food, name='display_all_food'),

    path('customer_dietician_list/', views.customer_dietician_list, name='customer_dietician_list'),
    path('dietician_customer_list/', views.dietician_customer_list, name='dietician_customer_list'),

    path('add_workout_plan/', views.add_workout_plan, name='add_workout_plan'),
    path('workout_plan_list/', views.workout_plan_list, name='workout_plan_list'),
    path('edit_workout_plan/<int:plan_id>/', views.edit_workout_plan, name='edit_workout_plan'),
    path('delete_workout_plan/<int:plan_id>/', views.delete_workout_plan, name='delete_workout_plan'),
    path('delete_workout_step/<int:step_id>/', views.delete_workout_step, name='delete_workout_step'),

    path('view_workout_customer/', views.view_workout_customer, name='view_workout_customer'),

    path('request_custom_diet/<int:plan_id>/', views.request_custom_diet, name='request_custom_diet'),
    path('view_custom_diet_requests/', views.view_custom_diet_requests, name='view_custom_diet_requests'),
    path('create_custom_diet_plan/<int:request_id>/',views.create_custom_diet_plan,name='approve_custom_diet_request'),
    path('view_customer_custom_diet_plans/',views.view_customer_custom_diet_plans,name='view_customer_custom_diet_plans'),
    path('toggle_custom_diet_step/<int:step_id>/',views.toggle_custom_diet_step,name='toggle_custom_diet_step'),


    path('customer_chat/<int:did>/', views.customer_chat, name='customer_chat'),
    path('dietician_chat/<int:cid>/', views.dietician_chat, name='dietician_chat'),

  
    # path('system-ip/', views.system_ip_location, name='system_ip_location'),

    path('view_all_workouts/', views.view_all_workouts, name='view_all_workouts'),
    path('view_workout_details/<int:id>/', views.view_workout_details, name='view_workout_details'),

    path('payment/<int:plan_id>/<str:action>/', views.payment_page, name='payment_page'),
    path('add_feedback/<int:plan_id>/', views.add_feedback, name='add_feedback'),

        # View all workout plans (customer)
    path('workouts/', views.view_workout_customer, name='view_workout_customer'),

    # Workout detail (after free / payment)
    path('workout-detail/<int:plan_id>/', views.workout_detail, name='workout_detail'),

    # Payment page
    path('workout-payment/<int:plan_id>/', views.workout_payment, name='workout_payment'),
    path('admin_feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),

]
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]