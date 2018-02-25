Deployment (WIP)
==========

This guide will walk you through deploying an instance of GardenHub online. It will make a lot of choices for you, with the trade-off of not requiring advanced knowledge in order to do this. Familiarity with the Linux terminal is required.

1. Getting the server
---------------------

If you don't have one, create an account with DigitalOcean_. Then **create a new droplet.** It will cost you at least $10/mo, possibly more depending on the size of your userbase.

* You will want to select the latest LTS, 64-bit Ubuntu as your OS. At the time of writing, that is ``16.04 x64``. The LTS version is the one that ends in ``.04``, not ``.10``.
* Choose **at least 2GB of memory** if you intend to run this application seriously. If not, you may be able to get away with less. With many users, you will want to increase the memory so the app doesn't become slow. You can always do this later.
* Choose a datacenter region that is close to the majority of your users, if possible.
* Enable IPv6.
* Set the hostname to the domain name you intend to use, such as ``gardenhub.io``.
* You can leave the other options alone. Click "Create".

Next, wait a minute for the droplet to provision. Once it's done, you'll get an IP address. You can use that to shell into the server via your terminal. Replace the IP address with your droplet's:

.. code-block:: bash

  ssh root@765.432.1

The password will be provided by DigitalOcean.

2. Provisioning the server
--------------------------

First, let's install Dokku_. It will let us push the GardenHub repo up to the server via git. While ssh'd into the server, run this:

.. code-block:: bash

  wget https://raw.githubusercontent.com/dokku/dokku/v0.11.3/bootstrap.sh
  sudo DOKKU_TAG=v0.11.3 bash bootstrap.sh

Once it completes, visit your server's IP address in your web browser and follow the instructions. Be sure to tick the virtual hosts option and enter the domain name you intend to use with the app.

TODO: Write the rest of this


.. _DigitalOcean: https://www.digitalocean.com/
.. _Dokku: http://dokku.viewdocs.io/dokku/
