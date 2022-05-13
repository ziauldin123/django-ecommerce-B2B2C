from apps.services.models import  Experience, ServiceProvider,Comment
from django.db.models import Q
from django.db.models import Max,Min

class ProviderFilter:
    def filter_provider(
        self,
        providers,
        sorting,
        query,
        price_from,
        price_to,
        experience,
        rating,
        *args,
        **kwargs):
        print('filter',query,experience,rating,price_from,price_to,rating)
        if price_from != None and price_to !=None:
            providers = providers.filter(Q(price__gte=price_from), Q(price__lte=price_to), ~Q(price=0))
        
        if rating:
            print('rating',rating)
            providers = providers.filter()

        providers_ids=[]
        for provider in providers:
            providers_ids.append(provider.id)

        providers =  ServiceProvider.objects.filter(id__in=set(providers_ids))
        if query:
            providers = ServiceProvider.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
        providers = self.provider_filter(providers,experience)
        min_price=providers.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=providers.aggregate(Max('price'))['price__max']

        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0    

        experience_list=[]
        for i in providers:
            experience_list.append(i.experience)
        
        return providers.order_by(sorting),min_price,max_price,rating,set(experience_list),      

    def provider_filter(self,providers,experience,*args,**kwargs):
        if experience:
            providers = providers.filter(experience__in=Experience.objects.filter(pk__in=experience))
        return providers

providers_filters = ProviderFilter()
        


