# Generated by Django 4.2.20 on 2025-05-13 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuoiky', '0008_remove_hanghoa_gia_niem_yet_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hanghoa',
            name='gioi_han_duoi',
            field=models.PositiveIntegerField(default=0, verbose_name='Giới hạn dưới tồn kho'),
        ),
    ]
