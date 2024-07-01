class Controller:
    def __init__(self) -> None:
        def func(value):
            print(value)
        
        model = Model(func)
    
    
class Model:
    def __init__(self, func :lambda x: x) -> None:
        print("Valor")
        func(20)
        
        
Controller()