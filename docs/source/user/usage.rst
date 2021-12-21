Usage
=====

Once the :ref:`prerequisties` are in place, any modern web client, programming packages with TLS support, etc. can be used to access the APIs. We list examples using Chrome based Web browser, python Request library, cURL and openssl

We assume that the SAE key-certificate pair together with the root CA is already installed in the certificate manager used by the Web browser for the first example. 
In the other examples, the key-certificate pair is in a PEM format in the same directory as that the commands are executed in. 


Web Browser
-----------

.. figure:: images\chrome_choose_cert.png
   :alt: Choose certificate
   
   Chrome prompts which certificate to use to do mutual authentication.
