# Generated by Django 3.0.7 on 2021-02-18 09:51

from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalonAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salonName', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50)),
                ('town', models.CharField(max_length=100)),
                ('postcode', models.CharField(max_length=10)),
                ('tel', models.CharField(max_length=50)),
                ('website', models.CharField(max_length=50)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('slogan', models.CharField(blank=True, max_length=250, null=True)),
                ('fblink', models.CharField(blank=True, max_length=250, null=True)),
                ('istarlink', models.CharField(blank=True, max_length=250, null=True)),
                ('snaplink', models.CharField(blank=True, max_length=250, null=True)),
                ('twitlink', models.CharField(blank=True, max_length=250, null=True)),
                ('firstName', models.CharField(blank=True, max_length=250, null=True)),
                ('lastName', models.CharField(blank=True, max_length=250, null=True)),
                ('county', models.CharField(blank=True, max_length=250, null=True)),
                ('email', models.CharField(blank=True, max_length=250, null=True)),
                ('futureAppointment', models.PositiveSmallIntegerField(default=60)),
            ],
            options={
                'verbose_name': 'SalonAccount',
                'verbose_name_plural': 'SalonAccounts',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is_staff')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('salonAcc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.SalonAccount')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
    ]