from django.db.models import Q
from apps.rental.models import Engine,Year

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
        make,
        model,
        *args,
        **kwargs
        ):
        
        rentals__idd=[]
        for rental in rentals:
            rentals__idd.append(rental.id)
        if query:
            rentals=rentals.filter(Q(title__icontains=query))    
        
        rentals = self.filter_by_atributes(rentals,engine,year)
        
        if instock:
            rentals = rentals.filter(num_available__gte=1)

        list_engine=[]
        list_year=[]
        for b in rentals:
            list_engine.append(b.engine)
            list_year.append(b.year)

        return rentals.order_by(sorting),list_engine,list_year    

    def filter_by_atributes(self,rentals,engine,year,*args,**kwargs):
        if engine:
            rentals = rentals.filter(engine__in=Engine.objects.filter(pk__in=engine))
        if year:
            rentals = rentals.filter(year__in=Year.objects.filter(pk__in=year))    
        return rentals 

rental_service = RentalService()