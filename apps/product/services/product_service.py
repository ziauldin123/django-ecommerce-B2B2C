from django.db.models import Q
from django.db.models import Max,Min
from apps.newProduct.models import Brand, Color, Length, Product, Size, Variants, Weight, Width,Height
from apps.rental.models import Year,Make,Item_Model,Engine

class ProductService:
    def filter_products(
        self,
        brand,
        products,
        variants_id,
        sorting,
        query,
        instock,
        price_from,
        price_to,
        color,
        weight,
        size,
        height,
        width,
        length,
        year,
        engine,
        make,
        model,
        *args,
        **kwargs
    ):
        print("filters",query,instock,color,height,width,length,sorting,weight, price_from,price_to,brand,year,engine,make,model)
        
        for pr in products: 
            if pr.price == 0:
                products = products.filter(Q(price__gte=price_from) , Q(price__lte=price_to))      
            else:
                if price_from != None and price_to != None:
                    products = products.filter(Q(price__gte=price_from) , Q(price__lte=price_to), ~Q(price=0))   
                else:
                    products = products.filter(Q(price__gte=price_from) , Q(price__lte=price_to))    
               
        variants= Variants.objects.filter(product_id__in=variants_id)
        all_variants=variants.filter(Q(price__gte=price_from) , Q(price__lte=price_to))
        products_idd = []
        
        for product in products:
            products_idd.append(product.id)
        for variant in all_variants:
            products_idd.append(variant.product.id)
        products= Product.objects.filter(id__in=set(products_idd))
        if query:
            products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
            #products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query),status=True,visible=True)
            variants = variants.filter(Q(title__icontains=query))
            
        products,variants = self.filter_by_variants(products,variants, brand, color, weight, height,width,length,size,year,engine,make,model)
        if instock:
            products = products.filter(num_available__gte=1)
        min_price=products.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=products.aggregate(Max('price'))['price__max']
        max_var_price=variants.aggregate(Max('price'))['price__max']
        min_var_price=variants.aggregate(Min('price'))['price__min']
        if max_price == None:
            max_price=0
        if min_price == None:
            min_price=0
        
        if max_var_price == None:
            max_var_price=0
        if max_var_price != None and max_price < max_var_price:
             max_price = max_var_price
        if min_var_price != None and min_price > min_var_price:
             min_price = min_var_price
        
        list_brands=[]
        list_weight=[]
        list_width=[]
        list_size=[]
        list_height=[]
        list_color=[]
        list_length=[]
        list_year=[]
        list_engine=[]
        list_make=[]
        list_model=[]
        for bp in products:
            list_brands.append(bp.brand)
            list_weight.append(bp.weight)
            list_width.append(bp.width)
            list_size.append(bp.size)
            list_height.append(bp.height)
            list_color.append(bp.color)
            list_length.append(bp.length)
            list_year.append(bp.year)
            list_engine.append(bp.engine)
            list_make.append(bp.make)
            list_model.append(bp.model)

        return products.order_by(sorting),min_price,max_price,set(list_brands),set(list_weight),set(list_width),set(list_size),set(list_height),set(list_color),set(list_length),set(list_year),set(list_engine),set(list_make),set(list_model),

    def filter_by_variants(
        self,
        products,
        variants,
        brand,
        color,
        weight,
        height,
        width,
        length,
        size,
        year,
        engine,
        make,
        model,
        *args,
        **kwargs
    ):
        if brand:
            products = products.filter(brand__in=Brand.objects.filter(pk__in=brand))
            variants= variants.filter(product__in=(products.filter(brand__in=Brand.objects.filter(pk__in=brand))))
        if color:
            products = products.filter(color__in=Color.objects.filter(pk__in=color))
            variants= variants.filter(product__in=(products.filter(color__in=Color.objects.filter(pk__in=color))))
        if weight:
            products = products.filter(weight__in=Weight.objects.filter(pk__in=weight))
            variants= variants.filter(product__in=(products.filter(weight__in=Weight.objects.filter(pk__in=weight))))
        if height:
            products = products.filter(height__in=Height.objects.filter(pk__in=height))
            variants= variants.filter(product__in=(products.filter(height__in=Height.objects.filter(pk__in=height))))
        if width:
            products = products.filter(width__in=Width.objects.filter(pk__im=width))
            variants= variants.filter(product__in=(products.filter(width__in=Width.objects.filter(pk__im=width))))
        if length:
            products = products.filter(length__in=Length.objects.filter(pk__in=length))
            variants= variants.filter(product__in=(products.filter(length__in=Length.objects.filter(pk__in=length))))
        if size:
            products = products.filter(size__in=Size.objects.filter(pk__in=size))
            variants= variants.filter(product__in=(products.filter(size__in=Size.objects.filter(pk__in=size))))
        if year:
            products = products.filter(year__in=Year.objects.filter(pk__in=year))   
        if engine:
            products = products.filter(engine__in=Engine.objects.filter(pk__in=engine))     
        if make:
            products = products.filter(make__in=Make.objects.filter(pk__in=make))
        if model:
            products = products.filter(model__in=Item_Model.objects.filter(pk__in=model))    

        return products,variants


product_service = ProductService()
