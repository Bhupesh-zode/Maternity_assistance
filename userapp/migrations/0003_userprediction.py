# Generated manually for per-user prediction storage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0002_delete_usermodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_sno', models.IntegerField(db_index=True, unique=True)),
                ('predicted_mode', models.CharField(max_length=120)),
                ('summary', models.CharField(blank=True, max_length=255)),
                ('form_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_predictions',
                'ordering': ['-updated_at'],
            },
        ),
    ]
