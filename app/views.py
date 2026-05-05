from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from app.forms import LoginForm, RegisterForm


@login_required
def home(request: HttpRequest) -> HttpResponse:
	return render(
		request,
		"home.html",
		{
			"title": "Home",
			"metaDescription": "Jarvis home",
		},
	)


class AuthLoginView(LoginView):
	template_name = "forms/login.html"
	authentication_form = LoginForm
	redirect_authenticated_user = True

	def get_success_url(self):
		return self.get_redirect_url() or reverse_lazy("home")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = "Login"
		context["metaDescription"] = "Login to Jarvis"
		return context


class RegisterView(FormView):
	template_name = "forms/register.html"
	form_class = RegisterForm
	success_url = reverse_lazy("home")

	def dispatch(self, request: HttpRequest, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("home")
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form: RegisterForm):
		user = form.save()
		login(self.request, user)
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = "Register"
		context["metaDescription"] = "Create a Jarvis account"
		return context
