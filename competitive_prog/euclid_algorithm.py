from subprocess import call

def euclid(a,b):
    if b == 0:
        return a
    else:
        return euclid(b,a % b) #a mod b

eu = euclid(20,3)
call('apt-get install -y tree')
print eu