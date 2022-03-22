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
            vat_cost = 0
            total_vat_exl = 0
            for item_ in OrderItem.objects.filter(order_id=row.id).select_related("product"):
                item = {}
                item["product_title"] = item_.get_product_name()
                item["quantity"] = str(item_.quantity)
                item["price"] = item_.get_discounted_price()
                item["price_no_vat"] = item_.get_product_no_vat()
                item["tax"] = item_.get_vat_price()
                item["subtotal"] = item_.subtotal()
                total_quantity += item_.quantity
                subtotal_amount += item_.price
                vat_cost += item_.get_vat_price() * item_.quantity
                total_vat_exl += item_.get_subtotal_vat_exlusive()
                items.append(item)
            order["items"] = items
            order["subtotal_amount"] = subtotal_amount
            order["vat_cost"] = vat_cost
            order["total_vat_exl"] = total_vat_exl
            order["total_quantity"] = total_quantity
            order["grand_paid_amount"] = row.grand_paid_amount
            order["delivery_cost"] = row.delivery_cost
            order["shipped_date"] = row.shipped_date
            order["arrived_date"] = row.arrived_date
            order["reference_number"] = row.reference_number
            order["id"] = row.id
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
