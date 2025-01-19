# urls.py
from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    CourseViewSet, ModuleViewSet,
    ContentViewSet, EnrollmentViewSet
)

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# Nested routes for modules within courses
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'modules', ModuleViewSet, basename='course-modules')

# Nested routes for content within modules
modules_router = routers.NestedDefaultRouter(courses_router, r'modules', lookup='module')
modules_router.register(r'contents', ContentViewSet, basename='module-contents')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(modules_router.urls)),
]