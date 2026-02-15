from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("maestros", "0003_alter_clients_nom_client"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PerfilUsuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "recurso",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="usuarios",
                        to="maestros.recurso",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil d'Usuari",
                "verbose_name_plural": "Perfils d'Usuaris",
            },
        ),
    ]
