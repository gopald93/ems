from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
	def decorator(func):
		def wrap(request,*args,**kwargs):
			if request.role in allowed_roles:
				return func(request,*args,**kwargs)
			else:
				return HttpResponseRedirect(reverse('employee_list'))
			    # raise PermissionDenied	
		return wrap
	return decorator