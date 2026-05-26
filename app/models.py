from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from typing import Optional


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: Optional[str], **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: Optional[str], **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    @property
    def full_name(self) -> str:
        name: Optional[str] = self.first_name if self.first_name else None
        surname: Optional[str] = self.last_name if self.last_name else None
        if name and surname:
            return f"{name} {surname}"
        else:
            return ""

    def __str__(self) -> str:
        return str(f"{self.first_name} {self.last_name}")


class MoleculeCache(models.Model):
    smiles = models.CharField(max_length=1000, unique=True)
    features_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Molecule (cache)"
        verbose_name_plural = "Molecules (cache)"

    def __str__(self) -> str:
        return self.smiles


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predictions")
    smiles = models.CharField(max_length=1000)
    prediction_class = models.CharField(max_length=32)
    probability = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.prediction_class} ({self.probability:.4f})"


class ModelInfo(models.Model):
    model_version = models.CharField(max_length=100, unique=True)
    metrics = models.JSONField(default=dict, blank=True)
    trained_at = models.DateTimeField(default=timezone.now, db_index=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-trained_at"]
        verbose_name = "Model info"
        verbose_name_plural = "Model info"

    def __str__(self) -> str:
        return self.model_version