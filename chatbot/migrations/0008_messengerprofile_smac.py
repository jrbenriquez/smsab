# Generated by Django 3.0.7 on 2020-07-21 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0007_messengerorderform_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='messengerprofile',
            name='smac',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
