To use vagrant with Varify:

1) Install vagrant and Oracle Virtual box
2) Run Vagrant up to start the virtual machine

Once the machine has been configured:

vagrant ssh (to get a prompt)
"cd varify-env"
". bin/activate" (to activate the virtual environment)
"cd varify"
"pip install -r requirements.txt"

add any necessary settings to your local_settings.py file

do a "make" in the /home/vagrant/varify-env/varify directory

run the development server with python bin/manage.py runserver 0.0.0.0:8000
 access from browser on local machine as 0.0.0.0:8000
