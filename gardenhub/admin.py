from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Crop, Garden, Plot, Pick, Order, Affiliation, User


class PlotAdmin(admin.ModelAdmin):
    list_display = ('get_plot', 'get_garden')

    def get_plot(self, obj):
        return "Plot #{}".format(obj.title)
    get_plot.admin_order_field = 'title'
    get_plot.short_description = 'Plot'

    def get_garden(self, obj):
        return obj.garden
    get_garden.admin_order_field = 'garden__title'
    get_garden.short_description = 'Garden'


class GardenAdmin(admin.ModelAdmin):
    list_display = ('title', 'address')


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
    list_display = (
        'get_order', 'requester', 'start_date', 'end_date', 'get_plot',
        'get_garden', 'timestamp'
    )

    def get_order(self, obj):
        return "Order #{}".format(obj.id)
    get_order.admin_order_field = 'id'
    get_order.short_description = 'Order'

    def get_plot(self, obj):
        return "Plot #{}".format(obj.plot.title)
    get_plot.admin_order_field = 'plot__title'
    get_plot.short_description = 'Plot'

    def get_garden(self, obj):
        return obj.plot.garden
    get_garden.admin_order_field = 'plot__garden__title'
    get_garden.short_description = 'Garden'


class PickAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
    list_display = ('timestamp', 'picker', 'get_plot', 'get_garden')

    def get_plot(self, obj):
        return obj.plot.title
    get_plot.admin_order_field = 'plot__title'
    get_plot.short_description = 'Plot'

    def get_garden(self, obj):
        return obj.plot.garden
    get_garden.admin_order_field = 'plot__garden__title'
    get_garden.short_description = 'Garden'


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'first_name',
                  'last_name', 'is_staff', 'is_active']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'email', 'first_name', 'last_name', 'is_active', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'photo')}),
        ('Status', {'fields': ('is_staff', 'is_active')})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name',
                       'last_name', 'is_active', 'is_staff')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


admin.site.register(Crop)
admin.site.register(Garden, GardenAdmin)
admin.site.register(Plot, PlotAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Affiliation)
admin.site.register(Pick, PickAdmin)
admin.site.register(User, UserAdmin)
