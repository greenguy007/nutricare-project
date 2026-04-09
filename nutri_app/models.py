from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Login(AbstractUser):
    usertype=models.CharField(max_length=50)
    viewpassword=models.CharField(max_length=50)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

class Customer(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='customer/')
    
class Dietician(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='dietician/')
    license_file = models.FileField(upload_to='dietician/license/', null=True, blank=True)

class DietPlan(models.Model):
    PLAN_TYPE = (
        ('free', 'Free'),
        ('paid', 'Paid'),
    )
    dietician = models.ForeignKey(Login, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='dietplans/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE, default='free')  # NEW
    price = models.FloatField(null=True, blank=True)  # NEW

class DietStep(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='steps')
    step_text = models.TextField()

class CustomerDietPlan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    
class CustomerDietStep(models.Model):
    customer_diet_plan = models.ForeignKey(CustomerDietPlan, on_delete=models.CASCADE)
    diet_step = models.ForeignKey(DietStep, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

class DietFeedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class CustomerBMI(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    height_cm = models.FloatField()  
    weight_kg = models.FloatField()  
    bmi = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerBMR(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    bmr = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class DietPlanPDF(models.Model):
    dietician = models.ForeignKey(Login, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    pdf_file = models.FileField(upload_to='dietplan_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Food(models.Model):
    dietician = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    MEAL_CHOICES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)

    calories = models.FloatField()
    carbs = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    zinc = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

class CustomerMeal(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class Chat(models.Model):
    sender = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='receiver')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class WorkoutPlan(models.Model):
    dietician = models.ForeignKey(Dietician, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='workout_plans/')
    video = models.FileField(upload_to='workout_videos/', null=True, blank=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

class WorkoutStep(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='workout_steps/')


class DietCustomizationRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    dietician = models.ForeignKey(Login, on_delete=models.CASCADE)
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    notes = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class CustomDietPlan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    dietician = models.ForeignKey(Login, on_delete=models.CASCADE)
    request = models.OneToOneField(DietCustomizationRequest, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class CustomDietStep(models.Model):
    custom_plan = models.ForeignKey(
        CustomDietPlan,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    step_text = models.TextField()
    is_completed = models.BooleanField(default=False)

class WorkoutPurchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'plan')


class WorkoutFeedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)