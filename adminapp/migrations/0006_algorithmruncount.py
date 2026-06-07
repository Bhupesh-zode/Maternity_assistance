from django.db import migrations, models
from django.utils import timezone


DEMO_RUN_COUNTS = (
    ('lr', 'Logistic Regression', 12),
    ('ad', 'Gradient Boost', 12),
    ('xg', 'XG Boost', 8),
)


def seed_demo_run_counts(apps, schema_editor):
    AlgorithmRunCount = apps.get_model('adminapp', 'AlgorithmRunCount')
    now = timezone.now()
    for algo_key, algo_name, times_used in DEMO_RUN_COUNTS:
        AlgorithmRunCount.objects.update_or_create(
            algo_key=algo_key,
            defaults={
                'algo_name': algo_name,
                'times_used': times_used,
                'last_run_at': now,
            },
        )


def clear_demo_run_counts(apps, schema_editor):
    AlgorithmRunCount = apps.get_model('adminapp', 'AlgorithmRunCount')
    AlgorithmRunCount.objects.filter(
        algo_key__in=[row[0] for row in DEMO_RUN_COUNTS],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0005_dataset_ad_accuracy_dataset_ad_algo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlgorithmRunCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('algo_key', models.CharField(max_length=10, unique=True)),
                ('algo_name', models.CharField(max_length=100)),
                ('times_used', models.PositiveIntegerField(default=0)),
                ('last_run_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'algorithm_run_counts',
            },
        ),
        migrations.RunPython(seed_demo_run_counts, clear_demo_run_counts),
    ]
