.PHONY: runserver, prepare

runserver:
	EMAIL_HOST=smtp.sendgrid.net EMAIL_HOST_USER=maxim-paas EMAIL_HOST_PASSWORD=pleasechangeme1 python manage.py runserver

prepare:
  python manage.py migrate
  python manage.py populate --email=maxim.millen@gmail.com
