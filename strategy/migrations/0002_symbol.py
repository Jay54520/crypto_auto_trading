# Generated by Django 2.0.5 on 2018-05-20 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('min_qty', models.DecimalField(decimal_places=8, max_digits=14)),
                ('step_size', models.DecimalField(decimal_places=8, max_digits=14)),
            ],
        ),
    ]