from django.db import models
import random
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomClientManager
from django.utils import timezone
from .paystack import Paystack
import secrets

# Create your models here.
gender = (("M", "Male"), ("F", "Female"))
duration = (("Day(s)", "Day(s)"), ("Week", "Week"), ("Month(s)", "Month(s)"))


class CustomClient(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=150, unique=True)
    sex = models.CharField(max_length=11, choices=gender)
    phone_number = models.CharField(max_length=11)
    client_tag = models.CharField(max_length=30, unique=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomClientManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.client_tag = (
            self.first_name[:2] + self.last_name[:2] + str(random.randrange(0, 1100))
        )
        super().save(*args, **kwargs)


class SubscriptionPlan(models.Model):
    title = models.CharField(max_length=150)
    price = models.IntegerField(null=True)
    max_member = models.IntegerField(null=True)
    validity_days = models.IntegerField()
    highlight_status = (models.BooleanField(default=False, null=True),)

    def __str__(self):
        return self.title

SUBSCRIPTION_PRICES = (
    ("Basic", "Basic $250"),
    ("Medium", "Medium $350"),
    ("Advance", "Advance $500"), 
)

class Subscription(models.Model):
    user = models.ForeignKey(CustomClient, on_delete=models.CASCADE, null=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True)
    price = models.CharField(null=True, choices=SUBSCRIPTION_PRICES,max_length=100)
    reg_date = models.DateField(
        default=timezone.now,
        null=True,
    )
    verified = models.BooleanField(default=False)
    paystack_payment_reference = models.CharField(max_length=100, default="", null=True)

    class Meta:
        ordering = ("-reg_date",)

    def __str__(self):
        return f"Payment: {self.price}"

    def get_absolute_url(self):
        return f"verify_payment/{str(self.paystack_payment_reference)}/"

    def save(self, *args, **kwargs):
        while not self.paystack_payment_reference:
            paystack_payment_reference = secrets.token_urlsafe(50)
            object_with_similar_ref = Subscription.objects.filter(
                paystack_payment_reference=paystack_payment_reference
            )
            if not object_with_similar_ref:
                self.paystack_payment_reference = paystack_payment_reference

        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.price) * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(
            self.paystack_payment_reference, self.price
        )
        if status:
            # if result["price"] / 100 == self.price:
            self.verified = True
            self.save()
        if self.verified:
            return True
        return False


class Subscriber(models.Model):
    user = models.ForeignKey(CustomClient, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    plan_validity = models.IntegerField()

    def __str__(self):
        return self.user


class Trainer(models.Model):
    fullname = models.CharField(max_length=150)
    address = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname


class PlanDiscount(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True)
    period = models.IntegerField(null=True)
    duration = models.CharField(max_length=100, choices=duration)
    discount_percent = models.IntegerField()