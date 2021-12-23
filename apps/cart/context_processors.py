from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def comparing(request):
    return {'comparing': request.session.get('comparing')}
