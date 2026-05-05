from typing import Any

from app.ai_service import AIIntegrationError, predict_smiles, train_cdk2_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from app.forms import LoginForm, PredictSmilesForm, RegisterForm, TrainModelForm


@login_required
def home(request: HttpRequest) -> HttpResponse:
	train_form = TrainModelForm(prefix="train")
	predict_form = PredictSmilesForm(prefix="predict")
	train_result: dict[str, Any] | None = None
	predict_result: dict[str, Any] | None = None
	ai_error: str | None = None

	if request.method == "POST":
		action = request.POST.get("action")

		if action == "train":
			train_form = TrainModelForm(request.POST, prefix="train")
			if train_form.is_valid():
				try:
					train_result = train_cdk2_model(
						num_epochs=train_form.cleaned_data["num_epochs"]
					)
				except AIIntegrationError as exc:
					ai_error = str(exc)

		if action == "predict":
			predict_form = PredictSmilesForm(request.POST, prefix="predict")
			if predict_form.is_valid():
				try:
					predict_result = predict_smiles(
						smiles=predict_form.cleaned_data["smiles"],
						threshold=predict_form.cleaned_data["threshold"],
					)
				except AIIntegrationError as exc:
					ai_error = str(exc)

	return render(
		request,
		"home.html",
		{
			"title": "Home",
			"metaDescription": "Jarvis home",
			"train_form": train_form,
			"predict_form": predict_form,
			"train_result": train_result,
			"predict_result": predict_result,
			"ai_error": ai_error,
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
