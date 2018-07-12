# Generated by Django 2.0.6 on 2018-07-09 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appgu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dealers',
            fields=[
                ('dealerID', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('telephone', models.CharField(max_length=12)),
                ('isBlocked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Dealers',
            },
        ),
        migrations.AlterModelOptions(
            name='orders',
            options={'verbose_name_plural': 'Orders'},
        ),
        migrations.RemoveField(
            model_name='orders',
            name='dealer_user_name',
        ),
        migrations.AddField(
            model_name='orders',
            name='dealerID',
            field=models.ForeignKey(db_column='dealerID', default=-1, on_delete=django.db.models.deletion.CASCADE, to='appgu.Dealers'),
            preserve_default=False,
        ),
    ]