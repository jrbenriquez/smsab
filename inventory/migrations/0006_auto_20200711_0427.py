# Generated by Django 3.0.7 on 2020-07-11 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_historicalitemstock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalitemstock',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='itemstock',
            name='level',
        ),
        migrations.RemoveField(
            model_name='itemstock',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='itemstock',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='itemstock',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='itemstock',
            name='tree_id',
        ),
    ]