# Generated by Django 4.1.4 on 2022-12-29 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_app', '0003_remove_menuitem_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='rank',
            field=models.IntegerField(default=0, editable=False, verbose_name='rank'),
        ),
    ]