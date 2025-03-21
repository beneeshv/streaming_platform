from django.db import migrations, models
import django.contrib.auth.models
from django.utils.text import slugify
import uuid

def generate_usernames(apps, schema_editor):
    UserReg = apps.get_model('myapp', 'UserReg')
    for user in UserReg.objects.all():
        base_username = slugify(user.email.split('@')[0])
        username = base_username
        counter = 1
        while UserReg.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        user.username = username
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreg',
            name='username',
            field=models.CharField(
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=150,
                unique=True,
                verbose_name='username',
                default=uuid.uuid4
            ),
            preserve_default=False,
        ),
        migrations.RunPython(generate_usernames),
    ] 