from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0003_studentprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='access_code_lookup',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='access_code_hash',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.CreateModel(
            name='StudentSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='catalog.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='StudentReadingProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_opened_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('scene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_progress', to='catalog.scene')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reading_progress', to='catalog.studentprofile')),
            ],
        ),
        migrations.AddConstraint(
            model_name='studentreadingprogress',
            constraint=models.UniqueConstraint(fields=('student', 'scene'), name='unique_student_scene_progress'),
        ),
    ]
