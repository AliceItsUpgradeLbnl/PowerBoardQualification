#raw_input('Enter your input :')
try:
    mode=int(raw_input('Input:'))
except ValueError:
    print "Not a number"

print 'the ID is: ', mode
