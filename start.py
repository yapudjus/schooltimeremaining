import gunicorn
from app import app
if __name__ == '__main__': gunicorn -w10 --bindm.yapudjusowndomain.fr:80 app
