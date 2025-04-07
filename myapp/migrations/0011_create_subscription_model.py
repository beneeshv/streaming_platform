from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_auto_20250329_1939'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_type', models.CharField(choices=[('monthly', 'Monthly Plan'), ('annual', 'Annual Plan')], max_length=20)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('payment_status', models.CharField(default='completed', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userreg')),
            ],
        ),
    ] 