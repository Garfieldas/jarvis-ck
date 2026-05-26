from typing import Any
import hashlib
from pathlib import Path

from app.ai_service import AIIntegrationError, predict_smiles, train_cdk2_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from app.forms import LoginForm, PredictSmilesForm, RegisterForm, TrainModelForm
from app.models import ModelInfo, MoleculeCache, Prediction


ALLOWED_GRAPH_FILES = {
	"training_history.png",
	"roc_curve.png",
	"confusion_matrix.png",
}


def _jarvis_model_dir() -> Path:
	return Path(settings.BASE_DIR) / "jarvis-ai" / "models"


def _collect_form_errors(*forms) -> list[str]:
	messages: list[str] = []
	for form in forms:
		for field_name, errors in form.errors.items():
			if field_name == "__all__":
				messages.extend(str(error) for error in errors)
				continue

			field = form.fields.get(field_name)
			label = field.label if field else field_name
			messages.extend(f"{label}: {error}" for error in errors)

	return messages


@login_required
def home(request: HttpRequest) -> HttpResponse:
	train_form = TrainModelForm(prefix="train")
	predict_form = PredictSmilesForm(prefix="predict")
	train_result: dict[str, Any] | None = None
	predict_result: dict[str, Any] | None = None
	ai_error: str | None = None
	ui_errors: list[str] = []
	latest_model_info = ModelInfo.objects.order_by("-trained_at").first()

	if request.method == "POST":
		action = request.POST.get("action")

		if action == "train":
			train_form = TrainModelForm(request.POST, prefix="train")
			if train_form.is_valid():
				try:
					train_result = train_cdk2_model(
						num_epochs=train_form.cleaned_data["num_epochs"]
					)
					trained_at = timezone.now()
					model_version = trained_at.strftime("cdk2-%Y%m%d%H%M%S%f")
					latest_model_info = ModelInfo.objects.create(
						model_version=model_version,
						metrics={
							"num_rows": train_result["num_rows"],
							"num_valid_fingerprints": train_result["num_valid_fingerprints"],
							"num_epochs": train_result["num_epochs"],
							"best_val_auc": train_result["best_val_auc"],
						},
						description=(
							f"CDK2 model trained from UI for "
							f"{train_form.cleaned_data['num_epochs']} epochs."
						),
						trained_at=trained_at,
					)
					train_result["model_version"] = latest_model_info.model_version
				except AIIntegrationError as exc:
					ai_error = str(exc)
					ui_errors.append(ai_error)
			else:
				ui_errors.extend(_collect_form_errors(train_form))

		if action == "predict":
			predict_form = PredictSmilesForm(request.POST, prefix="predict")
			if predict_form.is_valid():
				try:
					smiles_value = str(predict_form.cleaned_data["smiles"]).strip()
					predict_result = predict_smiles(
						smiles=smiles_value,
						threshold=predict_form.cleaned_data["threshold"],
					)

					features_hash = hashlib.sha256(smiles_value.encode("utf-8")).hexdigest()
					with transaction.atomic():
						MoleculeCache.objects.get_or_create(
							smiles=smiles_value,
							defaults={"features_hash": features_hash},
						)
						Prediction.objects.create(
							user=request.user,
							smiles=smiles_value,
							prediction_class=str(predict_result["prediction"]),
							probability=float(predict_result["probability"]),
						)
				except AIIntegrationError as exc:
					ai_error = str(exc)
					ui_errors.append(ai_error)
			else:
				ui_errors.extend(_collect_form_errors(predict_form))

	context = {
		"title": "Home",
		"metaDescription": "Jarvis home",
		"train_form": train_form,
		"predict_form": predict_form,
		"train_result": train_result,
		"predict_result": predict_result,
		"ai_error": ai_error,
		"ui_errors": ui_errors,
		"latest_model_info": latest_model_info,
	}

	if request.headers.get("HX-Request") == "true":
		return render(request, "components/home-content.html", context)

	return render(request, "home.html", context)


@login_required
def model_graphs(request: HttpRequest) -> HttpResponse:
	model_dir = _jarvis_model_dir()
	graphs: list[dict[str, str]] = []

	for filename in sorted(ALLOWED_GRAPH_FILES):
		file_path = model_dir / filename
		if file_path.exists() and file_path.is_file():
			graphs.append(
				{
					"name": filename.replace("_", " ").replace(".png", "").title(),
					"filename": filename,
				}
			)

	return render(
		request,
		"components/model-graphs.html",
		{
			"graphs": graphs,
		},
	)


@login_required
def model_graph_image(request: HttpRequest, filename: str) -> FileResponse:
	if filename not in ALLOWED_GRAPH_FILES:
		raise Http404("Graph not found.")

	file_path = _jarvis_model_dir() / filename
	if not file_path.exists() or not file_path.is_file():
		raise Http404("Graph not found.")

	return FileResponse(file_path.open("rb"), content_type="image/png")


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
