from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self,email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('Los usuarios deben tener un email')
        
        if not username:
            raise ValueError('Los usuarios deben tener un username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self,email, username, first_name, last_name, password=None):
        user = self.create_user(
            email= self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            password=password,
        )

        user.is_admin = True
        user.is_active = True 
        # user.is_staff = True
        user.is_superadmin = True 
        user.save(using=self._db)
        return user 

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address',max_length=100,unique=True,)
    first_name = models.CharField(max_length=50,null=True, blank=True)
    last_name = models.CharField(max_length=50,null=True, blank=True)
    username = models.CharField(max_length=50,null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    
    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True 

    @property
    def is_staff(self):
        return self.is_admin
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(blank=True, upload_to='userprofile/')
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    
    def __str__(self) -> str:
        return self.user.first_name
    
    def get_full_address(self):
        return f'{self.address_line_1}  {self.address_line_2}'
