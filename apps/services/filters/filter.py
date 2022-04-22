from apps.services.models import Daily_rate, Experience, ServiceProvider
from django.db.models import Q
from django.db.models import Max,Min

class ProviderFilter:
    def filter_provider(
        self,
        providers,
        daily_rate,
        sorting,
        query,
        price_from,
        price_to,
        experience,
        *args,
        **kwargs):
        print('filter',query,experience,sorting,price_from,price_to,daily_rate)
        if price_from != None and price_to !=None:
            providers = providers.filter(Q(price__gte=price_from), Q(price__lte=price_to), ~Q(price=0))

        providers_ids=[]
        for provider in providers:
            providers_ids.append(provider.id)

        providers =  ServiceProvider.objects.filter(id__in=set(providers_ids))
        if query:
            providers = ServiceProvider.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
        providers = self.provider_filter(providers,daily_rate,experience)
        min_price=providers.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=providers.aggregate(Max('price'))['price__max']

        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0    

        experience_list=[]
        daily_rate_list=[]
        for i in providers:
            experience_list.append(i.experience)
            daily_rate_list.append(i.daily_rate)

        return providers.order_by(sorting),min_price,max_price,set(experience_list),set(daily_rate_list)       

    def provider_filter(self,providers,daily_rate,experience,*args,**kwargs):
        if experience:
            providers = providers.filter(experience__in=Experience.objects.filter(pk__in=experience)) 
        if  daily_rate:
            providers = providers.filter(daily_rate__in=Daily_rate.objects.filter(pk__in=daily_rate))      
        
        return providers

providers_filters = ProviderFilter()
        


