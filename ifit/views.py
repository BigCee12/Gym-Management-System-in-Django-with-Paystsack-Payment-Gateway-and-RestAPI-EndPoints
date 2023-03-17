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
from rest_framework import generics,permissions
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
        
        return Response({"success": "Subscription Plan Created"})


class SubscriptionPurchaseApiView(APIView):
    serializer_class = SubscriptionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        Subscription.objects.create(**serializer.validated_data),
       
        return Response({"success": "Subscription Plan Created"})


class PlanDiscountViewset(viewsets.ModelViewSet):
    queryset = PlanDiscount.objects.all()
    serializer_class = PlanDiscountSerializer


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = CustomClient.objects.create_user(**serializer.validated_data)
            current_site = get_current_site(request)
            mail_subject = "Activation link has been sent to your email, pls click on the link for verification"
            message = render_to_string(
                "ifit/active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
       
            to_email = serializer.data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email],)
            email.send(fail_silently=False)
            return Response(
                "Please confirm your email address to complete the registration"
            )
        return Response(serializer.errors, status=400)


class UserActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomClient.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomClient.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                "Thank you for your email confirmation. Now you can login your account."
            )
        else:
            return Response("Activation link is invalid!", status=400)


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
            return Response({"status": "success"})
        return Response({"status": "failed"})