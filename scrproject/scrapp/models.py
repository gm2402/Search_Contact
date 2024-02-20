from django.db import models

class Contact(models.Model):
    name_profession = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)
    email = models.TextField()

    def __str__(self):
        return self.name_profession