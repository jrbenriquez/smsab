# Generated by Django 3.0.7 on 2020-07-16 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_auto_20200716_0043'),
        ('chatbot', '0006_auto_20200714_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='messengerorderform',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_forms', to='inventory.Order'),
        ),
    ]
