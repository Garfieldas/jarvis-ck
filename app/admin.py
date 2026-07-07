from django.contrib import admin

from app.models import ModelInfo, MoleculeCache, Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "prediction_class", "probability", "created_at")
	search_fields = ("smiles", "user__email", "prediction_class")
	list_filter = ("prediction_class", "created_at")


@admin.register(MoleculeCache)
class MoleculeCacheAdmin(admin.ModelAdmin):
	list_display = ("id", "smiles", "features_hash", "created_at")
	search_fields = ("smiles", "features_hash")
	list_filter = ("created_at",)


@admin.register(ModelInfo)
class ModelInfoAdmin(admin.ModelAdmin):
	list_display = ("id", "model_version", "trained_at")
	search_fields = ("model_version", "description")
	list_filter = ("trained_at",)
