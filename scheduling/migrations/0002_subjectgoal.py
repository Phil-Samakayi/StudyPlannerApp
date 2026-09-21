# Generated manually, matching the style of 0001_initial.py -- run
# `python manage.py makemigrations --check` to confirm this matches what
# Django itself would generate from the SubjectGoal model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text="What you're aiming to achieve, e.g. 'Master linked lists before the midterm'.", max_length=255)),
                ('target_date', models.DateField()),
                ('achieved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_goals', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='subjects.subject')),
            ],
            options={
                'db_table': 'subject_goal',
                'ordering': ['target_date'],
                'indexes': [models.Index(fields=['student', 'subject'], name='idx_goal_student_subject')],
            },
        ),
    ]
