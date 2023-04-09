def choose_item():
    print('Please choose an item:')
    print('1. Issues')
    print('2. Pull Requests')
    choice = int(input('Enter your choice (1 or 2): '))
    while choice not in [1, 2]:
        print('Invalid input. Please try again.')
        choice = int(input('Enter your choice (1 or 2): '))
    return choice
