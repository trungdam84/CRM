


from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
# from django_ckeditor_5.fields import CKEditor5Field
# from ckeditor_uploader.fields import RichTextUploadingField


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# from .managers import UserManager

# Create your models here.
class SalonAccount(models.Model):
    salonName = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    town = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    tel = models.CharField(max_length=50)
    website = models.CharField(max_length=50)
    createTime = models.DateTimeField(auto_now=True)
    slogan = models.CharField(max_length=250, null=True, blank=True)
    fblink = models.CharField(max_length=250, null=True, blank=True)
    istarlink = models.CharField(max_length=250, null=True, blank=True)
    snaplink = models.CharField(max_length=250, null=True, blank=True)
    twitlink = models.CharField(max_length=250, null=True, blank=True)
    firstName = models.CharField(max_length=250, null=True, blank=True)
    lastName = models.CharField(max_length=250, null=True, blank=True)
    county = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    futureAppointment = models.PositiveSmallIntegerField(default=60)
    frontEndAppointment = models.BooleanField(default=False)
    # services = RichTextUploadingField(null=True)
    # salonAccID = models.CharField(max_length=25)

    class Meta:
        verbose_name = _('SalonAccount')
        verbose_name_plural = _('SalonAccounts')


    def __str__(self):
        return "{}".format(self.salonName)

# def upload_to(instance, filename):
#     return 'images/{}/{}'.format(instance.user.user.salonAcc.salonName, filename)

# class Images(models.Model):
#     salonAcc = models.ForeignKey(SalonAccount, on_delete=models.CASCADE)
#     image = models.ImageField(_("image"), upload_to=upload_to, height_field=None, width_field=None, max_length=None)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('is_staff'), default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    salonAcc = models.ForeignKey(SalonAccount, on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)





