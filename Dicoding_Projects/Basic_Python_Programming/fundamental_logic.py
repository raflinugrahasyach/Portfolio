class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f'{self.name} says Woof!'

if __name__ == '__main__':
    my_dog = Dog('Buddy')
    print(my_dog.speak())

