# Generated by Django 5.1.5 on 2025-01-16 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('seller', models.CharField(max_length=255)),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3)),
                ('review_count', models.PositiveIntegerField(default=0)),
                ('images', models.TextField()),
            ],
        ),
    ]
