from django.db.models import Q
from django.db.models import Max,Min
from apps.rental.models import Item
from apps.vendor.models import Customer, Vendor

class ItemFilter:
    def filter_items(
        self,
        district,
        items,
        sorting,
        query,
        price_from,
        price_to,
        *args,
        **kwargs
        ):
        print("filters",query,price_from,price_to,district)
        if price_from != None and price_to != None:
            items = items.filter(Q(price__gte=price_from), Q(price__lte=price_to), ~Q(price=0))

        items_ids = []
        for item in items:
            items_ids.append(item.id)

        items = Item.objects.filter(id__in=set(items_ids))
        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))


        min_price=items.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=items.aggregate(Max('price'))['price__max']

        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0 
        
        locations=[]
        for i in items:
            # locations.append(i.location)
            if Customer.objects.filter(user=i.user).exists():
                user_loc=Customer.objects.get(user=i.user)
                locations.append(user_loc.district)
            else:
                user_loc=Vendor.objects.get(user=i.user)
                locations.append(user_loc.district)


        return items.order_by(sorting),min_price,max_price,set(locations)

items_filters= ItemFilter()                      