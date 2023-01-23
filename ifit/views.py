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
from rest_framework.decorators import api_view
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
    


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        CustomClient.objects.create_user(**serializer.validated_data)
        token = Token.objects.create(user=request.user)
        return Response({"success": "User Created","token": token.key,})


class Login(APIView):
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




class PaystackInitiatePayment(APIView):
    serializer_class = PaystackPaymentSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request):
            data = {
            "email" : request.data.get("email"),
            "price" : request.data.get("price"),
            "plan" : request.data.get("plan")
             }

            if data:
                pk = settings.PAYSTACK_PUBLIC_KEY

                payment = Subscription.objects.create(
                    price=data.get("price"), plan_id=data.get("plan"), user=request.user
                )
                payment.save()

                context = {
                    "payment": str(payment),
                    "field_values": request.data,
                    "paystack_pub_key": pk,
                    
                }
                return Response(context, status=status.HTTP_201_CREATED)
        
            return Response({"error": "Wrong Input"}, status=status.HTTP_400_BAD_REQUEST)
        



class VerifyPaymentAPI(APIView):
    serializer_class = PaystackVerifySerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, paystack_payment_reference):

        payment = Subscription.objects.get(paystack_payment_reference=paystack_payment_reference)
        verified = payment.verify_payment()

        if verified:
            payment.save()
            print(request.user.email, " funded wallet successfully")
            return Response({"status": "success"})
        return Response({"status": "failed"})