
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the accounts app URLs under the 'auth/' path (common convention)
    path('auth/', include('accounts.urls')), 
    path('api/', include('posts.urls')),
]
