from django.db.models import Q
from django.db.models import Max,Min
from apps.rental.models import Amenity, Application, Capacity, Engine,Year,Room, Type

class RentalService:
    def filter_rental(
        self,
        rentals,
        engine,
        sorting,
        query,
        instock,
        price_from,
        price_to,
        color,
        weight,
        size,
        height,
        length,
        width,
        year,
        rooms,
        amenity,
        application,
        capacity,
        rental_type,
        make,
        model,
        *args,
        **kwargs
        ):
        
        for rent in rentals:
            if price_from != None and price_to != None:
                rentals = rentals.filter(Q(price__gte=price_from), Q(price__lte=price_to), ~Q(price=0))
            else:
                rentals = rentals.filter(Q(price__gte=price_from),Q(price__lte=price_to))    

        rentals__idd=[]
        for rental in rentals:
            rentals__idd.append(rental.id)
        if query:
            rentals=rentals.filter(Q(title__icontains=query) | Q(description__icontains=query))    
        
        rentals = self.filter_by_atributes(rentals,engine,year,rooms,amenity,application,capacity,rental_type)
        
        min_price=rentals.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=rentals.aggregate(Max('price'))['price__max']
        
        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0    

        if instock:
            rentals = rentals.filter(num_available__gte=1)

        list_engine=[]
        list_year=[]
        list_rooms=[]
        list_amenity=[]
        list_application=[]
        list_capacity=[]
        list_type=[]
        for b in rentals:
            list_engine.append(b.engine)
            list_year.append(b.year)
            list_rooms.append(b.rooms)
            list_amenity.append(b.amenity)
            list_application.append(b.application)
            list_capacity.append(b.capacity)
            list_type.append(b.item_type)

        return rentals.order_by(sorting),min_price,max_price,set(list_engine),set(list_year),set(list_rooms),set(list_amenity),set(list_application),set(list_capacity),set(list_type)    

    def filter_by_atributes(self,rentals,engine,year,rooms,amenity,application,capacity,rental_type,*args,**kwargs):
        if engine:
            rentals = rentals.filter(engine__in=Engine.objects.filter(pk__in=engine))
        if year:
            rentals = rentals.filter(year__in=Year.objects.filter(pk__in=year))  
        if rooms:
            rentals = rentals.filter(rooms__in=Room.objects.filter(pk__in=rooms)) 
        if amenity:
            rentals = rentals.filter(amenity__in=Amenity.objects.filter(pk__in=amenity))
        if application:
            rentals = rentals.filter(application__in=Application.objects.filter(pk__in=application))
        if capacity:
            rentals = rentals.filter(capacity__in=Capacity.objects.filter(pk__in=capacity))  
        if rental_type:
            rentals = rentals.objects.filter(item_type__in=Type.objects.filter(pk__in=rental_type))                  
        return rentals 

rental_service = RentalService()