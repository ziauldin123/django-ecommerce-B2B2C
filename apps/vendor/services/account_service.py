from apps.coupon.models import Coupon
from apps.ordering.models import Order, OrderItem


class AccountService:
    def calculate_order_sum(self, username):
        orders = []
        for row in Order.objects.filter(email=username):
            order = {}
            order["created_at"] = row.created_at.strftime(
                "%Y/%m/%d, %H:%M:%S")
            order["status"] = row.status
            items = []
            total_quantity = 0
            subtotal_amount = 0
            for item_ in OrderItem.objects.filter(order_id=row.id).select_related("product"):
                item = {}
                item["product_title"] = item_.get_product_name()
                item["quantity"] = str(item_.quantity)
                item["price"] = item_.get_discounted_price()
                item["subtotal"] = item_.subtotal()
                total_quantity += item_.quantity
                subtotal_amount += item_.price
                items.append(item)
            order["items"] = items
            order["subtotal_amount"] = subtotal_amount
            order["total_quantity"] = total_quantity
            order["grand_paid_amount"] = row.grand_paid_amount
            order["delivery_cost"] = row.delivery_cost
            order["shipped_date"] = row.shipped_date
            order["arrived_date"] = row.arrived_date
            coupon_discount = ""
            coupon_code = str(row.used_coupon)
            if coupon_code != "None":
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon:
                        coupon_discount = str(
                            coupon.discount) + " %"
                except:
                    pass
            order["coupon_discount"] = coupon_discount
            orders.append(order)
        return orders


account_service = AccountService()