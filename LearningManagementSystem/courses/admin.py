from django.contrib import admin
from .models import Course, Module, Content, Enrollment

# Register your models here.

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Content)
admin.site.register(Enrollment)
