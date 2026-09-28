def extremely_complex_function(data, flag1, flag2, flag3, flag4, flag5):
    # Додаємо дуже глибоку вкладеність для Cognitive Complexity > 20
    if flag1:
        if flag2:
            for item in data:
                if item > 0:
                    if flag3:
                        if flag4:
                            if flag5:
                                for x in range(10):
                                    if x % 2 == 0:
                                        print(x)
                                    elif x % 3 == 0:
                                        print(x)
                                    else:
                                        print(item)
                        elif not flag4:
                            while item > 10:
                                item -= 1
                    else:
                        print("no flag3")
                elif item < 0:
                    if flag3 or flag4 or flag5:
                        print("negative")

def create_a_bug():
    # Явний баг/помилка на Reliability (застосування undefined variable / divide by zero)
    a = None
    return a.length()  # AttributeError або баг Reliability