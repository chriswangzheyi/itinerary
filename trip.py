class Trip:
    def __init__(self, city, num_travelers, num_days, has_elderly=False, has_children=False, has_special_needs=False):
        self.city = city
        self.num_travelers = num_travelers
        self.num_days = num_days
        self.has_elderly = has_elderly
        self.has_children = has_children
        self.has_special_needs = has_special_needs

    def set_city(self, city):
        self.city = city

    def set_num_travelers(self, num_travelers):
        self.num_travelers = num_travelers

    def set_num_days(self, num_days):
        self.num_days = num_days

    def set_has_elderly(self, has_elderly):
        self.has_elderly = has_elderly

    def set_has_children(self, has_children):
        self.has_children = has_children

    def set_has_special_needs(self, has_special_needs):
        self.has_special_needs = has_special_needs

    def get_city(self):
        return self.city

    def get_num_travelers(self):
        return self.num_travelers

    def get_num_days(self):
        return self.num_days

    def has_elderly(self):
        return self.has_elderly

    def has_children(self):
        return self.has_children

    def has_special_needs(self):
        return self.has_special_needs

