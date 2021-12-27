from django.db.models import Q

from apps.newProduct.models import Brand, Color, Length, Product, Size, Variants, Weight, Width,Height


class ProductService:
    def filter_products(
        self,
        products,
        variants_id,
        sorting,
        query,
        instock,
        price_from,
        price_to,
        brand,
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
        # print(products)
        if price_from != None and price_to != None:
            products = products.filter(Q(price__gte=price_from) , Q(price__lte=price_to), ~Q(price=0))

        variants= Variants.objects.filter(product_id__in=variants_id)
        all_variants=variants.filter(Q(price__gte=price_from) , Q(price__lte=price_to))
        print("all variants",all_variants)
        products_idd = []
        for product in products:
            # discounted_price = product.get_discounted_price()
            # if discounted_price >= float(price_from) and discounted_price <= float(price_to):
            products_idd.append(product.id)
        for variant in all_variants:
            products_idd.append(variant.product.id)
        products= Product.objects.filter(id__in=set(products_idd))
        print(products)
        if query:
            products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
            # for product in products:
            #     variants=variants.filter(Q(product=product))


        # print(products)
        products = self.filter_by_variants(products, brand, color, weight, height,width,length, size)
        # print("after filter",products)
        if instock:
            products = products.filter(num_available__gte=1)


        return products.order_by(sorting)

    def filter_by_variants(
        self,
        products,
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
            products = products.filter(brand__in=Brand.objects.filter(brand=brand))
        if color:
            products = products.filter(color__in=Color.objects.filter(name=color))
            print("after color",products)
        if weight:
            products = products.filter(weight__in=Weight.objects.filter(weight=weight))
        if height:
            products = products.filter(height__in=Height.objects.filter(height=height))
        if width:
            products = products.filter(width__in=Width.objects.filter(width=width))
        if length:
            products = products.filter(length__in=Length.objects.filter(length=length))
        if size:
            products = products.filter(size__in=Size.objects.filter(name=size))
        return products
        print("after color",products)

product_service = ProductService()
