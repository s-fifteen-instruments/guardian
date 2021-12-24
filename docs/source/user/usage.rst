Usage
=====

Once the :ref:`requirements <prerequisites>` are in place, any modern web client, programming packages with TLS support, etc. can be used to access the APIs. We list examples using Microsoft Edge (Chromium-based) web browser, and Python's ``request`` library, with hostnames ``kme1`` and ``kme2`` indicating the corresponding KMEs that ``sae1`` and ``sae2`` can authenticate respectively.

Web Browser
-----------

In this web browser example, the SAE key-certificate pair together with the root CA is already installed in the certificate manager used by the web browser for the first example. 

We type the URL, ``https://kme1/api/v1/keys/sae2/status`` to get the status of the connection between KME1 to the KME that handles SAE2 which is KME2 in this example. Before the connection continues, the correct certificate needs to be presented to the server for authentication.

.. figure:: ./images/chrome_choose_cert.png
   :alt: Choose certificate
   
   The web browser prompts which certificate to use to do mutual authentication.
   
.. figure:: ./images/chrome_status.png
   :alt: Status of connection to SAE2
   
   After authentication, we receive the response of the GET status method. The default key size is |default_size| bits and other limits are readable here.
   
To request two keys of length 256 bits to use in communicating to sae2, we use the Get Key method by send the URL, ``https://kme1/api/v1/keys/sae2/enc_keys?number=2&size=256``.

.. figure:: ./images/chrome_enc_more_keys.png
   :alt: Response from kme1 to sae1 with 2 keys of length 256 bits each.
   
   Response from kme1 to sae1 with 2 keys of length 256 bits each.
   
The keys are returned in a key container formatted using JSON. The keys are encoded in base64 which pads the final character using ``=`` if the total number of bits is not a multiple of 6 (2^6 = 64). Together with the key is the corresponding key_ID that has to be notified to sae2 for him/her to retrive his/her key from kme2. If the options ``number`` and ``size`` are not defined, kme1 will return the default one key with |default_size| bits.

.. figure:: ./images/chrome_enc_keys.png
   :alt: Response from kme1 to sae1 with one keys of length |default_size| bits.
   
   Without any options, the kme1 returns one key the size of |default_size| bits. 
 
Now sae1 has 3 keys with their corresponding key_IDs. The key_IDs are communicated to sae2 which then calls the Get key with Key ID method.

.. figure:: ./images/chrome_choose_cert_kme2.png
   :alt: Choose certificate to communicate to kme2
   
   The web browser prompts which certificate to use to do mutual authentication for sae2 and kme2.
   
Now we identify as sae2 itself sae2 certificate to kme2. With the Get method we send the URL ``https://kme2/api/v1/keys/sae1/dec_keys?key_ID=3f58ec7a-499b-5a05-b475-dd5f1e78092b``. With the Get method we can only request one key at a time.

.. figure:: ./images/chrome_dec_more_keys.png
   :alt: Get key with Key ID
   
   sae2 retrives the key from KME2.

.. figure:: ./images/chrome_dec_keys.png
   :alt: Get another key with Key ID
   
   sae2 retrives the another key from KME2. ``https://kme2/api/v1/keys/sae1/dec_keys?key_ID=4d90c421-a5fa-55c8-8da6-3e6ebde75477``   

Once the key is retrived, it is deleted from KME2 and a subsequent call is made, an error is reported that the key has been consumed.

.. figure:: ./images/chrome_dec_keys_twice.png
   :alt: Second call of Get key with Key ID with the same key ID
   
   sae2 tries to retrives the same key again from KME2. ``https://kme2/api/v1/keys/sae1/dec_keys?key_ID=4d90c421-a5fa-55c8-8da6-3e6ebde75477``   

With this, ``sae1`` and ``sae2`` both share a set of QKD keys that they can use to communicate with each other.

.. |default_size| replace:: 32


Python
------

In this Python 3 example, the key-certificate pair is in a PEM format in the same directory as that the commands are executed in. Some packages to install first:

.. code-block:: dosbatch
   
   pip install requests python-certifi-win32

In python, the ``requests`` module can be used to dispatch GET/POST calls without a web browser GUI. There are also several ways to do client-side verification of server: here we load the KME's root CA certificate into the Microsoft certificate store as a trusted CA on Windows, and loads this store into Python using ``python-certifi-win32``.

An example script to interface with the API:

.. code-block:: python
   :linenos:
   
   import requests
   cert_path = '/path/to/cert'
   key_path = '/path/to/key'

   status_url = 'https://kme1/api/v1/keys/sae2/status'
   print('Checking connection to kme1...')
   response = requests.get(status_url, cert=(cert_path,key_path))
   print('Connection to kme1 OK.')
   print(response.content)

   get_key_url = 'https://kme1/api/v1/keys/sae2/enc_keys'
   response = requests.get(get_key_url, cert=(cert_path,key_path))
   print(response.content)

Similarly, for a POST request,

.. code-block:: python
   :linenos:
   :lineno-start: 14

   get_key_url = 'https://kme1/api/v1/keys/sae2/enc_keys'
   query = {'number': 1, 'size': 32}
   response = requests.post(get_key_url, cert=(cert_path,key_path), data=query)
   print(response.json())




   

