from random import choice

def split(string):
    return [char for char in string]

def draw_board():
    print('\n---------------')
    for line in guess_list:
        word_ = split(word) # characters will be removed to handle yellow letters
        for x in range(5):
            if line[x] == word[x]:
                print(' %s ' %line[x].upper(), end='')
            elif line[x] in word_:
                print('(%s)' %line[x], end='')
                word_[x] = ' '
            else:
                print(' %s ' %line[x], end='')
        print()
    print('---------------')

with open('allowed guesses.txt', encoding='utf-8') as f:
    words = f.read().split('\n')
word = choice(words)

guess_list = [[' ']*5 for x in range(6)]

guesses = 0
while guesses < 6:
    guess = input('\nEnter your guess (5 letters): ').lower()
    if len(guess) != 5:
        print('The guess was not 5 letters.')
        continue
    if guess not in words:
        print('The word has not been recognised.')
        continue
    guess_list[guesses] = split(guess)
    draw_board()
    guesses += 1

    if guess == word:
        print('Found it!')
        break
if guess != word:
    print('Game Over')
    print('The word was:', word)
