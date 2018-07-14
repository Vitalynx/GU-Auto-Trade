# Generated by Django 2.0.7 on 2018-07-14 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgu', '0002_auto_20180714_0357'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=1000)),
                ('headline', models.CharField(max_length=1000)),
                ('description', models.CharField(max_length=1000)),
                ('image', models.ImageField(blank=True, null=True, upload_to='static/shelby_vehicles/')),
            ],
        ),
    ]
