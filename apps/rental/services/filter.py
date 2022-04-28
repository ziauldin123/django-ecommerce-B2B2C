from django.db.models import Q
from django.db.models import Max,Min
from apps.rental.models import Amenity, Application, Capacity, Item, Item_Model, Make, Room, Year, Engine,Type
from apps.vendor.models import Customer, Vendor
from apps.cart.models import District

class ItemFilter:
    def filter_items(
        self,
        district,
        items,
        sorting,
        query,
        price_from,
        price_to,
        sale,
        make,
        room,
        application,
        capacity,
        amenity,
        year,
        model,
        engine,
        item_type,
        *args,
        **kwargs
        ):
        print("filters",query,price_from,price_to,district,sale,sorting,make,room,application,capacity,amenity,year,model,engine,item_type)
        if price_from != None and price_to != None:
            items = items.filter(Q(price__gte=price_from), Q(price__lte=price_to), ~Q(price=0))

        if sale:
            items = items.filter(sale=True)
        else:
            items = items.filter(sale=False)        

        items_ids = []
        for item in items:
            items_ids.append(item.id)

        items = Item.objects.filter(id__in=set(items_ids))
        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

        items = self.filter_district(items,district,make,room,application,capacity,amenity,year,model,engine,item_type)
        min_price=items.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=items.aggregate(Max('price'))['price__max']

        print('min-price:',min_price)
        print('max_price:',max_price)

        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0 
        
        locations=[]
        list_make=[]
        list_room=[]
        list_application=[]
        list_capacity=[]
        list_amenity=[]
        list_year=[]
        list_model=[]
        list_engine=[]
        list_item_type=[]
        for i in items:
            locations.append(i.district)
            list_make.append(i.makes)
            list_room.append(i.rooms)
            list_application.append(i.application)
            list_capacity.append(i.capacity)
            list_amenity.append(i.amenity)
            list_year.append(i.year)
            list_model.append(i.model)
            list_engine.append(i.engine)
            list_item_type.append(i.item_type )
        
        return items.order_by(sorting),min_price,max_price,sale,set(locations),set(list_make),set(list_room),set(list_application),set(list_capacity),set(list_amenity),set(list_year),set(list_model),set(list_engine),set(list_item_type),   


    def filter_district(self,items,district,make,room,application,capacity,amenity,year,model,engine,item_type,*args,**kwargs):
        
        if district:       
            items = items.filter(district__in=District.objects.filter(pk__in=district))
        if make:
            items = items.filter(makes__in=Make.objects.filter(pk__in=make)) 
        if room:
            items = items.filter(rooms__in=Room.objects.filter(pk__in=room))  
        if application:
            items = items.filter(application__in=Application.objects.filter(pk__in=application))
        if capacity:
            items = items.filter(capacity__in=Capacity.objects.filter(pk__in=capacity))
        if amenity:
            items = items.filter(amenity__in=Amenity.objects.filter(pk__in=amenity))
        if year:
            items = items.filter(year__in=Year.objects.filter(pk__in=year))
        if model:
            items = items.filter(model__in=Item_Model.objects.filter(pk__in=model))
        if engine:
            items = items.filter(engine__in=Engine.objects.filter(pk__in=engine))  
        if item_type:
            items = items.filter(item_type__in=Type.objects.filter(pk__in=item_type))                                  
        
        print('filter:',items)
        return items
     


items_filters= ItemFilter()  
