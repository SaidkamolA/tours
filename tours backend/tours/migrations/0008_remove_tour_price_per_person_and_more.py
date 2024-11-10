# Generated by Django 4.2.16 on 2024-11-05 07:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tours', '0007_remove_tour_people_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='price_per_person',
        ),
        migrations.AlterField(
            model_name='booking',
            name='people_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User  '),
        ),
        migrations.AlterField(
            model_name='person',
            name='category',
            field=models.CharField(choices=[('child', 'Child'), ('adult', 'Adult'), ('senior', 'Senior')], max_length=10, unique=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User  '),
        ),
    ]
