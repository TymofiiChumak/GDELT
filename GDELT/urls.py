"""GDELT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from .settings import settings
from .views.main_view import main_index
from .views.parameters_views import parameters_index
from .views.function_views import make_plot_request, loading_page, wait_for_plot, draw_plot



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_index, name='index'),
    path('set_parameters/<function>', parameters_index, name='index'),
    path('plot_request/<function>', make_plot_request, name='index'),
    path('loading/<function>/<job_uuid>', loading_page, name='index'),
    path('wait_for_plot/', wait_for_plot, name='index'),
    path('plot/<function>/<job_uuid>', draw_plot, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


