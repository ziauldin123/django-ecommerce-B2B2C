from apps.services.models import Experience, ServiceProvider
from django.db.models import Q

class ProviderFilter:
    def filter_provider(self,providers,sorting,query,experience,*args, **kwargs):
        print('filter',query,experience,sorting)
        providers_ids=[]
        for provider in providers:
            providers_ids.append(provider.id)

        providers =  ServiceProvider.objects.filter(id__in=set(providers_ids))
        if query:
            providers = ServiceProvider.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
        providers = self.filter_provider(providers,experience)

        experince_list=[]
        for i in providers:
            experince_list.append(i.experience)

        return providers.order_by(sorting),set(experince_list)       

    def filter_provider(self,providers,experience,*args,**kwargs):
        if experience:
            providers = providers.filter(experience__in=Experience.objects.filter(pk__in=experience))    
        
        return providers

providers_filters = ProviderFilter()
        


