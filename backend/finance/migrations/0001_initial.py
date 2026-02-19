# Generated manually for portfolio scaffold
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("month", models.DateField(help_text="Use first day of month")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-month"], "unique_together": {("user", "month")}},
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("category_type", models.CharField(choices=[("income", "Income"), ("expense", "Expense"), ("saving", "Saving")], max_length=20)),
                ("is_default", models.BooleanField(default=False)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="categories", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"], "unique_together": {("user", "name", "category_type")}},
        ),
        migrations.CreateModel(
            name="SavingGoal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("deadline", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saving_goals", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["deadline", "created_at"]},
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("transaction_type", models.CharField(choices=[("income", "Income"), ("expense", "Expense"), ("saving", "Saving")], max_length=20)),
                ("date", models.DateField()),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="SavingContribution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("date", models.DateField()),
                ("note", models.CharField(blank=True, max_length=255)),
                ("goal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contributions", to="finance.savinggoal")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saving_contributions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
    ]
