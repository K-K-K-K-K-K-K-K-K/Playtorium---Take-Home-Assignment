import json
import math

class DiscountManager:
    def __init__(self, discount_json_file_path):

        self.coupon_amount = None
        self.coupon_percentage = None
        self.on_top_customer_point = None
        self.on_top_category_discounts = {}
        self.seasonal_every = None
        self.seasonal_discount = None

        try:
            with open(discount_json_file_path, 'r') as f:
                data = json.load(f)
                discount_data = data.get("discount", {})

                # Coupon discounts
                coupon = discount_data.get("coupon", {})
                self.coupon_amount = coupon.get("amount")
                self.coupon_percentage = coupon.get("percentage")

                # On-top discounts
                on_top_list = discount_data.get("on_top", [])
                for item in on_top_list:
                    if "customer_point" in item:
                        self.on_top_customer_point = item["customer_point"]
                    elif "category" in item:
                        for category_discount in item["category"]:
                            name = category_discount.get("name")
                            percentage = category_discount.get("percentage")
                            if name and percentage is not None:
                                self.on_top_category_discounts[name] = percentage

                # Seasonal discount
                seasonal = discount_data.get("seasonnal", {})
                self.seasonal_every = seasonal.get("every")
                self.seasonal_discount = seasonal.get("discount")

        except Exception as e:
            print(e)

    def set_cart(self, cart_json_file_path):
        self.cart_list = []
        try:
            with open(cart_json_file_path, 'r') as f:
                data = json.load(f)
                items = data.get("items", [])
                for item in items:
                    self.cart_list.append([
                        item.get("id"),
                        item.get("name"),
                        item.get("amount"),
                        item.get("category")
                    ])
                    
        except Exception as e:
            print(e)

    def get_cart(self):
            return self.cart_list
    
    def get_total_sum(self):
        local_cart_list = self.cart_list[:]
        total_sum = 0
        for item in local_cart_list:
            total_sum += item[2]
        return total_sum
    
    def get_discounted_sum(self, coupon_mode, ontop_mode):
        '''
        ● Apply only one campaign from the same category, i.e. users have to choose either Fixed amount or Percentage discount.
        ● The order of applying campaigns is Coupon > On Top > Seasonal.

        Args:
        coupon_mode: 0 is Fixed amount. 1 is Percentage of total sum.
        ontop_mode: 0 is Percentage discount by item. 1 is Discount by points but no more than 20%.

        Returns:
            final price. floating point.
        '''
        
        total_sum = self.get_total_sum()

        # Coupon discount
        if coupon_mode == 0:
            coupon_discount = self.coupon_amount
        else:
            coupon_discount = total_sum * (self.coupon_percentage)

        # On-top discounts
        if ontop_mode == 0:
            local_cart_list = self.cart_list[:]
            ontop_discount = self._calculate_ontop_category(local_cart_list)
        else:
            ontop_discount  = min(self.on_top_customer_point, total_sum * 0.20)

        # Seasonal discount
        multiplier = math.floor(total_sum / self.seasonal_every)
        seasonal_discount = self.seasonal_discount * multiplier

        return total_sum - (coupon_discount + ontop_discount + seasonal_discount)

    def _calculate_ontop_category(self, cart_list):
        total_discount = 0
        for item in cart_list:
            total_discount += item[2] * self.on_top_category_discounts[item[3]]
        return total_discount

# Example usage
if __name__ == "__main__":
    discount_file = "discount.json"
    cart_file = "cart.json"

   
    discount_manager = DiscountManager(discount_file)
    discount_manager.set_cart(cart_file)

    print(discount_manager.get_discounted_sum(0,0))

    print(''.join(["Full price: ", str(discount_manager.get_total_sum())]))
    print(''.join(["Discounted price: ", str(discount_manager.get_discounted_sum(0,0))]))
