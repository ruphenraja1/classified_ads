from django.db import models

class LOV(models.Model):
    type = models.CharField(max_length=50)
    lic = models.CharField(max_length=50, help_text="Language-independent code")
    display_name = models.CharField(max_length=200)
    language = models.CharField(max_length=10, choices=[('en', 'English'), ('ta', 'Tamil')])
    parent_value = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        unique_together = ('type', 'lic', 'display_name', 'language', 'is_active')
        ordering = ['order', 'display_name']

    def __str__(self):
        return f"{self.type} - {self.lic} ({self.language})"



class Ad(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15, null=True, blank=True)
    images = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default='PENDING')  # From LOV: PENDING, LIVE, BLOCKED, REVIEW
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)  # for daily filter

    def __str__(self):
        return self.title

class BlockedUser(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=20, default='BLOCKED')
    blocked_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.phone} - {self.status}"
