# Generated by Django 4.2.1 on 2023-06-13 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_remove_imagepreprocessing_image_preprocessing_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segmentation',
            name='k_means_score',
        ),
    ]
