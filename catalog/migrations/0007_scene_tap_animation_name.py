from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0006_alter_scene_prefab_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='tap_animation_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
    ]
