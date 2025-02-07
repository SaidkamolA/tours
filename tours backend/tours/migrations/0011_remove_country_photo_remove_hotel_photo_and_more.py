# Generated by Django 4.2.16 on 2024-11-09 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0010_alter_booking_people_count_alter_booking_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='photo',
        ),
        migrations.AddField(
            model_name='country',
            name='photo_url',
            field=models.CharField(default='https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg', verbose_name='photo_url'),
        ),
        migrations.AddField(
            model_name='hotel',
            name='photo_url',
            field=models.CharField(default='https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg', verbose_name='photo_url'),
        ),
        migrations.AddField(
            model_name='tour',
            name='photo_url',
            field=models.CharField(default='https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg', verbose_name='photo_url'),
        ),
    ]
