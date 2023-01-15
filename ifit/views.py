from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from django.conf import settings
import secrets
from .forms import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Create your views here.

User = get_user_model()


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = ViewAllSubscriptionSerializer
    permission_classes = (IsAuthenticated,)


class OutputUserViewSet(viewsets.ModelViewSet):
    queryset = CustomClient.objects.all()
    serializer_class = OutputUserDetailSerializer
    permission_classes = (IsAuthenticated,)


class SearchUsingClientTagListApiView(RetrieveAPIView):
    queryset = CustomClient.objects.all()
    serializer_class = SearchUsingClientTagSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "client_tag"


class RegisterApiView(APIView):
    serializer_class = RegisterUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        CustomClient.objects.create_user(**serializer.validated_data)
        token = Token.objects.create(user=request.user)
        return Response({"success": "User Created","token": token.key,})


class Login(APIView):
    permission_classes = ()
    authentication_classes = (TokenAuthentication,)
    serializer_class = LoginUserSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        check_email = CustomClient.objects.filter(email=email).exists()
        if check_email == False:
            return Response({"error": "There is no account with that email"})

        user = CustomClient.objects.get(email=email)
        if user.check_password(password) == False:
            return Response(
                {"Incorrect Password": "The password is inncorrect,Try again"}
            )
        user = authenticate(email=email, password=password)
        if user:
            return Response(
                {"token": user.auth_token.key, "Success": "Login Succesful"}
            )
        else:
            return Response(
                {"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionPlansApiView(APIView):
    serializer_class = SubscriptionPlanSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        SubscriptionPlan.objects.create(**serializer.validated_data)
        return Response({"success": "Subscription Created"})


class SubscriptionPurchaseApiView(APIView):
    serializer_class = SubscriptionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        Subscription.objects.create(**serializer.validated_data)
        return Response({"success": "Subscription Plan Created"})


class PlanDiscountViewset(viewsets.ModelViewSet):
    queryset = PlanDiscount.objects.all()
    serializer_class = PlanDiscountSerializer


def initiate_payment(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        price = request.POST.get("price")
        email = request.POST.get("email")
        plan = request.POST.get("plan")
        # print(price)

        pk = settings.PAYSTACK_PUBLIC_KEY

        payment = Subscription.objects.create(
            price=price, plan_id=plan, user=request.user
        )
        payment.save()

        context = {
            "payment": payment,
            "field_values": request.POST,
            "paystack_pub_key": pk,
            "amount_value": payment.amount_value(),
        }
        return render(
            request,
            "ifit/index_page.html",
            context,
        )
    form = SubscriptionForm()
    return render(request, "ifit/payment.html", {"form": form})


def verify_payment(request, paystack_payment_reference):
    payment = Subscription.objects.get(
        paystack_payment_reference=paystack_payment_reference
    )
    verified = payment.verify_payment()

    if verified:
        # user_wallet = Subscription.objects.get(user=request.user)
        # user_wallet.balance += payment.price
        payment.save()
        print(request.user.email, " funded wallet successfully")
        return render(request, "ifit/success.html")
    return render(request, "ifit/success.html")


def homepage(request):
    subs = SubscriptionPlan.objects.all()
    return render(request, "ifit/index_page.html", {"subs": subs})


def user_register(request):
    # you are yet to integrate the time span for payment
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        # return render(request, "ifit/user-register.html", {"form": form})
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activation link has been sent to your email id"
            message = render_to_string(
                "ifit/active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
            # login(request,user,backend='django.contrib.auth.backends.ModelBackend')
            # messages.success(request, "You have been registered")
            # return redirect("user_login")
    else:
        form = UserRegistrationForm()
    return render(request, "ifit/user_register.html", {"form": form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account."
        )
    else:
        return HttpResponse("Activation link is invalid!")

