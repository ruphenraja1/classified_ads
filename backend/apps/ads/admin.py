from django.contrib import admin
from django import forms
from .models import Ad, LOV, BlockedUser

class BlockedUserAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate status choices from LOV (English)
        statuses = LOV.objects.filter(type='BLOCKED_USER_STATUS', language='en', is_active=True).values_list('lic', 'display_name')
        self.fields['status'].widget = forms.Select(choices=[('', '---------')] + list(statuses))

    class Meta:
        model = BlockedUser
        fields = '__all__'

class BlockedUserAdmin(admin.ModelAdmin):
    form = BlockedUserAdminForm

class AdAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate city choices from LOV (English)
        cities = LOV.objects.filter(type='CITY', language='en', is_active=True).values_list('lic', 'display_name')
        self.fields['city'].widget = forms.Select(choices=[('', '---------')] + list(cities))
        # Populate category choices from LOV (English)
        categories = LOV.objects.filter(type='CATEGORY', language='en', is_active=True).values_list('lic', 'display_name')
        self.fields['category'].widget = forms.Select(choices=[('', '---------')] + list(categories))
        # Populate status choices from LOV (English)
        statuses = LOV.objects.filter(type='STATUS', language='en', is_active=True).values_list('lic', 'display_name')
        self.fields['status'].widget = forms.Select(choices=[('', '---------')] + list(statuses))

    class Meta:
        model = Ad
        fields = '__all__'

class AdAdmin(admin.ModelAdmin):
    form = AdAdminForm
    list_filter = ('status', 'city', 'category')

admin.site.register(Ad, AdAdmin)
admin.site.register(LOV)
admin.site.register(BlockedUser, BlockedUserAdmin)
