import os
if __name__ == '__main__': os.system('gunicorn -w 10 --bind m.yapudjusowndomain.fr:80 app:app')