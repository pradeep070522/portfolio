from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_profile_instagram_user_id_profile_profile_bg_color'),
    ]

    operations = [
        # 1. Remove is_active first (before unique_together changes)
        migrations.RemoveField(
            model_name='profilephoto',
            name='is_active',
        ),
        # 2. Add slot column with a default
        migrations.AddField(
            model_name='profilephoto',
            name='slot',
            field=models.CharField(
                choices=[
                    ('hero',  'Hero Section  (circular photo on home page)'),
                    ('about', 'About Me Section (rectangular photo beside bio)'),
                ],
                default='hero',
                max_length=10,
            ),
        ),
        # 3. Now add the unique_together constraint (slot column now exists)
        migrations.AlterUniqueTogether(
            name='profilephoto',
            unique_together={('profile', 'slot')},
        ),
        # 4. Update label help text
        migrations.AlterField(
            model_name='profilephoto',
            name='label',
            field=models.CharField(
                blank=True, max_length=60,
                help_text="Optional internal label e.g. 'Professional headshot'",
            ),
        ),
        # 5. Update photo help text
        migrations.AlterField(
            model_name='profilephoto',
            name='photo',
            field=models.ImageField(
                upload_to='uploads/profile/gallery/',
                help_text='Recommended: square (400×400) for Hero, portrait/landscape for About.',
            ),
        ),
        # 6. Update Meta ordering
        migrations.AlterModelOptions(
            name='profilephoto',
            options={'ordering': ['slot', '-uploaded_at'],
                     'verbose_name': 'Profile Photo',
                     'verbose_name_plural': 'Profile Photos'},
        ),
    ]
