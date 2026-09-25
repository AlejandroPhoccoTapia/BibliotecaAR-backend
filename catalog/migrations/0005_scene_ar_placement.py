from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0004_student_access_progress')]

    operations = [
        migrations.AddField(
            model_name='scene', name='ar_marker_width_cm',
            field=models.FloatField(default=6.0, validators=[MinValueValidator(2), MaxValueValidator(30)]),
        ),
        migrations.AddField(
            model_name='scene', name='ar_model_size_cm',
            field=models.FloatField(default=8.0, validators=[MinValueValidator(1), MaxValueValidator(50)]),
        ),
        migrations.AddField(
            model_name='scene', name='ar_offset_x_cm',
            field=models.FloatField(default=0.0, validators=[MinValueValidator(-50), MaxValueValidator(50)]),
        ),
        migrations.AddField(
            model_name='scene', name='ar_offset_y_cm',
            field=models.FloatField(default=0.5, validators=[MinValueValidator(-50), MaxValueValidator(50)]),
        ),
        migrations.AddField(
            model_name='scene', name='ar_offset_z_cm',
            field=models.FloatField(default=0.0, validators=[MinValueValidator(-50), MaxValueValidator(50)]),
        ),
        migrations.AddField(
            model_name='scene', name='ar_yaw_degrees',
            field=models.FloatField(default=0.0, validators=[MinValueValidator(-180), MaxValueValidator(180)]),
        ),
    ]
