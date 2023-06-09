# Generated by Django 4.2.1 on 2023-06-13 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_segmentation_created_at_segmentation_updated_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagepreprocessing',
            name='image_preprocessing',
        ),
        migrations.AddField(
            model_name='imagepreprocessing',
            name='image_preprocessing_color',
            field=models.ImageField(default='/static/images/preprocessing/color/color.jpg', upload_to='static/images/preprocessing/color/'),
        ),
        migrations.AddField(
            model_name='imagepreprocessing',
            name='image_preprocessing_gray',
            field=models.ImageField(default='/static/images/preprocessing/gray/gray.jpg', upload_to='static/images/preprocessing/gray/'),
        ),
        migrations.AlterField(
            model_name='image',
            name='color',
            field=models.CharField(choices=[('red', 'Red'), ('green', 'Green'), ('blue', 'Blue'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('purple', 'Purple'), ('pink', 'Pink'), ('brown', 'Brown'), ('black', 'Black'), ('white', 'White'), ('dark-white', 'Dark White'), ('gray', 'Gray'), ('cyan', 'Cyan'), ('magenta', 'Magenta'), ('lime', 'Lime'), ('olive', 'Olive'), ('maroon', 'Maroon'), ('navy', 'Navy'), ('teal', 'Teal'), ('aqua', 'Aqua'), ('silver', 'Silver'), ('gold', 'Gold'), ('bronze', 'Bronze'), ('beige', 'Beige'), ('azure', 'Azure'), ('ivory', 'Ivory'), ('lavender', 'Lavender'), ('coral', 'Coral'), ('salmon', 'Salmon'), ('tan', 'Tan'), ('turquoise', 'Turquoise'), ('violet', 'Violet'), ('indigo', 'Indigo'), ('crimson', 'Crimson'), ('fuchsia', 'Fuchsia'), ('orchid', 'Orchid'), ('plum', 'Plum'), ('khaki', 'Khaki'), ('chocolate', 'Chocolate'), ('tomato', 'Tomato'), ('wheat', 'Wheat'), ('snow', 'Snow'), ('seashell', 'Seashell'), ('salmon', 'Salmon'), ('mud-brown', 'Mud Brown'), ('dark-mud-brown', 'Dark Mud Brown'), ('random', 'Random')], default='white', max_length=20),
        ),
    ]
