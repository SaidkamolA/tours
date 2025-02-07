# Generated by Django 4.2.16 on 2024-11-04 07:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='review',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='price',
        ),
        migrations.AddField(
            model_name='review',
            name='hotel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tours.hotel', verbose_name='Hotel'),
        ),
        migrations.AddField(
            model_name='tour',
            name='price_per_person',
            field=models.IntegerField(default=100, verbose_name='Price per person'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='nutrition',
            field=models.TextField(verbose_name='Nutrition'),
        ),
        migrations.AlterField(
            model_name='person',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='people_count',
            field=models.IntegerField(verbose_name='People count'),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('people_count', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='People count')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Price')),
                ('booking_date', models.DateField(auto_now_add=True, verbose_name='Booking Date')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tours.tour', verbose_name='Tour')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
