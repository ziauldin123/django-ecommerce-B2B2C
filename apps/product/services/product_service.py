from django.db.models import Q
from django.db.models import Max,Min
from apps.newProduct.models import Brand, Color, Length, Product, Size, Variants, Weight, Width,Height


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
        *args,
        **kwargs
    ):
        print("filters",query,color,height,width,length,sorting, weight, price_from, price_to,brand)
        if price_from != None and price_to != None:
            products = products.filter(Q(price__gte=price_from) , Q(price__lte=price_to), ~Q(price=0))

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
            variants = variants.filter(Q(title__icontains=query))
            


        products,variants = self.filter_by_variants(products,variants, brand, color, weight, height,width,length, size)
        if instock:
            products = products.filter(num_available__gte=1)

        min_price=products.filter(~Q(price=0)).aggregate(Min('price'))['price__min']
        max_price=products.aggregate(Max('price'))['price__max']
        max_var_price=variants.aggregate(Max('price'))['price__max']
        min_var_price=variants.aggregate(Min('price'))['price__min']
        print("min_p:", min_price)
        print("max_p:", max_price)
        print("min_v:", min_var_price)
        print("max_v:", max_var_price)
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

        print("max:", max_price)
        print("min:", min_price )

        list_brands=[]
        list_weight=[]
        list_width=[]
        list_size=[]
        list_height=[]
        list_color=[]
        list_length=[]
        for bp in products:
            list_brands.append(bp.brand)
            list_weight.append(bp.weight)
            list_width.append(bp.width)
            list_size.append(bp.size)
            list_height.append(bp.height)

            list_color.append(bp.color)
            list_length.append(bp.length)
        
        return products.order_by(sorting),min_price,max_price,set(list_brands),set(list_weight),set(list_width),set(list_size),set(list_height),set(list_color),set(list_length)

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

        print("after more filter",products,variants)
        return products,variants


product_service = ProductService()
