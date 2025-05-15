class Person:
    def __init__(self, name, age):
        self.name = name        # Public attribute
        self.__age = age        # Private attribute (starts with "__")

    def get_age(self):          # Getter method to access the private attribute
        return self.__age

person = Person("Alice", 25)
print(person.name)       # ✅ Accessible
print(person.get_age())  # ✅ Accessible through method
print(person.__age)      # ❌ Error: AttributeError (not directly accessible)

